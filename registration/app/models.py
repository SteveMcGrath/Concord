from app import db, app
from datetime import datetime, date
from time import time
from random import random
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy import desc
from StringIO import StringIO
import base64, qrcode, markdown, hashlib


class Ticket(db.Model):
    __tablename__ = 'tickets'
    id = db.Column(db.Integer, primary_key=True)
    ticket_type = db.Column(db.Text)
    purchase_id = db.Column(db.Integer, db.ForeignKey('purchases.id'))
    date = db.Column(db.DateTime, default=datetime.now())
    ticket_hash = db.Column(db.Text)
    user_id = db.Column(db.Integer, default=None)
    redeemed = db.Column(db.Boolean, default=False)
    marketing = db.Column(db.Boolean, default=True)
    email = db.Column(db.Text)
    name = db.Column(db.Text)