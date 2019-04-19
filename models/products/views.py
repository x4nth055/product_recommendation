import os

from flask import Blueprint, render_template, request, session, current_app as app
from flask import redirect, url_for

from common.decorators import login_required
from models.products.product import Product, get_product_by_id
from recommender.core import r

product_blueprint = Blueprint("product", __name__)


@product_blueprint.route("<product_id>")
def product(product_id):
    p = get_product_by_id(product_id)
    # similar_products = p.get_similar_products(3)
    img = os.path.basename(p.image)
    # return render_template("product/product.html", product=p, img=img, similar_products=similar_products)
    return render_template("product/product.html", product=p, img=img, similar_products=[])
    