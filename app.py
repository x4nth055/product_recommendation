import os
import random
from flask import Flask, session, render_template, request, redirect, url_for, send_from_directory
from threading import Thread

from common.utils import get_unique_id, convert_audio, redirect_previous_url, get_sent_audio_file, remove_starting_digits
from common.database import Database
from models.users.views import user_blueprint
from models.users.user import get_user_by_id
from models.products.views import product_blueprint
from models.ratings.views import rating_blueprint
from models.ratings.rating import get_rating_by_both
from models.products.product import get_all_products, get_product_tags, get_products_by_tag, get_products_by_search_query
from emotion.text.test import get_emotions as get_emotion_by_text

# Recommender System
from recommender.core import r

# Speech Recognition Models
# from asr.keras.test import get_predictions as get_transcription_keras
import time

app = Flask(__name__)
# unique randomly generated key
app.secret_key = get_unique_id(32)

# load config from config.py
app.config.from_object("config")
app.config['UPLOAD_FOLDER'] = os.path.join('static', 'img', 'products')

# this function will run initially (i.e when the app is executed)
@app.before_first_request
def init_db():
    Database.init()


@app.route("/")
def home():
    products = get_all_products()
    sorted_products = products.copy()
    random.shuffle(products)
    if session.get("user_id"):
        user_id = session.get("user_id")
        ratings = [ get_rating_by_both(user_id, p.id) for p in products ]
    else:
        ratings = [None] * len(products)
    tags = get_product_tags()
    return render_template("index.html",
                            products=products,
                            ratings=ratings,
                            tags=tags,
                            chosen_products=sorted_products[:5],
                            os=os,
                            len=len,
                            range=range,
                            enumerate=enumerate,
                            zip=zip,
                            remove_starting_digits=remove_starting_digits)
    
@app.route("/recommended")
def recommended():
    user_id = session.get("user_id")
    user = get_user_by_id(user_id)
    products = user.get_recommended_products()
    ratings = [ get_rating_by_both(user_id, p.id) for p in products ]
    tags = get_product_tags()
    return render_template("index.html",
                            products=products,
                            ratings=ratings,
                            tags=tags,
                            chosen_products=products[:5],
                            os=os,
                            zip=zip,
                            len=len,
                            range=range,
                            enumerate=enumerate,
                            remove_starting_digits=remove_starting_digits)

@app.route("/categories/<category>")
def categories(category):
    products = get_products_by_tag(category)
    tags = get_product_tags()
    if session.get("user_id"):
        user_id = session.get("user_id")
        ratings = [ get_rating_by_both(user_id, p.id) for p in products ]
    else:
        ratings = [None] * len(products)
    return render_template("index.html",
                            products=products,
                            ratings=ratings,
                            tags=tags,
                            category=category,
                            chosen_products=products[:5],
                            os=os,
                            zip=zip,
                            len=len,
                            range=range,
                            enumerate=enumerate,
                            remove_starting_digits=remove_starting_digits)


@app.route("/search", methods=["GET"])
def search():
    query = request.args.get("q")
    products = get_products_by_search_query(query)
    if session.get("user_id"):
        user_id = session.get("user_id")
        ratings = [ get_rating_by_both(user_id, p.id) for p in products ]
    else:
        ratings = [None] * len(products)
    tags = get_product_tags()
    return render_template("index.html",
                            products=products,
                            ratings=ratings,
                            tags=tags,
                            chosen_products=products[:5],
                            os=os,
                            zip=zip,
                            len=len,
                            range=range,
                            enumerate=enumerate,
                            remove_starting_digits=remove_starting_digits)


@app.route("/upload", methods=["GET", "POST"])
def upload():
    if request.method == "POST":
        # get audio file from AJAX request
        get_sent_audio_file("fname")
        return True
    else:
        return redirect(url_for("test_upload_audio"))


@app.route("/test_speech")
def test_speech():
    return render_template("speech.html")


# register blueprints here
app.register_blueprint(user_blueprint, url_prefix="/user")
app.register_blueprint(product_blueprint, url_prefix="/product")
app.register_blueprint(rating_blueprint, url_prefix="/rating")