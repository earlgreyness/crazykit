import os.path

SQLALCHEMY_DATABASE_URI = 'postgresql://crazykit:password@localhost:5432/crazykit'
SQLALCHEMY_TRACK_MODIFICATIONS = False

SECRET_KEY = 'secret key must be secret'

LOGGER_NAME = 'crazykit'

PROJECT_DIR = os.path.dirname(os.path.realpath(__file__))
LOGGER_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '%(asctime)s [%(levelname).1s] %(message)s',
        },
    },
    'handlers': {
        'logfile': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(PROJECT_DIR, 'logs', 'app.log'),
            'formatter': 'standard',
            'maxBytes': 10 * 1024000,
            'backupCount': 10,
        },
    },
    'loggers': {
        LOGGER_NAME: {
            'handlers': ['logfile'],
            'level': 'DEBUG',
        },
    }
}
