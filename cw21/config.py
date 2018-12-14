import os


basedir = os.path.abspath(os.path.dirname(__file__))

#decide how many posts would be on one page
class Config(object):
    POSTS_PER_PAGE = 10
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    WTF_CSRF_ENABLED = True
    SECRET_KEY = 'wangxiyang'
    UPLOAD_FOLDER = '/app/static/avatars'
    ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])
