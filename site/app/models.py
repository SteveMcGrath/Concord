from app import db, app
from datetime import datetime, date
from time import time
from random import random
from flask.ext.login import UserMixin
from sqlalchemy.ext.hybrid import hybrid_property
#from sqlalchemy_utils import PasswordType, EmailType, ChoiceType, ArrowType
from sqlalchemy import desc
from StringIO import StringIO
from flask import render_template
from random import randint
import mistune as markdown
import base64, qrcode, hashlib
from app.utils import gen_hash, mdcheat


class Setting(db.Model):
    __tablename__ = 'settings'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), unique=True)
    value = db.Column(db.Text)


class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, info={'label': 'Email Address'})
    name = db.Column(db.String(255), info={'label': 'Full Name'})
    password = db.Column(db.String(32))
    admin = db.Column(db.Boolean, default=False)
    author = db.Column(db.Boolean, default=False)
    reviewer = db.Column(db.Boolean, default=False)
    chair = db.Column(db.Boolean, default=False)
    forgot = db.Column(db.String(32))
    shirtsize = db.Column(db.String(10), info={
        'label': 'Shirt Size',
        'choices': app.config['SHIRT_SIZES']
    })
    bio_md = db.Column(db.Text, info={
        'label': 'Biography',
        'description': 'Markdown formatted Bio %s' % mdcheat()
    })

    @hybrid_property
    def bio(self):
        return markdown.markdown(self.bio_md, escape=True)

    @hybrid_property
    def elevated(self):
        return self.admin or self.author or self.reviewer or self.chair

    def update_password(self, password):
        self.password = gen_hash(str(self.id), password)

    def check_password(self, password):
        return self.password == gen_hash(str(self.id), password)

    def forgot_password(self):
        self.forgot = gen_hash(str(self.id), datetime.now().isoformat())


class Upload(db.Model):
    __tablename__ = 'uploads'
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), unique=True)


class Post(db.Model):
    __tablename__ = 'posts'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    body_md = db.Column(db.Text, info={
        'label': 'Post Body',
        'description': 'Markdown Formatted %s' % mdcheat()
    })
    category = db.Column(db.String(16), info={
        'label': 'Category',
        'choices': app.config['POST_CATEGORIES']
    })
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    draft = db.Column(db.Boolean, default=True)
    mp3 = db.Column(db.Text)
    author = db.relationship('User', backref='posts')

    @hybrid_property
    def body(self):
        return markdown.markdown(self.body_md)


teachers = db.Table('trainers', 
    db.Column('class_id', db.Integer, db.ForeignKey('classes.id')),
    db.Column('user_id', db.Integer, db.ForeignKey('users.id'))
)

speakers = db.Table('speakers',
    db.Column('talk_id', db.Integer, db.ForeignKey('talks.id')),
    db.Column('user_id', db.Integer, db.ForeignKey('users.id'))
)

user_seats = db.Table('user_seats',
    db.Column('class_id', db.Integer, db.ForeignKey('classes.id')),
    db.Column('user_id', db.Integer, db.ForeignKey('users.id'))
)


class Round(db.Model):
    __tablename__ = 'rounds'
    id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.String(10), default='pending', info={
        'choices': [('pending', 'Pending'), ('open', 'Open'), ('closed', 'Closed')]
    })
    max_talks = db.Column(db.Integer)
    max_classes = db.Column(db.Integer)
    start_date = db.Column(db.DateTime)
    stop_date = db.Column(db.DateTime)
    submissions = db.relationship('Submission', backref='round')

    @hybrid_property
    def open_for_talks(self):
        count = 0
        for submission in submissions:
            if submission.submission_type == 'talk':
                count +=1
        return self.max_talks > count

    @hybrid_property
    def open_for_classes(self):
        count = 0
        for submission in submissions:
            if submission.submission_type == 'class':
                count +=1
        return self.max_classes > count


    def close(self):
        self.status = 'closed'
        for submission in self.submissions:
            submission.status = 'under review'



class Submission(db.Model):
    __tablename__ = 'submissions'
    id = db.Column(db.Integer, primary_key=True)
    submitted = db.Column(db.DateTime)
    round_id = db.Column(db.Integer, db.ForeignKey('rounds.id'))
    submission_type = db.Column(db.String(32), nullable=False)
    status = db.Column(db.String(20))
    title = db.Column(db.String(255))
    topic = db.Column(db.String(64), info={
        'label': 'Topic',
        'choices': app.config['CFP_TOPICS']
    })
    summary_md = db.Column(db.Text, info={
        'label': 'Abstract / Summary',
        'description': 'Markdown Formatted %s' % mdcheat()
    })
    outline_md = db.Column(db.Text, info={
        'label': 'Submission Outline',
        'description': 'Markdown Formatted %s' % mdcheat()
    })
    start = db.Column(db.DateTime)
    length = db.Column(db.Integer, default=60)   
    repeat = db.Column(db.Boolean, default=False, info={
        'label': 'This talk has been given before.'
    }) 
    comments = db.relationship('Comment', backref='submission')
    reviews = db.relationship('Review', backref='submission')
    __mapper_args__ = {'polymorphic_on': submission_type}

    @hybrid_property
    def summary(self):
        return markdown.markdown(self.summary_md, escape=True)

    @hybrid_property
    def outline(self):
        return markdown.markdown(self.outline_md, escape=True)

    @hybrid_property
    def reviewed_by(self):
        return [r.user for r in self.reviews]

    @hybrid_property
    def topic_pretty(self):
        for item in app.config['CFP_TOPICS']:
            if item[0] == self.topic:
                return item[1]
        return self.topic

    @hybrid_property
    def score(self):
        avg = 0
        count = 0
        for review in reviews:
            avg += review.score
            count += 1
        return float(avg)/count

    @hybrid_property
    def html_status(self):
        if self.status == 'accepted': return 'success'
        if self.status == 'rejected': return 'danger'
        if self.status == 'under review': return 'warning'
        return 'info'


