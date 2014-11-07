from flask import render_template, flash, redirect, session, url_for, abort, g
from flask.ext.login import login_user, logout_user, current_user, login_required
from app import app, db, login_manager, forms
from app.models import User, Ticket
from sqlalchemy import desc
from datetime import datetime


@app.route('/cfp')
def cfp_home():
    return render_template('/cfp/home.html', title='Call for Papers')



# Stubbed out for now.
#@app.route('/cfp/edit/new', methods=['GET', 'POST'])
#@app.route('/cfp/edit/<int:cfp_id>', methods=['GET', 'POST'])
#@login_required
#def cfp_edit(cfp_id=None):
#    if g.user.username == username or g.user.admin:
#        if cfp_id:
#            submission = Submission.query.filter_by(id=cfp_id).first_or_404()
#        else:
#            submission = Submission()
#            db.session.add(submission)
#        form = forms.CallForPaperForm(obj=submission)
#        if form.validate_on_submit():
#            form.populate_obj(submission)
#            db.session.commit()
#            if cfp_id:
#                flash('CFP Submission Updated')
#            else:
#                flash('CFP Submission Created')
#        return render_template('cfp/edit.html', submission=submission, 
#                               form=form, title='CFP Edit/Creation Form')
#    return redirect(url_for('home'))
#
#
#@app.route('/cfp/review/<int:cfp_id>', methods=['GET', 'POST'])
#@login_required
#def cfp_review(cfp_id):
#    if g.user.admin:
#        submission = Submission.query.filter_by(id=cfp_id).first_or_404()
#        if submission.status == 'submitted':
#            submission.status = 'pending review'
#            db.session.commit()
#        form = forms.CallForPaperReviewForm(obj=submission)
#        if form.validate_on_submit():
#            form.populate_obj(submission)
#            db.session.commit()
#            flash('Review Status Updated')
#        return render_template('cfp/review.html', submission=submission,
#                               title='CFP %s Review' % cfp_id)
#    return redirect(url_for('home'))
#
#
#@app.route('/cfp/review/<int:cfp_id>/accept', methods=['GET', 'POST'])
#@login_required
#def cfp_accept(cfp_id):
#    if g.user.admin:
#        submission = Submission.query.filter_by(id=cfp_id).first_or_404()
#        submission.status = 'accepted'
#        for speaker in submission.speakers:
#            speaker.gen_ticket()
#            mail.generate(render_template('mail/cfp_accepted.html', 
#                          speaker=speaker, submission=submission),
#                          send_to=speaker.email,
#                          subject='CircleCityCon 2015 Submission Accepted')
#        flash('Submission Accepted & Speakers Notified')
#    redirect(url_for('cfp_review', cfp_id=cfp_id))
#
#
#@app.route('/cfp/review/<int:cfp_id>/accept', methods=['GET', 'POST'])
#@login_required
#def cfp_reject(cfp_id):
#    if g.user.admin:
#        submission = Submission.query.filter_by(id=cfp_id).first_or_404()
#        submission.status = 'rejected'
#        for speaker in submission.speakers:
#            speaker.gen_ticket(price=100)
#            mail.generate(render_template('mail/cfp_rejected.html', 
#                          speaker=speaker, submission=submission),
#                          send_to=speaker.email,
#                          subject='CircleCityCon 2015 Submission Rejection')
#        flash('Submission Rejected & Speakers Notified')
#    redirect(url_for('cfp_review', cfp_id=cfp_id))
#
#
#@app.route('/cfp/review')
#@login_required
#def cfp_review_list():
#    if g.user.admin:
#        return render_template('cfp/review_list.html', 
#            unviewed=Submission.query.filter_by(status='submitted').all(),
#            pending = Submission.query.filter_by(status='pending review').all(),
#            reviewing = Submission.query.filter_by(status='under review').all(),
#            accepted = Submission.query.filter_by(status='accepted').all(),
#            rejected = Submission.query.filter_by(status='rejected').all())