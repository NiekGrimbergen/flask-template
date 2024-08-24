from flask import session, flash
from functools import wraps

def login():
    pass

def require_login(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if session and session.get("user_id"):
            return func(*args, **kwargs)  # Call the original function
        else:
            flash("Login required")
            return login()
    return wrapper
