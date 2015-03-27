from flask import Blueprint, render_template, redirect, url_for, flash, current_app, request
from flask.ext.login import login_user, logout_user, current_user, login_required
from flask.ext.mail import Message
from functools import wraps
from app.extensions import db, mail, login_manager
from .models import User, Role
from .forms import LoginForm, RegistrationForm, PasswordChangeForm


auth = Blueprint('auth', __name__, template_folder='templates', static_folder=None)


@login_manager.user_loader
def load_user(user_id):
    return User.query.filter_by(id=int(user_id)).first()


@auth.route('/login', methods=['GET', 'POST'])
def login():
    '''User login'''
    if current_user.is_authenticated():
        return redirect(request.args.get('next') or url_for('user.index', user_id=current_user.id))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and user.is_valid_password(form.password.data):
            user.forgot = None
            db.session.commit()
            login_user(user)
            return redirect(request.args.get('next') or url_for('user.index'))
        flash('Invalid email or password', 'danger')
    return render_template('login.html', form=form)


@auth.route('/register', methods=['GET', 'POST'])
def register():
    '''User registration and password retreival'''
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            # If we found an existing user, then we will send them an email
            # informing them how to reset their password.
            user.forgot_password()
            msg = Message(render_template('forgot_password.email', user=user))
            msg.subject = 'Password Recovery'
            msg.add_recipient(form.email.data)
            flash('Password recovery email has been sent.  Check your inbox.', 'warning')
        else:
            # If we were unable to find a user, then we will need to email out
            # a new user welcome email and create the user entry.
            user = User(email=form.email.data)
            user.forgot_password()
            db.session.add(user)
            msg = Message(render_template('new_user.email', user=user))
            msg.subject = 'New User Verification'
            msg.add_recipient(form.email.data)
        db.session.commit()
        current_app.logger.debug('Forgot: %s' % url_for('.recovery', recovery_id=user.forgot))
        mail.send(msg)
        return redirect(url_for('.login'))
    return render_template('register.html', form=form)


@auth.route('/recover/<recovery_id>', methods=['GET', 'POST'])
def recovery(recovery_id):
    form = PasswordChangeForm()
    user = User.query.filter_by(forgot=recovery_id).first()
    if user:
        if form.validate_on_submit():
            if form.password.data == form.verify.data:
                user.password = form.password.data
                db.session.commit()
                flash('Password successfully reset', 'success')
                return redirect(url_for('.login'))
            flash('Passwords did nto match', 'warning')
        return render_template('password_change.html', form=form)
    flash('Invalid password recovery hash', 'danger')
    return redirect(url_for('frontend.index'))


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('frontend.index'))
