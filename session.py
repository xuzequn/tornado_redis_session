# -*- coding:utf-8 -*-
import uuid
import hmac
import ujson
import hashlib
import redis


__author__ = 'karldoenitz'


"""
需要安装的第三方库：
python的redis连接：http://pypi.python.org/pypi?%3Aaction=search&term=redis&submit=search
需要ujson
安装方法：sudo easy_install ujson
"""


class SessionData(dict):
    """
    hmac:
        Hash-based message authentication code，利用哈希算法，以一个密钥和一个消息为输入，生成一个消息摘要作为输出
    """
    def __init__(self, session_id, hmac_key):
        self.session_id = session_id
        self.hmac_key = hmac_key


class Session(SessionData):
    def __init__(self, session_manager, request_handler):
        self.session_manager = session_manager
        self.request_handler = request_handler
        try:
            current_session = session_manager.get(request_handler)
        except InvalidSessionException:
            current_session = session_manager.get()
        for key, data in current_session.iteritems():
            self[key] = data
        self.session_id = current_session.session_id
        self.hmac_key = current_session.hmac_key

    def save(self):
        self.session_manager.set(self.request_handler, self)


class SessionManager(object):
    """
    redis的地址，端口和密码
    """
    def __init__(self, secret, store_options, session_timeout):
        self.secret = secret
        self.session_timeout = session_timeout
        try:
            if store_options['redis_pass']:
                self.redis = redis.StrictRedis(host=store_options['redis_host'], port=store_options['redis_port'], password=store_options['redis_pass'])
            else:
                self.redis = redis.StrictRedis(host=store_options['redis_host'], port=store_options['redis_port'])
        except Exception as e:
            print e

    def _fetch(self, session_id):
        try:
            session_data = raw_data = self.redis.get(session_id)
            if raw_data:
                self.redis.setex(session_id, self.session_timeout, raw_data)
                session_data = ujson.loads(raw_data)
            if isinstance(session_data, dict):
                return session_data
            else:
                return {}
        except IOError:
            return {}

    def get(self, request_handler=None):
        if not request_handler:
            session_id = None
            hmac_key = None
        else:
            session_id = request_handler.get_secure_cookie("session_id")
            hmac_key = request_handler.get_secure_cookie("verification")
        if not session_id:
            session_exists = False
            session_id = self._generate_id()
            hmac_key = self._generate_hmac(session_id)
        else:
            session_exists = True
        check_hmac = self._generate_hmac(session_id)
        if hmac_key != check_hmac:
            raise InvalidSessionException()
        session = SessionData(session_id, hmac_key)
        if session_exists:
            session_data = self._fetch(session_id)
            for key, data in session_data.iteritems():
                session[key] = data
        return session

    def set(self, request_handler, session):
        request_handler.set_secure_cookie("session_id", session.session_id)
        request_handler.set_secure_cookie("verification", session.hmac_key)
        session_data = ujson.dumps(dict(session.items()))
        self.redis.setex(session.session_id, self.session_timeout, session_data)

    def _generate_id(self):
        new_id = hashlib.sha256(self.secret + str(uuid.uuid4()))
        return new_id.hexdigest()

    def _generate_hmac(self, session_id):
        return hmac.new(session_id, self.secret, hashlib.sha256).hexdigest()


#此处可以自定义异常处理
class InvalidSessionException(Exception):
    pass