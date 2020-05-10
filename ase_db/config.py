import os

class Config(object):
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = 1
    MAIL_USERNAME = 'tpdb.info'
    MAIL_PASSWORD = os.environ.get('TPDB_PASSWORD')
    ADMINS = ['tpdb.info@gmail.com']
