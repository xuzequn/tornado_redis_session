# -*- coding:utf-8 -*-

import os
import sys
from session import *
from tornado.ioloop import IOLoop
import tornado
import session
from testhandler import HelloHandler, TestGetHandler
from tornado.web import Application, url
from tornado.options import define, options

reload(sys)
sys.setdefaultencoding('utf-8')

from base import BaseHandler
from tornado.web import HTTPError


def login_required(f):
    def _wrapper(self, *args, **kwargs):
        print self.get_current_user()
        logged = self.get_current_user()
        if logged == None:
            self.write('no login')
            self.finish()
        else:
            ret = f(self, *args, **kwargs)
    return _wrapper


class Application(tornado.web.Application):
    def __init__(self):
        settings = dict(
            cookie_secret="e446976943b4e8442f099fed1f3fea28462d5832f483a0ed9a3d5d3859f==78d",
            session_secret="3cdcb1f00803b6e78ab50b466a40b9977db396840c28307f428b25e2277f1bcc",
            session_timeout=60,
            store_options={
                'redis_host': 'localhost',
                'redis_port': 6379,
                'redis_pass': ''
            },
        )
        handlers = [
            (r'/test', TestGetHandler),
            (r'/hello', HelloHandler)
        ]
        tornado.web.Application.__init__(self, handlers, **settings)
        self.session_manager = session.SessionManager(settings['session_secret'],
                                                      settings['store_options'],
                                                      settings['session_timeout'])


define('port', default=8888, group='application')
if __name__ == '__main__':
    application = Application()
    print "Application start on port: ", options.port
    application.listen(options.port)

    tornado.ioloop.IOLoop.instance().start()
