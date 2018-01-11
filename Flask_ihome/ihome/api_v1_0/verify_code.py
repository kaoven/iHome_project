# coding:utf-8

from flask import current_app, jsonify
from . import api
from ihome.utils.captcha.captcha import captcha
from ihome import redis_store, constants
from ihome.utils.response_code import RET


# GET /image_codes/图片验证码编号
@api.route('/image_codes/<image_code_id>')
def get_image_code(image_code_id):
    """提供验证码图片"""
    name, text, image_data = captcha.generate_captcha()

    # 把验证码图片的真实值保存在redis中
    try:
        redis_store.setex('image_code_%s'% image_code_id, constants.IMAGE_CODE_REDIS_EXPIRES, text)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errorcode=RET.DBERR,errmsg="数据库异常")

    # 返回验证码图片
    return image_data, 200, {"Content-Type":"image/jpg"}