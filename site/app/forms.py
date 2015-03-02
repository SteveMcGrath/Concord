from datetime import date
from flask.ext.wtf import Form
from flask.ext.wtf.html5 import *
from wtforms.fields import *
from wtforms.ext.sqlalchemy.fields import QuerySelectField, QuerySelectMultipleField
from wtforms.validators import Required, Optional, Email
from sqlalchemy import desc, or_, and_
from app.models import Ticket, User, Seat
from app import app


def open_training():
    return Submission.query.filter(and_(
        Submission.training == True,
        len(Submission.tickets) < Submission.seats
    ))


def open_classes():
    sel_list = ()
    #for training in app.config['CLASSES']:
    #    c = app.config['CLASSES'][training]
    #    seats = Seat.query.filter_by(tag=c['id']).filter_by(paid=True).count()
    #    if seats < training['seats']:
    #        sel_list = sel_list + ((training, '%s ($%s USD)' % (c['name'], c['price'])))
    return sel_list


def gen_tickets():
    sel_list = ()
    #tickets = app.config['TICKETS']
    #for ticket in tickets:
    #    c = tickets[ticket]
    #    if c['visible']:
    #        if c['expiration'] is None or date.today() < c['expiration']:
    #            sel_list = sel_list + ((ticket, '%s ($%s USD)' % (c['name'], c['price'])),)
    return sel_list


def training_options():
    sel_list = ()
    #for tclass in Training.query().filter_by(accepted=True).all():
    #    sel_list = sel_list + ((tclass.id, '%s ($%s USD)' % (tclass.name, tclass.price)))
    return sel_list


class TrainingPurchaseForm(Form):
    training = SelectMultipleField('Training Options', choices=open_classes(),
                validators=[Required()])
    submit = SubmitField('Purchase')


class LoginForm(Form):
    username = TextField('Username', validators=[Required()])
    password = PasswordField('Password', validators=[Required()])
    submit = SubmitField('Login')


class PurchaseForm(Form):
    email = EmailField('Email Address', validators=[Required()])
    ticket_type = SelectField('Ticket Type', choices=gen_tickets(), validators=[Required()], default='earlybird')
    discountcode = TextField('Discount Code', validators=[Optional()])
    children = SelectField('Number of Children under 16?', choices=(
        ('0', 'No Child'),
        ('1', '1 Child'),
        ('2', '2 Children'),
        ('3', '3 Children')
    ), default='0')
    submit = SubmitField('Purchase')


class TicketInfoForm(Form):
    name = TextField('Name', validators=[Required()])
    company = TextField('Company Name', validators=[Optional()])
    phone = TextField('Phone Number', validators=[Optional()])
    twitter = TextField('Twitter Account', validators=[Optional()])
    linkedin = TextField('LinkedIn Account', validators=[Optional()])
    facebook = TextField('Facebook Account', validators=[Optional()])
    fri_party = BooleanField('Do you plan to attend the Friday night party/entertainment?')
    sat_party = BooleanField('Do you plan to attend the Saturday night party/entertainment?')
    thu_hfd = BooleanField('Would you be interested in attending a Hacker Family Dinner event on Thursday?')
    fri_hfd = BooleanField('Would you be interested in attending a Hacker Family Dinner event on Friday?')
    sat_hfd = BooleanField('Would you be interested in attending a Hacker Family Dinner event on Saturday?')
    helpus = TextAreaField('Please let us know any suggestions you have for events, entertainment, training, contests, etc to make Circlecitycon a better event for everyone.', validators=[Optional()])
    shirt = SelectField('Shirt Size', choices=(
        ('M:S', 'Mens Small'),
        ('M:M', 'Mens Medium'),
        ('M:L', 'Mens Large'),
        ('M:XL', 'Mens XL'),
        ('M:XXL', 'Mens XXL'),
        ('M:2XL', 'Mens 2XL'),
        ('M:3XL', 'Mens 3XL'),
        ('M:4XL', 'Mens 4XL'),
        ('M:5XL', 'Mens 5XL'),
        ('W:S', 'Womens Small'),
        ('W:M', 'Womens Medium'),
        ('W:L', 'Womens Large'),
        ('W:XL', 'Womens XL'),
        ('W:2XL', 'Womens 2XL'),
        ('W:3XL', 'Womens 3XL'),
        ('W:4XL', 'Womens 4XL'),
        ('W:5XL', 'Womens 5XL'),
        ('C:S', 'Childrens Small'),
        ('C:M', 'Childrens Medium'),
        ('C:L', 'Childrens Large'),
        ('C:XL', 'Childrens XL')
    ), validators=[Optional()])
    marketing = BooleanField('Would you like to be contacted from our sponsors?', default=True)
    submit = SubmitField('Submit Questionare')


class NewsForm(Form):
    title = TextField('Title', validators=[Required()])
    draft = BooleanField('Draft Post')
    body_md = TextAreaField('Post Body', validators=[Required()])
    submit = SubmitField('Add/Update')


