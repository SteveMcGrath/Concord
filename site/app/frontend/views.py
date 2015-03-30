from flask import Blueprint, render_template
from app.submissions.models import Round

frontend = Blueprint('frontend', __name__, 
    template_folder='templates', 
    static_folder='static')


@frontend.route('/')
def index():
    return render_template('homepage.html')
