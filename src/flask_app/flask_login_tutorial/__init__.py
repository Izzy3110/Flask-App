from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from .config import Config

db = SQLAlchemy()
login_manager = LoginManager()


import inspect
import os
import sys


test_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
src_dir = os.path.join(test_dir, "config.py")
sys.path.append(src_dir)


def create_app():
    app = Flask(__name__, instance_relative_config=False)
    app.config.from_object("config.Config")

    db.init_app(app)
    login_manager.init_app(app)

    with app.app_context():
        from . import auth, routes, scrape
        from .assets import compile_static_assets

        app.register_blueprint(routes.main_bp)
        app.register_blueprint(auth.auth_bp)
        app.register_blueprint(scrape.scrape_bp)
        app.config.from_object(Config)
        db.create_all()

        if app.config["FLASK_ENV"] == "development":
            compile_static_assets(app)

        return app
