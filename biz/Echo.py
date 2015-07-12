# coding: utf-8
import tornado.websocket

from lib.tools import Log


logger = Log().getLog()


class EchoWebSocket(tornado.websocket.WebSocketHandler):
    def check_origin(self, origin):
        return True

    def open(self):
        # print("WebSocket opened")
        logger.info('opened!')

    def on_message(self, message):
        self.write_message(u"You said: " + message)

    def on_close(self):
        print("WebSocket closed")