"""Flask app configuration."""
from os import environ, path
import os
from dotenv import load_dotenv
from datetime import datetime

basedir = path.abspath(path.dirname(__file__))
load_dotenv(path.join(basedir, ".env"))

table_prefix = "flapp_"


def date_filestr(timestamp: int = None):
    dt_file_format = "%Y%m%d_%H%M%S"
    if timestamp is not None:
        return datetime.fromtimestamp(timestamp).strftime(dt_file_format)
    return datetime.now().strftime(dt_file_format)


class Config:
    """Set Flask configuration from environment variables."""

    FLASK_APP = environ.get("FLASK_APP", "wsgi.py")
    FLASK_ENV = environ.get("FLASK_ENV", "production")
    SECRET_KEY = environ.get("SECRET_KEY", os.urandom(32))

    # Flask-SQLAlchemy
    SQLALCHEMY_DATABASE_URI = environ.get("SQLALCHEMY_DATABASE_URI", "mysql+pymysql://flask_app_mysql:myFlaskMysqlPass1@localhost:3306/flask_app")
    SQLALCHEMY_ECHO = True
    SQLALCHEMY_TRACK_MODIFICATIONS = True

    # Flask-Assets
    LESS_BIN = environ.get("LESS_BIN")
    ASSETS_DEBUG = environ.get("ASSETS_DEBUG")
    LESS_RUN_IN_DEBUG = environ.get("LESS_RUN_IN_DEBUG")

    # Static Assets
    STATIC_FOLDER = "static"
    TEMPLATES_FOLDER = "templates"
    COMPRESSOR_DEBUG = environ.get("COMPRESSOR_DEBUG", True)
