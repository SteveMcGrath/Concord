from datetime import date
from flask.ext.wtf import Form
from wtforms_alchemy import model_form_factory, ModelForm, ModelFieldList, ModelFormField
from flask.ext.wtf.html5 import *
from wtforms.fields import *
from wtforms.ext.sqlalchemy.fields import QuerySelectField, QuerySelectMultipleField
from wtforms.validators import Required, Optional, Email
from app import app, db
from app.models import *


BaseModelForm = model_form_factory(Form)

def get_categories():
    return Category.query


class ModelForm(BaseModelForm):
    @classmethod
    def get_session(self):
        return db.session


class LoginForm(Form):
    email = EmailField('Email', validators=[Required(), Email()])
    password = PasswordField('Password', validators=[Required()])


class ForgotPasswordForm(Form):
    email = EmailField('Email', validators=[Required(), Email()])


class NewUserForm(Form):
    email = EmailField('Email', validators=[Required(), Email()])


class PasswordRecoveryForm(Form):
    passwd = PasswordField('Password', validators=[Required()])
    verify = PasswordField('Verify Password', validators=[Required()])


class SettingForm(ModelForm):
    class Meta:
        model = Setting


class UserForm(ModelForm):
    class Meta:
        model = User
        exclude = ['password', 'forgot']
        field_args = {'email': {'validators': [Email()]}}


class CFPUserForm(ModelForm):
    class Meta:
        model = User
        include = ['email', 'name', 'bio_md']
        field_args = {
            'email': {'validators': [Email(), Required()]},
            'name': {'validators': [Required()]},
        }


class PostForm(ModelForm):
    class Meta:
        model = Post


class RoundForm(ModelForm):
    class Meta:
        model = Round


class CommentForm(ModelForm):
    class Meta:
        model = Comment


class DiscountCodeForm(ModelForm):
    class Meta:
        model = DiscountCode


class TicketForm(ModelForm):
    class Meta:
        model = Ticket


class TicketTypeForm(ModelForm):
    class Meta:
        model = TicketType


class ClassForm(ModelForm):
    class Meta:
        model = Class
        exclude = ['status', 'start']
        field_args = {'length': {
            'choices': app.config['CLASS_LENGTHS'], 
            'label': 'Length of class (in hours)'
        }}


class TalkForm(ModelForm):
    class Meta:
        model = Talk
        exclude = ['status', 'start']
        field_args = {'length': {
            'choices': app.config['TALK_LENGTHS'],
            'label': 'Length of Talk (in minutes)'
        }}


class TalkSPeakerForm(Form):
    email = EmailField('Email Address', validators=[Required()])
    name = TextField('Speaker Name', validators=[Required()])
    bio_md = TextAreaField ('Speaker Bio', validators=[Required()])


class RemoveSpeakerForm(Form):
    email = EmailField('Speaker\'s Email', validators=[Required()])





