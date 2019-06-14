import os

from flask import Blueprint, render_template, request, session, current_app as app
from flask import redirect, url_for

from common.decorators import login_required, login_required_to_login
from models.products.product import Product, get_product_by_id, add_score_to_product, delete_product
from models.ratings.rating import Rating, get_rating_by_both
from common.utils import redirect_previous_url, remove_starting_digits, get_sent_audio_file
from recommender.core import r
from emotion.speech.production import get_review_stars, get_emotion


product_blueprint = Blueprint("product", __name__)


@product_blueprint.route("<product_id>")
@login_required_to_login
def product(product_id):
    p = get_product_by_id(product_id)
    user_id = session['user_id']
    rating = get_rating_by_both(user_id, product_id)
    review = rating.review if rating else 0
    emotion = rating.emotion if rating else None
    similar_products = p.get_similar_products(9)
    similar_ratings = [ get_rating_by_both(user_id, p.id) for p in similar_products ]
    print(similar_products)
    img = os.path.basename(p.image)
    return render_template("product/product.html",
                        product=p,
                        img=img,
                        similar_products=similar_products,
                        similar_ratings=similar_ratings,
                        review=review,
                        emotion=emotion,
                        os=os,
                        zip=zip,
                        remove_starting_digits=remove_starting_digits)
    

@product_blueprint.route("/upload_review", methods=['GET', 'POST'])
def upload_review():
    if request.method == "POST":
        # # get transcription from the SpeechRecognition MDN API
        # transcription = request.form.get('transcription')
        # if transcription is None:
        #     # offline, audio file is sent instead
        #     audio_file = get_sent_audio_file("fname")
        #     transcription = get_transcription(audio_file)
        #     print("Transcription:", transcription)
        # get the audio file that is sent from product.html
        audio_file = get_sent_audio_file("fname")
        # retrieve review stars from text
        review_stars = float(get_review_stars(audio_file))
        # retrieve emotion from text
        emotion = get_emotion(audio_file)
        # get the user id from the session ( logged in )
        user_id = session['user_id']
        # get the product id from the form
        product_id = request.form['product_id']
        # add score to the corresponding product
        add_score_to_product(user_id, product_id, review_stars)
        # save the new review
        Rating(user_id=user_id, product_id=product_id, review=review_stars, emotion=emotion).save()
        # update recommender system matrices
        r.update_matrices()
        return str(review_stars) + "|" + emotion


@product_blueprint.route("/delete/<id>")
def delete(id):
    delete_product(id)
    return redirect_previous_url()