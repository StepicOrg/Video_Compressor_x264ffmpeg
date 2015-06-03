# -*- coding: utf-8 -*-

import tornado.ioloop
import tornado.web
import tornado.gen
import time
from tornado.web import RequestHandler
import os, uuid
from sockjs.tornado.stats import StatsCollector

from sockjs.tornado import SockJSConnection, SockJSRouter, proto


__UPLOADS__ = "uploads/"

class IndexHandler(tornado.web.RequestHandler):
    """Regular HTTP handler to serve the ping page"""
    def get(self):
        self.render('index.html')

    def post(self):
        print("something posted!")

@tornado.web.stream_request_body
class UploadHandler(tornado.web.RequestHandler):
    # def post(self):
    #     fileinfo = self.request.files['filearg'][0]
    #     # print("fileinfo is", fileinfo)
    #     fname = fileinfo['filename']
    #     extn = os.path.splitext(fname)[-1]
    #     cname = str(uuid.uuid4()) + extn
    #     fh = open(__UPLOADS__ + cname, 'wb')
    #     fh.write(fileinfo['body'])
    #     self.finish(cname + " is uploaded!! Check %s folder" %__UPLOADS__)

    @tornado.web.asynchronous
    def post(self):
        pass

    def upload_complete(self, response):
        if response.error:
            self.finish()
            raise response.error

        self.write({
            'size': int(self.request.headers['Content-Length']),
            'sha256': self.hash.hexdigest(),
            'timeTaken': time.time() - self.start_time
        })
        self.finish()

    def upload_file(self):
        raise NotImplemented()

    @tornado.gen.coroutine
    def data_received(self, data):
        yield self.q.put(data)
        self.hash.update(data)

        if not self.upload_started:
            # Make sure there is at least one chunk in the queue
            self.upload_started = True
            self.upload_file()




class StatsHandler(tornado.web.RequestHandler):
    def get(self):
        self.render('stats.html')


# Out broadcast connection
class BroadcastConnection(SockJSConnection):
    clients = set()

    def on_open(self, info):
        self.clients.add(self)

    def on_message(self, msg):
        self.broadcast(self.clients, msg)

    def on_close(self):
        self.clients.remove(self)

BroadcastRouter = SockJSRouter(BroadcastConnection, '/broadcast')


class StatsConnection(SockJSConnection):
    clients = set()

    def on_open(self, info):
        self.clients.add(self)
        self.loop = tornado.ioloop.PeriodicCallback(self._send_stats, 1000)
        self.loop.start()

    def on_message(self, message):
        print(message)

    def on_close(self):
        self.loop.stop()
        self.clients.remove(self)

    def _send_stats(self):
        data = "Connected!"
        print([o.session.session_id for o in self.clients])
        self.send(data)

StatsRouter = SockJSRouter(StatsConnection, '/statsconn')

if __name__ == "__main__":
    import logging
    logging.getLogger().setLevel(logging.DEBUG)

    # Create application
    app = tornado.web.Application(
            [(r"/", IndexHandler), (r"/stats", StatsHandler),
            (r"/upload", UploadHandler)] +
            BroadcastRouter.urls +
            StatsRouter.urls
    )
    app.listen(8084)

    print('Listening on 0.0.0.0:8084')

    tornado.ioloop.IOLoop.instance().start()
