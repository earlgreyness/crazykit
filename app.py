from functools import partial
import logging.handlers
import logging

import arrow
from celery import Celery
from flask import Flask, request, render_template
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Unicode, Integer, Index, text, CheckConstraint
from sqlalchemy.exc import IntegrityError
from sqlalchemy_utils import ArrowType

Column = partial(Column, nullable=False)
ArrowType = partial(ArrowType, timezone=True)
NO_WHITESPACE_REGEX = r'^\S*$'

# sudo apt-get install rabbitmq-server
# sudo service rabbitmq-serveer status

# service uwsgi_crazykit restart; service nginx restart
# celery -A app.celery worker --task-events --loglevel=info \
# --uid=www-data --logfile=/var/www/crazykit/logs/celery.log --detach

# pkill -9 -f 'celery worker'
# ps auxww | grep 'celery worker'


def make_celery(app):
    celery = Celery(app.import_name, broker=app.config['CELERY_BROKER_URL'])
    TaskBase = celery.Task

    class ContextTask(TaskBase):
        abstract = True

        def __call__(self, *args, **kwargs):
            with app.app_context():
                app.logger.debug('=' * 80)
                app.logger.debug('Celery Task Started with: {}, {}'.format(args, kwargs))
                app.logger.debug('=' * 80)
                return TaskBase.__call__(self, *args, **kwargs)

    celery.Task = ContextTask
    return celery


app = Flask(__name__)
app.config.from_object('settings')

handler = logging.handlers.RotatingFileHandler(
    app.config['LOG_FILE'], maxBytes=10 * 1024000, backupCount=10, encoding='utf-8')
handler.setFormatter(
    logging.Formatter('[%(asctime)s] [%(levelname).1s] (%(name)s:%(lineno)d) %(message)s'))
handler.setLevel(logging.DEBUG)
app.logger.addHandler(handler)
app.logger.setLevel(logging.DEBUG)

requests_logger = logging.getLogger('requests')
requests_logger.addHandler(handler)
requests_logger.setLevel(logging.DEBUG)

cors = CORS(app, resources={'*': {'origins': '*'}})
db = SQLAlchemy(app)
celery = make_celery(app)


class PrimaryKeyMixin:
    id = Column(Integer, primary_key=True)


class Participant(db.Model, PrimaryKeyMixin):
    __tablename__ = 'participants'

    name = Column(Unicode)
    phone = Column(Unicode)
    email = Column(Unicode)
    occupation = Column(Unicode)
    employees = Column(Unicode)
    website = Column(Unicode)
    selected_prizes = Column(Unicode)

    added = Column(ArrowType(), default=arrow.utcnow)
    subscribed_to_newsletter = Column(ArrowType(), nullable=True)

    __table_args__ = (
        CheckConstraint("email ~ '{}' AND length(email) > 4".format(NO_WHITESPACE_REGEX)),
        Index('index_unique_lowercase_email', text('lower(email)'), unique=True),
    )


class Prize(db.Model, PrimaryKeyMixin):
    __tablename__ = 'prizes'

    label = Column(Integer, unique=True)
    vendor = Column(Unicode)
    name = Column(Unicode)

    @staticmethod
    def create_all():
        prizes = [
            (1, 'Sipuni', '3 мес. работы в виртуальной АТС на неограниченое кол-во операторов + 1 тел. номер'),
        ]
        try:
            for label, vendor, name in prizes:
                db.session.add(Prize(label=label, vendor=vendor, name=name))
            db.session.commit()
        except Exception:
            db.session.rollback()
            raise


class SendPulseToken(db.Model, PrimaryKeyMixin):
    __tablename__ = 'sendpulse_tokens'
    access_token = Column(Unicode)
    token_type = Column(Unicode)
    expires_in = Column(Integer)
    gotten = Column(ArrowType(), default=arrow.utcnow)


@celery.task
def add_participant(data):
    def get(key): return data.get(key, '').strip()

    try:
        participant = Participant(
            name=get('name'),
            phone=get('tel'),
            email=get('email'),
            occupation=get('occupation'),
            employees=get('workers'),
            website=get('website'),
            selected_prizes=get('prizes').strip(';'),
        )
        db.session.add(participant)
        db.session.commit()
    except IntegrityError as e:
        db.session.rollback()
        app.logger.error(e)
    except Exception:
        db.session.rollback()
        raise
    else:

        try:
            sendpulse.add_address(participant.email)
            participant.subscribed_to_newsletter = arrow.utcnow()
            db.session.commit()
        except Exception:
            db.session.rollback()
            raise


@app.route('/add', methods=['POST'])
def show_add_participant():

    form = request.form.to_dict(flat=True)

    app.logger.debug('New participant: {}'.format(form))
    add_participant.delay(form)

    return ''


@app.route('/46a5cd3b-9284-4b6a-9368-b7184946bfeb')
def show_status():
    participants = Participant.query.order_by(Participant.added.desc()).all()
    return render_template('status.html', participants=participants)


import sendpulse  # noqa: E402


if __name__ == '__main__':
    app.run(debug=True)
