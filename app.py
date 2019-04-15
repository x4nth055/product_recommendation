from flask import Flask, session, render_template, request, redirect, url_for
from threading import Thread

from common.utils import get_unique_id, convert_audio
from common.database import Database
from models.users.views import user_blueprint
import time

app = Flask(__name__)
# unique randomly generated key
app.secret_key = get_unique_id(32)

# load config from config.py
app.config.from_object("config")

# this function will run initially (i.e when program is executed)
@app.before_first_request
def init_db():
    Database.init()


@app.route("/")
def home():
    # return f"<h2>hi {session['email']}</h2>"
    return render_template("index.html")



@app.route("/upload", methods=["GET", "POST"])
def upload():
    if request.method == "POST":
        # get audio file
        name = request.form["fname"]
        split = name.split(".")
        audio = request.files['data']
        time_now = time.strftime("%Y%m%d_%H%M%S")
        tmp_file = f"audio_uploads/{time_now}_temp.{split[1]}"
        target_file = f"audio_uploads/{time_now}.{split[1]}"
        audio.save(tmp_file)
        Thread(target=convert_audio, args=(tmp_file, target_file), kwargs={"remove": True}).start()
        return "hi"
        # return str(request.form["fname"])
    else:
        print("hi2")
        return redirect(url_for("test_index"))

@app.route("/test_audio")
def test_index():
    return render_template("test_audio.html")


@app.route("/test_speech")
def test_speech():
    return render_template("speech.html")


# register blueprints here
app.register_blueprint(user_blueprint, url_prefix="/user")