from flask import Blueprint, render_template, render_template_string, redirect, url_for, request, current_app, jsonify
from pprint import pprint
import requests
import extruct
from w3lib.html import get_base_url
import time
import uuid
import os
import json
from urllib.parse import urlparse
from bs4 import BeautifulSoup
import lxml.html as lh
import lxml
from flask_login import current_user, login_required, logout_user
from flask_login_tutorial.models import OAuth2Client, db, create_bearer_token_validator, OAuth2Token
from werkzeug.security import gen_salt
from authlib.integrations.flask_oauth2 import current_token


from authlib.integrations.flask_oauth2 import (
    AuthorizationServer,
    ResourceProtector,
)


require_oauth = ResourceProtector()
bearer_cls = create_bearer_token_validator(db.session, OAuth2Token)
require_oauth.register_token_validator(bearer_cls())

oauth_bp = Blueprint(
    "oauth_bp", __name__, url_prefix="/oauth", template_folder="templates", static_folder="static"
)



def split_by_crlf(s):
    return [v for v in s.splitlines() if v]


@oauth_bp.route('/authorize', methods=['GET', 'POST'])
def oauth_authorize():
    authorization = current_app.config['auth']
    user = current_user
    # if user log status is not true (Auth server), then to log it in
    if not user:
        return redirect(url_for('oauth_bp.oauth_index', next=request.url))
    if request.method == 'GET':
        try:
            grant = authorization.get_consent_grant(end_user=user)
        except OAuth2Error as error:
            return error.error
        return render_template("oauth2_authorize.jinja2",
                           template="dashboard-template",
                           body="OAuth Index", user=user, grant=grant)
    if not user and 'username' in request.form:
        username = request.form.get('username')
        user = User.query.filter_by(name=username).first()
    if request.form['confirm']:
        grant_user = user
    else:
        grant_user = None
    return authorization.create_authorization_response(grant_user=grant_user)



@login_required
@oauth_bp.route("/", methods=['GET', 'POST'])
def oauth_index():
    if request.method == 'POST':
        username = request.form.get('username')
        user = User.query.filter_by(name=username).first()
        if not user:
            user = User(name=username)
            db.session.add(user)
            db.session.commit()
        session['id'] = user.id
        # if user is not just to log in, but need to head back to the auth page, then go for it
        next_page = request.args.get('next')
        if next_page:
            return redirect(next_page)
        return redirect('/')
    else:
        if current_user.is_authenticated:
            clients = OAuth2Client.query.filter_by(user_id=current_user.id).all()
        else:
            return redirect(url_for("auth_bp.login"))
        json_ = "{}"
        return render_template("oauth.jinja2",
                               template="dashboard",
                               body="OAuth Index",
                               user=current_user, clients=clients
                               )

@oauth_bp.route("/create_client", methods=['GET', 'POST'])
def oauth_create_client():
    if current_user.is_authenticated:
        clients = OAuth2Client.query.filter_by(user_id=current_user.id).all()
        print(clients)
    if request.method == "GET":
        return render_template("oauth2_create_client.jinja2", template="dashboard-template",
        body="CREATE CLIENT")
       
    client_id = gen_salt(24)
    client_id_issued_at = int(time.time())
    client = OAuth2Client(
        client_id=client_id,
        client_id_issued_at=client_id_issued_at,
        user_id=current_user.id,
    )
    form = request.form
    
    client_metadata = {
        "client_name": form["client_name"],
        "client_uri": form["client_uri"],
        "grant_types": split_by_crlf(form["grant_type"]),
        "redirect_uris": split_by_crlf(form["redirect_uri"]),
        "response_types": split_by_crlf(form["response_type"]),
        "scope": form["scope"],
        "token_endpoint_auth_method": form["token_endpoint_auth_method"]
    }
    client.set_client_metadata(client_metadata)
    
    
    
    if form['token_endpoint_auth_method'] == 'none':
        client.client_secret = ''
    else:
        client.client_secret = gen_salt(48)
    
    db.session.add(client)
    db.session.commit()
    return redirect(url_for("oauth_bp.oauth_index"))

@oauth_bp.route('/token', methods=['POST'])
def issue_token():
    authorization = current_app.config['auth']
    
    resp = authorization.create_token_response()
    return resp

@oauth_bp.route('/revoke', methods=['POST'])
def revoke_token():
    authorization = current_app.config['auth']
    return authorization.create_endpoint_response('revocation')
