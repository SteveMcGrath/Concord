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


@app.route('/')
def home():
    return render_template('home.html', title='Home')


@app.route('/cfp')
def cfp():
    return render_template('construction.html', title='Call For Papers')


@app.route('/cfp/edit/new', methods=['GET', 'POST'])
@app.route('/cfp/edit/<int:cfp_id>', methods=['GET', 'POST'])
@login_required
def cfp_edit(cfp_id=None):
    if g.user.username == username or g.user.admin:
        if cfp_id:
            submission = Submission.query.filter_by(id=cfp_id).first_or_404()
        else:
            submission = Submission()
            db.session.add(submission)
        form = forms.CallForPaperForm(obj=submission)
        if form.validate_on_submit():
            form.populate_obj(submission)
            db.session.commit()
            if cfp_id:
                flash('CFP Submission Updated')
            else:
                flash('CFP Submission Created')
        return render_template('cfp/edit.html', submission=submission, 
                               form=form, title='CFP Edit/Creation Form')
    return redirect(url_for('home'))


@app.route('/cfp/review/<int:cfp_id>', methods=['GET', 'POST'])
@login_required
def cfp_review(cfp_id):
    if g.user.admin:
        submission = Submission.query.filter_by(id=cfp_id).first_or_404()
        if submission.status == 'submitted':
            submission.status = 'pending review'
            db.session.commit()
        form = forms.CallForPaperReviewForm(obj=submission)
        if form.validate_on_submit():
            form.populate_obj(submission)
            db.session.commit()
            flash('Review Status Updated')
        return render_template('cfp/review.html', submission=submission,
                               title='CFP %s Review' % cfp_id)
    return redirect(url_for('home'))


@app.route('/cfp/review/<int:cfp_id>/accept', methods=['GET', 'POST'])
@login_required
def cfp_accept(cfp_id):
    if g.user.admin:
        submission = Submission.query.filter_by(id=cfp_id).first_or_404()
        submission.status = 'accepted'
        for speaker in submission.speakers:
            speaker.gen_ticket()
            mail.generate(render_template('mail/cfp_accepted.html', 
                          speaker=speaker, submission=submission),
                          send_to=speaker.email,
                          subject='CircleCityCon 2015 Submission Accepted')
        flash('Submission Accepted & Speakers Notified')
    redirect(url_for('cfp_review', cfp_id=cfp_id))


@app.route('/cfp/review/<int:cfp_id>/accept', methods=['GET', 'POST'])
@login_required
def cfp_reject(cfp_id):
    if g.user.admin:
        submission = Submission.query.filter_by(id=cfp_id).first_or_404()
        submission.status = 'rejected'
        for speaker in submission.speakers:
            speaker.gen_ticket(price=100)
            mail.generate(render_template('mail/cfp_rejected.html', 
                          speaker=speaker, submission=submission),
                          send_to=speaker.email,
                          subject='CircleCityCon 2015 Submission Rejection')
        flash('Submission Rejected & Speakers Notified')
    redirect(url_for('cfp_review', cfp_id=cfp_id))


@app.route('/cfp/review')
@login_required
def cfp_review_list():
    if g.user.admin:
        return render_template('cfp/review_list.html', 
            unviewed=Submission.query.filter_by(status='submitted').all(),
            pending = Submission.query.filter_by(status='pending review').all(),
            reviewing = Submission.query.filter_by(status='under review').all(),
            accepted = Submission.query.filter_by(status='accepted').all(),
            rejected = Submission.query.filter_by(status='rejected').all())


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
    return ticket.generate(app.config['CONFERENCE_EVENT'])