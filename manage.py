from app import create_app, db, wiki_pwd, mail
from app.models import WikiUser, WikiPage
from flask_script import Manager, Shell

app = create_app()
manager = Manager(app)


def make_shell_context():
    return dict(app=app, db=db, WikiUser=WikiUser, WikiPage=WikiPage, mail=mail)
manager.add_command('shell', Shell(make_context=make_shell_context))


@manager.command
def create_admin():
    WikiUser(name=app.config['ADMIN_USERNAME'],
             email=app.config['ADMIN_EMAIL'],
             password_hash=wiki_pwd.hash(app.config['ADMIN_PASSWORD']),
             permissions={'super': 0xff}).save()

if __name__ == '__main__':
    manager.run()
