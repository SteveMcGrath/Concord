from flask import current_app
from flask.ext.wtf import Form
from wtforms.fields import TextField, SelectField, TextAreaField
from flask.ext.wtf.html5 import EmailField
from wtforms.validators import Required, Email
from wtforms.ext.sqlalchemy.fields import QuerySelectField, QuerySelectMultipleField
from app.auth.models import Role, User

def get_roles():
    return Role.query


class ProfileForm(Form):
    name = TextField('Name')
    email = EmailField('Email Address', validators=[Required(), Email()])
    shirt = SelectField('Short Size')
    roles = QuerySelectMultipleField('Roles', query_factory=get_roles, get_label='name', allow_blank=True)
    bio_md = TextAreaField('Bio', description='Markdown Supported')
