from flask import render_template, flash, redirect, session, url_for, abort, g
from flask.ext.login import login_user, logout_user, current_user, login_required
from app import app, db, login_manager, forms
from app.models import User, Ticket, Post
from sqlalchemy import desc
from datetime import datetime

from app.views.admin import *
from app.views.tickets import *
from app.views.cfp import *
from app.views.statistics import *

@app.before_request
def before_request():
    g.user = current_user
    g.con_name = app.config['CONFERENCE_NAME']
    g.google_analytics = app.config['GOOGLE_ANALYTICS']

@app.route('/')
def home():
    return render_template('home.html', title='Home')


@app.route('/schedule')
def schedule():
    return render_template('construction.html', title='Schedule')


@app.route('/schedule/bios')
def speaker_bios():
    return render_template('schedule/bios.html', title='Speaker Bios')


@app.route('/training')
def training():
    return render_template('schedule/training.html', title='Training List')


@app.route('/talks')
def talks():
    return render_template('schedule/talks.html', title='Talks List')


#@app.route('/sponsors')
#def sponsors():
#    return render_template('construction.html', title='Sponsors')


@app.route('/location')
def location():
    return render_template('location.html', title='Location')


@app.route('/events')
def events():
    return render_template('events.html', title='Events')


@app.route('/about')
def about():
    return render_template('construction.html', title='About Us')


@app.route('/cft')
def cft():
    return render_template('cft/cft.html', title='Call for Training')


@app.route('/news')
def news():
    posts = Post.query.all()
    return render_template('news.html', title='Conference News', posts=posts)


@app.route('/sponsors')
def sponsors():
    return render_template('sponsors.html', title='CircleCityCon Sponsors')


@app.route('/news/edit/<int:post_id>', methods=['GET', 'POST'])
@app.route('/news/new', methods=['GET', 'POST'])
@login_required
def news_edit(post_id=None):
    if post_id is not None:
        post = Post.query.filter_by(id=post_id).first_or_404()
    else:
        post = Post()
    form = forms.NewsForm(obj=post)
    flash(form.errors)
    if form.validate_on_submit():
        form.populate_obj(post)
        if post_id is not None:
            db.session.merge(post)
        else:
            db.session.add(post)
        db.session.commit()
        flash('Post Submitted!', 'success')
        return redirect(url_for('news'))
    return render_template('news_edit.html', form=form, title='Edit News Article')