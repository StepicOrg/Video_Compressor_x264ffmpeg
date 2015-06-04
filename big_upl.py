import tornado.httpserver, tornado.web, tornado.ioloop, os.path
from shutil import move
from sockjs.tornado import SockJSConnection, SockJSRouter, sessioncontainer
import sqlite3, sqlalchemy
from db_models import session, FileLookup
import queue
from converter import ConverterQueue, ConverterTask
import asyncio
import zmq
from STATE import GlobalSessionsTable


context = zmq.Context()


__UPLOADS__ = "uploads"
__COMPRESSED_FILES_FOLDER__ = "ready"

mainQueue = queue.Queue(0)
converterQueue = ConverterQueue(mainQueue)
WORKERS = 4



def insert_to_db(md5_name, file_name):
    new_file = FileLookup(md5_name=md5_name, real_name=file_name)
    session.add(new_file)
    session.commit()


class RequestHandler(tornado.web.RequestHandler):

    dest_dir = __UPLOADS__

    def get(self):
        pass

    def post(self):
        fname = self.request.body_arguments.get('infile_name')[0].decode("utf-8")
        content_type = self.request.body_arguments.get('infile_content_type', None)[0].decode("utf-8")
        file_path = self.request.body_arguments.get('infile_path', '')[0].decode("utf-8")
        file_size = self.request.body_arguments.get('infile_size', -1)[0].decode("utf-8")
        file_hash = self.request.body_arguments.get('infile_md5', '')[0].decode("utf-8")
        file_ext = fname.split('.')[-1]
        new_fname = ".".join([file_hash, file_ext])
        move(file_path, '%s/%s' % (self.dest_dir, new_fname))
        insert_to_db(new_fname, fname)

        # socket = context.socket(zmq.REQ)
        # socket.connect("tcp://localhost:5555")
        # socket.send(b"Hello")

        global converterQueue
        global mainQueue
        task = ConverterTask('%s/%s' % (self.dest_dir, new_fname), '%s/%s' % (__COMPRESSED_FILES_FOLDER__, new_fname), curr=file_hash)
        GlobalSessionsTable[file_hash] = 0
        if converterQueue.is_empty():
            mainQueue = queue.Queue(0)
            converterQueue = ConverterQueue(mainQueue)
            mainQueue.put(task)
            converterQueue.start()
        else:
            mainQueue.put(task)

        self.render("static/status.html", token=file_hash)


class MainPageHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("static/index.html")

class ConvertionStatusPage(tornado.web.RequestHandler):
    def get(self):
        self.render("static/status.html")

class ConvertionStatus(SockJSConnection):

    def on_open(self, info):
        import random
        print('SOMEONE CONNECTED!!!', self)
        # self.loop = tornado.ioloop.PeriodicCallback(self._send_stats, 1000)
        # self.r = random.randint(10, 100000)
        # self.loop.start()

    def on_message(self, data):
        GlobalSessionsTable[data] = self

    # def on_close(self):
    #     self.loop.stop()

    # def _send_stats(self):
    #     data = self.r
    #     self.send(data)


WsRouter = SockJSRouter(ConvertionStatus, '/ws')



#Main App
static_path = os.path.join(os.path.dirname(__file__), "static")
application = tornado.web.Application([(r'/', MainPageHandler), (r'/upload', RequestHandler),
                                       (r'/status', ConvertionStatusPage),
                                       (r"/static/(.*)", tornado.web.StaticFileHandler, {"path": static_path})])

#Sockets App
ws_app = tornado.web.Application(WsRouter.urls)


if __name__=='__main__':

    application.listen(8080)
    ws_app.listen(8084)
 
    tornado.ioloop.IOLoop.instance().start()
