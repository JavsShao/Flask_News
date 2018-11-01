import redis
import logging


class Config(object):
    """工程配置信息"""
    DEBUG = True

    # 数据库的配置信息（MySQL）
    SQLALCHEMY_DATABASE_URI = "mysql://root:970202@127.0.0.1:3306/Flask_News"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Redis配置
    REDIS_HOST = '127.0.0.1'
    REDIS_PORT = 6379

    SECRET_KEY = "EjpNVSNQTyGi1VvWECj9TvC/+kq3oujee2kTfQUs8yCM6xX9Yjq52v54g+HVoknA"
    ...
    # flask_session的配置信息
    SESSION_TYPE = "redis"  # 指定 session 保存到 redis 中
    SESSION_USE_SIGNER = True  # 让 cookie 中的 session_id 被加密签名处理
    SESSION_REDIS = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT)  # 使用 redis 的实例
    PERMANENT_SESSION_LIFETIME = 86400  # session 的有效期，单位是秒

    # 默认日志等级
    LOG_LEVEL = logging.DEBUG

class DevelopmentConfig(Config):
    """开发模式下的配置"""
    # 开发环境日志等级
    LEVEL_LOG = logging.DEBUG

class ProductionConfig(Config):
    """生产模式下的配置"""
    DEBUG = False
    LOG_LEVEL = logging.ERROR
    SQLALCHEMY_DATABASE_URI = 'mysql://root:970202@127.0.0.1:3306/Flask_News'
    # 生产环境日志等级

class UnittestConfig(Config):
    """测试环境"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'mysql://root:970202@127.0.0.1:3306/Flask_News'

# 定义配置字典,存储关键字对应的不同的配置类的类名
configs = {
    "dev":DevelopmentConfig,
    "pro":ProductionConfig,
    "unit":UnittestConfig
}
