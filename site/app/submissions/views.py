from flask import Blueprint, render_template, redirect, url_for, current_app, flash
from flask.ext.login import current_user, login_required
from app.extensions import db
from app.auth.models import User
from .models import Round, Submission
from .forms import (RoundForm, SubmissionTypeForm, SubmissionForm, SpeakerForm,
                    WithdrawForm, RoundValidationForm, ReviewForm)

subs = Blueprint('subs', __name__, template_folder='templates', static_folder=None)

@subs.route('/round/list')
@login_required
def round_list():
    if current_user.has_role('chair'):
        rounds = Round.query.all()
        return render_template('round_list.html', rounds=rounds)
    flash('You are not authorized to view this page', 'danger')
    return redirect(url_for('frontend.index'))


@subs.route('/round/new', methods=['GET', 'POST'])
@subs.route('/round/edit/<int:round_id>', methods=['GET', 'POST'])
@login_required
def round_edit(round_id=None):
    if current_user.has_role('chair'):
        if round_id:
            cfpround = Round.query.filter_by(id=round_id).first()
            if not cfpround:
                flash('Round doesn\'t exist', 'danger')
                return redirect(url_for('round_list'))
        else:
            cfpround = Round()
        form = RoundForm(obj=cfpround)
        if form.validate_on_submit():
            form.populate_obj(cfpround)
            if not round_id:
                db.session.add(cfpround)
            db.session.commit()
            flash('Round updated', 'success')
            return redirect(url_for('.round_list'))
        return render_template('round_edit.html', form=form, cfpround=cfpround)
    flash('You are not authorized to view this page', 'danger')
    return redirect(url_for('frontend.index'))


@subs.route('/round/<status>/<int:round_id>', methods=['GET', 'POST'])
@login_required
def round_status(status, round_id):
    if current_user.has_role('chair') and status in ['open', 'close']:
        cfpround = Round.query.filter_by(id=round_id).first()
        if not cfpround:
            flash('Round doesn\t exist', 'danger')
            return redirect(url_for('.round_list'))
        form = RoundValidationForm()
        if form.validate_on_submit():
            if form.validation.data == 'yes':
                cfpround.status = status
            db.session.commit()
            flash('Round forcefully opened', 'success')
            return redirect(url_for('.round_list'))
        return render_template('round_force.html', form=form, cfpround=cfpround, status=status)
    flash('Invalid round id or round status', 'danger')
    return redirect(url_for('.round_list'))


@subs.route('/submit/new', methods=['GET', 'POST'])
@login_required
def submission_type():
    form = SubmissionTypeForm()
    if form.validate_on_submit():
        submission = Submission()
        submission.speakers.append(current_user)
        cfpround = Round.query.filter_by(status='open').first()
        submission.round_id = cfpround.id
        submission.type = form.sub_type.data
        db.session.add(submission)
        db.session.commit()
        return redirect(url_for('.submission_edit', sub_id=submission.id))
    return render_template('submission_type.html', form=form)


@subs.route('/submit/details/<int:sub_id>', methods=['GET', 'POST'])
@login_required
def submission_edit(sub_id):
    submission = Submission.query.filter_by(id=sub_id).first()
    if not submission or current_user not in submission.speakers:
        flash('Invalid submission id', 'danger')
        return redirect(url_for('user.index'))
    form = SubmissionForm(obj=submission)
    if submission.type == 'talk':
        form.length.choices = current_app.config['TALK_LENGTHS']
        form.topic.choices = current_app.config['TALK_TOPICS']
    else:
        form.length.choices = current_app.config['CLASS_LENGTHS']
        form.topic.choices = current_app.config['CLASS_TOPICS']
    if form.validate_on_submit():
        form.populate_obj(submission)
        db.session.commit()
        return redirect(url_for('.submission_speakers', sub_id=submission.id))
    return render_template('submission_details.html', form=form, submission=submission)


@subs.route('/submit/speakers/<int:sub_id>/list')
@login_required
def submission_speakers(sub_id):
    submission = Submission.query.filter_by(id=sub_id).first()
    if not submission or current_user not in submission.speakers:
        flash('Invalid submission id', 'danger')
        return redirect(url_for('user.index'))
    return render_template('submission_speakers.html', submission=submission)


@subs.route('/submit/speakers/<int:sub_id>/new', methods=['GET', 'POST'])
@subs.route('/submit/speakers/<int:sub_id>/edit/<int:speaker_id>', methods=['GET', 'POST'])
def submission_speaker_edit(sub_id, speaker_id=None):
    submission = Submission.query.filter_by(id=sub_id).first()
    if not submission or current_user not in submission.speakers:
        flash('Invalid submission id', 'danger')
        return redirect(url_for('user.index'))
    if speaker_id:
        speaker = User.query.filter_by(id=speaker_id).first()
        if not speaker or speaker not in submission.speakers:
            flash('This speaker is not valid for this submission', 'danger')
            return redirect(url_for('.submission_speakers'))
    else:
        speaker = User()
    form = SpeakerForm(obj=speaker)
    if form.validate_on_submit():
        form.populate_obj(speaker)
        if speaker not in submission.speakers:
            check = User.query.filter_by(email=form.email.data).first()
            if check:
                speaker = check
                flash('Speaker already exists, using their existing info instead', 'warning')
            submission.speakers.append(speaker)
            flash('Speaker added to submission', 'success')
        if not speaker_id:
            db.session.add(speaker)
        else:
            flash('Speaker updated', 'success')
        db.session.commit()
        return redirect(url_for('.submission_speakers', sub_id=submission.id))
    return render_template('submission_speaker_edit.html', form=form, submission=submission)


@subs.route('/submit/review/<int:sub_id>', methods=['GET', 'POST'])
def submission_review(sub_id):
    submission = Submission.query.filter_by(id=sub_id).first()
    if not submission or current_user not in submission.speakers:
        flash('Invalid submission id', 'danger')
        return redirect(url_for('user.index'))
    form = ReviewForm()
    if form.validate_on_submit():
        submission.status = 'submitted'
        if len(submission.round.submissions) >= submission.round.max_subs:
            submission.round.status = 'closed'
        db.session.commit()
        flash('Submission submitted, thank you!', 'success')
        return redirect(url_for('.submission_list'))
    return render_template('submission_review.html', form=form, submission=submission)


@subs.route('/submission/list')
def submission_list():
    cfpround = Round.query.filter_by(status='open').first()
    return render_template('submission_list.html', cfpround=cfpround)


@subs.route('/submission/withdraw/<w_type>/<int:sub_id>', methods=['GET', 'POST'])
def submission_withdraw(w_type, sub_id):
    submission = Submission.query.filter_by(id=sub_id).first()
    if not submission or current_user not in submission.speakers:
        flash('Invalid submission id', 'danger')
        return redirect(url_for('.submission_list'))
    form = WithdrawForm()
    if form.validate_on_submit():
        if form.email.data == current_user.email:
            if w_type == 'speaker':
                submission.speakers.remove(current_user)
                flash('You have withdrawn from this submission', 'warning')
            if w_type == 'submission' or len(submission.speakers) == 0:
                db.session.delete(submission)
                flash('Your submission has been withdrawn', 'warning')
            db.session.commit()
            return redirect(url_for('.submission_list'))
        flash('The email entered does not match your own', 'warning')
    return render_template('submission_withdraw.html', form=form, submission=submission, w_type=w_type)
