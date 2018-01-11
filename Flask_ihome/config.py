# coding:utf-8
import redis


class Config(object):
    """配置信息"""
    SECRET_KEY = "JKASDJFKDSAJFKJ"

    # flask_session的配置信息
    SESSION_TYPE = 'redis'  # 指明session数据保存在redis中
    SESSION_USE_SIGNER = True  # 指明在cookie中保存的session_id进行加密
    PERMANENT_SESSION_LIFETIME = 3 * 24 * 3600  # 指明session的有效期


class DevelopConfig(Config):
    DEBUG = True

    # 设置数据库的连接
    SQLALCHEMY_DATABASE_URI = "mysql://root:mysql@192.168.128.134:3306/ihome"
    SQLALCHEMY_TRACK_MODIFICATIONS = True

    # 设置redis连接参数
    REDIS_HOST = '192.168.128.134'
    REDIS_PORT = 6379
    REDIS_DB = 0

    SESSION_REDIS = redis.StrictRedis(host='192.168.128.134', port=6379, db=1)  # 保存session的数据库


class ProductConfig(Config):
    pass


config_map = {
    "product": ProductConfig,
    'develop': DevelopConfig
}