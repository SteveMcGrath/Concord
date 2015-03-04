from datetime import date
from flask.ext.wtf import Form
from flask.ext.wtf.html5 import *
from wtforms.fields import *
from wtforms.ext.sqlalchemy.fields import QuerySelectField, QuerySelectMultipleField
from wtforms.validators import Required, Optional, Email
from sqlalchemy import desc, or_, and_
from app import app


class LoginForm(Form):
    email = EmailField('Email', validators=[Required(), Email()])
    password = PasswordField('Password', validators=[Required()])
    submit = SubmitField('Login')


class ForgotPasswordForm(Form):
    email = EmailField('Email', validators=[Required(), Email()])
    submit = SubmitField('Reset Password')


class NewUserForm(Form):
    email = EmailField('Email', validators=[Required(), Email()])
    submit = SubmitField('Create User')


class PasswordRecoveryForm(Form):
    passwd = PasswordField('Password', validators=[Required()])
    verify = PasswordField('Verify Password', validators=[Required()])
    submit = SubmitField('Reset Password')


class UserForm(Form):
    email = EmailField('Email Address', validators=[Required(), Email()])
    admin = BooleanField('Administrative Priviledge')
    author = BooleanField('News Posting Priviledge')
    reviewer = BooleanField('CFP Reviewing Priviledge')
    char = BooleanField('CFP Chair Priviledge')
    bio_md = TextAreaField('Biography', description='Markdown Text')
    submit = SubmitField('Update User')


class NewsForm(Form):
    title = TextField('Title', validators=[Required()])
    draft = BooleanField('Draft Post')
    body_md = TextAreaField('Post Body', validators=[Required()])
    submit = SubmitField('Add/Update')


class CFPRoundForm(Form):
    start_date = DateTimeField('When to Open the Round Automatically?', validators=[Required()])
    stop_date = DateTimeField('When to Close the Round Automaticaly?', validators=[Required()])
    started = BooleanField('Has the CFP Round Started?')
    closed = BooleanField('Has the CFP Round Ended?')
    accept_classes = BooleanField('Are we accepting Training Classes?')
    accept_talks = BooleanField('Are We Accepting Talks?')
    submit = SubmitField('Add/Update Round')


class CFPAddSpeakerForm(Form):
    email = EmailField('Email Address', validators=[Required(), Email()])
    name = TextField('Name/Handle', validators=[Required()])
    bio_md = TextAreaField('Biography', validators=[Required()])
    submit = SubmitField('Add Speaker')


class CFPTalkQuestionnaireForm(Form):
    pass


class CFPClassQuestionnaireForm(Form):
    pass


class CFPCommentsForm(Form):
    text_md = TextAreaField('Comment')
    public = BooleanField('Should the Submitter see this comment?')
    status = SelectField('Status', choices=(
        ('info', 'Informational'),
        ('warning', 'Warning'),
        ('danger', 'Issue'),
        ('success', 'Approval')
    ), default='info')
    submit = SubmitField('Add Comment')

