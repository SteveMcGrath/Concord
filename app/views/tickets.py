from flask import render_template, flash, redirect, session, url_for, abort, g
from flask.ext.login import login_user, logout_user, current_user, login_required
from app import app, db, login_manager, forms
from app.models import User, Ticket
from sqlalchemy import desc
from datetime import datetime


@app.route('/tickets')
def tickets():
    #attendees = Ticket.query.filter_by(ticket_type='attendee').count()
    #tickets = 'On Sale %s' % app.config['TICKETS_START'].strftime('%Y-%m-%d %H:%M')
    return render_template('ticketing/main.html', title='Tickets')


@app.route('/tickets/print/<ticket_id>')
def ticket_print(ticket_id):
    '''
    Generates a printable ticket.
    '''
    ticket = Ticket.query.filter_by(ticket_hash=ticket_id).first_or_404()
    return ticket.generate(app.config['CONFERENCE_EVENT'])


@app.route('/tickets/press', methods=['GET', 'POST'])
def press_ticket():
    '''
    Press Ticket Form 
    '''
    #form = forms.PressTicketForm()
    #if form.validate_on_submit():
    #    press = 
    # Stub all of that out until after vacation...
    return render_template('ticketing/press.html', title='Press Tickets')
