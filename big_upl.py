import tornado.httpserver, tornado.web, tornado.ioloop
from shutil import move
from settings import MAX_WORKERS
from sockjs.tornado import SockJSConnection, SockJSRouter
from db_models import session, MainDatabase, insert_to_db, FileLookupByToken
from converter import ConverterTask
from STATE import GlobalSessionsTable
import concurrent.futures
import os
from settings import __UPLOADS__, __COMPRESSED_FILES_FOLDER__, __STATIC__

class UploadPostRequestHandler(tornado.web.RequestHandler):

    dest_dir = __UPLOADS__

    def get(self):
        self.write("405. Not Allowed")

    def post(self):
        fname = self.request.body_arguments.get('infile_name')[0].decode("utf-8")
        content_type = self.request.body_arguments.get('infile_content_type', None)[0].decode("utf-8")
        file_path = self.request.body_arguments.get('infile_path', '')[0].decode("utf-8")
        file_size = self.request.body_arguments.get('infile_size', -1)[0].decode("utf-8")
        file_hash = self.request.body_arguments.get('infile_md5', '')[0].decode("utf-8")
        file_ext = fname.split('.')[-1]
        new_fname = ".".join([file_hash, file_ext])
        move(file_path, '%s/%s' % (self.dest_dir, new_fname))
        rec_obj = insert_to_db(new_fname, fname)

        task = ConverterTask('%s/%s' % (self.dest_dir, new_fname), '%s/%s' % (__COMPRESSED_FILES_FOLDER__, new_fname), curr=file_hash)
        converter = executor.submit(task.run)
        converter.add_done_callback(lambda x: GlobalSessionsTable[task.watchers].send('done'))
        self.render("static/status.html", token=file_hash, file_url=rec_obj.url)


class MainPageHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("static/index.html")

class ConvertionStatusPage(tornado.web.RequestHandler):
    def get(self):
        self.render("static/status.html")

class ConvertionStatus(SockJSConnection):

    def __init__(self, *args, **kwargs):
        self.global_obj_key = ""
        SockJSConnection.__init__(self, *args, **kwargs)

    def on_open(self, info):
        print('Someone connected', self, info)

    def on_message(self, data):
        self.global_obj_key = data
        GlobalSessionsTable[data] = self

    def on_close(self):
        del GlobalSessionsTable[self.global_obj_key]

class FilePageHandler(tornado.web.RequestHandler):
    def get(self, token=None):
        try:
            self.render("static/file_page.html", token=token, url=FileLookupByToken(token).file_url())
        except IndexError:
            self.write('404. File not Found')


if __name__ == '__main__':

    executor = concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS)
    WsRouter = SockJSRouter(ConvertionStatus, '/ws')

    # Main App
    application = tornado.web.Application([(r'/', MainPageHandler), (r'/uploaded', UploadPostRequestHandler),
                                           (r'/status', ConvertionStatusPage),
                                           (r"/static/(.*)", tornado.web.StaticFileHandler, {"path": __STATIC__}),
                                           (r"/get/(.*)", tornado.web.StaticFileHandler, {"path": __COMPRESSED_FILES_FOLDER__}),
                                           (r"/file/([^/]*)", FilePageHandler)])

    # Sockets App
    ws_app = tornado.web.Application(WsRouter.urls)

    application.listen(8080)
    ws_app.listen(8084)

    tornado.ioloop.IOLoop.instance().start()
