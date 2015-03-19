from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.login import LoginManager
from flask.ext.migrate import Migrate, MigrateCommand
from flask.ext.script import Manager
from flask.ext.bootstrap import Bootstrap
from flask.ext.mail import Mail

__version__ = '0.2.0a'
__author__ = 'Steven McGrath <steve@chigeek.com>'

app = Flask(__name__)
app.config.from_object('config')

db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
Bootstrap(app)
migrate = Migrate(app, db)
mail = Mail(app)

manager = Manager(app)
manager.add_command('db', MigrateCommand)

from app import models, views