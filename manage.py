from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import redis


app = Flask(__name__)

class Config(object):
    """工程配置信息"""
    DEBUG = True

    # 数据库的配置信息（MySQL）
    SQLALCHEMY_DATABASE_URI = "mysql://root:970202@127.0.0.1:3306/Flask_News"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Redis配置
    REDIS_HOST = '127.0.0.1'
    REDIS_PORT = 6379



app.config.from_object(Config)
db = SQLAlchemy(app)
redis_store = redis.StrictRedis(host=Config.REDIS_HOST,port=Config.REDIS_PORT)

@app.route('/index')
def index():
    return 'index'

if __name__ == '__main__':
    app.run()