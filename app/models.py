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


#instructors = db.Table('instructors',
#    db.Column('user_id', db.Integer, db.ForeignKey('users.id')),
#    db.Column('class_id', db.Integer, db.ForeignKey('classes.id'))
#)
#
#speakers = db.Table('speakers',
#    db.Column('user_id', db.Integer, db.ForeignKey('users.id')),
#    db.Column('talks_id', db.Integer, db.ForeignKey('talks.id'))
#)
#
#talk_tags = db.Table('talk_tags',
#    db.Column('tags_id', db.Integer, db.ForeignKey('tags.id')),
#    db.Column('talks_id', db.Integer, db.ForeignKey('talks.id'))
#)
#
#class_tags = db.Table('class_tags',
#    db.Column('tags_id', db.Integer, db.ForeignKey('tags.id')),
#    db.Column('class_id', db.Integer, db.ForeignKey('classes.id'))
#)


class Ticket(db.Model):
    __tablename__ = 'tickets'
    id = db.Column(db.Integer, primary_key=True)
    ticket_type = db.Column(db.Text, default='attendee')
    ticket_sub = db.Column(db.Text, default='general')
    ticket_hash = db.Column(db.Text)
    redeem_hash = db.Column(db.Text)
    email = db.Column(db.Text)
    opt_in = db.Column(db.Boolean)
    price = db.Column(db.Integer)
    user_id = db.Column(db.Integer, default=None)
    redeemed = db.Column(db.Boolean, default=False)
    training_id = db.Column(db.Integer, default=None)

    def __init__(self, email, opt_in=False, ticket_type='attendee', subtype='general'):
        self.ticket_type = ticket_type
        self.ticket_sub = subtype
        self.email = email
        self.opt_in = opt_in
        self.redeem_hash = gen_hash(email, str(time()))
        self.ticket_hash = gen_hash(email, self.redeem_hash)

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
        return render_template('ticketing/print.html', 
                event_name=event,
                ticket_type=self.ticket_type,
                image_data=self.qrgen(),
                ticket_id=self.ticket_hash,
            )


class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True)
    password = db.Column(db.String(32))
    email = db.Column(db.String(255))
    admin = db.Column(db.Boolean, default=False)
    bio = db.Column(db.Text, default='Currently no Bio')
    tickets = db.relationship(Ticket, backref='user',
        primaryjoin='User.id==Ticket.user_id',
        foreign_keys=[Ticket.__table__.c.user_id],
        passive_deletes='all')

    @hybrid_property
    def is_speaker(self):
        value = False
        for talk in self.talks:
            if talk.status == 'accepted':
                value = True
        for training in self.trainings:
            if training.status == 'accepted':
                value = True
        return value

    @hybrid_property
    def pretty_bio(self):
        return markdown.markdown(self.bio)

    def update_password(self, password):
        self.password = gen_hash(password)

    def check_password(self, password):
        return self.password == gen_hash(password)

    def gen_ticket(self, price=0, ticket_type='speaker'):
        ticket = Ticket(self.email, ticket_type=ticket_type)
        ticket.price = price
        ticket.user_id = self.id



