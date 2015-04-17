from flask.ext.wtf import Form 
from flask.ext.wtf.html5 import *
from wtforms.fields import *
from wtforms.validators import Required


class ReviewForm(Form):
    score = SelectField('Score', choices=(
        ('0', '0 Stars'),
        ('1', '1 Star'),
        ('2', '2 Stars'),
        ('3', '3 Stars'),
        ('4', '4 Stars'),
        ('5', '5 Stars'),
    ), validators=[Required()])


class CommentForm(Form):
    text_md = TextAreaField('Comment', validators=[Required()])
    public = BooleanField('Visible to Submitter', default=False)