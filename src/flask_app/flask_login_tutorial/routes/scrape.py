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

scrape_bp = Blueprint(
    "scrape_bp", __name__, url_prefix="/scrape", template_folder="templates", static_folder="static"
)

scrapes = {}


def scrape(url: str, scrape_uuid: str):
    html = get_html(url)

    parsed_url = urlparse(url)
    netloc = parsed_url.netloc
    if not os.path.isdir(os.path.join(os.getcwd(), "data")):
        os.mkdir(os.path.join(os.getcwd(), "data"))
    if not os.path.isdir(os.path.join("data", netloc)):
        os.mkdir(os.path.join("data", netloc))

    soup = BeautifulSoup(html.decode("utf-8"), "lxml")  # make BeautifulSoup

    links = soup.findAll("a")
    links_ = []
    if len(links) > 0:
        for link in links:
            links_.append(
                (
                    link.getText() if link.getText() is not None else "",
                    link.get("href") if link.get("href") is not None else "",
                    link.get("target") if link.get("target") is not None else ""
                )
            )
        with open(os.path.join("data", netloc, str(scrape_uuid) + "-links.csv"), "w") as links_f:
            for current_l in links_:
                text, url, target = current_l
                links_f.write(text.strip()+","+url+","+target+"\n")
            links_f.close()

    pretty_html = soup.prettify()

    with open(os.path.join("data", netloc, str(scrape_uuid) + ".html"), "w") as test_json_f:
        test_json_f.write(pretty_html)
        test_json_f.close()

    metadata = get_metadata(html, url)
    return metadata
    

def get_html(url):
    headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Access-Control-Max-Age': '3600',
        'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0'
    }
    req = requests.get(url, headers=headers)
    return req.content


def get_metadata(html: bytes, url: str):
    metadata = extruct.extract(
        html,
        base_url=get_base_url(url),
        syntaxes=['json-ld','microdata', 'opengraph', 'rdfa'],
        uniform=True,
        return_html_node=True
    )
    if bool(metadata) and isinstance(metadata, list):
        metadata = metadata[0]
    return metadata


def get_json(url):
    global scrapes
    time_start = time.time()
    scrape_uuid = str(uuid.uuid4())
    metadata = scrape(url, scrape_uuid)
    time_end = time.time()

    time_str = str(time.time())
    json_data = {
        "uuid": scrape_uuid,
        "url": url,
        "scrape_json": metadata,
        "elapsed": time_end - time_start
    }
    scrapes[time_str] = json_data
    if not os.path.isdir("data"):
        os.mkdir("data")
    parsed_url = urlparse(url)
    netloc = parsed_url.netloc
    if not os.path.isdir(os.path.join("data", netloc)):
        os.mkdir(os.path.join("data", netloc))
      
    with open(os.path.join("data", netloc, str(scrape_uuid)+".json"), "w") as test_json_f:
        test_json_f.write(json.dumps(json_data, indent=4))
        test_json_f.close()
    return json.dumps(json_data)


@login_required
@scrape_bp.route("/", methods=['GET', 'POST'])
def scrape_index():
    if request.method == "POST":
        if request.values.get("url") is not None:
            test_url = request.values.get("url")
            json_ = get_json(url=test_url)
            return render_template("scrape.jinja2",
                                   template="dashboard-template",
                                   body="Scrape Index",
                                   scrape_json=json.dumps(json.loads(json_), indent=4)
                                   )
    else:
        test_url = 'https://hackersandslackers.com/creating-django-views/'
        json_ = get_json(url=test_url)
        return render_template("scrape.jinja2",
                               template="dashboard-template",
                               body="Scrape Index",
                               scrape_json=json.dumps(json.loads(json_), indent=4)
                               )
    if request.method == "POST":
        token_ = request.headers.get("Authorization").split("Basic ")[1]
        username, password = (b64decode(token_)).decode().split(":")
        user = User.query.filter_by(email=username).first()
        if user and user.check_password(password=password):
            user.update_last_login()
            
            login_user(user)
            next_page = request.args.get("next")
            return redirect(next_page or url_for("scrape_bp.scrape_index"))
        else:
            return redirect(url_for("auth_bp.login"))
