from flask import render_template, flash, request, redirect, session, url_for, abort, g
from flask.ext.login import login_user, logout_user, current_user, login_required
from app import app, db, login_manager, forms, mail
from app.models import *
from sqlalchemy import desc
from utils import send_email, get_open_reviews
from datetime import datetime
from functools import wraps
from sqlalchemy.exc import IntegrityError

login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(userid):
    return User.query.filter_by(id=int(userid)).first()


@app.before_request
def before_request():
    g.user = current_user
    g.settings = app.config
    g.talkround = Round.query.filter_by(status='open')\
                             .filter(Round.max_talks > 0).first()
    g.classround = Round.query.filter_by(status='open')\
                              .filter(Round.max_classes > 0).first()
    if g.user.reviewer:
        g.reviewround = Round.query.filter(Review.status.in_(['closed', 'finalizing'])).first()
        g.revcounter = len(need_to_review())


def admin_access(func):
    @wraps(func)
    def wrapped(*args, **kwargs):
        if g.user.is_authenticated() and g.user.admin:
            return func(*args, **kwargs)
        else:
            flash('Not an admin. Access to this page is denied.')
            return redirect(url_for('home'))
    return wrapped


def author_access(func):
    @wraps(func)
    def wrapped(*args, **kwargs):
        if g.user.author:
            return func(*args, **kwargs)
        else:
            flash('Not an author. Access to this page is denied.', 'warning')
            return redirect(url_for('home'))
    return wrapped


def chair_access(func):
    @wraps(func)
    def wrapped(*args, **kwargs):
        if g.user.chair:
            return func(*args, **kwargs)
        else:
            flash('Not a chair. Access to this page is denied.', 'warning')
            return redirect(url_for('home'))
    return wrapped


def reviewer_access(func):
    @wraps(func)
    def wrapped(*args, **kwargs):
        if g.user.reviewer:
            return func(*args, **kwargs)
        else:
            flash('Not an reviewer. Access to this page is denied.', 'warning')
            return redirect(url_for('home'))
    return wrapped


def user_or_admin_access(func):
    @wraps(func)
    def wrapped(*args, **kwargs):
        print kwargs
        if g.user.id == kwargs['user_id'] or g.user.admin:
            return func(*args, **kwargs)
        else:
            flash('You do not have access to view this page.', 'warning')
            return redirect(url_for('home'))
    return wrapped


@app.route('/')
def home():
    print 
    return render_template('home.html')


@app.route('/user/login', methods=['GET', 'POST'])
def login():
    if g.user.is_authenticated():
        return redirect(url_for('user', user=g.user.id))
    form = forms.LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and user.check_password(form.password.data):
            print user.id, user.email
            user.forgot = ''
            db.session.merge(user)
            db.session.commit()
            login_user(user)
            return redirect(request.args.get("next") or url_for('user', user_id=user.id))
        else:
            user = None
        if user == None:
            flash('Invalid Email or Password', 'warning')
    return render_template('auth/login.html', form=form)


