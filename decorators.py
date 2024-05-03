from functools import wraps
from flask import abort
from flask_login import current_user

def notlogin(f):
    @wraps(f)
    def decorator_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return f(*args, **kwargs)
        else:
            return abort(404)
    return decorator_function

def adminonly(f):
    @wraps(f)
    def decorator_function(*args, **kwargs):
        if current_user.id == 1:
            return f(*args, **kwargs)
        else:
            return abort(404)
    return decorator_function