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

    FLASK_APP = environ.get("FLASK_APP")
    FLASK_ENV = environ.get("FLASK_ENV")
    SECRET_KEY = environ.get("SECRET_KEY")

    # Flask-SQLAlchemy
    SQLALCHEMY_DATABASE_URI = environ.get("SQLALCHEMY_DATABASE_URI", "sqlite:///database_"+date_filestr()+".db")
    SQLALCHEMY_ECHO = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Flask-Assets
    LESS_BIN = environ.get("LESS_BIN")
    ASSETS_DEBUG = environ.get("ASSETS_DEBUG")
    LESS_RUN_IN_DEBUG = environ.get("LESS_RUN_IN_DEBUG")

    # Static Assets
    STATIC_FOLDER = "static"
    TEMPLATES_FOLDER = "templates"
    COMPRESSOR_DEBUG = environ.get("COMPRESSOR_DEBUG")