class Comment(db.Model):
    __tablename__ = 'comments'
    id = db.Column(db.Integer, primary_key=True)
    submission_id = db.Column(db.Integer, db.ForeignKey('submissions.id'))
    public = db.Column(db.Boolean, default=False)
    status = db.Column(db.String(16), default='info')
    text_md = db.Column(db.Text)

    @hybrid_property
    def text(self):
        return markdown.markdown(self.text_md)


class Review(db.Model):
    __tablename__ = 'reviews'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    submission_id = db.Column(db.Integer, db.ForeignKey('submissions.id'))
    score = db.Column(db.Integer)
    user = db.relationship('User', backref='reviews')


class Class(Submission):
    __tablename__ = 'classes'
    __mapper_args__ = {'polymorphic_identity': 'class'}
    id = db.Column(db.Integer, db.ForeignKey('submissions.id'), primary_key=True)
    teachers = db.relationship('User', secondary=teachers, backref='teaching')
    max_seats = db.Column(db.Integer, default=40)
    cost = db.Column(db.Integer, default=0, info={
        'label': 'Is there a cost associated with this training (per seat)?'
    })
    seats = db.relationship('User', secondary=user_seats, backref='classes')

    @hybrid_property
    def open_seats(self):
        return self.max_seats > len(self.seats)


class Talk(Submission):
    __tablename__ = 'talks'
    __mapper_args__ = {'polymorphic_identity': 'talk'}
    id = db.Column(db.Integer, db.ForeignKey('submissions.id'), primary_key=True)
    speakers = db.relationship('User', secondary=speakers, backref='speaking')


class TicketType(db.Model):
    __tablename__ = 'ticket_types'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    sellable = db.Column(db.Boolean, default=False, info={
        'label': 'Can this ticket type be purchased?'
    })
    cost = db.Column(db.Integer, default=0, info={
        'label': 'How much should this ticket type cost?'
    })
    max_per = db.Column(db.Integer, default=0, info={
        'label': 'Maximum number of this ticket type can a purchaser hold?'
    })
    max_tickets = db.Column(db.Integer, default=0, info={
        'label': 'Maximum number of tickets to be sold of this type',
        'description': 'Setting this to 0 means unlimited.'
    })
    start = db.Column(db.DateTime, info={
        'label': 'When should ticket sales for this ticket type start?'
    })
    end = db.Column(db.DateTime, info={
        'label': 'When should ticket sales for this ticket type stop?'
    })

    @hybrid_property
    def remaining(self):
        return self.max_tickets - len(self.tickets)


ticket_classes = db.Table('ticket_classes',
    db.Column('ticket_id', db.Integer, db.ForeignKey('tickets.id')),
    db.Column('class_id', db.Integer, db.ForeignKey('classes.id'))
)


class Ticket(db.Model):
    __tablename__ = 'tickets'
    id = db.Column(db.Integer, primary_key=True)
    hash = db.Column(db.String(32), unique=True, default=gen_hash(datetime.now().isoformat(), str(randint(0,5000))))
    type_id = db.Column(db.Integer, db.ForeignKey('ticket_types.id'))
    cart_id = db.Column(db.Integer, db.ForeignKey('carts.id'))
    valid = db.Column(db.Boolean, default=False)
    name = db.Column(db.String(64))
    type = db.relationship('TicketType', backref='tickets')
    classes = db.relationship('Class', secondary='ticket_classes', backref='tickets')
    cart = db.relationship('Cart', backref='tickets')


class Discount(db.Model):
    __tablename__ = 'discounts'
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(40))
    value = db.Column(db.Integer, default=0)
    ticket_override = db.Column(db.Integer, default=None, info={
        'label': 'Overload the Ticket Type?'
    })
    max_uses = db.Column(db.Integer, default=0, info={
        'label': 'Maximum Number of Uses'
    })

    @hybrid_property
    def remaining(self):
        return self.max_uses - len(self.carts)


cart_classes = db.Table('cart_classes',
    db.Column('cart_id', db.Integer, db.ForeignKey('carts.id')),
    db.Column('class_id', db.Integer, db.ForeignKey('classes.id'))
)


class Cart(db.Model):
    __tablename__ = 'carts'
    id = db.Column(db.Integer, primary_key=True)
    hash = db.Column(db.String(32), default=gen_hash(datetime.now().isoformat(), str(randint(0,5000))))
    discount_id = db.Column(db.Integer, db.ForeignKey('discounts.id'))
    classes = db.relationship('Class', secondary=cart_classes)




