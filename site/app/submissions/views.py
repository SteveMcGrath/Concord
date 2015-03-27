from flask import Blueprint, render_template, redirect, url_for, current_app, flash
from flask.ext.login import current_user, login_required
from app.extensions import db
from .models import User, Round, Submission
from .forms import RoundForm, SubmissionTypeForm, SubmissionForm, SpeakerForm

subs = Blueprint('subs', __name__, template_folder='templates', static_folder=None)