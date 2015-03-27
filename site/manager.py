#!/usr/bin/env python
from app import create_app
from flask.ext.script import Manager
from flask.ext.migrate import MigrateCommand
from app.auth.models import User, Role
from app.extensions import db

app = create_app()
manager = Manager(app)
manager.add_command('db', MigrateCommand)


#@manager.command
#def setting(name=None, value=None):
#    if name:
#        setting = Setting.query.filter_by(name=name).first()
#        if value:
#            if setting:
#                setting.value = value
#                db.session.merge(setting)
#            else:
#                setting = Setting(name=name, value=value)
#                db.session.add
#            db.session.flush()
#            db.session.commit()
#        else:
#            print '%s = %s' % (setting.name, setting.value)
#    else:
#        for setting in Setting.query.all():
#            print setting.name


@manager.command
def populate():
    admin = Role(name='admin')
    db.session.add(admin)
    db.session.add(Role(name='author'))
    db.session.add(Role(name='reviewer'))
    db.session.add(Role(name='chair'))
    email = raw_input('Create Admin User - Enter Email: ')
    user = User(email=email)
    user.roles.append(admin)
    db.session.add(user)
    db.session.commit()


if __name__ == '__main__':
    manager.run()