import os

from flask import Blueprint, render_template, request, session, current_app as app
from flask import redirect, url_for

from common.decorators import login_required, login_required_to_login
from models.products.product import Product, get_product_by_id, add_score_to_product
from models.ratings.rating import Rating, get_rating_by_both
from recommender.core import r
from sentiment.production import get_review_stars

product_blueprint = Blueprint("product", __name__)


@product_blueprint.route("<product_id>")
@login_required_to_login
def product(product_id):
    p = get_product_by_id(product_id)
    user_id = session['user_id']
    rating = get_rating_by_both(user_id, product_id)
    review = rating.review if rating else 0
    similar_products = p.get_similar_products(3)
    print(similar_products)
    img = os.path.basename(p.image)
    return render_template("product/product.html",
                        product=p,
                        img=img,
                        similar_products=similar_products,
                        review=review,
                        os=os)
#     return render_template("product/product.html", product=p, img=img, similar_products=[], review=review)
    

@product_blueprint.route("/upload_review", methods=['GET', 'POST'])
def upload_review():
    if request.method == "POST":
        transcription = request.form['transcription']
        review_stars = float(get_review_stars(transcription))
        user_id = session['user_id']
        product_id = request.form['product_id']
        add_score_to_product(user_id, product_id, review_stars)
        Rating(user_id=user_id, product_id=product_id, review=review_stars).save()
        return str(review_stars)