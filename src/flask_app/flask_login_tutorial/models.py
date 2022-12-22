"""Database models."""
from flask_login import UserMixin, AnonymousUserMixin
from werkzeug.security import check_password_hash, generate_password_hash
import os
import inspect
import sys
# from . import db
import time    
from datetime import datetime, date, time, timezone, timedelta
import pytz
import base64
from sqlalchemy.dialects.mysql import LONGTEXT

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
from authlib.oauth2.rfc6749 import grants
from authlib.oauth2.rfc7636 import CodeChallenge

import unittest
import json

from flask import request, jsonify, current_app

from authlib.integrations.sqla_oauth2 import (
    OAuth2ClientMixin,
    OAuth2AuthorizationCodeMixin,
    OAuth2TokenMixin,
)

import inspect
import os
import sys
import onetimepass
import importlib.util
import sys
from flask_sqlalchemy import SQLAlchemy



db = SQLAlchemy()




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



config_spec = importlib.util.spec_from_file_location("config", os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "flask_app", "config.py"))
loader = importlib.util.LazyLoader(config_spec.loader)
config_spec.loader = loader
module = importlib.util.module_from_spec(config_spec)
name = "config"
sys.modules[name] = module
loader.exec_module(module)
config = module
from config import date_filestr, table_prefix



class User(UserMixin, db.Model):
    """User account model."""
    
    __tablename__ = table_prefix+"user"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=False)
    username = db.Column(db.String(100), nullable=False, unique=True)
    email = db.Column(db.String(40), unique=True, nullable=False)
    twofactor_enabled = db.Column(db.Integer, unique=False, nullable=True)
    password = db.Column(
        LONGTEXT, primary_key=False, unique=True, nullable=False
    )
    website = db.Column(db.String(60), index=False, unique=False, nullable=True)
    created_on = db.Column(db.String(60), index=False, unique=False, nullable=True)
    last_login = db.Column(db.String(60), index=False, unique=False, nullable=True)
    otp_secret = db.Column(db.String(length=16), index=False, unique=False, nullable=True)

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if self.otp_secret is None:
            self.otp_secret = base64.b32encode(os.urandom(10)).decode('utf-8')
 
    def to_dict(self):
        return {
                "id": self.id,
                "name": self.name,
                "email": self.email,
                "website": self.website,
                "created_on": self.created_on,
                "otp_secret": self.otp_secret,
                
                
                
                }
 
    def get_totp_secret(self):
        return self.otp_secret
        
    def get_totp_uri(self):
        #return f'otpauth://totp/TOTPDemo:{self.name}?secret={self.otp_secret}&issuer=TOTPDemo'
        return 'otpauth://totp/WYL OAuth:{0}?secret={1}&issuer=WYL-OAuth' \
            .format(self.username, self.otp_secret)

    def verify_totp(self, token):
        return onetimepass.valid_totp(token, self.otp_secret)

    def update_last_login(self):
        self.last_login = mysql_time()
        db.session.commit()  # Create new user


    def set_two_factor(self, state):
        self.twofactor_enabled = 1 if state == "false" else 0
        print("###################################\n")
        print(self.twofactor_enabled)
        db.session.commit()  # Create new user
        print("###################################\n")

    def set_password(self, password):
        """Create hashed password."""
        self.password = password

    def check_password(self, password, sec_man, user):
        """Check hashed password."""
        return sec_man.decrypt_from_base(user.password) == password
        #print(password)
        #return check_password_hash(self.password, password)

    def get_user_id(self):
        return self.id

    def check_email_password_auth(self, user_email_, password):
        user = User.query.filter_by(email=user_email_).first()
        if user and self.check_password(password=user.password, sec_man=current_app.config["sec_man"]):
            return user
        return False

    def __repr__(self):
        return "<User {}>".format(self.name)



class OAuth2Client(db.Model, OAuth2ClientMixin):
    __tablename__ = 'oauth2_client'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey(table_prefix+"user.id", ondelete='CASCADE'))
    user = db.relationship('User')


class OAuth2AuthorizationCode(db.Model, OAuth2AuthorizationCodeMixin):
    __tablename__ = 'oauth2_code'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey(table_prefix+"user.id", ondelete='CASCADE'))
    user = db.relationship('User')


class OAuth2Token(db.Model, OAuth2TokenMixin):
    __tablename__ = 'oauth2_token'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey(table_prefix+"user.id", ondelete='CASCADE'))
    user = db.relationship('User')

    def is_refresh_token_active(self):
        if self.revoked:
            return False
        expires_at = self.issued_at + self.expires_in * 2
        return expires_at >= time.time()

class AuthorizationCodeGrant(grants.AuthorizationCodeGrant):
    TOKEN_ENDPOINT_AUTH_METHODS = [
        'client_secret_basic',
        'client_secret_post',
        'none',
    ]

    def save_authorization_code(self, code, request):
        code_challenge = request.data.get('code_challenge')
        code_challenge_method = request.data.get('code_challenge_method')
        auth_code = OAuth2AuthorizationCode(
            code=code,
            client_id=request.client.client_id,
            redirect_uri=request.redirect_uri,
            scope=request.scope,
            user_id=request.user.id,
            code_challenge=code_challenge,
            code_challenge_method=code_challenge_method,
        )
        db.session.add(auth_code)
        db.session.commit()
        return auth_code

    def query_authorization_code(self, code, client):
        auth_code = OAuth2AuthorizationCode.query.filter_by(
            code=code, client_id=client.client_id).first()
        if auth_code and not auth_code.is_expired():
            return auth_code

    def delete_authorization_code(self, authorization_code):
        db.session.delete(authorization_code)
        db.session.commit()

    def authenticate_user(self, authorization_code):
        return User.query.get(authorization_code.user_id)


class PasswordGrant(grants.ResourceOwnerPasswordCredentialsGrant):
    def authenticate_user(self, username, password):
        user = User.query.filter_by(name=username).first()
        if user is not None and user.check_password(password):
            return user


class RefreshTokenGrant(grants.RefreshTokenGrant):
    def authenticate_refresh_token(self, refresh_token):
        token = OAuth2Token.query.filter_by(refresh_token=refresh_token).first()
        if token and token.is_refresh_token_active():
            return token

    def authenticate_user(self, credential):
        return User.query.get(credential.user_id)

    def revoke_old_credential(self, credential):
        credential.revoked = True
        db.session.add(credential)
        db.session.commit()


