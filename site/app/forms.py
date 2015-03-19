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


class CategoryForm(ModelForm):
    class Meta:
        model = Category


class PostForm(ModelForm):
    class Meta:
        model = Post
    category = QuerySelectField('Category', query_factory=get_categories, get_label='name')


class RoundForm(ModelForm):
    class Meta:
        model = Round


class CommentForm(ModelForm):
    class Meta:
        model = Comment


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


class TalkSubForm(ModelForm):
    class Meta:
        model = TalkQuestionnaire


class ClassSubForm(ModelForm):
    class Meta:
        model = ClassQuestionnaire


