from sqlalchemy.ext.hybrid import hybrid_property
from app.extensions import db
from app.user.models import User


class Round(db.Model):
    __tablename__ = 'rounds'
    id = db.Column(db.Integer, primary_key=True)
    max_subs = db.Column(db.Integer, default=0)
    start = db.Column(db.DateTime)
    stop = db.Column(db.DateTime)
    status = db.Column(db.String(20), default='pending')


class Speaker(db.Model):
    __tablename__ = 'speakers'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'))
    sub_id = db.Column(db.Integer, db.ForeignKey('submissions.id', ondelete='CASCADE'))


class Submission(db.Model):
    __tablename__ = 'submissions'
    id = db.Column(db.Integer, primary_key=True)
    round_id = db.Column(db.Integer, db.ForeignKey('rounds.id'))
    title = db.Column(db.String(255))
    type = db.Column(db.String(10))
    abstract_md = db.Column(db.Text)
    outline_md = db.Column(db.Text)
    requests_md = db.Column(db.Text)
    length = db.Column(db.Integer)
    speakers = db.relationship('User', secondary='speakers', backref='submissions')
    
