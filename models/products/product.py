import common.utils as utils
from common.database import Database

class Product:
    def __init__(self, name, price, description, image, tags, score, id=None):
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
            self.price = data['price']
            self.description = data['description']
            self.image = data['image']
            self.tags = data['tags']
            self.score = data['score']

    def __str__(self):
        return f"<Product name={self.name} price={self.price} score={self.score}>"

    def __repr__(self):
        return self.__str__()
