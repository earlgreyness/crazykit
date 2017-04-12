from functools import partial
import logging.handlers
import logging
from datetime import timedelta
import csv
from io import StringIO

import arrow
from celery import Celery
from flask import Flask, request, render_template, redirect, url_for, make_response
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_login import (LoginManager, login_user, logout_user,
                         UserMixin, login_required, current_user)
from sqlalchemy import Column, Unicode, Integer, Index, text, CheckConstraint
from sqlalchemy_utils import ArrowType

Column = partial(Column, nullable=False)
ArrowType = partial(ArrowType, timezone=True)
NO_WHITESPACE_REGEX = r'^\S*$'
SECS_IN_HOUR = 3600

"""

sudo apt-get install rabbitmq-server
sudo service rabbitmq-server status

service uwsgi_crazykit restart
celery -A app.celery worker -D -l INFO -f /var/www/crazykit/logs/celery.log --uid=www-data
ps auxww | grep 'celery worker'
pkill -9 -f 'celery worker'; rm celeryd.pid

"""


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

cors = CORS(app, resources={'*': {'origins': '*'}})
db = SQLAlchemy(app)
celery = make_celery(app)

login_manager = LoginManager(app)
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(user_id):
    if user_id == app.config['ADMIN_LOGIN']:
        user = UserMixin()
        user.id = user_id
        return user
    return None


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
    job_title = Column(Unicode)

    added = Column(ArrowType(), default=arrow.now)
    subscribed_to_newsletter = Column(ArrowType(), nullable=True)

    __table_args__ = (
        CheckConstraint("email ~ '{}' AND length(email) > 4".format(NO_WHITESPACE_REGEX)),
        Index('index_unique_lowercase_email', text('lower(email)'), unique=True),
    )

    def __repr__(self):
        return '<Participant "{}">'.format(self.email)


class Prize(db.Model, PrimaryKeyMixin):
    __tablename__ = 'prizes'

    label = Column(Integer, unique=True)
    vendor = Column(Unicode)
    name = Column(Unicode)


class SendPulseToken(db.Model, PrimaryKeyMixin):
    __tablename__ = 'sendpulse_tokens'
    access_token = Column(Unicode)
    token_type = Column(Unicode)
    expires_in = Column(Integer)
    gotten = Column(ArrowType(), default=arrow.now)


class TooLateForUpdate(Exception):
    pass


@celery.task
def add_participant(data):
    def get(key): return data.get(key, '').strip()

    info = dict(
        name=get('name'),
        phone=get('tel'),
        email=get('email'),
        occupation=get('occupation'),
        employees=get('workers'),
        website=get('website'),
        selected_prizes=get('prizes').strip(';'),
        job_title=get('job_title'),
    )

    new = True

    try:
        participant = Participant.query.filter_by(email=info['email']).first() or Participant()
        new = participant.id is None

        if new:
            db.session.add(participant)
        elif (arrow.now() - participant.added).total_seconds() > SECS_IN_HOUR:
            raise TooLateForUpdate
        for k, v in info.items():
            setattr(participant, k, v)
        db.session.commit()

    except TooLateForUpdate:
        app.logger.warning("It's too late for {} to update.".format(participant))

    finally:

        # Rollback uncommited changes.
        db.session.rollback()

        if new:
            try:
                sendpulse.add_address(info['email'])
                participant.subscribed_to_newsletter = arrow.now()
                db.session.commit()
            finally:
                db.session.rollback()


@celery.task
def resubmit_failed_addresses():
    try:
        failed = (Participant.query
                             .filter_by(subscribed_to_newsletter=None)
                             .order_by(Participant.added)
                             .all())
        if failed:
            app.logger.warning('Found failed addresses: {}'.format(failed))

        for person in failed:
            try:
                app.logger.warning('Resubmitting address "{}"...'
                                   .format(person.email))
                sendpulse.add_address(person.email)
                person.subscribed_to_newsletter = arrow.now()
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                app.logger.error('Failed to submit address "{}": {}'
                                 .format(person.email, e))

    finally:
        db.session.rollback()


@app.route('/add', methods=['POST'])
def show_add_participant():

    form = request.form.to_dict(flat=True)

    app.logger.debug('New participant: {}'.format(form))
    add_participant.delay(form)

    return ''


@app.route('/46a5cd3b-9284-4b6a-9368-b7184946bfeb')
@login_required
def show_status():
    participants = Participant.query.order_by(Participant.added.desc()).all()

    now = arrow.now()
    delta_instant = timedelta(hours=app.config.get('DELTA_HOURS') or 6)
    amount_instant = Participant.query.filter(Participant.added > now - delta_instant).count()
    frequency_instant = amount_instant / delta_instant.total_seconds()
    delta_full_span = now - participants[-1].added
    try:
        frequency = len(participants) / delta_full_span.total_seconds()
    except ZeroDivisionError:
        frequency = None

    return render_template('status.html', participants=participants,
                           frequency=frequency, frequency_instant=frequency_instant)


@app.route('/report')
@login_required
def generate_report():
    stream = StringIO()
    writer = csv.writer(stream, delimiter=";", quoting=csv.QUOTE_ALL)

    PRIZES_RANGE = list(str(x) for x in range(1, 18))

    # Writing header.
    header = 'Добавлен Имя E-mail Телефон Сайт Должность Отрасль Сотрудников'.split()
    header.extend(PRIZES_RANGE)
    writer.writerow(header)

    participants = Participant.query.order_by(Participant.added.desc()).all()
    for p in participants:
        prizes = p.selected_prizes.split(';')
        row = [
            p.added.format('YYYY-MM-DD HH:mm:ss'),
            p.name,
            p.email,
            p.phone,
            p.website,
            p.job_title,
            p.occupation,
            p.employees,
        ]
        row.extend('1' if x in prizes else '' for x in PRIZES_RANGE)
        writer.writerow(row)

    response = make_response(stream.getvalue().encode('cp1251'))
    response.headers['Content-Disposition'] = 'attachment; filename=crazykit.csv'
    response.headers['Content-Type'] = 'text/csv; charset=windows-1251'
    return response


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if (username, password) == \
                (app.config['ADMIN_LOGIN'], app.config['ADMIN_PASSWORD']):
            login_user(load_user(username), remember=False)

    if current_user.is_authenticated:
        return redirect(url_for('show_status'))
    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


import sendpulse  # noqa: E402


if __name__ == '__main__':
    app.run(debug=True)
