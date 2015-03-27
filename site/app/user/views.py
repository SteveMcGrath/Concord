from flask import Blueprint, render_template, redirect, url_for, current_app, flash
from flask.ext.login import current_user, login_required
from app.extensions import db
from .models import User
from .forms import ProfileForm

user = Blueprint('user', __name__, template_folder='templates', static_folder=None)


@user.route('/profile')
@login_required
def index():
    return redirect(url_for('.profile', user_id=current_user.id))


@user.route('/profile/<int:user_id>', methods=['GET', 'POST'])
@login_required
def profile(user_id):
    if current_user.id == user_id or current_user.has_role('admin'):
        user = User.query.filter_by(id=user_id).first()
        if user:
            form = ProfileForm(obj=user)
            form.shirt.choices = current_app.config.get('SHIRT_SIZES')
            if form.validate_on_submit():
                user.email = form.email.data
                user.name = form.name.data
                user.bio = form.bio_md.data
                user.shirt = form.shirt.data
                if current_user.has_role('admin'):
                    user.roles = form.roles.data
                db.session.commit()
                flash('User profile updated', 'success')
            return render_template('profile.html', form=form, user=user)
        flash('Not a valid user', 'danger')
    else:
        flash('Access denied', 'danger')
    return redirect(url_for('frontend.index'))