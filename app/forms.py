from datetime import date
from flask.ext.wtf import Form
from wtforms.fields import *
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from wtforms.validators import Required, Optional, Email
from sqlalchemy import desc, or_, and_
from app.models import Ticket, User
from app import app


def open_training():
    return Submission.query.filter(and_(
        Submission.training == True,
        len(Submission.tickets) < Submission.seats
    ))


def gen_tickets():
    sel_list = ()
    tickets = app.config['TICKETS']
    for ticket in tickets:
        c = tickets[ticket]
        if c['visible']:
            if c['expiration'] is None or date.today() < c['expiration']:
                sel_list = sel_list + ((ticket, '%s ($%s USD)' % (c['name'], c['price'])),)
    return sel_list


class LoginForm(Form):
    username = TextField('Username', validators=[Required()])
    password = PasswordField('Password', validators=[Required()])
    submit = SubmitField('Login')


class PurchaseForm(Form):
    email = TextField('Email Address', validators=[Required(), Email()])
    opt_in = BooleanField('Opt In', default=True)
    ticket_type = SelectField('Ticket Type', choices=gen_tickets(), validators=[Required()])
    discountcode = TextField('Discount Code', validators=[Optional()])
    submit = SubmitField('Purchase')