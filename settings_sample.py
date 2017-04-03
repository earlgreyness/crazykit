import os.path

SQLALCHEMY_DATABASE_URI = 'postgresql://crazykit:password@localhost:5432/crazykit'
SQLALCHEMY_TRACK_MODIFICATIONS = False
SECRET_KEY = 'This key must be secret'
LOGGER_NAME = 'crazykit'
LOGGER_CONFIG = {
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '%(asctime)s [%(levelname).1s] %(message)s',
        },
    },
    'handlers': {
        'logfile': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join('logs', 'app.log'),
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
