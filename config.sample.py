import os
from datetime import date

DEBUG = False
BASE_PATH = os.path.abspath(os.path.dirname(__file__))

# WTF Settings
CSRF_ENABLED = True
SECRET_KEY = 'something_awful'

# Database Settings
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(BASE_PATH, 'database.db')
SQLALCHEMY_MIGRATE_REPO = os.path.join(BASE_PATH, 'db_repository')

# Conference Settings
CONFERENCE_NAME = 'SuperAwesomeCon'
CONFERENCE_EVENT = 'SuperAwesomeCon 1.0'

# Email Settings
REPLY_EMAIL = 'no-reply@superawesomecon.com'
TICKETING_EMAIL = 'ticketing@superawesomecon.com'

# Ticket Prices
TICKETS = {
    'student': {
        'price': 100, 
        'name': 'Student', 
        'expiration': None,
        'visible': True,
    },
    'earlybird': {
        'price': 125, 
        'name': 'Early Bird', 
        'expiration': date(2015, 01, 01),
        'visible': True,
    },
    'attendee': {
        'price': 150, 
        'name': 'Attendee', 
        'expiration': None,
        'visible': True,
    },
    'family': {
        'price': 200, 
        'name': 'Family', 
        'expiration': None,
        'visible': True,
    },
    'child': {
        'price': 0,
        'name': 'Child',
        'expiration': None,
        'visible': False,
    },
    'press': {
        'price': 0,
        'name': 'Press',
        'expiration': None,
        'visible': False,
    },
    'volunteer': {
        'price': 0,
        'name': 'Volunteer',
        'expiration': None,
        'visible': False,
    },
    'staff': {
        'price': 0,
        'name': 'Staff',
        'expiration': None,
        'visible': False,
    },
    'sponsor': {
        'price': 0,
        'name': 'Sponsor',
        'expiration': None,
        'visible': False,
    },
}

# Stripe Settings
STRIPE_SKEY = 'sk_test_TESTKEY'
STRIPE_PKEY = 'pk_test_TESTKEY'
