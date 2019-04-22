from flask import Blueprint
from models.ratings.rating import delete_rating
from common.utils import redirect_previous_url

rating_blueprint = Blueprint("rating", __name__)


@rating_blueprint.route("/delete/<id>")
def delete(id):
    delete_rating(id)
    return redirect_previous_url()