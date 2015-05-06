from flask import Blueprint, render_template, redirect, url_for, flash, current_app, request
from flask.ext.login import current_user, login_required
from flask.ext.mail import Message
from app.extensions import db, mail
from app.submissions.models import Submission, Round
from app.auth.models import User
from .models import Review, Comment
from .forms import ReviewForm, CommentForm

review = Blueprint('review', __name__, template_folder='templates', static_folder=None)

@review.route('/<int:round_id>')
@login_required
def list(round_id):
	if current_user.has_role('reviewer'):
		submissions = Submission.query.filter_by(round_id=round_id).all()
		return render_template('review_list.html', submissions=submissions)
    flash('You are not authorized to view this page', 'danger')
    return redirect(url_for('frontend.index'))


@review.route('/detail/<int:sub_id>')
@login_required
def detail(sub_id):
	if current_user.has_role('reviewer'):
		submission = Submission.query.filter_by(id=sub_id).first_or_404()
		return render_template('review_detail.html', submission=submission)
    flash('You are not authorized to view this page', 'danger')
    return redirect(url_for('frontend.index'))


@review.route('/comment/<int:sub_id>', methods=['GET', 'POST'])
@review.route('/comment/<int:sub_id>/<int:comment_id>', methods=['GET', 'POST'])
@login_required
def comment(sub_id, comment_id=None):
	if current_user.has_role('reviewer'):
		submission = Submission.query.filter_by(id=sub_id).first_or_404()
		if comment_id:
			comment = Comment.query.filter_by(id=comment_id).first_or_404()
		else:
			comment = Comment()
		form = CommentForm(obj=comment)
		if form.validate_on_submit():
			if not comment_id or comment.reviewer == current_user or current_user.has_role('chair'):
				form.populate_obj(comment)
				db.session.commit()
				flash('Comment Created/Updated', 'success')
			else:
				flash('You are not authorized to edit this comment', 'danger')
			return redirect(url_for('.detail', sub_id=submission.id))
		return render_template('review_comment.html', submission=submission, form=form)
    flash('You are not authorized to view this page', 'danger')
    return redirect(url_for('frontend.index'))


@review.route('/review/<int:sub_id>', methods=['GET', 'POST'])
@login_required
def review(sub_id):
	if current_user.has_role('reviewer'):
		submission = Submission.query.filter_by(id=sub_id).first_or_404()
		if current_user in submission.reviewers:
			flash('You have already reviewed this submission', 'warning')
			return redirect(url_for('.list'))
		form = ReviewForm()
		if form.validate_on_submit():
			review = Review()
			form.populate_obj(review)
			submission.reviews.append(review)
			current_user.reviews.append(review)
			db.session.commit()
			flash('Review Submitted', 'success')
			return redirect(url_for('.list'))
		return render_template('review_review.html', submission=submission, form=form)
    flash('You are not authorized to view this page', 'danger')
    return redirect(url_for('frontend.index'))


@review.route('/close/<int:round_id>', methods=['GET', 'POST'])
@login_required
def close(round_id):
	if current_user.has_role('chair'):
		cfpround = Round.query.filter_by(id=round_id).first_or_404()
		cfpround.status = 'reviewed'
		db.session.commit()
		flash('Submission Review Process is now closed', 'success')
    flash('You are not authorized to view this page', 'danger')
    return redirect(url_for('frontend.index'))


@review.route('/select/<int:round_id>', methods=['GET', 'POST'])
@login_required
def select_list(round_id):
	if current_user.has_role('reviewer'):
		submissions = Submission.query.filter_by(round_id=round_id).all()
		for submission in submissions:
			if submission.status == 'generated' and submission.avg_score >= current_app.config['AUTO_ACCEPT']:
				submission.status = 'accepted'
			elif submission.status == 'generated':
				submission.status = 'rejected'
			db.session.commit()
		return render_template('select_list.html', submissions=submissions)
    flash('You are not authorized to view this page', 'danger')
    return redirect(url_for('frontend.index'))


@review.route('/select/accept/<int:sub_id>')
@login_required
def accept(sub_id):
	if current_user.has_role('chair'):
		submission = Submission.query.filter_by(id=sub_id).first_or_404()
		submission.status = 'accepted'
		db.session.commit()
		flash('Submission Changed to Accepted')
    flash('You are not authorized to view this page', 'danger')
    return redirect(url_for('frontend.index'))


@review.route('/select/reject/<int:sub_id>')
@login_required
def reject(sub_id):
	if current_user.has_role('chair'):
		submission = Submission.query.filter_by(id=sub_id).first_or_404()
		submission.status = 'rejected'
		db.session.commit()
		flash('Submission Changed to Rejected')
    flash('You are not authorized to view this page', 'danger')
    return redirect(url_for('frontend.index'))


@review.route('/select/alternate/<int:sub_id>')
@login_required
def alternate(sub_id):
	if current_user.has_role('chair'):
		submission = Submission.query.filter_by(id=sub_id).first_or_404()
		submission.status = 'accepted'
		db.session.commit()
		flash('Submission Changed to Alternate')
    flash('You are not authorized to view this page', 'danger')
    return redirect(url_for('frontend.index'))


@review.route('/complete/<int:round_id>')
@login_required
def complete(round_id):
	if current_user.has_role('chair'):
		cfpround = Round.query.filter_by(id=round_id).first_or_404()
		cfpround.status = 'completed'
		for submission in cfpround.submissions:
			for user in submission.speakers:
				pass
				# We need to add the emailing process and and the
				# ticket creation for speakers here...
		flash('Review Process completed and speakers have been notified', 'success')
    flash('You are not authorized to view this page', 'danger')
    return redirect(url_for('frontend.index'))