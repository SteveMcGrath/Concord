from flask import render_template, flash, request, redirect, session, url_for, abort, g
from flask.ext.login import login_user, logout_user, current_user, login_required
from app import app, db, login_manager, forms, mail
from app.models import *
from sqlalchemy import desc
from utils import send_email
from datetime import datetime
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


@app.route('/')
def home():
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
            return redirect(request.args.get("next") or url_for('user', userid=user.id))
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


@app.route('/user/info/<int:userid>', methods=['GET', 'POST'])
@login_required
def user(userid):
    print g.user
    user = User.query.filter_by(id=userid).first_or_404()
    form = forms.UserForm(obj=user)
    if form.validate_on_submit():
        if g.user.id == userid or g.user.admin:
            form.populate_obj(user)
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
        except IntegrityError:
            flash('User Already Exists, sending a password reset email...')
            send_email('auth/forgot_password.eml', 'Password Recovery', user)
    return render_template('form.html', form=form, title='Create a New User')


@app.route('/settings')
@login_required
def settings():
    if not g.user.admin:
        flash('Not Authorized to View Settings', 'warning')
        return redirect(url_for('user', userid=g.user.id))
    settings = Setting.query.all()
    return render_template('admin/settings.html', settings=settings)


@app.route('/settings/<name>', methods=['GET', 'POST'])
@login_required
def setting_update(name):
    new = False
    if not g.user.admin:
        flash('Not Authorized to Edit Settings', 'warning')
        return redirect(url_for('user', userid=g.user.id))
    setting = Setting.query.filter_by(name=name).first()
    if not setting:
        new = True
        setting = Setting(name=name)
    form = forms.SettingForm(obj=setting)
    if form.validate_on_submit():
        form.populate_obj(setting)
        if new:
            db.session.add(setting)
        else:
            db.session.merge(setting)
        db.session.commit()
        return redirect(url_for('settings'))
    return render_template('form.html', form=form)


@app.route('/news')
@app.route('/news/category/view/<int:category_id>')
def news(category_id=None):
    if category_id:
        posts = Post.query.filter_by(category_id=category_id).all()
    else:
        posts = Post.query.all()
    return render_template('news.html', posts=posts)


@app.route('/news/edit/<int:post_id>', methods=['GET', 'POST'])
@app.route('/news/new', methods=['GET', 'POST'])
@login_required
def news_edit(post_id=None):
    if not g.user.author:
        flash('Not Authorized to Add/Edit News Articles', 'warning')
        return redirect(url_for('home'))
    if post_id is not None:
        post = Post.query.filter_by(id=post_id).first_or_404()
    else:
        post = Post()
    form = forms.PostForm(obj=post)
    if form.validate_on_submit():
        form.populate_obj(post)
        if post_id is not None:
            db.session.merge(post)
        else:
            db.session.add(post)
        db.session.commit()
        return redirect(url_for('news_edit', post_id=post.id))
    return render_template('admin/post_edit.html', form=form, title='Edit News Article', post=post)


@app.route('/news/remove/<int:post_id>')
@login_required
def news_remove(post_id):
    if not g.user.author:
        flash('Not Authorized to Remove News Articles', 'warning')
        return redirect(url_for('home'))
    post = Post.query.filter_by(id=post_id).first_or_404()
    db.session.delete(post)
    db.session.commit()
    return redirect(url_for('news'))


@app.route('/submissions/list/<int:userid>')
@login_required
def submission_list(userid):
    if g.user.admin or g.user.id == userid:
        user = User.query.filter_by(id=userid).first_or_404()
    else:
        flash('Not Authorized to View Other User Profiles', 'warning')
        return redirect(url_for('user', userid=g.user.id))
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
        if talk_id:
            db.session.merge(talk)
        else:
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
        db.session.merge(talk)
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



@app.route('/cfp/submit/class')
@login_required
def submit_class():
    pass

