import tornado.httpserver, tornado.web, tornado.ioloop, os.path
from shutil import move
from sockjs.tornado import SockJSConnection, SockJSRouter
from db_models import session, FileLookup
from converter import ConverterTask
from STATE import GlobalSessionsTable, renew_queue, converterQueue, mainQueue


__UPLOADS__ = "uploads"
__COMPRESSED_FILES_FOLDER__ = "ready"


def insert_to_db(md5_name, file_name):
    new_file = FileLookup(md5_name=md5_name, real_name=file_name,
                           token="".join(str(md5_name).split(".")[0:-1]))
    session.add(new_file)
    session.commit()
    return new_file


class RequestHandler(tornado.web.RequestHandler):

    dest_dir = __UPLOADS__

    def get(self):
        pass

    def post(self):
        print(self.request.body_arguments)
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
        GlobalSessionsTable[file_hash] = 0
        if converterQueue.is_empty():
            renew_queue(task)
        else:
            mainQueue.put(task)

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

class FileHandler(tornado.web.RequestHandler):
    def get(self, token=None):
        try:
            url=session.query(FileLookup).filter(FileLookup.token==token)[0].url
            print(url)
        except IndexError:
            url="None"
        self.render("static/file_page.html", token=token, url=url)




WsRouter = SockJSRouter(ConvertionStatus, '/ws')

#Main App
static_path = os.path.join(os.path.dirname(__file__), "static")
get_files_path = os.path.join(os.path.dirname(__file__), "ready")
application = tornado.web.Application([(r'/', MainPageHandler), (r'/upload', RequestHandler),
                                       (r'/status', ConvertionStatusPage),
                                       (r"/static/(.*)", tornado.web.StaticFileHandler, {"path": static_path}),
                                       (r"/get/(.*)", tornado.web.StaticFileHandler, {"path": get_files_path}),
                                       (r"/file/([^/]*)", FileHandler)])

#Sockets App
ws_app = tornado.web.Application(WsRouter.urls)


if __name__=='__main__':

    application.listen(8080)
    ws_app.listen(8084)
 
    tornado.ioloop.IOLoop.instance().start()