# coding:utf-8

from . import api
from ihome.models import User
from flask import request, g, jsonify, current_app
from ihome.utils.response_code import RET
from ihome.utils import storage
from ihome import db, constants
from ihome.utils.commons import login_require
import re


# POST   /users/avatars　参数：用户头像，用户id
@api.route('/users/avatars', methods=["POST"])
@login_require
def upload_avatars():
    """上传保存用户头像"""
    # 获取数据
    file_obj = request.files.get("avatar")
    user_id = g.user_id

    # 校验数据
    if file_obj is None:
        return jsonify(errcode=RET.PARAMERR, errmsg="数据不完整")

    # 将图片保存在七牛:
    # 1.读取图片数据
    file_data = file_obj.read()
    # 2.调用函数将图片上传到七牛
    try:
        file_name = storage.storage_image(file_data)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errcode=RET.THIRDERR, errmsg="上传图片失败")

    # 把上传图片返回的file_name保存到数据库中
    try:
        User.query.filter_by(id=user_id).update({"avatar_url": file_name})
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(e)
        return jsonify(RET.DBERR, errmsg="保存图片信息失败")

    # 返回数据
    avatar_url = constants.QINIU_URL_DOMIAN+file_name
    return jsonify(errcode=RET.OK, errmsg="上传成功", data={"avatar_url": avatar_url})


@api.route('/users/username', methods=["POST"])
@login_require
def update_username():
    """修改用户名"""
    # 获取信息
    user_id = g.user_id
    username = request.form.get("name")

    # 验证信息
    if username is None:
        return jsonify(errcode=RET.PARAMERR, errmsg="数据不完整")

    # 查询数据库，查看用户名是否已被使用
    try:
        user = User.query.filter_by(name=username).first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errcode=RET.DBERR, errmsg="数据库异常")
    else:
        if user:
            return jsonify(errcode=RET.DATAEXIST, errmsg="用户名已存在")
    # 保存数据
    try:
        User.query.filter_by(id=user_id).update({"name":username})
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(e)
        return jsonify(RET.DBERR, errmsg="用户名保存失败")
    return jsonify(errcode=RET.OK, errmsg="用户名保存成功")


# GET /api/v1.0/users/userinfo
@api.route('/users/userinfo')
@login_require
def get_userinfo():
    """展示个人信息首页"""
    # 获取用户id
    user_id = g.user_id
    # 根据用户id获取用户对象
    try:
        user = User.query.get(user_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errcode=RET.DBERR, errmsg="数据库异常")
    else:
        username = user.name
        mobile = user.mobile
        avatar_url = user.avatar_url

    avatar_url = constants.QINIU_URL_DOMIAN + avatar_url
    # 返回数据
    return jsonify(errcode=RET.OK, errmsg="OK",
                   data={"username": username, "mobile": mobile, "avatar_url": avatar_url})


# GET /api/v1.0/user/auth
@api.route('/user/auth')
@login_require
def get_auth():
    """查询用户是否已实名认证"""
    user_id = g.user_id
    try:
        user = User.query.filter_by(id=user_id).first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errcode=RET.DBERR, errmsg="数据库异常")
    else:
        real_name = user.real_name
        id_card = user.id_card
        if not real_name and not id_card:
            return jsonify(errcode=RET.NODATA, errmsg="用户还未注册")
        else:
            return jsonify(errcode=RET.DATAEXIST, errmsg="用户已注册", data={"real_name":real_name, "id_card":id_card})


# POST /api/v1.0/users/auth  参数：real_name，id_card
@api.route('/users/auth', methods=["POST"])
@login_require
def auth():
    """用户实名认证"""
    # 获取参数
    real_name = request.form.get("real_name")
    id_card = request.form.get("id_card")
    user_id = g.user_id

    # 校验参数
    if not all([real_name, id_card]):
        return jsonify(errcode=RET.PARAMERR, errmsg="数据不完整")
    # 验证身份证号是否合法
    if not re.match(r"\d{15}|\d{18}", id_card):
        return jsonify(errcode=RET.DATAERR, errmsg="身份证号不合法")

    # 保存数据
    try:
        User.query.filter_by(id=user_id).update({"real_name": real_name, "id_card": id_card})
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(e)
        return jsonify(errcode=RET.DBERR, errmsg="数据库异常")
    # 返回数据
    return jsonify(errcode=RET.OK, errmsg="数据提交成功")


















