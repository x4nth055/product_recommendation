from flask import Blueprint, render_template, request, session
from flask import redirect, url_for

from models.users.user import User, get_user_by_email, new_user, is_user_admin
from models.products.product import Product
import common.utils as utils
from common.decorators import login_required

user_blueprint = Blueprint("user", __name__)

@user_blueprint.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "GET":
        # first time coming to login page
        return render_template("user/login.html", error=False)
    elif request.method == "POST":
        # requested login
        email = request.form.get("email")
        password = request.form.get("password")
        user = User(email, password)
        user_data = user.valid()
        if user_data:
            # maybe add more than email later
            session['email'] = email
            user_type = user_data['type']
            if user_type == "admin":
                return redirect(url_for(".admin"))
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
            name = request.form.get("first_name") + " " + request.form.get("last_name")
            password = request.form.get("password")
            # tempo
            if email == "admin@admin.admin":
                user_type = "admin"
            else:
                user_type = "normal"
            user = User(email=email, name=name, password=password, user_type=user_type)
            user.save()
            return redirect(url_for(".login"), code=307)
        else:
            # either email not valid or already exists in db
            return render_template("user/register.html", error=True)

@user_blueprint.route("/logout")
def logout():
    del session['email']
    return utils.redirect_previous_url()

### Below is for admin ###

@user_blueprint.route("/admin")
@login_required
def admin():
    return render_template("admin/index.html")


@user_blueprint.route("/admin/tables")
@login_required
def admin_tables():
    return render_template("admin/tables.html")


@user_blueprint.route("/admin/new_product", methods=['GET', 'POST'])
@login_required
def add_product():
    if request.method == 'POST':
        name = request.form.get("name")
        description = request.form.get("description")
        price = request.form.get("price")
        tags = request.form.get("tags")
        image = utils.get_sent_image_file("img_file")
        product = Product(name=name,
                            description=description,
                            price=price,
                            tags=tags,
                            score=0,
                            image=image)
        product.save()
        message = f"Product: {name} Saved successfully"
    else:
        message = ""
    return render_template("admin/new_product.html", message=message)