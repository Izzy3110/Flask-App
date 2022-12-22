from flask import Blueprint, render_template, render_template_string, redirect, url_for, request
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
from flask_login import current_user, login_required, logout_user, login_user
from flask_httpauth import HTTPBasicAuth
from base64 import b64decode
from flask_login_tutorial.models import User
from flask_login_tutorial.decorators import login_required_ext
invoices_bp = Blueprint(
    "invoices_bp", __name__, url_prefix="/invoices", template_folder="templates", static_folder="static"
)


@login_required_ext
@invoices_bp.route("/", methods=['GET', 'POST'])
def invoices_index():
    return render_template("invoices.jinja2",
                           template="dashboard-template",
                           body="Invoices Index")

@login_required_ext
@invoices_bp.route("/create", methods=['GET', 'POST'])
def invoices_create_index():
    if request.method == "GET":
        return render_template("invoices_create.jinja2",
                           template="dashboard-template",
                           body="Invoices CREATE")
    else:
        return render_template("invoices_create-show.jinja2",
                           template="dashboard-template",
                           body="Invoices CREATE")