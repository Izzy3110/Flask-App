from flask import Blueprint, render_template, render_template_string, redirect, url_for, request, jsonify
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

api_bp = Blueprint(
    "api_bp", __name__, url_prefix="/api", template_folder="templates", static_folder="static"
)



def split_by_crlf(s):
    return [v for v in s.splitlines() if v]







@login_required
@api_bp.route("/", methods=['GET', 'POST'])
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
            print(clients)
        json_ = "{}"
        return render_template("oauth.jinja2",
                               template="dashboard-template",
                               body="OAuth Index",
                               user=current_user, clients=clients
                               )

@api_bp.route('/me')
@require_oauth('profile')
def api_me():
    user = current_token.user
    return jsonify(id=user.id, name=user.name)
