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
               notification=('Please check your inbox for further instructions.', 'success'), 
               **kwargs):
    kwargs['user'] = user
    msg = Message(subject=subject,
                  body=render_template(template, **kwargs), 
                  recipients=[user.email],
    )
    if 'TESTING' in app.config:
        print '\n%s\n' % msg
    mail.send(msg)
    if notification:
        flash(notification[0], notification[1])


from app.models import Submission


def need_to_review():
    # This is very unoptimized.  There has to be a way to make SQLAlchemy spit
    # this out.
    submissions = Submission.query.filter_by(round_id=g.reviewround.id).all()
    opensubs = []
    for sub in submissions:
        if g.user not in sub.reviewed_by:
            opensubs.append(sub)
    return opensubs