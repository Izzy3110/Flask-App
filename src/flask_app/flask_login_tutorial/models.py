"""Database models."""
from flask_login import UserMixin, AnonymousUserMixin
from werkzeug.security import check_password_hash, generate_password_hash
import os
import inspect
import sys
from . import db
import time    
from datetime import datetime, date, time, timezone, timedelta
import pytz


import unittest
import json

from flask import request, jsonify

import inspect
import os
import sys

import importlib.util
import sys


def mysql_time() -> str:
    unaware_utc = datetime.now(timezone.utc)
    print('Timezone naive:', unaware_utc)

    then = unaware_utc + timedelta(hours=1)

    aware = datetime.now(pytz.utc)
    print('Timezone Aware:', aware)

    # US/Central timezone datetime
    aware_europe_berlin = datetime.now(pytz.timezone('Europe/Berlin'))
    print('Europe/Berlin DateTime', aware_europe_berlin)

    return aware_europe_berlin.strftime('%Y-%m-%d %H:%M:%S')




print("LAZY")
config_spec = importlib.util.spec_from_file_location("config", os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "flask_app", "config.py"))
loader = importlib.util.LazyLoader(config_spec.loader)
config_spec.loader = loader
module = importlib.util.module_from_spec(config_spec)
name = "config"
sys.modules[name] = module
loader.exec_module(module)
config = module
from config import date_filestr, table_prefix

print("LAZY")


class User(UserMixin, db.Model):
    """User account model."""
    
    __tablename__ = table_prefix+"user"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=False)
    email = db.Column(db.String(40), unique=True, nullable=False)
    password = db.Column(
        db.String(200), primary_key=False, unique=False, nullable=False
    )
    website = db.Column(db.String(60), index=False, unique=False, nullable=True)
    created_on = db.Column(db.DateTime, index=False, unique=False, nullable=True)
    last_login = db.Column(db.DateTime, index=False, unique=False, nullable=True)

    def update_last_login(self):
        self.last_login = mysql_time()
        db.session.commit()  # Create new user

    def set_password(self, password):
        """Create hashed password."""
        self.password = generate_password_hash(password, method="sha256")

    def check_password(self, password):
        """Check hashed password."""
        return check_password_hash(self.password, password)

    def __repr__(self):
        return "<User {}>".format(self.name)
