# coding: utf-8
import tornado.websocket

from core import *
from objs.User import *
from objs.Message import Msg


class Operations(object):
    def login(self, username):
        user = User(username)
        user.login()
        return user.uid

    def logout(self, uid):
        user = UserPool.select_user(uid)
        user.logout()

    def set_notifier(self, uid, handler):
        user = UserPool.select_user(uid)
        user.set_notify_handler(handler)

    def talk_to(self, from_uid, to_uid, s_msg):
        from_user = UserPool.select_user(from_uid)
        # to_user = UserPool.select_user(to_uid)
        from_user.talk_to(to_uid, Msg(content=s_msg, level=Level.user | Level.info))


@Application.register(path='/user/byname/(\w+)/login')
class Login(ThreadBasedHandler):
    def get(self, username):
        self.bins(username)

    @ThreadBasedHandler.threadable
    def bins(self, username):
        uid = Operations().login(username)
        return {
            'uid': uid,
            'op': 'login',
        }


@Application.register(path='/user/byid/(\w+)/logout')
class Logout(ThreadBasedHandler):
    def get(self, uid):
        self.bins(uid)

    @ThreadBasedHandler.threadable
    def bins(self, uid):
        Operations().logout(uid)
        return {
            'op': 'logout'
        }


@Application.register(path='/user/byid/(\w+)')
class EchoWebSocket(tornado.websocket.WebSocketHandler):
    def check_origin(self, origin):
        return True

    def open(self, uid):
        # print("WebSocket opened")
        logger.info('opened!%s', uid)
        self.uid = uid
        Operations().set_notifier(self.uid, self)

    def on_message(self, message):
        try:
            o_msg = json.loads(message)
            to_uid = o_msg['to_uid']
            content = o_msg['content']
            Operations().talk_to(self.uid, to_uid, content)
        except Exception, e:
            logger.exception(e)
            self.close(500)

    def on_close(self):
        print("WebSocket closed")