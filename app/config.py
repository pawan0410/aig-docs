"""
Configuration file
"""


class Config:
    """
    Base Configuration
    """

    DEBUG = True
    SECRET_KEY = r'f\x13\xd9fM\xdc\x82\x01b\xdb\x03'
    SQLALCHEMY_POOL_SIZE = 5
    SQLALCHEMY_POOL_TIMEOUT = 120
    SQLALCHEMY_POOL_RECYCLE = 280
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 465
    MAIL_USERNAME = r'ithelpdesk@aigbusiness.in'
    MAIL_PASSWORD = r'Reset@123'
    MAIL_USE_TLS = False
    MAIL_USE_SSL = True
    FTP_SERVER = 'aigbusiness.in'
    FTP_USER = 'policies@aigbusiness.in'
    FTP_PASSWORD = 'policy123'
    SERVER_NAME = '182.74.64.202:5050'
    SESSION_COOKIE_NAME = '182.74.64.202:5050'
    SESSION_COOKIE_DOMAIN = '182.74.64.202:5050'


class DevelopmentConfig(Config):
    """
    Local Development
    """

    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'mysql://root:root@127.0.0.1/aig_docs'


class ProductionConfig(Config):
    """
    Production configurations
    """

    DEBUG = False
    SQLALCHEMY_DATABASE_URI = 'mysql://root:maria@aig2016@127.0.0.1/aig_docs'


app_config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig
}