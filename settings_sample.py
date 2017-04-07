import os.path

SQLALCHEMY_DATABASE_URI = 'postgresql+psycopg2://crazykit:password@localhost:5432/crazykit'
SQLALCHEMY_TRACK_MODIFICATIONS = False

SECRET_KEY = ''

PROJECT_DIR = os.path.dirname(os.path.realpath(__file__))
LOG_FILE = os.path.join(PROJECT_DIR, 'logs', 'app.log')

SENDPULSE_CLIENT_ID = ''
SENDPULSE_CLIENT_SECRET = ''
SENDPULSE_ADDRESSBOOK_ID = ''

CELERY_BROKER_URL = 'amqp://guest:guest@localhost:5672//'

ADMIN_LOGIN = ''
ADMIN_PASSWORD = ''

DELTA_HOURS = 6
