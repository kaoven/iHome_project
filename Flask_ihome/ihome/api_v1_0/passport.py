# coding:utf-8

from . import api
from flask import request, jsonify, current_app, session
from ihome.utils.response_code import RET
import re
from ihome import redis_store, db
from werkzeug.security import generate_password_hash
from ihome.models import User
from sqlalchemy.exc import IntegrityError  # 如果字段的约束有nuique,在保存数据时如果该字段重复，则抛出此异常


# POST /user
@api.route('/users', methods=["POST"])
def register():
    # 接收参数，手机号，短信验证码，密码，确认密码
    req_dict = request.get_json()
    mobile = req_dict.get("mobile")
    sms_code = req_dict.get("sms_code")
    password = req_dict.get("password")
    password2 = req_dict.get("password2")

    # 验证信息
    if not all([mobile, sms_code, password, password2]):
        return jsonify(errcode=RET.PARAMERR, errmsg="数据不完整")

    # 验证手机号码格式
    if not re.match(r'1[3456789]\d{9}', mobile):
        return jsonify(errcode=RET.PARAMERR, errmsg="手机号不合法")

    # 验证密码的一致
    if password != password2:
        return jsonify(errcode=RET.PARAMERR, errmsg="两次密码输入不一致")

    # 从redis中获取保存的短信验证码
    try:
        real_sms_code = redis_store.get('sms_code_%s'%mobile)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errcode=RET.DBERR, errmsg="数据库异常")

    # 验证短信验证码是否有效
    if real_sms_code is None:
        return jsonify(errcode=RET.NODATA, errmsg="验证码已过期")

    # 验证验证码是否正确
    if sms_code != real_sms_code:
        return jsonify(errcode=RET.PARAMERR, errmsg="验证码错误")

    # 对密码进行加密处理
    password_hash = generate_password_hash(password)

    # 将用户的数据保存在数据库中
    user = User(
        name=mobile,
        password_hash=password_hash,
        mobile=mobile
    )
    try:
        db.session.add(user)
        db.session.commit()
    except IntegrityError as e:
        # 表示手机号已经被注册过
        return jsonify(errcode=RET.DATAEXIST, errmsg="手机号已被注册")
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errcode=RET.DBERR, errmsg="保存用户数据异常")

    # 用session保存登录状态
    session["user_id"] = user.id
    session["mobile"] = mobile
    session["username"] = mobile

    # 返回注册成功的信息
    return jsonify(errcode=RET.OK,errmsg="注册成功", data={"user_id":user.id})
