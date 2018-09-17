from threading import Thread
from flask import current_app
from flask_mail import Message
from . import mail


def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)


def send_email(recipients, subject, content):
    if recipients:
        app = current_app._get_current_object()
        msg = Message(app.config['MAIL_SUBJECT_PREFIX'] + ' ' + subject,
                      sender=app.config['MAIL_SENDER'], recipients=recipients)
        msg.html = content
        thr = Thread(target=send_async_email, args=[app, msg])
        thr.start()
        return thr
