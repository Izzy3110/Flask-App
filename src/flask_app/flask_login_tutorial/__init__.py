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
import inspect
from .models import db, OAuth2Client, OAuth2Token, AuthorizationCodeGrant, PasswordGrant, RefreshTokenGrant
from authlib.oauth2.rfc6749 import grants
from authlib.oauth2.rfc7636 import CodeChallenge

from authlib.integrations.flask_oauth2 import (
    AuthorizationServer,
    ResourceProtector,
)

from authlib.integrations.sqla_oauth2 import (
    create_query_client_func,
    create_save_token_func,
    create_revocation_endpoint,
    create_bearer_token_validator,
)

require_oauth = None

def c_oauth(app):
    global require_oauth
    query_client = create_query_client_func(db.session, OAuth2Client)
    save_token = create_save_token_func(db.session, OAuth2Token)
    authorization = AuthorizationServer(
        query_client=query_client,
        save_token=save_token,
    )
    require_oauth = ResourceProtector()

        
    
    config_oauth(app, authorization, require_oauth)


def config_oauth(app, authorization, require_oauth):
    authorization.init_app(app)
    

    # support all grants
    authorization.register_grant(grants.ImplicitGrant)
    authorization.register_grant(grants.ClientCredentialsGrant)
    authorization.register_grant(AuthorizationCodeGrant, [CodeChallenge(required=True)])
    authorization.register_grant(PasswordGrant)
    authorization.register_grant(RefreshTokenGrant)

    # support revocation
    revocation_cls = create_revocation_endpoint(db.session, OAuth2Token)
    authorization.register_endpoint(revocation_cls)

    # protect resource
    bearer_cls = create_bearer_token_validator(db.session, OAuth2Token)
    require_oauth.register_token_validator(bearer_cls())
    app.config['auth'] = authorization

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

path_ = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "wyl", "__init__.py")
if os.path.isfile(path_):
    wyl_spec = importlib.util.spec_from_file_location("wyl", path_)
    loader = importlib.util.LazyLoader(wyl_spec.loader)
    wyl_spec.loader = loader
    wyl_module = importlib.util.module_from_spec(wyl_spec)
    name = "wyl"
    sys.modules[name] = wyl_module
    loader.exec_module(wyl_module)
    wyl = wyl_module
    if "rsa_key.bin" in os.listdir(os.path.dirname(os.path.abspath(__file__))):
        sec_man = wyl.SecMan(
            privatekey_filedir="/usr/local/src/Flask-App/src/flask_app/flask_login_tutorial", 
            password_str=os.environ.get("APP_PASSWORD")
        )
    else:
        print(">>>> <<<< NO KEY!")


from config import table_prefix, date_filestr, Config as CurrentConfig

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
            else:
                print(">>> Config loaded")
except NameError:
    pass






login_manager = LoginManager()


def import_abs_module(filepath):
    if os.path.isfile(filepath): 
        file_nameonly = os.path.basename(filepath).rstrip(".py")
        mod_spec = importlib.util.spec_from_file_location(file_nameonly, filepath)
        if mod_spec is not None:
            loader = importlib.util.LazyLoader(mod_spec.loader)
            mod_spec.loader = loader
            module = importlib.util.module_from_spec(mod_spec)
            sys.modules[file_nameonly] = module
            loader.exec_module(module)
            return module
        else:
            print("error NONE")




def create_app():
    global sec_man
    app = Flask(__name__, instance_relative_config=False)
    app.config.from_object(CurrentConfig)
    app.config["OAUTH2_REFRESH_TOKEN_GENERATOR"] = True
    app.config["AUTHLIB_INSECURE_TRANSPORT"] = 1
    app.config["sec_man"] = sec_man
    app.config["APP_BASE"] = os.path.dirname(os.path.abspath(__file__))
    if app.config["FLASK_DEBUG"] == "development":
        app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database_"+date_filestr()+".db"
    
    db.init_app(app)
    login_manager.init_app(app)
    
    routes_ = {}
    routes_path = os.path.join(os.getcwd(), "flask_login_tutorial", "routes")
    if os.path.isdir(routes_path):
        for file in os.listdir(routes_path):
            file_nameonly = os.path.basename(file).rstrip(".py")
            routes_[file_nameonly] = import_abs_module(os.path.join(routes_path, file_nameonly+".py"))
            found_bp = None
            for m in inspect.getmembers(routes_[file_nameonly]):
                if not m[0].startswith("_"):
                    if m[0].endswith("_bp"):
                        found_bp = m[1]
                        break
                    #else:
                    #    print(m[0])
                        
            if found_bp is not None:
                print("BP "+found_bp.url_prefix+": "+file_nameonly)
                
                            
                app.register_blueprint(found_bp)
    else:
        print("no routes")
    c_oauth(app)
    
    with app.app_context():
        db.create_all()
        
        print("ENV: "+str(app.config["FLASK_DEBUG"]))
        if app.config["FLASK_DEBUG"] == "development":
            from .assets import compile_static_assets
            print("compiling assets...")
            compile_static_assets(app)

        return app
