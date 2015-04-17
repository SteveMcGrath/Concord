from flask import Blueprint, render_template, redirect, url_for, current_app, flash, request
from flask.ext.login import current_user, login_required
from werkzeug import secure_filename
from app.extensions import db
from .utils import convert_image
from .models import SponsorTier, Sponsor
from .forms import SponsorTierForm, SponsorForm

sponsors = Blueprint('sponsors', __name__, template_folder='templates', static_folder=None)


@sponsors.route('/')
def index():
    tiers = SponsorTier.query.order_by(SponsorTier.weight).all()
    return render_template('sponsor_index.html', tiers=tiers)


@sponsors.route('/images/<int:sponsor_id>')
def image(sponsor_id):



@aponsors.route('/list')
@login_required
def list():
    if current_user.has_role('admin'):
        sponsors = Sponsor.query.all()
        tiers = SponsorTier.query.order_by(SponsorTier.weight).all()
        return render_template('sponsor_list.html', tiers=tiers, sponsors=sponsors)
    flash('Access denied', 'danger')
    return redirect(url_for('.index'))


@sponsors.route('/tier/new', methods=['GET', 'POST'])
@sponsors.route('/tier/edit/<int:tier_id>', methods=['GET', 'POST'])
@login_required
def tier_edit(tier_id=None):
    if current_user.has_role('admin'):
        if tier_id:
            tier = SponsorTier.query.filter_by(id=tier_id).first()
            if not tier:
                flash('Invalid Sponsor Tier', 'danger')
                return redirect(url_for('.list'))
        else:
            tier = SponsorTier()
        form = SponsorTierForm(obj=tier)
        if form.validate_on_submit():
            form.populate_obj(tier)
            if not tier_id:
                db.session.add(tier)
            db.session.commit()
            flash('Tier Updated', 'success')
            return redirect(url_for('.list'))
        return render_template('sponsor_tier_edit.html', form=form)
    else:
        flash('Access denied', 'danger')
    return redirect(url_for('.index'))


@sponsors.route('/sponsor/new', methods=['GET', 'POST'])
@sponsors.route('/sponsor/edit/<int:sponsor_id>', methods=['GET', 'POST'])
@login_required
def sponsor_edit(sponsor_id=None):
    if current_user.has_role('admin'):
        if sponsor_id:
            sponsor = Sponsor.query.filter_by(id=sponsor_id).first()
            if not sponsor:
                flash('Invalid Sponsor', 'danger')
                return redirect(url_for('.list'))
        else:
            sponsor = Sponsor()
        form = SponsorForm(obj=sponsor)
        if form.validate_on_submit():
            form.populate_obj(sponsor)
            if form.image_file.data:
                # if an image file has been uploaded, then we will
                # need to convert the image and then store it on
                # the filesystem.
                image_data = request.FILES[form.image.name].read()
                img = convert_image(image_data)
                img.save()
            if not sponsor_id:
                db.session.add(sponsor)
            db.session.commit()
            flash('Sponsor Updated', 'success')
            return redirect(url_for('.list'))
        return render_template('sponsor_edit.html', form=form)
    else:
        flash('Access denied', 'danger')
    return redirect(url_for('.index'))


@sponsors.route('/<obj_type>/remove/<int:obj_id>', methods=['GET', 'POST'])
@login_required
def obj_remove(obj_type, obj_id):
    if current_user.has_role('admin'):
        if obj_type not in ['tier', 'sponsor']:
            flash('Not a valid object type', 'danger')
            return redirect(url_for('.list'))
        if obj_type == 'tier':
            obj = SponsorTier.query.filter_by(id=obj_id).first()
            if obj and obj.sponsors:
                flash('Sponsors are still associated to this tier', 'warning')
                return redirect(url_for('.list'))
        else:
            obj = Sponsor.query.filter_by(id=obj_id).first()
        if obj:
            form = VerificationForm()
            if form.validate_on_submit():
                db.session.delete(obj)
                db.session.commit()
                flash('Object Deleted', 'success')
                return redirect(url_for('.list'))
            return render_template('sponsor_remove.html', obj=obj, form=form)
    else:
        flash('Access denied', 'danger')
    return redirect(url_for('.index'))