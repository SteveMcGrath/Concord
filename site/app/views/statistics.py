from flask import render_template, flash, redirect, session, url_for, abort, g
from flask.ext.login import login_user, logout_user, current_user, login_required
from app import app, db, login_manager, forms
from app.models import Ticket, Purchase,Seat
from datetime import datetime, timedelta
from sqlalchemy import func

@app.route('/stats/main')
#@login_required
def stats_main_page():
    seven_days_ago = datetime.now() - timedelta(days=7)
    return render_template('stats/main.html',
        t_total=Ticket.query.filter().count(),
        t_new=Ticket.query.filter(Ticket.date >= seven_days_ago).count(),
        classes=db.session.query(Seat.name, func.count(Seat.name)).filter(Seat.paid==True).group_by(Seat.name).all(),
        t_types=db.session.query(Ticket.ticket_type, func.count(Ticket.ticket_type)).group_by(Ticket.ticket_type).all(),
    )
