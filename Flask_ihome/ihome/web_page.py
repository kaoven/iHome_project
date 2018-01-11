# coding:utf-8

from flask import Blueprint, current_app, make_response
from flask_wtf import csrf


html = Blueprint('html', __name__)


@html.route('/<re(r".*"):file_name>')
def get_html_file(file_name):
    """提供静态的html文件"""
    if not file_name:
        file_name = "index"

    if file_name != "favicon.ico":
        file_name = "html/" + file_name

    resp = make_response(current_app.send_static_file(file_name+'.html'))

    # 生成csrf_token的随机字符串的值
    csrf_token = csrf.generate_csrf()
    # 设置csrf到cookie
    resp.set_cookie("csrf_token", csrf_token)
    return resp
