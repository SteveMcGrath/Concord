from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.login import LoginManager
from flask.ext.migrate import Migrate, MigrateCommand
from flask.ext.script import Manager
from flask.ext.bootstrap import Bootstrap

app = Flask(__name__)
app.config.from_object('config')

db = SQLAlchemy(app)
Bootstrap(app)

migrate = Migrate(app, db)

manager = Manager(app)
manager.add_command('db', MigrateCommand)


class Ticket(db.Model):
    __tablename__ = 'tickets'
    id = db.Column(db.Integer, primary_key=True)
    ticket_type = db.Column(db.Text)
    ticket_hash = db.Column(db.Text)
    redeemed = db.Column(db.Boolean, default=False)
    email = db.Column(db.Text)
    name = db.Column(db.Text)


@app.route('/<tickethash>')
def checkin(tickethash):
    ticket = Ticket.query.filter_by(ticket_hash=tickethash).first()
    if ticket is None:
        flash('No Ticket Found!', 'danger')
    if ticket.redeemed:
        flash('Ticket Already Checked In!', 'warning')
    else:
        ticket.redeemed = True
        db.session.merge(ticket)
        db.session.commit()
        flash('Ticket Successfully Checked in!', 'success')
    return render_template('page.html')