@app.route('/user/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route('/user/new/admin')
@app.route('/user/info/<int:user_id>', methods=['GET', 'POST'])
@login_required
@user_or_admin_access
def user(user_id=None):
    if user_id:
        user = User.query.filter_by(id=user_id).first_or_404()
    else:
        user = User()
    form = forms.UserForm(obj=user)
    if form.validate_on_submit():
        form.populate_obj(user)
        if not user_id:
            db.session.add(user)
        db.session.merge(user)
        db.session.commit()   
    return render_template('auth/user_info.html', form=form, user=user)


@app.route('/user/forgot', methods=['GET', 'POST'])
def forgot_password():
    form = forms.ForgotPasswordForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None:
            user.forgot_password()
            db.session.merge(user)
            db.session.commit()
            send_email('auth/forgot_password.eml', 'Password Recovery', user)
    return render_template('form.html', form=form, title='Forgot Password')


@app.route('/user/forgot/<recovery>', methods=['GET', 'POST'])
def recover_password(recovery):
    user = User.query.filter_by(forgot=recovery).first_or_404()
    form = forms.PasswordRecoveryForm()
    if form.validate_on_submit():
        if form.passwd.data == form.verify.data:
            user.update_password(form.passwd.data)
            db.session.merge(user)
            db.session.commit()
            flash('Password Successfully Reset!', 'success')
            return redirect(url_for('login'))
        flash('Passwords did not match!', 'danger')
    return render_template('form.html', form=form, title='Password Recovery')


@app.route('/user/new', methods=['GET', 'POST'])
def new_user():
    form = forms.NewUserForm()
    if form.validate_on_submit():
        user = User()
        form.populate_obj(user)
        user.forgot_password()
        try:
            db.session.add(user)
            db.session.commit()
            send_email('auth/new_user.eml', 'New User Verification', user)
            return redirect(url_for('login'))
        except IntegrityError:
            db.session.rollback()
            user = User.query.filter_by(email=form.email.data).first_or_404()
            user.forgot_password()
            db.session.merge(user)
            db.session.commit()
            send_email('auth/forgot_password.eml', 'Password Recovery', user,
                ('User Already Exists, sending a password reset email...', 'warning'))
            return redirect(url_for('login'))
    return render_template('form.html', form=form, title='Create a New User')


@app.route('/user/list')
@admin_access
def user_list():
    user = User.query.all()
    return render_template('admin/user_list.html', users=users)


@app.route('/settings')
@login_required
@admin_access
def settings():
    settings = Setting.query.all()
    return render_template('admin/settings.html', settings=settings)


@app.route('/settings/<name>', methods=['GET', 'POST'])
@login_required
@admin_access
def setting_update(name):
    new = False
    setting = Setting.query.filter_by(name=name).first()
    if not setting:
        new = True
        setting = Setting(name=name)
    form = forms.SettingForm(obj=setting)
    if form.validate_on_submit():
        form.populate_obj(setting)
        if new:
            db.session.add(setting)
        db.session.commit()
        return redirect(url_for('settings'))
    return render_template('form.html', form=form)


@app.route('/news')
@app.route('/news/category/view/<category>')
def news(category=None):
    if category_id:
        posts = Post.query.filter_by(category=category).all()
    else:
        posts = Post.query.all()
    return render_template('news.html', posts=posts)


@app.route('/news/edit/<int:post_id>', methods=['GET', 'POST'])
@app.route('/news/new', methods=['GET', 'POST'])
@login_required
@author_access
def news_edit(post_id=None):
    if post_id is not None:
        post = Post.query.filter_by(id=post_id).first_or_404()
    else:
        post = Post()
    form = forms.PostForm(obj=post)
    if form.validate_on_submit():
        form.populate_obj(post)
        if not post_id:
            db.session.add(post)
        db.session.commit()
        return redirect(url_for('news_edit', post_id=post.id))
    return render_template('admin/post_edit.html', form=form, title='Edit News Article', post=post)


@app.route('/news/remove/<int:post_id>')
@login_required
@author_access
def news_remove(post_id):
    post = Post.query.filter_by(id=post_id).first_or_404()
    db.session.delete(post)
    db.session.commit()
    return redirect(url_for('news'))


@app.route('/submissions/list/<int:user_id>')
@login_required
@user_or_admin_access
def submission_list(user_id):
    user = User.query.filter_by(id=user_id).first_or_404()
    return render_template('auth/submission_list.html', user=user)


@app.route('/cfp/submit/talk/details', methods=['GET', 'POST'])
@app.route('/cfp/submit/talk/details/<int:talk_id>', methods=['GET', 'POST'])
@login_required
def submit_talk_details(talk_id=None):
    if talk_id:
        talk = Talk.query.filter_by(id=talk_id)
    else:
        talk = Talk()
        talk.speakers.append(g.user)
    if not g.user.admin or g.user not in talk.speakers:
        flash('You do not have permission to modify this talk.', 'warning')
        return redirect(url_for('home'))
    form = forms.TalkForm(obj=talk)
    if form.validate_on_submit():
        form.populate_obj(talk)
        if not talk_id:
            db.session.add(talk)
        db.session.commit()
        return redirect(url_for('submit_talk_speakers', talk_id=talk.id))
    return render_template('ctp/submit_talk_details.html', talk=talk, form=form)


@app.route('/cfp/submit/talk/speakers/<int:talk_id>', methods=['GET', 'POST'])
@login_required
def submit_talk_speakers(talk_id):
    talk = Talk.query.filter_by(id=talk_id).first_or_404()
    form = forms.TalkSpeakerForm()
    if not g.user.admin or g.user not in talk.speakers:
        flash('You do not have permission to modify this talk.', 'warning')
        return redirect(url_for('home'))
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if not user:
            user = User()
            form.populate_obj(user)
            db.session.add(user)
        talk.speakers.append(user)
        db.session.commit()
    return render_template('cfp/submit_talk_speakers.html', talk=talk, form=form)


@app.route('/cfp/submit/talk/speakers/<int:talk_id>/remove/<int:user_id>', methods=['GET', 'POST'])
@login_required
def submit_talk_remove_speaker(talk_id, user_id):
    talk = Talk.query.filter_by(id=talk_id).first_or_404()
    user = User.query.filter_by(id=user_id).first_or_404()
    form = forms.RemoveSpeakerForm()
    if not g.user.admin or g.user not in talk.speakers:
        flash('You do not have permission to modify this talk.', 'warning')
        return redirect(url_for('home'))
    if g.user == user:
        flash('You cannot remove yourself from a talk.', 'warning')
        return redirect(url_for('submit_talk_speakers', talk_id=talk.id))
    if form.validate_on_submit():
        if form.email.data == user.email:
            talk.speakers.remove(user)
            flash('%s Removed from Talk' % user.email, 'success')
        else:
            flash('%s Was not Removed' % user.email, 'warning')
        return redirect(url_for('submit_talk_speakers', talk_id=talk.id))
    return render_template('cfp/submit_talk_remove_speaker.html', user=user, talk=talk, form=form)


@app.route('/cfp/submit/talk/review/<int:talk_id>', methods=['GET', 'POST'])
@login_required
def submit_talk_review(talk_id):
    talk = Talk.query.filter_by(id=talk_id).first_or_404()
    if not g.user.admin or g.user not in talk.speakers:
        flash('You do not have permission to modify this talk.', 'warning')
        return redirect(url_for('home'))
    if request.method == 'POST':
        talk.status = 'submitted'
        talk.submitted = datetime.now()
        db.session.merge(talk)
        db.session.commit()
        return redirect(url_for('submission_list'), userid=g.user.id)
    return render_template('cfp/submit_talk_review.html', talk=talk)


@app.route('/cfp/round/list')
@login_required
@chair_access
def round_list():
    rounds = Round.query.all()
    return render_template('cfp/round_list.html', rounds=rounds)


@app.route('/cfp/round/new', methods=['GET', 'POST'])
@app.route('/cfp/round/edit/<int:round_id>', methods=['GET', 'POST'])
@login_required
@chair_access
def round_edit(round_id=None):
    if round_id:
        cfp_round = Round.query.filter_by(id=round_id).first_or_404()
    else:
        cfp_round = Round()
    form = forms.RoundForm(obj=cfp_round)
    if form.validate_on_submit():
        form.populate_obj(cfp_round)
        if not round_id:
            db.session.add(cfp_round)
        db.session.commit()
        return redirect(url_for('round_list'))
    return render_template('form.html', form=form)


@app.route('/tickets/discounts/list')
@login_required
@admin_access
def discounts_list():
    codes = DiscountCode.query.all()
    return render_template('tickets/discount_codes_list.html', codes=codes)


@app.route('/tickets/discounts/new', methods=['GET', 'POST'])
@app.route('/tickets/discounts/edit/<int:code_id>', methods=['GET', 'POST'])
@login_required
@admin_access
def discounts_edit(code_id=None):
    if code_id:
        code = DiscountCode.query.filter_by(id=code_id).first_or_404()
    else:
        code = DiscountCode()
    form = forms.DiscountCodeForm(obj=code)
    if form.validate_on_submit():
        form.populate_obj(code)
        if not code_id:
            db.session.add(code)
        db.session.commit()
        return redirect(url_for('discounts_list'))
    return render_template('form.html', form=form)


@app.route('/cfp/review/list')
@login_required
@reviewer_access
def review_list():
    if g.reviewround.status = 'finalizing':
        return redirect(url_for('review_finalize'))
    submissions = need_to_review()
    return render_template('cfp/review_list.html', submissions=submissions)


@app.route('/cfp/review/full_list', methods=['GET', 'POST'])
@login_required
@chair_access
def review_full_list():
    form = forms.FinalizeReviewsForm()
    if form.validate_on_submit():
        g.reviewround.status = 'finalizing'
        db.session.commit()
        return redirect(url_for('review_finalize'))
    return render_template('cfp/review_full_list.html', form=form)


@app.route('/cfp/review/detail/<int:sub_id>')
@login_required
@reviewer_access
def review_detail(sub_id):
    submission = Submission.query.filter_by(id=sub_id).first_or_404()
    if g.user in submission.reviewed_by:
        flash('You have already reviewed this item!', 'danger')
    return render_template('cfp/review_detail.html', submission=submission)


@app.route('/cfp/review/comment/<int:sub_id>', methods=['GET', 'POST'])
@login_required
@reviewer_access
def review_add_comment(sub_id):
    submission = Submission.query.filter_by(id=sub_id).first_or_404()
    if g.user in submission.reviewed_by:
        flash('You have already reviewed this item!', 'danger')
        return redirect(url_for('review_list'))
    form = forms.CommentForm()
    if form.validate_on_submit():
        comment = Comment()
        form.populate_obj(comment)
        db.session.add(comment)
        submission.comments.append(comment)
        db.session.commit()
        flash('Comment Added')
        return redirect(url_for('review_detail', sub_id=submission.id))
    return render_template('form.html', form=form, submission=submission)


@app.route('/cfp/review/score/<int:sub_id>', methods=['GET', 'POST'])
@login_required
@reviewer_access
def review_add_comment(sub_id):
    submission = Submission.query.filter_by(id=sub_id).first_or_404()
    if g.user in submission.reviewed_by:
        flash('You have already reviewed this item!', 'danger')
        return redirect(url_for('review_list'))
    form = forms.ReviewForm()
    if form.validate_on_submit():
        comment = Review()
        form.populate_obj(comment)
        db.session.add(comment)
        submission.reviews.append(comment)
        db.session.commit()
        flash('Comment Added')
        return redirect(url_for('review_detail', sub_id=submission.id))
    return render_template('form.html', form=form, submission=submission)


@app.route('/cfp/review/finalize', methods=['GET', 'POST'])
@login_required
@reviewer_access
def review_finalize():
    form = forms.FinalizeReviewForm()
    if form.validate_on_submit():
        tmpl = {
            'c': {
                'accepted': 'cfp/accept_class.eml',
                'rejected': 'cfp/reject_class.eml',
                'alternate': 'cfp/alternate_class.eml'
            },
            't': {
                'accepted': 'cfp/accept_talk.eml',
                'rejected': 'cfp/reject_talk.eml',
                'alternate': 'cfp/alternate_talk.eml'            
            }
        }
        for submission in g.reviewround:
            if submission.status not in ['accepted', 'rejected', 'alternate']:
                if submission.score >= app.config['CFP_ACCEPT']:
                    submission.status = 'accepted'
                else:
                    submission.status = 'rejected'
                db.session.merge(submission)
        for talk in Talk.query.filter_by(round_id=g.reviewround.id).all():
            for speaker in talk.speakers:
                send_email(tmpl['t'][talk.status], 'Talk Rejected', speaker,
                            notification=None, talk=talk)
        for training in Class.query.filter_by(round_id=g.reviewround.id).all():
            for trainer in training.trainers:
                send_email(tmpl['c'][training.status], 'Class Rejected', trainer,
                            notification=False, training=training)
        g.reviewround.status = 'completed'
        db.session.commit()
    return render_template('cfp/review_finalize.html')


@app.route('/cfp/review/<status>/<int:sub_id>')
@login_required
@chair_access
def submission_status(state, sub_id):
    submission = Submission.query.filter_by(id=sub_id).first_or_404()
    submission.status = state
    db.session.commit()
    return redirect(url_for('review_finalize'))
