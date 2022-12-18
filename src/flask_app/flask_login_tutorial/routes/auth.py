from flask import Blueprint, flash, redirect, render_template, request, url_for, current_app
from flask_login import current_user, login_user
from flask_login_tutorial import login_manager
from flask_login_tutorial.forms import LoginForm, SignupForm
from flask_login_tutorial.models import User, db
import time    
from datetime import datetime, date, time, timezone, timedelta
import pytz


auth_bp = Blueprint(
    "auth_bp", __name__, url_prefix="/"
)


def mysql_time() -> str:
    unaware_utc = datetime.now(timezone.utc)
    current_app.logger.debug('tz: Timezone naive:', unaware_utc)

    then = unaware_utc + timedelta(hours=1)

    aware = datetime.now(pytz.utc)
    current_app.logger.debug('tz: Timezone Aware:', aware)

    # US/Central timezone datetime
    aware_europe_berlin = datetime.now(pytz.timezone('Europe/Berlin'))
    current_app.logger.debug('tz: Europe/Berlin DateTime', aware_europe_berlin)

    return aware_europe_berlin.strftime('%Y-%m-%d %H:%M:%S')


@auth_bp.route("/signup", methods=["GET", "POST"])
def signup():
    """
    User sign-up page.

    GET requests serve sign-up page.
    POST requests validate form & user creation.
    """
    form = SignupForm()
    if form.validate_on_submit():
        existing_user = User.query.filter_by(email=form.email.data).first()
        if existing_user is None:
            user = User(
                name=form.name.data, email=form.email.data, website=form.website.data, created_on=mysql_time()
            )
            user.set_password(form.password.data)
            db.session.add(user)
            db.session.commit()  # Create new user

            current_app.logger.debug("LOGIN detected: "+user.email)

            login_user(user)  # Log in as newly created user
            return redirect(url_for("main_bp.dashboard"))
        flash("A user already exists with that email address.")
    return render_template(
        "signup.jinja2",
        title="Create an Account.",
        form=form,
        template="signup-page",
        body="Sign up for a user account.",
    )


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    current_app.logger.debug("CONN: "+str(request.headers.get('X-Real-Ip')))
    """
    Log-in page for registered users.

    GET requests serve Log-in page.
    POST requests validate and redirect user to dashboard.
    """
    # Bypass if user is logged in
    if current_user.is_authenticated:
        current_app.logger.debug("LOGIN detected: "+current_user.email)            
        return redirect(url_for("main_bp.dashboard"))

    form = LoginForm()
    # Validate login attempt
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(password=form.password.data):

            print("UPDATE USER LOGIN TIME")
            user.update_last_login()
            
            login_user(user)
            next_page = request.args.get("next")
            return redirect(next_page or url_for("main_bp.dashboard"))
        flash("Invalid username/password combination")
        return redirect(url_for("auth_bp.login"))
    return render_template(
        "login.jinja2",
        form=form,
        title="Log in.",
        template="login-page",
        body="Log in with your User account.",
    )


@login_manager.user_loader
def load_user(user_id):
    """Check if user is logged-in upon page load."""
    if user_id is not None:
        return User.query.get(user_id)
    return None


@login_manager.unauthorized_handler
def unauthorized():
    """Redirect unauthorized users to Login page."""
    flash("You must be logged in to view that page.")
    return redirect(url_for("auth_bp.login"))
