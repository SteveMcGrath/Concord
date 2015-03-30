from flask import Flask, render_template, redirect, url_for
from flask.ext.bootstrap import Bootstrap
from flask.ext.mail import email_dispatched
from os import path

def log_message(message, app):
    app.logger.debug(message.subject)


def create_app():
    app = Flask(__name__, static_folder='tmpl')

    app.config.from_object('app.defaults')
    if path.exists('settings.py'):
        app.config.from_object('settings.py')
        
    import extensions
    extensions.init_app(app)
    email_dispatched.connect(log_message)

    from frontend import frontend
    from auth import auth
    from user import user
    from submissions import subs
    app.register_blueprint(frontend, url_prefix='/con')
    app.register_blueprint(auth, url_prefix='/auth')
    app.register_blueprint(user, url_prefix='/user')
    app.register_blueprint(subs, url_prefix='/submissions')

    @app.route('/')
    def homepage(): 
        return redirect(url_for('frontend.index'))
    return app