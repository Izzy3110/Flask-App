"""Logged-in page routes."""
from flask import Blueprint, redirect, render_template, url_for, request, session, abort, jsonify
from flask_login import current_user, login_required, logout_user
from flask_login_tutorial.models import User
main_bp = Blueprint(
    "main_bp", __name__, template_folder="templates", static_folder="static", url_prefix="/"
)
from io import BytesIO
import pyqrcode

@main_bp.route("/", methods=["GET"])
@login_required
def dashboard():
    """Logged-in User Dashboard."""
    return render_template(
        "dashboard.jinja2",
        title="Flask-Login Tutorial",
        template="dashboard-template",
        current_user=current_user,
        body="You are now logged in!",
    )


@main_bp.route("/logout")
@login_required
def logout():
    """User log-out logic."""
    logout_user()
    return redirect(url_for("auth_bp.login"))

@main_bp.route('/qrcode')
def qrcode():
    if not current_user.is_authenticated:
        abort(404)
    user = User.query.filter_by(username=current_user.username).first()
    print(user.get_totp_uri())
    url = pyqrcode.create(user.get_totp_uri())
    stream = BytesIO()
    url.svg(stream, scale=5)
    xml_data = stream.getvalue()
    return xml_data, 200, {
        'Content-Type': 'image/svg+xml',
        'Cache-Control': 'no-cache, no-store, must-revalidate',
        'Pragma': 'no-cache',
        'Expires': '0'}


@main_bp.route('/set_2fa_enabled', methods=["GET", "POST"])
def set_2fa_enabled():
    if not current_user.is_authenticated:
        abort(404)
    user = User.query.filter_by(username=current_user.username).first()
    print(request.values.get("new_state"))
    print(dict(request.values).keys())
    state_ = request.values.get("new_state")
    
    user.set_two_factor(state_)
    return jsonify({"success": user.twofactor_enabled == state_})
    
