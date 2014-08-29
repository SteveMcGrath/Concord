from flask import render_template, flash, redirect, session, url_for, abort, g
from flask.ext.login import login_user, logout_user, current_user, login_required
from app import app, db, login_manager
from app.models import User, Submission, Ticket
from sqlalchemy import desc
import forms


@login_manager.user_loader
def load_user(userid):
    return User.query.filter_by(id=int(userid)).first()


@app.before_request
def before_request():
    g.user = current_user


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
    return render_template('login.html', title='Sign In', login=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route('/user/<username>')
def user_info(username):
    if g.user.username == username or g.user.admin:
        user = User.query.filter_by(username=username).first_or_404()
        return render_template('user_info.html', person=user, 
                                title='%s - Information' % user.username)
    return redirect(url_for('home'))




@app.route('/')
def home():
    return render_template('home.html', title='Home')


@app.route('/cfp')
def cfp():
    return render_template('construction.html', title='Call For Papers')


@app.route('/cfp/<cfp_id>', methods=['GET', 'POST'])
@login_required
def cfp_edit(cfp_id='new'):
    form = forms.CallForPaperForm()



@app.route('/tickets')
def tickets():
    return render_template('construction.html', title='Tickets')


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
    return render_template('construction.html', title='Events')


@app.route('/training')
def training():
    return render_template('construction.html', title='Training')


@app.route('/about')
def about():
    return render_template('construction.html', title='About Us')


@app.route('/tickets/print/<ticket_id>')
def ticket_print(ticket_id):
    '''
    Generates a printable ticket.
    '''
    ticket = Ticket.query.filter_by(ticket_hash=ticket_id).first_or_404()
    return ticket.generate('CircleCityCon 2015')