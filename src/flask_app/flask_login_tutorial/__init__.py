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
import inspect


basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, "..", ".env"))


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


config_spec = importlib.util.spec_from_file_location("config", os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "config.py"))
loader = importlib.util.LazyLoader(config_spec.loader)
config_spec.loader = loader
module = importlib.util.module_from_spec(config_spec)
name = "config"
sys.modules[name] = module
loader.exec_module(module)
config = module
from config import table_prefix, Config as CurrentConfig

try:
    if Config is not None:
        if type(CurrentConfig) == type(Config):
            if not CurrentConfig == Config:
                common_ = {}
                uncommon_ = {}
                for m in inspect.getmembers(CurrentConfig):
                    if not m[0].startswith("_"):
                        if hasattr(Config, m[0]):
                            if getattr(Config, m[0]) == m[1]:
                                common_[m[0]] = m[1]
                            else:
                                uncommon_[m[0]] = m[1]
                        print("--")
                print(len(uncommon_.keys()))
                print(uncommon_)
                print(common_)
                #print("---")
                #for m in inspect.getmembers(Config):
                #    if not m[0].startswith("_"):
                #        print(m)
                print("---##")
            else:
                print("Config loaded")
except NameError:
    pass

db = SQLAlchemy()
login_manager = LoginManager()


def create_app():
    app = Flask(__name__, instance_relative_config=False)
    app.config.from_object(CurrentConfig)
    db.init_app(app)
    login_manager.init_app(app)

    with app.app_context():
        from . import auth, routes, scrape
        from .assets import compile_static_assets

        app.register_blueprint(routes.main_bp)
        app.register_blueprint(auth.auth_bp)
        app.register_blueprint(scrape.scrape_bp)
        

        db.create_all()

        if app.config["FLASK_ENV"] == "development":
            print("compiling assets...")
            compile_static_assets(app)

        return app
