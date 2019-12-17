# coding:utf-8

import redis


class Config(object):
    """基础配置信息"""

    SECRET_KEY = 'qwertasdf123'
    # 数据库
    SQLALCHEMY_DATABASE_URI = 'mysql://root:Qwer6666@10.168.0.4:3306/ihome'
    SQLALCHEMY_TRACK_MODIFICATIONS = True

    # redis
    REDIS_HOST = '10.168.0.4'
    REDIS_PORT = 6379

    # session配置
    SESSION_TYPE = 'redis'
    SESSION_REDIS = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT)
    SESSION_USE_SIGNER = True  # 对cookis的session进行隐藏处理
    PERMANENT_SESSION_LIFETIME = 86400  # session数据的有效期（1天），单位：秒


class DevConfig(Config):
    """开发模式配置信息"""
    DEBUG = True


class ProConfig(Config):
    """生产模式配置信息"""
    pass


config_map = {
    'develop': DevConfig,
    'product': ProConfig
}