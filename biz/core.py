# coding: utf-8
import os
import sys
import json
from types import FunctionType

import tornado.web
import tornado.ioloop
import tornado.web
from lxml import etree

from lib.autoconf import conf_drawer
from lib import path
from lib.tools import XMLUtils
from lib.halo import executor
from lib.tools import Log
from lib.web.err import BizError


logger = Log().getLog()


@conf_drawer.register_my_setup()
def setup():
    # automic scan dirs
    files_list = os.listdir(path._BIZ_PATH)
    files_list = set(['.'.join([os.path.basename(path._BIZ_PATH), x[:x.rfind(".")]])
                      for x in files_list if x.endswith(".py")])
    map(__import__, files_list)


class Application(tornado.web.Application):
    handlers = []

    @classmethod
    def register(cls, **kwargs):
        args = kwargs
        path = kwargs.get('path')

        def deco(Handler):
            clazz = Handler
            if path not in [k for k, v in Application.handlers]:
                Application.handlers.append((path, clazz))
            else:
                logger.critical('PATH[%s] conflicts!')
                sys.exit(1)
            return Handler

        return deco

    def __init__(self):
        settings = {
            'xsrf_cookies': False
        }
        if Application.handlers:
            super(Application, self).__init__(Application.handlers, settings)
        else:
            logger.critical('no handlers found in application\'s settings')
            sys.exit(1)


def call_wrap(call, hnd, *args, **kwargs):
    try:
        hnd.set_header('Content-Type', 'application/json')
        res = call(hnd, *args, **kwargs) or ''
        ret = {
            'status': '100',
            'message': 'OK',
            'data': res
        }
        if isinstance(ret, dict):
            ret = json.dumps(ret)
        tornado.ioloop.IOLoop.instance().add_callback(lambda: hnd.finish(ret))
    except BizError, e:
        ret = {
            'status': e.code,
            'message': e.reason,
        }
        tornado.ioloop.IOLoop.instance().add_callback(lambda: hnd.finish(json.dumps(ret)))
    except Exception, e:
        logger.exception(e)
        tornado.ioloop.IOLoop.instance().add_callback(lambda: hnd.send_error(500))


class ThreadBaseMeta(type):
    @classmethod
    def _meta_call(cls, func):
        fun = tornado.web.asynchronous(func)
        return fun

    def __new__(mcs, name, fathers, attrs):
        # print mcs
        for name, value in attrs.iteritems():
            if name in ['get', 'post', 'delete', 'head', 'put', 'options', 'patch'] and type(value) == FunctionType:
                value = mcs._meta_call(value)
                attrs[name] = value
                # return type.__new__(mcs, name, fathers, attrs)
        return super(ThreadBaseMeta, mcs).__new__(mcs, name, fathers, attrs)


class ThreadBasedHandler(tornado.web.RequestHandler):
    __metaclass__ = ThreadBaseMeta

    def prepare(self):
        # 获得正确的客户端ip
        ip = self.request.headers.get("X-Real-Ip", self.request.remote_ip)
        ip = self.request.headers.get("X-Forwarded-For", ip)
        ip = ip.split(',')[0].strip()
        self.request.remote_ip = ip
        # 允许跨域请求
        req_origin = self.request.headers.get("Origin")
        if req_origin:
            self.set_header("Access-Control-Allow-Origin", req_origin)
            self.set_header("Access-Control-Allow-Credentials", "true")
            self.set_header("Allow", "GET, HEAD, POST")
            if self.request.method == "OPTIONS":
                self.set_header("Access-Control-Allow-Methods", "POST, GET, OPTIONS")
                self.set_header("Access-Control-Allow-Headers", "Accept, Cache-Control, Content-Type")
                self.finish()
                return
            else:
                self.set_header("Cache-Control", "no-cache")
        #
        # 参数处理
        self.json_args = {}
        # json格式请求
        if self.request.headers.get('Content-Type', '').find("application/json") >= 0:
            try:
                self.json_args = json.loads(self.request.body)
            except Exception as ex:
                self.send_error(400)
        # xml格式请求
        elif self.request.headers.get('Content-Type', '').find('application/xml') >= 0:
            try:
                xu = XMLUtils()
                xml = self.request.body
                root = etree.fromstring(xml)
                root_dict = xu.parseElement(root)
                self.json_args = root_dict
            except Exception, e:
                self.send_error(501)
        # 普通参数请求
        elif self.request.arguments:
            self.json_args = dict((k, v[-1]) for k, v in self.request.arguments.items())

    @classmethod
    def threadable(cls, func):
        def deco(*args, **kwargs):
            if func.__name__ not in ['get', 'post', 'delete', 'head', 'put', 'options', 'patch']:
                # fun = tornado.web.asynchronous(func)
                executor.submit(call_wrap, func, *args, **kwargs)
            else:
                return func(*args, **kwargs)

        return deco