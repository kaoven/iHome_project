# coding:utf-8

# 图片验证码有效期
IMAGE_CODE_REDIS_EXPIRES = 300

# 短信验证码有效期
SMS_CODE_REDIS_EXPIRES = 600

# 发送短信的模板的id
SMS_CODE_TEMPLATE = 1

# 发送短信的时间间隔
SEND_SMS_CODE_INTERVAL = 60

# 最多登录失败次数
WRONG_LOGIN_MAX_TIMES = 5

# 用户登录禁止时间 单位：秒
WRONG_LOGIN_FORBID_TIME = 600