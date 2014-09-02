import os
BASE_PATH = os.path.abspath(os.path.dirname(__file__))

# WTF Settings
CSRF_ENABLED = True
SECRET_KEY = 'something_aweful'

# Database Settings
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(BASE_PATH, 'database.db')
SQLALCHEMY_MIGRATE_REPO = os.path.join(BASE_PATH, 'db_repository')

# Other Settings
CONFERENCE_NAME = 'CircleCityCon'
CONFERENCE_EVENT = 'CircleCityCon 2015'
CONFERENCE_TICKETS = 300
CONFERENCE_EARLYBIRD_TICKETS = 100
