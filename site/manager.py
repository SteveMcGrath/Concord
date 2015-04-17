#!/usr/bin/env python
from app import create_app
from flask.ext.script import Manager
from flask.ext.migrate import MigrateCommand
from app.auth.models import User, Role
from app.extensions import db

app = create_app()
manager = Manager(app)
manager.add_command('db', MigrateCommand)


@manager.command
def cron():
    from datetime import datetime, timedelta
    from app.submissions.models import Submission

    # Incomplete Submission Cleanout
    yesterday = datetime.now() - timedelta(hours=app.config['SUBMISSION_AGE'])
    subs = Submission.query.filter_by(state='generated').filter(Submission.created < yesterday).all()
    db.session.delete(subs)
    print 'Cleaned out %d stale submissions' % len(subs)

    # Incomplete Ticket Sales Cleanout


    # Incomplete Training Sales Cleanout


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