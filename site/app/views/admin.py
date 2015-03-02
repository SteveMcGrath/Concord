from flask import render_template, flash, redirect, session, url_for, abort, g
from flask.ext.login import login_user, logout_user, current_user, login_required
from app import app, db, login_manager, forms
from app.models import User, Ticket
from common import display_errors


@login_manager.user_loader
def load_user(userid):
    return User.query.filter_by(id=int(userid)).first()


def administrative(func):
    def wrapped(*args, **kwargs):
        if not g.user.admin:
            flash('Not Authorized to access that page.  Not an Admin', 'danger')
            return redirect(url_for('home'))
        return func(*args, **kwargs)
    return wrapped


def author(func):
    def wrapped(*args, **kwargs):
        if not g.user.author:
            flash('Not Authorized to access that page.  Not an Author', 'danger')
            return redirect(url_for('home'))
        return func(*args, **kwargs)
    return wrapped


def reviewer(func):
    def wrapped(*args, **kwargs):
        if not g.user.reviewer:
            flash('Not Authorized to access that page.  Not a Reviewer', 'danger')
            return redirect(url_for('home'))
        return func(*args, **kwargs)
    return wrapped


@app.route('/login', methods=['GET', 'POST'])
def login():
    if g.user.is_authenticated():
        return redirect(url_for('home'))
    form = forms.LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is not None and user.check_password(form.password.data):
            login_user(user)
            return redirect(url_for('home'))
        else:
            user = None
        if user == None:
            flash('Invalid Username or Password', 'error')
    return render_template('login.html', title='Sign In', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route('/user/new', methods=['GET', 'POST'])
@app.route('/user/<username>', methods=['GET', 'POST'])
def user_info(username=None):
    if g.user.username == username or g.user.admin:
        user = User.query.filter_by(username=username).first_or_404()
        tickets = Ticket.query.filter_by(user_id=user.id).all()
        return render_template('user_info.html', person=user, tickets=tickets,
                                title='%s - Information' % user.username)
    return redirect(url_for('home'))