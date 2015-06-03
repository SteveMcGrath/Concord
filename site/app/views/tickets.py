from flask import render_template, flash, redirect, session, url_for, abort, g, request
from flask.ext.login import login_user, logout_user, current_user, login_required
from app import app, db, login_manager, forms
from app.models import User, Ticket, Purchase, DiscountCode, TrainingPurchase, Seat
from sqlalchemy import desc
from datetime import date, datetime
import stripe
import smtplib

stripe.api_key = app.config['STRIPE_SKEY']

@app.route('/tickets')
def tickets():
    #attendees = Ticket.query.filter_by(ticket_type='attendee').count()
    #tickets = 'On Sale %s' % app.config['TICKETS_START'].strftime('%Y-%m-%d %H:%M')
    return render_template('ticketing/main.html', title='Tickets')


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


@app.route('/tickets/purchase', methods=['GET', 'POST'])
def purchase_tickets():
    tickets = app.config['TICKETS']
    form = forms.PurchaseForm()
    if form.validate_on_submit():
        purchase = Purchase()
        purchase.date = datetime.now()
        form.populate_obj(purchase)

        # First thing that we need to do is check to make sure that the email
        # actually is a .edu address.  If not, tell the user they fucked up and
        # set it back to attendee. 
        if purchase.ticket_type == 'student' and purchase.email[-3:] != 'edu':
            flash('Not a student, defaulting to Attendee')
            # The student was a lie!  Reset it to attendee.
            purchase.ticket_type = 'attendee'
            purchase.price = tickets[purchase.ticket_type]['price']
        
        # Next we need to match up the ticket types to make sure that no one
        # was mucking about with the ticket types.  If everything matches, then
        # go ahead and trust what the form is telling us and apply the price.
        if (purchase.ticket_type in tickets 
            and tickets[purchase.ticket_type]['visible']
            and (tickets[purchase.ticket_type]['expiration'] is None
                or date.today() < tickets[purchase.ticket_type]['expiration'])):
            purchase.price = tickets[purchase.ticket_type]['price']
        else:
            flash('Invalid Ticket Type...resetting to Attendee')
            # If it looks like someone was actually sending odd form values,
            # then we wont trust the ticket type and override it with a regular
            # attendee ticket type.
            purchase.ticket_type = 'attendee'
            purchase.price = tickets[purchase.ticket_type]['price']
        if form.discountcode.data != '':
            # Lets check to see if the discount code is valid.  If it is, then
            # we will be overriding the price and the ticket type associated
            # with this purchase.
            code = DiscountCode.query.filter_by(code=form.discountcode.data).first()
            if code is None or code.uses < 1:
                flash('Invalid or Expired Discount Code')
            else:
                purchase.price = code.price
                purchase.ticket_type = code.t_type

        # Add the purchase to the database and then return the confirmation page.
        db.session.add(purchase)
        db.session.commit()
        return render_template('ticketing/confirm.html', 
            purchase=purchase, 
            title='Purchase Confirmation',
            stripe_key=app.config['STRIPE_PKEY'])
    return render_template('ticketing/purchase.html', 
            form=form,
            title='Ticket Purchasing')


@app.route('/tickets/charge/<purchase_hash>', methods=['POST'])
def charge_card(purchase_hash):
    purchase = Purchase.query.filter_by(ref_hash=purchase_hash).first()
    if purchase == None:
        flash('There was an error with your transaction', 'danger')
        return redirect(url_for('purchase_tickets'))

    if purchase.price > 0:
        # Now we will actually charge the card.  Based off of how the stripe
        # examples looked, this seems to be the correct way to charge a card.
        purchase.payment_type = 'stripe'
        purchase.payment_token = request.form['stripeToken']
        customer = stripe.Customer.create(
            email=purchase.email, 
            card=purchase.payment_token
        )

        if purchase.purchase_type == 'ticket':
            description = 'CircleCityCon %s Ticket' % purchase.ticket_type
        elif purchase.purchase_type == 'training':
            description = 'CircleCityCon Training'

        charge = stripe.Charge.create(
            customer=customer.id,
            amount=int(purchase.price * 100),  #Stripe Expects the payment in cents.
            currency='usd',
            description=description
        )
    else:
        purchase.payment_type = 'comp'
        purchase.payment_token = 'comp'

    # Now to update the payment object with the payment information, append
    # the ticket codes to the purchase, and then to mark the payment as done.
    if purchase.ticket_type in ['family', 'attendee_x2']:
        purchase.tickets.append(Ticket(purchase.email, ticket_type='attendee'))
        purchase.tickets.append(Ticket(purchase.email, ticket_type='attendee'))
    else:
        purchase.tickets.append(Ticket(purchase.email, ticket_type=purchase.ticket_type))
    for i in range(purchase.children):
        purchase.tickets.append(Ticket(purchase.email, ticket_type='child'))
    purchase.completed = True

    # If there is a discount code involved, we will need to decriment the use
    # counter as well.
    if purchase.discountcode != '':
        code = DiscountCode.query.filter_by(code=purchase.discountcode).first()
        if code is not None:
            code.uses -= 1
            db.session.merge(code)

    # Commit all of the database changes!
    db.session.merge(purchase)
    db.session.commit()

    # Next we will generate the email that will be sent to the address specified
    # with the redemption code.
    msg = render_template('ticketing/pickup.eml', 
        purchase=purchase,
        url=app.config['SITE_ADDRESS'],
        con_name=app.config['CONFERENCE_NAME'],
        reply_email=app.config['REPLY_EMAIL'],
        ticketing_email=app.config['TICKETING_EMAIL'],
    )
    #print msg
    if app.config['DEBUG']:
        print '\n' + msg + '\n'
    else:
        smtp = smtplib.SMTP('localhost')
        smtp.sendmail('no-reply@circlecitycon.com', [purchase.email], msg)

    # Lastly tell the user that the purchase is complete and to check their
    # email for the ticket codes.
    return render_template('ticketing/charged.html', 
        purchase=purchase,
        title='Purchase Completed')


