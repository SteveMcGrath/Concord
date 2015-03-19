from flask import render_template, flash, g
from flask.ext.mail import Message
from app import app, db, mail
import hashlib


def mdcheat():
    return '<a class="btn btn-xs btn-info" href="https://gist.github.com/jonschlinkert/5854601#file-markdown-md" target="_blank">cheatsheet</a>'


def gen_hash(*elements):
    md5 = hashlib.md5()
    for item in elements:
        md5.update(item)
    return md5.hexdigest()


def send_email(template, subject, user,
               notification='Please check your inbox for further instructions.', 
               **kwargs):
    kwargs['user'] = user
    msg = Message(subject=subject,
                  body=render_template(template, **kwargs), 
                  recipients=[user.email],
    )
    if 'TESTING' in app.config:
        print '\n%s\n' % msg
    mail.send(msg)
    flash(notification, 'info')