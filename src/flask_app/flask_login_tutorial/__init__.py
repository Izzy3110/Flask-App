import importlib
import sys

from dotenv import load_dotenv
from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask import has_request_context, request
from flask.logging import default_handler
import logging
import os
from os import environ

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, ".env"))


class RequestFormatter(logging.Formatter):
    def format(self, record):
        if has_request_context():
            record.url = request.url
            record.remote_addr = request.remote_addr
        else:
            record.url = None
            record.remote_addr = None

        return super().format(record)   


formatter = RequestFormatter(
    '[%(asctime)s] %(remote_addr)s requested %(url)s\n'
    '%(levelname)s in %(module)s: %(message)s'
)
default_handler.setFormatter(formatter)


config_spec = importlib.util.spec_from_file_location("config", os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "flask_app", "config.py"))
loader = importlib.util.LazyLoader(config_spec.loader)
config_spec.loader = loader
module = importlib.util.module_from_spec(config_spec)
name = "config"
sys.modules[name] = module
loader.exec_module(module)
config = module
print(config)
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


db = SQLAlchemy()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__, instance_relative_config=False)
    app.config.from_object(Config)

    

    db.init_app(app)
    login_manager.init_app(app)

    with app.app_context():
        from . import auth, routes, scrape
        from .assets import compile_static_assets

        app.register_blueprint(routes.main_bp)
        app.register_blueprint(auth.auth_bp)
        app.register_blueprint(scrape.scrape_bp)
        app.config.from_object(Config)

        # db.create_all()

        if app.config["FLASK_ENV"] == "development":
            compile_static_assets(app)

        return app
