from flask.ext.wtf import Form 
from flask.ext.wtf.html5 import EmailField
from wtforms.fields import PasswordField
from wtforms.validators import Required
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from .models import SponsorTier


def get_sponsor_tiers():
    return SponsorTier.query


class SponsorTierForm(Form):
    name = TextField('Tier Name', validators=[Required()])
    weight = IntegerField('Weight', default=0, validators=[Required()])


class SponsorForm(Form):
    name = TextField('Sponsor Name', validators=[Required()])
    link = TextField('Sponsor Homepage', validators=[Required()])
    image_file = FileField('Sponsor Logo', validators=[Required()])
    tier = QuerySelectField('Tier', query_factory=get_sponsor_tiers, 
                            get_label='name', allow_blank=False)
