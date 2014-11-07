from datetime import date
from flask.ext.wtf import Form
from wtforms.fields import *
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from wtforms.validators import Required, Optional, Email
from sqlalchemy import desc, or_, and_
from app.models import Ticket, User


def open_training():
    return Submission.query.filter(and_(
        Submission.training == True,
        len(Submission.tickets) < Submission.seats
    ))


class LoginForm(Form):
    username = TextField('Username', validators=[Required()])
    password = PasswordField('Password', validators=[Required()])
    submit = SubmitField('Login')


class TicketPurchaseForm(Form):
    email = TextField('email', validators=[Required(), Email()])
    opt_in = BooleanField('Opt In', default=True)
    training = QuerySelectField('Training', query_factory=open_training,
        get_pk=lambda t: t.id, 
        get_label=lambda t: t.title,
        allow_blank=True,
    )
    submit = SubmitField('Purchase')


class CFPSubmissionForm(Form):
    title = TextField('Title', validators=[Required()])
    abstract = TextAreaField('Abstract', validators=[Required()])
    outline = TextAreaField('Outline', validators=[Required()])
    panel = BooleanField('Is this talk a panel?', default=False)
    tool = BooleanField('Will there be a tool released?', default=False)
    exploit = BooleanField('Will there be an exploit released?', default=False)
    demo = BooleanField('Will there be a live demo?', default=False)
    new_talk = BooleanField('Is this a new talk?', default=False)
    time = IntegerField('How many minutes is this Talk?', default=50)
    why = TextAreaField('Why should we accept your talk?')
    needs = TextAreaField('Are there any Specific Needs?')
    submit = SubmitField('Submit CFP Submission')


class CFTSubmissionForm(Form):
    title = TextField('Title', validators=[Required()])
    abstract = TextAreaField('Abstract', validators=[Required()])
    outline = TextAreaField('Syllabus', validators=[Required()])
    new_class = BooleanField('Is this a new training class?', default=False)
    days = IntegerField('How many days is this training?', default=1)
    hours = IntegerField('How many hours a day is this training?', default=4)
    min_seats = IntegerField('Whats the Minimum number of students?', default=10)
    max_seats = IntegerField('Whats the maximum number of students?', default=30)
    why = TextAreaField('Why should we accept your class?')
    needs = TextAreaField('Are there any Specific Needs?')
    submit = SubmitField('Submit CFT Submission')


class CFPReviewForm(Form):
    status = SelectField('Review Status', choices=(
        ('pending review', 'Pending Review'),
        ('under review', 'Currently Under Review'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
    ))
    review_rating = SelectField('Rating', choices=(
        (0, 'Un-rated'),
        (1, '1 Star'),
        (2, '2 Stars'),
        (3, '3 Stars'),
        (4, '4 Stars'),
        (5, '5 Stars'),
    ), validators=[Required()])
    review_notes = TextField('Review Notes')
    submit = SubmitField('Update Review Status')