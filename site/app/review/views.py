from flask import Blueprint, render_template, redirect, url_for, flash, current_app, request
from flask.ext.login import current_user, login_required
from flask.ext.mail import Message
from app.extensions import db, mail
from app.submissions.models import Submission
from app.auth.models import User
from .models import Review, Comment
from .forms import ReviewForm, CommentForm