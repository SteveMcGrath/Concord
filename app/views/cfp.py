from flask import render_template, flash, redirect, session, url_for, abort, g
from flask.ext.login import login_user, logout_user, current_user, login_required
from app import app, db, login_manager, forms
from app.models import User, Ticket
from sqlalchemy import desc
from datetime import datetime


@app.route('/cfp')
def cfp():
    return render_template('/cfp/home.html', title='Call for Papers')