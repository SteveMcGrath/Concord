from flask.ext.wtf import Form
from wtforms.fields import *
from flask.ext.wtf.html5 import *
from wtforms.validators import Required, Email, Optional


class RoundForm(Form):
    status = SelectField('Round Status', choices=(
        ('pending', 'Not Yet Open'),
        ('open', 'Open'),
        ('filled', 'Filled'),
        ('reviewing', 'Under Review'),
        ('reviewed', 'Reviews Completed'),
        ('completed', 'Round Closed & Completed'),
    ))
    start = DateTimeField('Automatically Open')
    stop = DateTimeField('Automaticially Close')
    max_subs = IntegerField('Maximum Submissions')


class SubmissionTypeForm(Form):
    sub_type = SelectField('Submission Type', choices=(
        ('talk', 'Talk'),
        ('class', 'Training Class/Workshop'),
    ))


class SubmissionForm(Form):
    title = TextField('Submission Title')
    length = SelectField('Length of the Talk')
    abstract_md = TextAreaField('Abstract', description='Markdown Formatted')
    outline_md = TextAreaField('Outline', description='Markdown Formatted')
    requests_md = TextAreaField('Are there any special requests or anything else we need to be aware of?', 
        description='Markdown Formatted')


class SpeakerForm(Form):
    email = EmailField('Email', validators=[Required(), Email()])
    name = TextField('Name', validators=[Required()])
    bio = TextAreaField('Bio')
