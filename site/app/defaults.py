import os

CONFERENCE_NAME = 'SampleCon'
CSRF_ENABLED = True
DEBUG = True
TESTING = True
SECRET_KEY = 'This is the default key INSECURE!'
MAIL_SERVER = 'localhost'
MAIL_DEFAULT_SENDER = 'SampleCon <no-reply@samplecon.com>'
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(os.path.abspath(os.path.dirname(__file__)), '..', 'database.db')
SQLALCHEMY_MIGRATE_REPO = 'db_repository'
SERVER_NAME = 'localhost:5000'
SHIRT_SIZES = (
    ('M:S', 'Mens Small'),
    ('M:M', 'Mens Medium'),
    ('M:L', 'Mens Large'),
    ('M:XL', 'Mens XL'),
    ('M:XXL', 'Mens XXL'),
    ('M:2XL', 'Mens 2XL'),
    ('M:3XL', 'Mens 3XL'),
    ('M:4XL', 'Mens 4XL'),
    ('M:5XL', 'Mens 5XL'),
    ('W:S', 'Womens Small'),
    ('W:M', 'Womens Medium'),
    ('W:L', 'Womens Large'),
    ('W:XL', 'Womens XL'),
    ('W:2XL', 'Womens 2XL'),
    ('W:3XL', 'Womens 3XL'),
    ('W:4XL', 'Womens 4XL'),
    ('W:5XL', 'Womens 5XL'),
    ('C:S', 'Childrens Small'),
    ('C:M', 'Childrens Medium'),
    ('C:L', 'Childrens Large'),
    ('C:XL', 'Childrens XL'),
)
TALK_LENGTHS = (
    ('20', '20 Minutes'),
    ('50', '50 Minutes'),
    ('80', '80 Minutes'),
    ('110', '110 Minutes'),
)
CLASS_LENGTHS = (
    ('120', '2 Hours'),
    ('240', '4 Hours'),
    ('360', '6 Hours'),
    ('480', '8 Hours'),
)
TALK_TOPICS = (
    ('red team', 'Red Team'),
    ('blue team', 'Blue Team'),
    ('purple team', 'Purple Team'),
)
CLASS_TOPICS = (
    ('training', 'Training'),
)