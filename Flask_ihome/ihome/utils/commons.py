# coding:utf-8

from werkzeug.routing import BaseConverter
import functools
from flask import session, g, jsonify
from ihome.utils.response_code import RET


class ReConverter(BaseConverter):
    def __init__(self, url_map, regex):
        super(ReConverter, self).__init__(url_map)
        self.regex = regex


def login_require(view_func):
    """登录验证装饰器"""
    @functools.wraps(view_func)
    def wrapper(*args, **kwargs):
        user_id = session["user_id"]
        if user_id is not None:
            # 将用户的id保存在g对象中，以便在视图函数中使用
            g.user_id = user_id
            # 如果用户已登录，则执行视图函数
            return view_func(*args, **kwargs)
        else:
            return jsonify(errcode=RET.SESSIONERR, errmsg="用户未登录")
    return wrapper
