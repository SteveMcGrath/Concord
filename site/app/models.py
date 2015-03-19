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

seats = db.Table('seats',
    db.Column('class_id', db.Integer, db.ForeignKey('classes.id')),
    db.Column('user_id', db.Integer, db.ForeignKey('users.id'))
)


class Round(db.Model):
    __tablename__ = 'rounds'
    id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.String('10'), default='pending', info={
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
    submission_id = db.Column(db.Integer, db.ForeignKey('submissions.id'))
    score = db.Column(db.Integer)


class Class(Submission):
    __tablename__ = 'classes'
    __mapper_args__ = {'polymorphic_identity': 'class'}
    id = db.Column(db.Integer, db.ForeignKey('submissions.id'), primary_key=True)
    teachers = db.relationship('User', secondary=teachers, backref='teaching')
    max_seats = db.Column(db.Integer, default=40)
    cost = db.Column(db.Integer, default=0, info={
        'label': 'Is there a cost associated with this training (per seat)?'
    })
    seats = db.relationship('User', secondary=seats, backref='classes')

    @hybrid_property
    def open_seats(self):
        return self.max_seats > len(self.seats)


class Talk(Submission):
    __tablename__ = 'talks'
    __mapper_args__ = {'polymorphic_identity': 'talk'}
    id = db.Column(db.Integer, db.ForeignKey('submissions.id'), primary_key=True)
    speakers = db.relationship('User', secondary=speakers, backref='speaking')

