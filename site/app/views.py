from flask import render_template, flash, request, redirect, session, url_for, abort, g
from flask.ext.login import login_user, logout_user, current_user, login_required
from app import app, db, login_manager, forms
from app.models import Setting, User, Post, Class, Talk, Round
from sqlalchemy import desc
from utils import send_email
from datetime import datetime

login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(userid):
    return User.query.filter_by(id=int(userid)).first()


@app.before_request
def before_request():
    g.user = current_user
    g.settings = app.config
    g.talkround = Round.query.filter_by(started=True)\
                                .filter_by(closed=False)\
                                .filter_by(accept_talks=True).first()
    g.classround = Round.query.filter_by(started=True)\
                                 .filter_by(closed=False)\
                                 .filter_by(accept_classes=True).first() 


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
            send_email('auth/forgot_password.eml', user=user)
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
        db.session.add(user)
        db.session.commit()
        send_email('auth/new_user.eml', user=user)
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
def news():
    posts = Post.query.all()
    return render_template('news.html', posts=posts)


@app.route('/news/edit/<int:article_id>', methods=['GET', 'POST'])
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
    form = forms.NewsForm(obj=post)
    if form.validate_on_submit():
        form.populate_obj(post)
        if post_id is not None:
            db.session.merge(post)
        else:
            db.session.add(post)
        db.session.commit()
    return render_template('form.html', form=form, title='Edit New Article')


@app.route('/submissions/list/<int:userid>')
@login_required
def submission_list(userid):
    if g.user.admin or g.user.id == userid:
        user = User.query.filter_by(id=userid).first_or_404()
    else:
        flash('Not Authorized to View Other User Profiles', 'warning')
        return redirect(url_for('user', userid=g.user.id))
    return render_template('auth/submission_list.html', user=user)


@app.route('/cfp/submit/talk')
@login_required
def submit_talk():
    pass


@app.route('/cfp/submit/class')
@login_required
def submit_class():
    pass

