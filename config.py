import os
basedir = os.path.abspath(os.path.join(os.path.abspath(os.path.dirname(__file__)), '..'))


class Config:
    DEBUG = os.environ.get('DEBUG', False)
    SECRET_KEY = os.environ.get('SECRET_KEY', '<put some hard to guess string here>')
    WTF_CSRF_ENABLED = True
    
    # The database username and password will be asked for later.
    MONGODB_SETTINGS = {
        'db': os.environ.get('DB_NAME', 'admin'),
        'host': os.environ.get('DB_SERVICE', '127.0.0.1'),
        'port': os.environ.get('DB_PORT', 27017),
        'username': os.environ.get('DB_USER', '<database username>'),
        'password': os.environ.get('DB_PASS', '<database password>')
    }
    
    # Email to send out notification to users
    # Here Gmail is used as an example. 
    # If you want to stay with Gmail, 
    # you need to `Allow less secure apps to access accounts`.
    # More info: https://support.google.com/a/answer/6260879?hl=en
    # and https://github.com/miguelgrinberg/flasky/issues/65
    MAIL_SERVER = 'smtp.googlemail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME', '<email>')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD', '<email password>')
    MAIL_SENDER = 'Project Wiki <{}>'.format(os.environ.get('MAIL_USERNAME', '<email>'))
    MAIL_SUBJECT_PREFIX = '[Do-not-reply]'
    
    # Super admin username, email, and password
    # The email can be the same as the one above.
    ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME', '<admin username>')
    ADMIN_EMAIL = os.environ.get('ADMIN_EMAIL', '<admin email>')
    ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', '<admin password>')

    DATA_FOLDER = 'Project_Wiki_Data'
    UPLOAD_FOLDER = os.path.join(basedir, DATA_FOLDER, 'uploads')


config = Config()
