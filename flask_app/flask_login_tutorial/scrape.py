from flask import Blueprint, render_template, render_template_string


scrape_bp = Blueprint(
    "scrape_bp", __name__, url_prefix="/scrape"
)


@scrape_bp.route("/")
def login():
    return render_template_string("<html><head></head><body>SCRAPE INDEX</body></html>")
