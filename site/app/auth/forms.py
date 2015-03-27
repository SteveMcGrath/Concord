from flask.ext.wtf import Form 
from flask.ext.wtf.html5 import EmailField
from wtforms.fields import PasswordField
from wtforms.validators import Required, Email


class LoginForm(Form):
    '''Primary authentication form'''
    email = EmailField('Email', validators=[Required(), Email()])
    password = PasswordField('Password', validators=[Required()])


class RegistrationForm(Form):
    '''User registration and password retreival form'''
    email = EmailField('Email', validators=[Required()])


class PasswordChangeForm(Form):
    '''User Password Change Form'''
    password = PasswordField('Password', validators=[Required()])
    verify = PasswordField('Verify Password', validators=[Required()])