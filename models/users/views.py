from flask import Blueprint, render_template, request, session
from flask import redirect, url_for

from models.users.user import User, get_user_by_email, new_user
import common.utils as utils

user_blueprint = Blueprint("user", __name__)

@user_blueprint.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "GET":
        # first time coming to login page
        return render_template("user/login.html", error=False)
    elif request.method == "POST":
        # requested login
        email = request.form["email"]
        password = request.form["password"]
        user = User(email, password)
        user_data = user.valid()
        if user_data:
            # maybe add more than email later
            session['email'] = email
            return redirect("/")
        else:
            # no user with this combo email:pw
            return render_template("user/login.html", error=True)


@user_blueprint.route("/new", methods=["POST", "GET"])
def register():
    if request.method == "GET":
        return render_template("user/register.html", error=False)
    elif request.method == "POST":
        email = request.form.get('email')
        if utils.email_valid(email) and not get_user_by_email(email):
            # login with same method (POST) and same values
            name = request.form.get("name")
            password = request.form.get("password")
            user = User(email=email, name=name, password=password)
            user.save()
            return redirect(url_for(".login"), code=307)
        else:
            # either email not valid or already exists in db
            return render_template("user/register.html", error=True)


@user_blueprint.route("/logout")
def logout():
    del session['email']
    return utils.redirect_previous_url()