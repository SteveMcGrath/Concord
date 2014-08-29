from flask import (render_template, flash, redirect, session, url_for, 
                   abort, g, make_response)
from app import app
import ticket

@app.route('/')
def home():
    return render_template('home.html', title='Home')


@app.route('/cfp')
def cfp():
    return render_template('construction.html', title='Call For Papers')


@app.route('/tickets')
def tickets():
    return render_template('construction.html', title='Tickets')


@app.route('/schedule')
def schedule():
    return render_template('construction.html', title='Schedule')


@app.route('/sponsors')
def sponsors():
    return render_template('construction.html', title='Sponsors')


@app.route('/location')
def location():
    return render_template('location.html', title='Location')


@app.route('/events')
def events():
    return render_template('construction.html', title='Events')


@app.route('/training')
def training():
    return render_template('construction.html', title='Training')


@app.route('/about')
def about():
    return render_template('construction.html', title='About Us')


@app.route('/tickets/print/<ticket_id>')
def ticket_print(ticket_id):
    '''
    Generates a printable ticket.
    '''
    ### ADD CHECKING CODE HERE
    ### ADJUST THIS CODE TO PULL FROM DB!!!!
    event_name = 'CircleCityCon 2015'
    return render_template('ticket.html', 
        event_name=event_name,
        image_data=ticket.qrgen(ticket_id, True),
        ticket_id=ticket_id,
        ticket_footer='\n'.join([
            '<p>This is my ticket.',
            'There are many others like it but this one is mine.',
            '</p>',
            '<p>This ticket grants one entry into',
            '<strong>%s</strong>.' % event_name,
            'Take care with it, as if multiple\'s exist, only the',
            'first person to get this ticket scanned will be allowed',
            'entry.  Take care!<br />',
            '&nbsp;&nbsp;&nbsp;&nbsp;--Your Ticket</p>'
        ]),
    )