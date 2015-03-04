from flask import render_template, flash, g
from app import app, db
from app.models import User, Setting
import smtplib

def send_email(template, 
               notification='Please Check you Inbox for Further Instructions.', 
               **kwargs):
	message = render_template(template, **kwargs)
	if 'DEVELOPER' in app.config:
		print '\n%s\n' % message
	else:
		server = smtplib.SMTP(Setting.query().filter_by(name='EMAIL_SERVER'))
		server.sendmail(Setting.query().filter_by(name='EMAIL_NOREPLY'),
					    [user.email], message)
	flash(notification, 'info')