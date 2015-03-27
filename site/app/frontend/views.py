from flask import Blueprint, render_template

frontend = Blueprint('frontend', __name__, 
    template_folder='templates', 
    static_folder='static')


@frontend.route('/')
def index():
    return render_template('homepage.html')
