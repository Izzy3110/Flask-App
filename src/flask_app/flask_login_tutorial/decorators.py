from functools import wraps
from flask import request, jsonify
from flask_login_tutorial.models import User
from flask_login import current_user, login_user


def login_required_ext(f):
    """ basic auth for api and endpoints """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = None
        auth = request.authorization
        if auth is not None:
            user = User.query.filter_by(email=auth.username).first()
            x = getattr(user, 'check_email_password_auth', None)
            if x is not None:
                user = user.check_email_password_auth(auth.username, auth.password)
            
        if not auth or user is None:
            return jsonify({'message': 'Authentication required'}), 401
        
        if not current_user.is_authenticated:
            login_user(user)
        else:
            print("already in - doing nothing")
        return f(*args, **kwargs)
    return decorated_function
