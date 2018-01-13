# coding:utf-8

from flask import current_app, jsonify,request
from . import api
from ihome.utils.captcha.captcha import captcha
from ihome import redis_store, constants
from ihome.utils.response_code import RET
from ihome.models import User
import random
from ihome.libs.yuntongxun.sms import CCP


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


# GET /sms_codes/手机号?image_code_id=XXX&image_code_text=XXX
@api.route('/sms_codes/<re(r"1[3456789]\d{9}"):mobile>')
def send_sms_code(mobile):
    """发送短信验证码"""
    # 获取参数
    image_code_id = request.args.get("image_code_id")
    image_code_text = request.args.get("image_code_text")
    # 校验参数
    if not all([image_code_id,image_code_text]):
        return jsonify(errcode=RET.PARAMERR,errmsg="数据不完整")

    # 验证图片验证码的正确性
    # 从redis中获取保存的真实验证码的值
    try:
        real_image_code_text = redis_store.get('image_code_%s'% image_code_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errcode=RET.DBERR,errmsg="数据库异常")

    # 判断验证码是否过期
    if real_image_code_text is None:
        return jsonify(errcode=RET.NODATA,errmsg="验证码已过期")

    # 删除验证码，防止用户对同一个验证码进行多次尝试
    try:
        redis_store.delete('image_code_%s'% image_code_id)
    except Exception as e:
        current_app.logger.error(e)
    # 将验证码的真实值与用户输入的值进行比较
    if real_image_code_text.lower() != image_code_text.lower():
        return jsonify(errcode=RET.DATAERR, errmsg="验证码错误")

    # 如果验证码验证成功：
    # 验证手机号是否已经被注册
    try:
        user = User.query.filter_by(mobile=mobile).first()
    except Exception as e:
        current_app.logger.error(e)
    else:
        if user is not None:
            return jsonify(errcode=RET.DATAEXIST, errmsg="手机号已注册")

    # 如果手机号没有被注册，判断是否60s内已经发送过验证码，如果发送过，则提前终止
    try:
        flag = redis_store.get('send_sms_code_flag_%s'%mobile)
    except Exception as e:
        current_app.logger.error(e)
    else:
        if flag is not None:
            return jsonify(errcode=RET.PARAMERR, errmsg="发送过于频繁")

    # 生成短信验证码
    sms_code = '%06d'% random.randint(0, 999999)

    # 保存手机号和短信验证码
    try:
        redis_store.setex('sms_code_%s'%mobile, constants.SMS_CODE_REDIS_EXPIRES, sms_code)
    except Exception as e:
        current_app.logger.error(e)

    # 保存发送记录，以便知道是否在６０s内发送过
    try:
        redis_store.setex('send_sms_code_flag_%s' % mobile, constants.SEND_SMS_CODE_INTERVAL, 1)
    except Exception as e:
        current_app.logger.error(e)

    # 使用celery发送短信
    try:
        ccp = CCP()
        result = ccp.send_template_sms(mobile, [sms_code, str(constants.SMS_CODE_REDIS_EXPIRES // 60)],
                                       constants.SMS_CODE_TEMPLATE)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errcode=RET.THIRDERR, errmsg="发送短信异常")

    if result == -1:
        return jsonify(errcode=RET.THIRDERR, errmsg="发送短信失败")
    else:
        return jsonify(errcode=RET.OK, errmsg="发送短信成功")
