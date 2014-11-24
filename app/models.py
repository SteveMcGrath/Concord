from app import db, app
from datetime import datetime, date
from time import time
from random import random
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


ticket_purchases = db.Table('ticket_purchases',
    db.Column('purchase_id', db.Integer, db.ForeignKey('purchases.id')),
    db.Column('tickets_id', db.Integer, db.ForeignKey('tickets.id'))
)

class DiscountCode(db.Model):
    __tablename__ = 'discountcodes'
    id = db.Column(db.Integer, primary_key=True)
    uses = db.Column(db.Integer, default=0)
    code = db.Column(db.Text)
    t_type = db.Column(db.Text, default='attendee')
    price = db.Column(db.Integer)


class Purchase(db.Model):
    __tablename__ = 'purchases'
    id = db.Column(db.Integer, primary_key=True)
    ref_hash = db.Column(db.Text)
    email = db.Column(db.Text)
    price = db.Column(db.Integer)
    ticket_type = db.Column(db.Text)
    discountcode = db.Column(db.Text)
    payment_type = db.Column(db.Text)
    payment_token = db.Column(db.Text)
    children = db.Column(db.Integer)
    completed = db.Column(db.Boolean, default=False)
    tickets = db.relationship('Ticket', backref='purchase')

    def __init__(self):
        self.ref_hash = gen_hash(str(time()), str(random()))


class Ticket(db.Model):
    __tablename__ = 'tickets'
    id = db.Column(db.Integer, primary_key=True)
    ticket_type = db.Column(db.Text)
    purchase_id = db.Column(db.Integer, db.ForeignKey('purchases.id'))
    ticket_hash = db.Column(db.Text)
    user_id = db.Column(db.Integer, default=None)
    redeemed = db.Column(db.Boolean, default=False)
    marketing = db.Column(db.Boolean, default=True)
    email = db.Column(db.Text)
    name = db.Column(db.Text)
    company = db.Column(db.Text)
    phone = db.Column(db.Text)
    twitter = db.Column(db.Text)
    linkedin = db.Column(db.Text)
    facebook = db.Column(db.Text)
    shirt = db.Column(db.Text)
    fri_party = db.Column(db.Boolean)
    sat_party = db.Column(db.Boolean)
    thu_hfd = db.Column(db.Boolean)
    fri_hfd = db.Column(db.Boolean)
    sat_hfd = db.Column(db.Boolean)
    helpus = db.Column(db.Text)

    def __init__(self, email, ticket_type='attendee'):
        self.ticket_type = ticket_type
        self.email = email
        self.ticket_hash = gen_hash(email, str(time()), str(random()))

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
                event_name=app.config['CONFERENCE_EVENT'],
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



