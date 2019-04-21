import common.utils as utils
from common.database import Database
from recommender.core import r

class Product:
    def __init__(self, name=None, price=None, description=None, image=None, tags=None, score=None, id=None):
        self.name = name
        self.price = price
        self.description = description
        self.image = image
        self.tags = tags
        self.score = score
        if id is None:
            self.id = utils.get_unique_id(12)
        else:
            self.id = id

    def save(self):
        Database.save_product(**self.json())

    def exists(self):
        data = Database.get_product_by_id(self.id)
        return data

    def json(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "price": self.price,
            "image": self.image,
            "tags": self.tags,
            "score": self.score
        }

    def load(self):
        """Loads the correct data from database by `self.id` if it does exist"""
        exists = self.exists()
        if exists:
            data = exists
            self.name = data['name']
            self.price = float(data['price'])
            self.description = data['description']
            self.image = data['image']
            self.tags = data['tags']
            self.score = data['score']

    def get_similar_products(self, n):
        similar_products = r.find_similar_products(self.id, n=n)
        print("similar products:", similar_products)
        return [ get_product_by_id(id) for id in similar_products.index.values ]

    def __str__(self):
        return f"<Product name={self.name} price={self.price} score={self.score}>"

    def __repr__(self):
        return self.__str__()


def get_product_by_id(id):
    p = Product(id=id)
    p.load()
    return p


def get_all_products():
    products = Database.get_all_products()
    return [ Product(**product) for product in products ]

def get_product_tags():
    return Database.get_product_tags()

def get_products_by_tag(tag):
    products = Database.get_products_by_tag(tag)
    if products:
        return [ Product(**product) for product in products ]
    else:
        return []

def add_score_to_product(user_id, product_id, score):
    Database.product_increment_score(user_id, product_id, score-3)