import tornado.httpserver, tornado.web, tornado.ioloop, os.path
from shutil import move
from sockjs.tornado import SockJSConnection, SockJSRouter, proto
import sqlite3, sqlalchemy
from db_models import session, FileLookup
import queue
from converter import ConverterQueue
import asyncio
import zmq

context = zmq.Context()



__UPLOADS__ = "uploads/"

# db = sqlite3.connect('compressor_db')
# db = sqlalchemy.create_engine('sqlite:///compressor_db')

# def instert_to_db(_md5_name, _file_name):
#     cursor = db.
#     md5_name = _md5_name
#     file_name = _file_name
#
#     cursor.execute('''INSERT INTO files(md5_name, real_name)
#                       VALUES(?,?)''', (md5_name, file_name))
#     print('inserted!')
#     db.commit()

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


        socket = context.socket(zmq.REQ)
        socket.connect("tcp://localhost:5555")
        socket.send(b"Hello")


        self.redirect('/status')



class ConvertionStatusPage(tornado.web.RequestHandler):
    def get(self):
        self.render("static/status.html")

class ConvertionStatus(SockJSConnection):

    def on_open(self, info):
        print('SOMEONE CONNECTED!!!')
        self.loop = tornado.ioloop.PeriodicCallback(self._send_stats, 1000)
        self.loop.start()

    def on_message(self, data):
        pass

    def on_close(self):
        self.loop.stop()

    def _send_stats(self):
        data = "IM FINE!"
        self.send(data)


WsRouter = SockJSRouter(ConvertionStatus, '/ws')


@asyncio.coroutine
def hello_world():
    print("Hello World!")
    import random, time
    time.sleep(random.randint(10, 100) / 1000.0)
    print("Done")


application = tornado.web.Application([(r'/upload', RequestHandler), (r'/status', ConvertionStatusPage)],)
ws_app = tornado.web.Application(WsRouter.urls)


if __name__=='__main__':

    application.listen(8080)
    ws_app.listen(8084)
 
    tornado.ioloop.IOLoop.instance().start()

    loop = asyncio.get_event_loop()
    # Blocking call which returns when the hello_world() coroutine is done
    loop.run_until_complete(hello_world())
    loop.close()
