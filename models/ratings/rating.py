from common.database import Database


class Rating:
    def __init__(self, user_id, product_id, review, emotion=None):
        self.user_id = user_id
        self.product_id = product_id
        self.review = review
        self.emotion = emotion

    def json(self):
        return {
            "user_id": self.user_id,
            "product_id": self.product_id,
            "review": self.review,
            "emotion": self.emotion
        }

    def save(self):
        Database.add_rating(**self.json())
        return True


def get_ratings_by_user_id(user_id):
    return Rating(**Database.get_ratings_by_user_id(user_id))

def get_ratings_by_product_id(product_id):
    return Rating(**Database.get_ratings_by_product_id(product_id))

def get_rating_by_both(user_id, product_id, fn=lambda x: sum(x) / len(x)):
    """Get user ratings for a specific product, fn is a function executed
    to the rating when more than a review is found"""
    ratings = Database.get_ratings_by_both(user_id, product_id)
    if ratings:
        if len(ratings) == 1:
            return Rating(**ratings[0])
        else:
            reviews = []
            emotions = []
            for rating in ratings:
                reviews.append(rating['review'])
                emotions.append(rating['emotion'])
            # picking the last emotion
            return Rating(user_id=user_id, product_id=product_id, review=fn(reviews), emotion=emotions[-1])

def get_all_ratings(formalize=True):
    ratings = Database.get_all_ratings(formalize=formalize)
    if not formalize:
        return ratings
    return [ Rating(**r) for r in ratings ]

def get_rating_fields():
    return [ field.capitalize() for field in Database.RATING_FIELDS ]

def delete_rating(id):
    user_id, product_id = id.split("*")
    return Database.delete_rating_by_both(user_id=user_id, product_id=product_id)

def get_number_of_ratings():
    return Database.get_number_of_ratings()
