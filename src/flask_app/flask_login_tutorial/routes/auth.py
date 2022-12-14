from flask import Blueprint, flash, redirect, render_template, request, url_for, current_app
from flask_login import current_user, login_user
from flask_login_tutorial import login_manager
from flask_login_tutorial.forms import LoginForm, SignupForm, FALoginForm
from flask_login_tutorial.models import User, db
import time    
from datetime import datetime, date, time, timezone, timedelta
import pytz
# pyotp
import pyotp
import inspect
from sqlalchemy.sql import text
from flask import session
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.orm.exc import MultipleResultsFound


    

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

    return aware_europe_berlin


@auth_bp.route("/signup", methods=["GET", "POST"])
def signup():
    """
    User sign-up page.

    GET requests serve sign-up page.
    POST requests validate form & user creation.
    """
    form = SignupForm()
    if form.validate_on_submit():
        existing_email = User.query.filter_by(email=form.email.data).first()
        existing_username = User.query.filter_by(username=form.username.data).first()
        print("EX_USER: "+str(existing_username))
        print("EX_MAIL: "+str(existing_email))
        
        if existing_email is None and existing_username is None:
            pass_encrypted = current_app.config["sec_man"].encrypt_to_base(form.password.data.encode("utf-8"))
            user = User(
                name=form.name.data, username=form.username.data, email=form.email.data, website=form.website.data, created_on=mysql_time()
            )
                        
            current_app.logger.debug("CONN: "+str(request.headers.get('X-Real-Ip')))
            print("pass: "+str(pass_encrypted))
            user.set_password(pass_encrypted)
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
    """
    Log-in page for registered users.

    GET requests serve Log-in page.
    POST requests validate and redirect user to dashboard.
    """
    
    if "login_method" in dict(request.values).keys():
        print(request.values.get("login_method") == "2fa")
        print(request.values.get("token"))
        
        user = User.query.filter_by(email=request.values.get("email")).first()     
        if user is not None:
            session["email"] = user.email
            if user.verify_totp(request.values.get("token")):
                user.update_last_login()
                
                login_user(user)
                next_page = request.args.get("next")
                return redirect(next_page or url_for("main_bp.dashboard"))
            else:
                print("cannot verify")
        return render_template(
            "2fa-login.jinja2",
            title="2FA Login",
            email=session["email"] if "email" in session.keys() else "",
            template="dashboard-template",
            body="2FA"
        )
    
    
    
    
    
    # Bypass if user is logged in
    if current_user.is_authenticated:
        current_app.logger.debug("LOGIN detected: "+current_user.email)            
        return redirect(url_for("main_bp.dashboard"))

    form = LoginForm()
    # Validate login attempt
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()            
        if user is not None:
            if user.twofactor_enabled:
                return render_template(
                    "2fa-login.jinja2",
                    title="2FA Login",
                    email=user.email,
                    template="dashboard-template",
                    body="2FA"
                )
        
        if user and user.check_password(password=form.password.data, sec_man=current_app.config["sec_man"], user=user):

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

# 2FA page route



@auth_bp.route("/2fa/<int:generate_new>", methods=['GET', 'POST'], strict_slashes=False)
def login_2fa_gen(generate_new=None):
    secret = None
    secret_ = pyotp.random_base32()
    if request.method == "GET":
        if not current_user.is_authenticated:
            return redirect(url_for("auth_bp.login"))
    if current_user.is_authenticated:
        user = User.query.filter_by(email=current_user.email).first()
        user_dict = user.to_dict()
        if "otp_secret" in user_dict.keys():
            if user_dict["otp_secret"] is None or (generate_new is not None and generate_new):
                user.otp_secret = secret_
                db.session.commit()
            else:
                secret = user.otp_secret
    else:
        secret = secret_
    if secret is None:
        secret = secret_
        
    return render_template(
        "2fa.jinja2",
        title="2FA",
        template="dashboard-template",
        body="2FA",
        secret=secret
    )


@auth_bp.route("/2fa", methods=['GET', 'POST'], strict_slashes=False)
def login_2fa():
    if request.method == "GET":
        if not current_user.is_authenticated:
            return redirect(url_for("auth_bp.login"))
    if current_user.is_authenticated:
        user = User.query.filter_by(email=current_user.email).first()
        
        user_dict = user.to_dict()
        if "otp_secret" in user_dict.keys():
            if user_dict["otp_secret"] is None:
                user.otp_secret = secret
                db.session.commit()
            else:
                secret = user.otp_secret
    else:
        secret = pyotp.random_base32()
        
        
    return render_template(
        "2fa.jinja2",
        template="dashboard-template",
        title="2FA",
        body="2FA",
        totp_url=user.get_totp_uri(),
        secret=secret,
        twofactor_enabled=user.twofactor_enabled
    )
    
   
    
# 2FA form route
@auth_bp.route("/2fa", methods=["POST"])
def login_2fa_form():
    # getting secret key used by user
    secret = request.form.get("secret")
    # getting OTP provided by user
    otp = int(request.form.get("otp"))

    # verifying submitted OTP with PyOTP
    if pyotp.TOTP(secret).verify(otp):
        # inform users if OTP is valid
        flash("The TOTP 2FA token is valid", "success")
        return redirect(url_for("auth_bp.login_2fa"))
    else:
        # inform users if OTP is invalid
        flash("You have supplied an invalid 2FA token!", "danger")
        return redirect(url_for("auth_bp.login_2fa"))
