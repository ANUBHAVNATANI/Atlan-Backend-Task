from os import environ,path

basedir = path.abspath(path.dirname(__file__))

db_key = 'dfewfew123213rwdsgert34tgfd1234trgf'
db_uri = 'sqlite:///collect.db'

class Config:
    #general config
    FLASK_DEBUG = 1
    FLASK_APP = 'app.py'
    #database config
    SQLALCHEMY_DATABASE_URI = db_uri #environ['DATABASE_URL']
    SECRET_KEY = db_key
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    #upload and thread config
    STATUSES = ['READY', 'UPLOADING', 'PAUSED', 'STOPPED', 'UPLOADED','EXPORTING']
    ALLOWED_EXTENSIONS = {'.csv'}
    UPLOAD_PATH = 'uploads'
