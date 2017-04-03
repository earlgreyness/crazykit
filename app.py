import functools
import logging

import arrow
from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Boolean, Unicode, Integer
from sqlalchemy_utils import ArrowType

log = logging.getLogger(__name__)
Column = functools.partial(Column, nullable=False)


SQLALCHEMY_TRACK_MODIFICATIONS = False


app = Flask(__name__)
app.config.from_object(__name__)
app.config.from_object('settings')
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
    added = Column(ArrowType, default=arrow.now)
    subscribed_to_newsletter = Column(Boolean, default=False)


if __name__ == '__main__':
    app.run(debug=True)
