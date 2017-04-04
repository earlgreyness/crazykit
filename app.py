from functools import partial
import logging.config

import arrow
from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Unicode, Integer, Index, text, CheckConstraint
from sqlalchemy_utils import ArrowType

log = logging.getLogger(__name__)
Column = partial(Column, nullable=False)
ArrowType = partial(ArrowType, timezone=True)

NO_WHITESPACE_REGEX = r'^\S*$'

app = Flask(__name__)
app.config.from_object('settings')
logging.config.dictConfig(app.config['LOGGER_CONFIG'])
cors = CORS(app, resources={'*': {'origins': '*'}})
db = SQLAlchemy(app)


class PrimaryKeyMixin:
    id = Column(Integer, primary_key=True)


class Participant(db.Model, PrimaryKeyMixin):
    __tablename__ = 'participants'

    name = Column(Unicode)
    phone = Column(Unicode)
    email = Column(Unicode)
    occupation = Column(Unicode)
    employees = Column(Unicode)
    selected_prizes = Column(Unicode)

    added = Column(ArrowType(), default=arrow.utcnow)
    subscribed_to_newsletter = Column(ArrowType(), nullable=True)

    __table_args__ = (
        CheckConstraint("email ~ '{}'".format(NO_WHITESPACE_REGEX)),
        Index('index_unique_lowercase_email', text('lower(email)'), unique=True),
    )


if __name__ == '__main__':
    app.run(debug=True)
