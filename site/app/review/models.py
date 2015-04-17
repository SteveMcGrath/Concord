from sqlalchemy.ext.hybrid import hybrid_property
from datetime import datetime
from app.submissions.models import Submission
from app.extensions import db
import mistune


class Review(db.Model):
    __tablename__ = 'reviews'
    id = db.Column(db.Integer, primary_key=True)
    score = db.Column(db.Integer)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    sub_id = db.Column(db.Integer, db.ForeignKey('submissions.id'))
    reviewer = db.relationship('User', backref='reviews')
    submission = db.relationship('Submission', backref='reviews')


class Comment(db.Model):
    __tablename__ = 'comments'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    sub_id = db.Column(db.Integer, db.ForeignKey('submissions.id'))
    text_md = db.Column(db.Text)
    public = db.Column(db.Boolean)
    reviewer = db.relationship('User', backref='comments')
    submission = db.relationship('Submission', backref='comments')