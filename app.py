from flask import Flask, session
from common.utils import get_unique_id
from common.database import Database
from models.users.views import user_blueprint

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
    return f"<h2>hi {session['email']}</h2>"


# register blueprints here
app.register_blueprint(user_blueprint, url_prefix="/user")