import tornado.httpserver, tornado.web, tornado.ioloop
from shutil import move
from settings import MAX_WORKERS
from sockjs.tornado import SockJSConnection, SockJSRouter
from db_models import insert_to_db, FileLookupByToken
from converter import ConverterTask
import concurrent.futures
import logging
from settings import __UPLOADS__, __COMPRESSED_FILES_FOLDER__, __STATIC__
from STATE import *


class BaseHandler(tornado.web.RequestHandler):
    pass
    # def _handle_request_exception(self, e):
    #     logging.error('Handled exception!')
    #     self.render("static/error.html")


class UploadPostRequestHandler(BaseHandler):

    dest_dir = __UPLOADS__

    def __init__(self, *args, **kwargs):
        self.task = None
        self.data = {}
        logging.debug("Created UploadPostRequestHandler obj %s", self)
        super(UploadPostRequestHandler, self).__init__(*args, **kwargs)

    def get(self):
        self.write("405. Not Allowed")
        # print("New get:", self.data, self)
        # self.render("static/status.html", token=self.data.get('token'), file_url=self.data.get('file_url'))

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
        converter.add_done_callback(lambda x: task.stop_and_delete_original())
        self.data['token'] = file_hash
        self.data['file_url'] = rec_obj.url
        # self.render("static/status.html", token=file_hash, file_url=rec_obj.url
        self.write({'status': "OK", 'token': file_hash})

    def _handle_request_exception(self, e):
        logging.error('Handled exception!')
        self.render("static/error.html")


class MainPageHandler(BaseHandler):
    def get(self):
        self.render("static/index.html")

    def _handle_request_exception(self, e):
        logging.exception("Exception from AAA request.")
        self.render("static/error.html")


class AboutPageHandler(BaseHandler):
    def get(self):
        self.render("static/about.html")


class ContactPageHandler(BaseHandler):
    def get(self):
        self.render("static/contact.html")


class ErrorPage(BaseHandler):
    def get(self):
        self.render("static/error.html")


class ConvertionStatusPage(BaseHandler):
    def get(self, token=None):
        # self.write(token)
        self.render("static/status.html", token=token, file_url=FileLookupByToken(token).page_url())

    def _handle_request_exception(self, e):
        logging.exception("Exception from CONV request.")
        self.render("static/error.html")


class ConvertionStatus(SockJSConnection):

    def __init__(self, *args, **kwargs):
        self.global_obj_key = ""
        SockJSConnection.__init__(self, *args, **kwargs)

    def on_open(self, info):
        print('Someone connected', self, info)

    def on_message(self, token):
        self.global_obj_key = token
        if not GlobalSessionsTable.get(token):
            GlobalSessionsTable[token] = set()
        GlobalSessionsTable[token].add(self)
        print(GlobalSessionsTable[token])

    def on_close(self):
        del GlobalSessionsTable[self.global_obj_key]


class APIHandler(tornado.web.RequestHandler):

    def __operation__(self, operation, id):
        if operation == "stop":
            try:
                ConverterTask.stop_by_pid(_id=id)
            except Exception:
                pass

    def post(self, *args):
        id = args[0]
        self.__operation__(args[1], id)


class FilePageHandler(BaseHandler):
    def get(self, token=None):
        # self.render("static/file_page.html", token=token, url=FileLookupByToken(token).file_url())
        print("DATA:", [x for x in GlobalRunningTaskTable])
        try:
            if not token in GlobalRunningTaskTable:
                self.render("static/file_page.html", token=token, url=FileLookupByToken(token).file_url())
            else:
                self.render("static/status.html", token=token, file_url=FileLookupByToken(token).page_url())

        except IndexError:
            self.write('404. File not Found')

if __name__ == '__main__':

    executor = concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS)
    WsRouter = SockJSRouter(ConvertionStatus, '/ws')

    # Main App
    application = tornado.web.Application([(r"/", MainPageHandler), (r'/uploaded', UploadPostRequestHandler),
                                           (r"/status/(.*)", ConvertionStatusPage),
                                           (r"/static/(.*)", tornado.web.StaticFileHandler, {"path": __STATIC__}),
                                           (r"/get/(.*)", tornado.web.StaticFileHandler, {"path": __COMPRESSED_FILES_FOLDER__}),
                                           (r"/file/([^/]*)", FilePageHandler),
                                           (r"/about", AboutPageHandler),
                                           (r"/contact", ContactPageHandler),
                                           (r"/error", ErrorPage),
                                           (r"/api/video/(.*)/(.*)", APIHandler)])

    # Sockets App
    ws_app = tornado.web.Application(WsRouter.urls)

    application.listen(8080)
    ws_app.listen(8084)

    app = tornado.ioloop.IOLoop()
    app.instance().start()
