import os
import random
from flask import Flask, session, render_template, request, redirect, url_for, send_from_directory
from threading import Thread

from common.utils import get_unique_id, convert_audio, redirect_previous_url, get_sent_audio_file
from common.database import Database
from models.users.views import user_blueprint
from models.products.views import product_blueprint
from models.products.product import get_all_products, get_product_tags, get_products_by_tag

# Recommender System
from recommender.core import r

# Speech Recognition Models
# HMM
# from asr.pocketsphinx.production import get_transcription as get_transcription_hmm
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
    # return f"<h2>hi {session['email']}</h2>"
    products = get_all_products()
    sorted_products = products.copy()
    random.shuffle(products)
    tags = get_product_tags()
    return render_template("index.html",
                            products=products,
                            tags=tags,
                            chosen_products=sorted_products[:5],
                            os=os,
                            len=len,
                            range=range,
                            enumerate=enumerate)
    

@app.route("/categories/<category>")
def categories(category):
    products = get_products_by_tag(category)
    tags = get_product_tags()
    return render_template("index.html",
                            products=products,
                            tags=tags,
                            category=category,
                            chosen_products=products[:5],
                            os=os,
                            len=len,
                            range=range,
                            enumerate=enumerate)


@app.route("/upload", methods=["GET", "POST"])
def upload():
    if request.method == "POST":
        # get audio file from AJAX request
        get_sent_file("fname")
        return True
    else:
        return redirect(url_for("test_upload_audio"))


@app.route("/test_hmm", methods=["GET", "POST"])
def test_hmm():
    if request.method == "POST":
        target_file = get_sent_audio_file("fname")
        return get_transcription_hmm(target_file)
    else:
        return render_template("speech_sphinx.html")


# @app.route("/test_keras", methods=["GET", "POST"])
# def test_keras():
#     if request.method == "POST":
#         target_file = get_sent_file_audio_file("fname")
#         return get_transcription_keras(target_file)
#     else:
#         return render_template("speech_keras.html")


@app.route("/test_upload_audio")
def test_upload_audio():
    return render_template("test_audio.html")


@app.route("/test_speech")
def test_speech():
    return render_template("speech.html")



# register blueprints here
app.register_blueprint(user_blueprint, url_prefix="/user")
app.register_blueprint(product_blueprint, url_prefix="/product")