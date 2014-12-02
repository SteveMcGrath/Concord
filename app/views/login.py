from flask import render_template, flash, redirect, session, url_for, abort, g
from flask.ext.login import login_user, logout_user, current_user, login_required
from app import app, db, login_manager, forms
from app.models import User, Ticket

@login_manager.user_loader
def load_user(userid):
    return User.query.filter_by(id=int(userid)).first()


@app.route('/login', methods=['GET', 'POST'])
def login():
    if g.user.is_authenticated():
        return redirect(url_for('user_info', username=g.user.username))
    form = forms.LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is not None and user.check_password(form.password.data):
            login_user(user)
            return redirect(url_for('user_info', username=user.username))
        else:
            user = None
        if user == None:
            flash('Invalid Username or Password', 'error')
    return render_template('login.html', title='Sign In', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route('/user/<username>')
def user_info(username):
    if g.user.username == username or g.user.admin:
        user = User.query.filter_by(username=username).first_or_404()
        tickets = Ticket.query.filter_by(user_id=user.id).all()
        return render_template('user_info.html', person=user, tickets=tickets,
                                title='%s - Information' % user.username)
    return redirect(url_for('home'))