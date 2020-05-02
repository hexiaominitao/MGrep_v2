import os


class Config(object):
    # cat /dev/urandom | tr -cd 'a-f0-9' | head -c 32 获取随机字符
    SECRET_KEY = '6c61a71132325a99fecc0716b1b6d650'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DIALECT = "mysql"
    DRIVER = 'pymysql'
    USERNAME = os.environ.get('SQL_USERNAME')
    PASSWORD = os.environ.get('SQL_PASSWORD')
    HOST = '127.0.0.1'
    PORT = os.environ.get('SQL_PORT')
    DATABASE = os.environ.get('SQL_DATABASE')
    MY_SQL = 'mysql+pymysql://{}:{}@127.0.0.1:{}/{}?charset=utf8'.format(USERNAME, PASSWORD, PORT, DATABASE)
    SQLALCHEMY_DATABASE_URI = MY_SQL
    STATIC_DIR = 'app/static'
    COUNT_DEST = 'app/static/upload'
    PRE_REPORT = 'app/static/pre_report'  # 报告需求文件夹
    RES_REPORT = 'app/static/res_report'  # 报告结果保存文件夹
    UPLOADED_FILESAM_DEST = 'app/static/upload'
    UPLOADED_FILEOKR_DEST = 'app/static/upload'

    MONGODB_SETTING = {
        'db': 'local',
        'host': 'localhost',
        'port': 27017
    }

    # celery 配置
    CELERY_BROKER_URL = 'amqp://guest@localhost//'
    CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'

    # 邮件服务  腾讯企业邮箱
    MAIL_SERVER = 'smtp.exmail.qq.com'
    MAIL_PORT = 465
    MAIL_USE_SSL = True
    MAIL_USE_TLS = False
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')


class ProdConfig(Config):
    RESULT_DIR = '/data/MGR/IR_Analysis/'


class DevConfig(Config):
    DEBUG = True
    RESULT_DIR = '/home/hemin/Desktop/信息录入/ir_result'



class TestConfig(Config):
    pass