@app.route('/tickets/pickup/<purchase_hash>')
def ticket_pickup(purchase_hash):
    purchase = Purchase.query.filter_by(ref_hash=purchase_hash, completed=True).first_or_404()
    return render_template('ticketing/pickup.html', purchase=purchase, title='Ticket Pickup')


@app.route('/tickets/info/<ticket_id>', methods=['GET', 'POST'])
def ticket_information(ticket_id):
    ticket = Ticket.query.filter_by(ticket_hash=ticket_id).first_or_404()
    form = forms.TicketInfoForm()
    if form.validate_on_submit():
        form.populate_obj(ticket)
        ticket.redeemed = True
        db.session.merge(ticket)
        db.session.commit()
        return redirect(url_for('ticket_print', ticket_id=ticket_id))
    return render_template('ticketing/pickup_info.html', title='Ticket Info', form=form, ticket=ticket)


@app.route('/tickets/print/<ticket_id>')
def ticket_print(ticket_id):
    '''
    Generates a printable ticket.
    '''
    ticket = Ticket.query.filter_by(ticket_hash=ticket_id).first_or_404()
    return ticket.generate(app.config['CONFERENCE_EVENT'])


@app.route('/tickets/get_training/<ticket_id>', methods=['GET', 'POST'])
def purchase_training(ticket_id):
    ticket = Ticket.query.filter_by(ticket_hash=ticket_id).first_or_404()
    form = forms.TrainingPurchaseForm()
    form.training.choices = open_classes()
    if form.validate_on_submit():
        purchase = TrainingPurchase()
        purchase.ticket_id = ticket.id
        purchase.price = 0
        for item in form.training.data:
            seat = Seat()
            seat.ticket_id = ticket.id
            seat.name = app.config['CLASSES'][item]['name']
            seat.tag = app.config['CLASSES'][item]['id']
            seat.sub = app.config['CLASSES'][item]['sub']
            purchase.price += app.config['CLASSES'][item]['price']
            purchase.classes.append(seat)
        db.session.add(purchase)
        db.session.commit()
        return render_template('ticketing/training_confirm.html',
            purchase=purchase,
            title='Purchase Confirmation',
            stripe_key=app.config['STRIPE_PKEY'])
    return render_template('ticketing/training_purchase.html',
        form=form,
        title='Training Purchase')


@app.route('/tickets/training/charge/<purchase_hash>', methods=['POST'])
def charge_training(purchase_hash):
    purchase = TrainingPurchase.query.filter_by(ref_hash=purchase_hash).first_or_404()
    purchase.payment_type = 'stripe'
    purchase.payment_token = request.form['stripeToken']
    customer = stripe.Customer.create(email=purchase.ticket.email,card=purchase.payment_token)
    charge = stripe.Charge.create(customer=customer.id, 
        amount=int(purchase.price * 100),
        currency='usd',
        description='CircleCityCon Training'
    )
    for item in purchase.classes:
        item.paid = True
        db.session.merge(item)
    purchase.completed = True
    db.session.merge(purchase)
    db.session.commit()
    return render_template('ticketing/training_completed.html',
            purchase=purchase,
            title='Training Purchased')
