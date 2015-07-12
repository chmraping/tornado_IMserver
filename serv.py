# coding: utf-8
import getopt

import tornado

from lib.autoconf import *
from lib import path
from lib.tools import Log
from biz import core


def prepare(conf_file):
    cpff = ConfigParserFromFile()
    conf_file | E(cpff.parseall) | E(conf_drawer.setup)


if __name__ == "__main__":
    port = 8888
    includes = None
    opts, argvs = getopt.getopt(sys.argv[1:], "c:p:h")
    for op, value in opts:
        if op == '-c':
            includes = value
            path._ETC_PATH = os.path.dirname(os.path.abspath(value))
        elif op == '-p':
            port = int(value)
        elif op == '-h':
            print u'''使用参数启动:
                        usage: [-p|-c]
                        -p [prot] ******启动端口,默认端口:%d
                        -c <file> ******加载配置文件
                   ''' % port
            sys.exit(0)
    if not includes:
        includes = os.path.join(path._ETC_PATH, 'includes_dev.json')
        print "no configuration found!,will use [%s] instead" % includes
    prepare(includes)

    app = core.Application()
    app.listen(port)
    logger = Log().getLog()
    logger.info("starting..., listen [%d], configured by (%s)", port, includes)
    tornado.ioloop.IOLoop.instance().start()
