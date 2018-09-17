from flask import Flask
from werkzeug.contrib.fixers import ProxyFix
from flask_mongoengine import MongoEngine
from flask_login import LoginManager
from flask_mail import Mail
from passlib.context import CryptContext
from datetime import timedelta

from config import config, basedir

db = MongoEngine()
login_manager = LoginManager()
login_manager.session_protection = 'strong'
mail = Mail()
wiki_pwd = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__rounds=12,  # This value is logarithmic.
    )

from . import models
from .wiki_util import wiki_markdown, logger

wiki_md = wiki_markdown.WikiMarkdown()


def create_app():
    app = Flask(__name__)
    app.config.from_object(config)
    # User will be logged out after being inactive for 1 day.
    app.permanent_session_lifetime = timedelta(days=1)
    app.wsgi_app = ProxyFix(app.wsgi_app)
    db.init_app(app)

    all_groups = [g.name_no_whitespace for g in models.WikiGroup.objects(active=True).all()]
    for group in all_groups:
        db.register_connection(alias=group, name=group,
                               host=config.MONGODB_SETTINGS['host'],
                               port=config.MONGODB_SETTINGS['port'])
    app.logger.addHandler(logger)

    login_manager.init_app(app)
    login_manager.anonymous_user = models.AnonymousUser
    mail.init_app(app)

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from .admin import admin as admin_blueprint
    app.register_blueprint(admin_blueprint)

    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)
    
    return app
