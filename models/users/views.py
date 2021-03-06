from flask import Blueprint, render_template, request, session
from flask import redirect, url_for

from models.users.user import User, get_user_by_email, new_user, is_user_admin, get_user_fields, get_all_users, delete_user, edit_user, get_user_by_id
from models.users.user import get_user_ratings_joined_with_products, get_number_of_users
from models.products.product import Product, get_all_products, get_product_fields, get_number_of_products
from models.products.product import get_number_of_rated_products
from models.ratings.rating import get_all_ratings, get_rating_fields, get_number_of_ratings
import common.utils as utils
from common.decorators import login_required

import os

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
            session['user_id'] = user_data['id']
            session['name'] = user_data['name']
            user_type = user_data['type']
            if user_type == "admin":
                return redirect(url_for(".admin"))
            return redirect("/")
            # return utils.redirect_previous_url()
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
            user = User(email=email, name=name, password=password, type=user_type)
            user.save()
            return redirect(url_for(".login"), code=307)
        else:
            # either email not valid or already exists in db
            return render_template("user/register.html", error=True)


@user_blueprint.route("/profile")
def profile():
    user_id = session.get("user_id")
    if user_id is None:
        return utils.redirect_previous_url()
    user = get_user_by_id(user_id)
    fields, elements = get_user_ratings_joined_with_products(user_id)
    return render_template("user/profile.html",
                            user=user,
                            fields=fields,
                            elements=elements,
                            os=os,
                            len=len,
                            str=str)


@user_blueprint.route("/logout")
def logout():
    if session.get("user_id"):
        # logged in
        del session['email']
        del session['user_id']
        del session['name']
    return redirect(url_for('home'))

@user_blueprint.route("/delete/<id>")
@login_required
def delete(id):
    delete_user(id)
    return utils.redirect_previous_url()

### Below is for admin ###

@user_blueprint.route("/admin")
@login_required
def admin():
    n_products = get_number_of_products()
    n_users    = get_number_of_users()
    n_ratings  = get_number_of_ratings()
    n_rated_products = get_number_of_rated_products()
    return render_template("admin/index.html",
                            n_ratings=n_ratings,
                            n_products=n_products,
                            n_users=n_users,
                            n_rated_products=n_rated_products,
                            round=round)


@user_blueprint.route("/admin/users")
@login_required
def users():
    name = "User"
    description = "The table of data of users"
    headers = get_user_fields()
    items  = get_all_users(formalize=False)
    return render_template("admin/tables.html",
                            name=name,
                            description=description,
                            headers=headers,
                            items=items,
                            len=len,
                            str=str,
                            os=os)

@user_blueprint.route("/admin/products")
@login_required
def products():
    name = "Product"
    description = "The table of data of all available products"
    headers = get_product_fields()
    items = get_all_products(formalize=False)
    return render_template("admin/tables.html",
                            name=name,
                            description=description,
                            headers=headers,
                            items=items,
                            len=len,
                            str=str,
                            os=os)


@user_blueprint.route("/admin/ratings")
@login_required
def ratings():
    name = "Rating"
    description = "The table of all ratings done by users to products"
    headers = get_rating_fields()
    items = get_all_ratings(formalize=False)
    return render_template("admin/tables.html",
                            name=name,
                            description=description,
                            headers=headers,
                            items=items,
                            len=len,
                            str=str,
                            os=os)


@user_blueprint.route("/admin/new_product", methods=['GET', 'POST'])
@login_required
def add_product():
    optgroups = {
        "Fast food": ["pizza", "hamburger", "sandwich"],
        "Drinks": ["shakes_smoothies", "cocktails", "soda", "coffee"],
        "Pasteries & bakery food": ["pastry", "bakery"],
        "Sea Food": ["sushi", "fish_dish"],
        "Pasta": ["italian_pasta", "noodles"],
        "Dessert & Salad": ["fruit_salad", "ice_cream", "veggie_salad", "fruits"],
        "Dishes": ["middle_east_food", "asian_dishes"],
        "Meals": ["barbeque", "roast_food"]
    }
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
    return render_template("admin/new_product.html", message=message, optgroups=optgroups)


