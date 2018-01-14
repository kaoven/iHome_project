# coding:utf-8

from . import api
from flask import request, jsonify, current_app, session
from ihome.utils.response_code import RET
import re
from ihome import redis_store, db
from ihome.models import User
from sqlalchemy.exc import IntegrityError  # 如果字段的约束有nuique,在保存数据时如果该字段重复，则抛出此异常
from ihome import constants


# POST /users
@api.route('/users', methods=["POST"])
def register():
    """注册用户"""
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
        real_sms_code = redis_store.get('sms_code_%s' % mobile)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errcode=RET.DBERR, errmsg="数据库异常")

    # 验证短信验证码是否有效
    if real_sms_code is None:
        return jsonify(errcode=RET.NODATA, errmsg="验证码已过期")

    # 验证验证码是否正确
    if sms_code != real_sms_code:
        return jsonify(errcode=RET.PARAMERR, errmsg="验证码错误")

    # 将用户的数据保存在数据库中
    user = User(
        name=mobile,
        password_hash="",
        mobile=mobile
    )

    # 对密码进行加密处理(原始方法)
    # password_hash = generate_password_hash(password)

    # 调用对象方法更新对象的password_hash属性
    user.password = password

    try:
        db.session.add(user)
        db.session.commit()
    except IntegrityError as e:
        # 表示手机号已经被注册过
        return jsonify(errcode=RET.DATAEXIST, errmsg="手机号已被注册")
    except Exception as e:
        # 进行回滚
        db.session.rollback()
        current_app.logger.error(e)
        return jsonify(errcode=RET.DBERR, errmsg="保存用户数据异常")

    # 用session保存登录状态
    session["user_id"] = user.id
    session["mobile"] = mobile
    session["username"] = mobile

    # 返回注册成功的信息
    return jsonify(errcode=RET.OK, errmsg="注册成功", data={"user_id": user.id})


# POST /session  请求参数mobile,password
@api.route('/sessions', methods=["POST"])
def login():
    """登录"""
    # 接收参数
    req_dict = request.get_json()
    mobile = req_dict.get("mobile")
    password = req_dict.get("password")
    # 验证参数
    if not all([mobile, password]):
        return jsonify(errcode=RET.PARAMERR, errmsg="参数不完整")

    # 验证手机号是否合法
    if not re.match(r"1[3456789]\d{9}", mobile):
        return jsonify(errcode=RET.PARAMERR, errmsg="手机号不合法")

    # 查询用户错误登录次数，并且进行判断，如果超过规定次数，则禁止访问，封用户ip
    user_ip = request.remote_addr
    try:
        wrong_access_num = redis_store.get("access_num_%s" % user_ip)
    except Exception as e:
        current_app.logger.error(e)
    else:
        # 判断是否超过规定次数
        if wrong_access_num is not None and int(wrong_access_num) >= constants.WRONG_LOGIN_MAX_TIMES:
            return jsonify(errcode=RET.REQERR, errmsg="错误次数太多，请稍后再试")

    # 验证手机号和密码
    try:
        user = User.query.filter_by(mobile=mobile).first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errcode=RET.DBERR, errmsg="数据库异常")

    # 如果验证失败，保存用户验证失败次数
    if user is None or not user.check_password(password):
        try:
            # 把错误次数保存在redis中
            # 如果是用户第一次登录错误，错误次数保存为１
            # 如果用户登录错误次数大于１次，在错误次数＋１
            redis_store.incr("access_num_%s"%user_ip)
            # 设置记录过期时间，即是用户被禁止时间
            redis_store.expire("access_num_%s" % user_ip, constants.WRONG_LOGIN_FORBID_TIME)
        except Exception as e:
            current_app.logger.error(e)
        return jsonify(errcode=RET.DATAERR, errmsg="手机号或密码错误")

    # 如果手机号和密码正确，保存用户登录记录
    session["user_id"] = user.id
    session["mobile"] = mobile
    session["user_name"] = user.name
    # 返回信息
    return jsonify(errcode=RET.OK, errmsg="登录成功")