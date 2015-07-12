# coding: utf-8
import threading
import time

from Message import *
from lib.tools import Log


logger = Log().getLog()


class User(object):
    __slots__ = ('uid', 'username', 'notify_handler')

    def __init__(self, username):
        self.username = username

    def set_notify_handler(self, handler):
        self.notify_handler = handler
        UserPool.mod_user(self.uid, self)

    def login(self):
        self.uid = str(int(UserPool._max_uid) + 1)
        UserPool.mod_user(self.uid, self)
        logger.info('%s(%s) login!', self.username, self.uid)
        UserPool.broadcast(Msg(level=Level.sys | Level.info,
                               title='New Player',
                               content='%s - %s came in!' % (time.strftime('%X'), self.username)).toString())

    def logout(self):
        self.notify_handler = None
        UserPool.delete_user(self.uid)
        logger.info('%s(%s) logout!', self.username, self.uid)
        UserPool.broadcast(Msg(level=Level.sys | Level.info,
                               title='New Player',
                               content='%s - %s just left!' % (time.strftime('%X'), self.username)).toString())

    def talk_to(self, uid, msg):
        obj_user = UserPool.select_user(uid)
        if not obj_user or not obj_user.notify_handler:
            self.notify_handler.write_message(Msg(content='user is not online who you talked to',
                                                  level=Level.sys | Level.warn).toString())
            return
        try:
            obj_user.notify_handler.write_message(msg.toString())
        except Exception, e:
            logger.info(e)


class UserPool(object):
    users = {}
    _lock = threading.Lock()
    _max_uid = 0

    @classmethod
    def mod_user(cls, uid, user):
        with cls._lock:
            cls.users[uid] = user
            cls._max_uid = uid

    @classmethod
    def select_user(cls, uid):
        return cls.users[uid]

    @classmethod
    def delete_user(cls, uid):
        with cls._lock:
            cls.users.pop(uid)

    @classmethod
    def broadcast(cls, msg):
        for uid, user in cls.users.iteritems():
            try:
                user.notify_handler.write_message(msg) if user.notify_handler else None
            except Exception, e:
                pass