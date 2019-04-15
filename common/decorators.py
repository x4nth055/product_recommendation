from functools import wraps
from flask import abort, request, session, render_template

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
                # user is admin, allow
                return utils.redirect_previous_url()
        return f(*args, **kws)            
    return decorated_function