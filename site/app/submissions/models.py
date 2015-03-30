from sqlalchemy.ext.hybrid import hybrid_property
from app.extensions import db
from app.auth.models import User
from datetime import datetime
import mistune


class Round(db.Model):
    __tablename__ = 'rounds'
    id = db.Column(db.Integer, primary_key=True)
    max_subs = db.Column(db.Integer, default=0)
    start = db.Column(db.Date)
    stop = db.Column(db.Date)
    status = db.Column(db.String(20), default='pending')


class Speaker(db.Model):
    __tablename__ = 'speakers'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'))
    sub_id = db.Column(db.Integer, db.ForeignKey('submissions.id', ondelete='CASCADE'))


class Submission(db.Model):
    __tablename__ = 'submissions'
    id = db.Column(db.Integer, primary_key=True)
    created = db.Column(db.DateTime, default=datetime.now())
    round_id = db.Column(db.Integer, db.ForeignKey('rounds.id'))
    status = db.Column(db.String(20), default='generated')
    title = db.Column(db.String(255))
    type = db.Column(db.String(10))
    topic = db.Column(db.String(30))
    abstract_md = db.Column(db.Text)
    outline_md = db.Column(db.Text)
    requests_md = db.Column(db.Text)
    length = db.Column(db.Integer)
    speakers = db.relationship('User', secondary='speakers', backref='submissions')
    round = db.relationship('Round', backref='submissions')

    @hybrid_property
    def abstract(self):
        return mistune.markdown(self.abstract_md, escape=True)

    @hybrid_property
    def requests(self):
        return mistune.markdown(self.abstract_md, escape=True)

    @hybrid_property
    def outline(self):
        return mistune.markdown(self.outline_md, escape=True)
    
