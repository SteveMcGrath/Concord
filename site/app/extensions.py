from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.bootstrap import Bootstrap
from flask.ext.migrate import Migrate
from flask.ext.script import Manager
from flask.ext.login import LoginManager
from flask.ext.mail import Mail
from wtforms_alchemy import model_form_factory
from flask.ext.wtf import Form


mail = Mail()
login_manager = LoginManager()
migrate = Migrate()
db = SQLAlchemy()


login_manager.login_view = 'auth.login'


def init_app(app):
    Bootstrap(app)
    mail.init_app(app)
    login_manager.init_app(app)
    db.init_app(app)
    migrate.init_app(app, db)


BaseModelForm = model_form_factory(Form)
class ModelForm(BaseModelForm):
    @classmethod
    def get_session(self):
        return db.session