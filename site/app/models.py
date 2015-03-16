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


class Setting(db.Model):
    __tablename__ = 'settings'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), unique=True)
    value = db.Column(db.Text)


class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True)
    name = db.Column(db.String(255))
    password = db.Column(db.String(32))
    admin = db.Column(db.Boolean, default=False)
    author = db.Column(db.Boolean, default=False)
    reviewer = db.Column(db.Boolean, default=False)
    chair = db.Column(db.Boolean, default=False)
    forgot = db.Column(db.String(32))
    bio_md = db.Column(db.Text)

    @hybrid_property
    def bio(self):
        return markdown.markdown(self.bio_md)

    def update_password(self, password):
        self.password = gen_hash(str(self.id), password)

    def check_password(self, password):
        return self.password == gen_hash(str(self.id), password)

    def forgot_password(self):
        self.forgot = gen_hash(str(self.id), datetime.now().isoformat())


class Category(db.Model):
    __tablename__ = 'categories'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), unique=True)


class Upload(db.Model):
    __tablename__ = 'uploads'
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), unique=True)


class Post(db.Model):
    __tablename__ = 'posts'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    body_md = db.Column(db.Text)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'))
    draft = db.Column(db.Boolean, default=True)
    mp3 = db.Column(db.Text)
    category = db.relationship('Category', backref='posts')
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
    started = db.Column(db.Boolean, default=False)
    closed = db.Column(db.Boolean, default=False)
    start_date = db.Column(db.DateTime)
    stop_date = db.Column(db.DateTime)
    accept_classes = db.Column(db.Boolean, default=True)
    accept_talks = db.Column(db.Boolean, default=True)
    submissions = db.relationship('Submission', backref='round')

    @hybrid_property
    def close(self):
        self.closed = True
        for submission in self.submissions:
            submission.under_review = True


class Submission(db.Model):
    __tablename__ = 'submissions'
    id = db.Column(db.Integer, primary_key=True)
    round_id = db.Column(db.Integer, db.ForeignKey('rounds.id'))
    submission_type = db.Column(db.String(32), nullable=False)
    under_review = db.Column(db.Boolean, default=False)
    title = db.Column(db.String(255))
    summary_md = db.Column(db.Text)
    start = db.Column(db.DateTime)
    accepted = db.Column(db.Boolean, default=False)
    rejected = db.Column(db.Boolean, default=False)
    length = db.Column(db.Integer, default=60)    
    comments = db.relationship('Comment', backref='submission')
    reviews = db.relationship('Review', backref='submission')
    __mapper_args__ = {'polymorphic_on': submission_type}

    @hybrid_property
    def summary(self):
        return markdown.markdown(self.summary_md)

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
        if accepted: return 'success'
        if rejected: return 'danger'
        if under_review: return 'warning'
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
    cost = db.Column(db.Integer, default=0)
    seats = db.relationship('User', secondary=seats, backref='classes')


class Talk(Submission):
    __tablename__ = 'talks'
    __mapper_args__ = {'polymorphic_identity': 'talk'}
    id = db.Column(db.Integer, db.ForeignKey('submissions.id'), primary_key=True)
    speakers = db.relationship('User', secondary=speakers, backref='speaking')


class Questionnaire(db.Model):
    __tablename__ = 'questionnaires'
    id = db.Column(db.Integer, primary_key=True)
    class_type = db.Column(db.String(5))
    __mapper_args__ = {'polymorphic_on': class_type}


class TalkQuestionnaire(Questionnaire):
    __tablename__ = 'talk_questionnaires'
    __mapper_args__ = {'polymorphic_identity': 'talk'}
    id = db.Column(db.Integer, db.ForeignKey('questionnaires.id'), primary_key=True)


class ClassQuestionnaire(Questionnaire):
    __tablename__ = 'class_questionnaires'
    __mapper_args__ = {'polymorphic_identity': 'class'}
    id = db.Column(db.Integer, db.ForeignKey('questionnaires.id'), primary_key=True)

