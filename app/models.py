from app import db
from datetime import datetime, date
from time import time
from flask.ext.login import UserMixin
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy import desc
from StringIO import StringIO
from flask import render_template
import base64, qrcode, markdown, hashlib


def gen_hash(*elements):
    md5 = hashlib.md5()
    for item in elements:
        md5.update(item)
    return md5.hexdigest()


user_subs = db.Table('user_subs',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id')),
    db.Column('submission_id', db.Integer, db.ForeignKey('submissions.id'))
)


class Ticket(db.Model):
    __tablename__ = 'tickets'
    id = db.Column(db.Integer, primary_key=True)
    ticket_type = db.Column(db.Text, default='attendee')
    ticket_hash = db.Column(db.Text)
    redeem_hash = db.Column(db.Text)
    email = db.Column(db.Text)
    opt_in = db.Column(db.Boolean)
    price = db.Column(db.Integer)
    user_id = db.Column(db.Integer, default=None)
    redeemed = db.Column(db.Boolean, default=False)
    training_id = db.Column(db.Integer, default=None)

    def __init__(self, email, opt_in=False, ticket_type='attendee'):
        self.ticket_type = ticket_type
        self.email = email
        self.opt_in = opt_in
        self.redeem_hash = gen_hash(email, str(time()))
        self.ticket_hash = gen_hash(email, self.redeem_hash)

    @hybrid_property
    def training(self):
        if self.training_id is not None:
            return Submission.query.filter_by(id=self.training_id).first()
        return None

    def qrgen(self, encode=True):
        imgbuf = StringIO()
        imgraw = qrcode.make('http://ticket/%s' % self.ticket_hash)
        imgraw.save(imgbuf, 'PNG')
        data = imgbuf.getvalue()
        imgbuf.close()
        if encode:
            return base64.b64encode(data)
        else:
            return response

    def generate(self, event):
        return render_template('ticket.html', 
                event_name=event,
                ticket_type=self.ticket_type,
                image_data=self.qrgen(),
                ticket_id=self.ticket_hash,
            ]),
        )




class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True)
    password = db.Column(db.String(32))
    email = db.Column(db.String(255))
    admin = db.Column(db.Boolean, default=False)
    bio = db.Column(db.Text, default='Currently no Bio')
    submissions = db.relationship('Submission', secondary=user_subs,
                            backref=db.backref('speakers', lazy='dynamic'))

    @hybrid_property
    def is_speaker(self):
        value = False
        for submission in self.submissions:
            if submission.accepted:
                value = True
        return value

    @hybrid_property
    def pretty_bio(self):
        return markdown.markdown(self.bio)

    def update_password(self, password):
        self.password = gen_hash(password)

    def check_password(self, password):
        return self.password == gen_hash(password)

    def gen_ticket(self, price=0):
        ticket = Ticket(self.email, ticket_type='speaker')
        ticket.price = price
        ticket.user_id = self.id


class Submission(db.Model):
    __tablename__ = 'submissions'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    accepted = db.Column(db.Boolean, default=False)
    status = db.Column(db.String(16), default='submitted')
    abstract = db.Column(db.Text)
    title = db.Column(db.String(255))
    outline = db.Column(db.Text)
    tool = db.Column(db.Boolean, default=False)
    exploit = db.Column(db.Boolean, default=False)
    panel = db.Column(db.Boolean, default=False)
    demo = db.Column(db.Boolean, default=False)
    time = db.Column(db.Integer, default=50)
    training = db.Column(db.Boolean, default=False)
    new_talk = db.Column(db.Boolean, default=False)
    other_speakers = db.Column(db.Text)     #For Email addresses for later association.
    needs = db.Column(db.Text)
    track = db.Column(db.String(32))
    seats = db.Column(db.Integer)
    tod = db.Column(db.DateTime)
    review_rating = db.Column(db.Integer)
    review_notes = db.Column(db.Text)

    @hybrid_property
    def pretty_abstract(self):
        return markdown.markdown(self.abstract)