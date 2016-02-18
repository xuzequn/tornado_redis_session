# -*- coding:utf-8 -*-
from base import BaseHandler


class HelloHandler(BaseHandler):
    def get(self):
        l = []
        hello = self.get_argument('non1')
        world = self.get_argument('non2')
        print self.session
        l.append(hello)
        l.append(world)
        l.append(self.session['first_session_value'])
        self.render('./templates/hello.html', page_object=l)


class TestGetHandler(BaseHandler):
    def get(self):
        test = self.get_argument('test', '')
        self.session['first_session_value'] = '来offer啊'
        self.session.save()
        print self.session
        self.write(test)
        self.finish()
