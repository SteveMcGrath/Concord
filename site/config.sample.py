import os
from datetime import date

# CFP Settings
CFP_TOPICS = (
    ('redteam', 'Red Team'),
    ('blueteam', 'Blue Team'),
    ('purpleteam', 'Purple Team'),
)
CFP_ACCEPT = 4
CFP_DENY = 2

# Global Settings
CONFERENCE_NAME = 'SuperAwesomeCon'
BASE_URL = 'http://localhost:5000'
TESTING = True
DEBUG = True
BASE_PATH = os.path.abspath(os.path.dirname(__file__))
POST_CATEGORIES = (
    ('general', 'General'),
    ('sponsors', 'Sponsors'),
)
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
    ('C:XL', 'Childrens XL')
)
CLASS_LENGTHS = (
    (2, 2),
    (4, 4),
    (8, 8),
)
TALK_LENGTHS = (
    (20, 20),
    (50, 50),
    (80, 80),
    (110, 110),
)

# WTF Settings
CSRF_ENABLED = True
SECRET_KEY = 'something_awful'

# Database Settings
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(BASE_PATH, 'database.db')
SQLALCHEMY_MIGRATE_REPO = os.path.join(BASE_PATH, 'db_repository')

# Mail Settings
MAIL_SERVER = 'localhost'
MAIL_DEFAULT_SENDER = 'ConferenceName <no-reply@con.com>'