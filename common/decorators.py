from functools import wraps
from flask import abort, request, session, render_template, url_for, redirect

import common.utils as utils
from models.users.user import is_user_admin


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kws):
        email = session.get("email")
        if email is None:
            # if not logged in, get back from where you came!
            return utils.redirect_previous_url()
        else:
            if not is_user_admin(email):
                # user is not admin, deny
                return utils.redirect_previous_url()
        return f(*args, **kws)            
    return decorated_function

def login_required_to_login(f):
    @wraps(f)
    def decorated_function(*args, **kws):
        email = session.get("email")
        if email is None:
            return redirect(url_for("user.login"))
        else:
            return f(*args, **kws)
    return decorated_function