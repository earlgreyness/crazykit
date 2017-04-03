import functools
import logging

import arrow
from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Unicode, Integer, Index, text, CheckConstraint
from sqlalchemy_utils import ArrowType

log = logging.getLogger(__name__)
Column = functools.partial(Column, nullable=False)

NO_WHITESPACE_REGEX = r'^\S*$'

app = Flask(__name__)
app.config.from_object('settings')
logging.config.dictConfig(app.config['LOGGER_CONFIG'])
cors = CORS(app, resources={'*': {'origins': '*'}})
db = SQLAlchemy(app)


class Participant(db.Model):
    __tablename__ = 'participants'

    id = Column(Integer, primary_key=True)

    name = Column(Unicode)
    phone = Column(Unicode)
    email = Column(Unicode)
    occupation = Column(Unicode)
    employees = Column(Unicode)

    added = Column(ArrowType(timezone=True), default=arrow.utcnow)
    subscribed_to_newsletter = Column(ArrowType(timezone=True), nullable=True)

    __table_args__ = (
        CheckConstraint("email ~ '{}'".format(NO_WHITESPACE_REGEX)),
        Index('index_unique_lowercase_email', text('lower(email)'), unique=True),
    )


if __name__ == '__main__':
    app.run(debug=True)
