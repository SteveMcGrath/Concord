from flask import render_template, flash, redirect, session, url_for, abort, g
from flask.ext.login import login_user, logout_user, current_user, login_required
from app import app, db, login_manager, forms
from app.models import User, Ticket
from sqlalchemy import desc
from datetime import datetime

from app.views.login import *
from app.views.tickets import *
from app.views.cfp import *

@app.route('/')
def home():
    return render_template('home.html', title='Home')


@app.route('/cfp')
def cfp():
    return render_template('construction.html', title='Call For Papers')

@app.route('/schedule')
def schedule():
    return render_template('construction.html', title='Schedule')


@app.route('/sponsors')
def sponsors():
    return render_template('construction.html', title='Sponsors')


@app.route('/location')
def location():
    return render_template('location.html', title='Location')


@app.route('/events')
def events():
    return render_template('events.html', title='Events')


@app.route('/training')
def training():
    return render_template('construction.html', title='Training')


@app.route('/about')
def about():
    return render_template('construction.html', title='About Us')