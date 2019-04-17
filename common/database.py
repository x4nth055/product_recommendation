import sqlite3
from common.utils import get_query
from collections import defaultdict

class Database:
    URL = "db/first_db.sqlite3"
    DATABASE = None

    #### Initializing tables here ####

    # all models' (i.e tables') fields should be listed here
    USER_FIELDS = {
        "ID": "VARCHAR",
        "NAME": "VARCHAR",
        "EMAIL": "VARCHAR",
        "PASSWORD": "VARCHAR",
        "TYPE": "VARCHAR",
        # "LIKED_TAGS": "TEXT" # what category user likes, format like this: adventure=5,action=2,drama=1 
    }

    PRODUCT_FIELDS = {
        "ID": "VARCHAR",
        "NAME": "VARCHAR",
        "PRICE": "INTEGER",
        "DESCRIPTION": "TEXT",
        "IMAGE": "TEXT", # absolute path of the image associated with this product
        "TAGS": "TEXT", # categories separated by ',' (e.g adventure,action,drama) 
        "SCORE": "REAL", # the score of product
        # Score is increment by:
        #   - +2 for very good sentiment ( 5 stars )
        #   - +1 for good sentiment ( 4 stars )
        #   - +0 for neutral sentiment ( 3 stars )    
        #   - -1 for bad sentiment ( 2 stars )
        #   - -2 for very bad sentiment ( 1 star )
    }

    RATING_FIELDS = {
        "USER_ID": "VARCHAR",
        "PRODUCT_ID": "VARCHAR",
        "REVIEW": "REAL" # Between 1 and 5
    }

    # all table queries need to be added here
    TABLE_QUERIES = [
        get_query("USER", USER_FIELDS),
        get_query("PRODUCT", PRODUCT_FIELDS),
        get_query("RATING", RATING_FIELDS)
    ]
        
    @classmethod
    def init(cls):
        cls.DATABASE = sqlite3.connect(cls.URL, check_same_thread=False)
        # create tables
        for query in cls.TABLE_QUERIES:
            cls.DATABASE.execute(query)


    ### User Entity ###

    @classmethod
    def save_user(cls, **kwargs):
        """Saves user to the database"""
        id = kwargs.get("id")
        name = kwargs.get("name")
        email = kwargs.get("email")
        password = kwargs.get("password")
        user_type = kwargs.get("type")
        # using the secure Python DB-API 2.0’s parameter substitution 
        # for preventing SQL Injection
        parameters = (id, name, email, password, user_type)
        cls.DATABASE.execute("INSERT INTO USER VALUES (?, ?, ?, ?, ?)", parameters)
        cls.DATABASE.commit()

    @classmethod
    def _get_user_by(cls, key, value):
        cursor = cls.DATABASE.execute(f"SELECT * FROM USER WHERE {key}=?", (value,))
        returned_data = cursor.fetchone()
        if returned_data is None:
            return None
        data = {}
        for i, field in enumerate(cls.USER_FIELDS):
            data[field.lower()] = returned_data[i]
        return data

    @classmethod
    def get_user_by_id(cls, id):
        """Get user data from its id.
            The returned dict is in the format:
            {'ID': id, 'NAME': name, 'EMAIL': email, 'PASSWORD': password}
            Returns None when user is not found
                """
        return cls._get_user_by("ID", id)

    @classmethod
    def get_user_by_email(cls, email):
        """Get user data from its email, more info at `get_user_by_id`"""
        return cls._get_user_by("EMAIL", email)

    @classmethod
    def get_user_id_by_email(cls, email):
        """Gets user id by email"""
        return cls.get_user_by_email(email)['id']

    # @classmethod
    # def get_user_liked_tags_by_id(cls, id):
    #     """Get user liked tags by its ID
    #         Format is
    #             {   'adventure': 3,
    #                 'action': 2,
    #                 'comedy': 1     }"""
    #     cursor = cls.DATABASE.execute("SELECT LIKED_TAGS FROM USER WHERE ID=?", (id,))
    #     returned_data = cursor.fetchone()
    #     if not returned_data:
    #         return None
    #     data = returned_data[0].split(",")
    #     # ['adventure=3', 'action:2', 'comedy:5']
    #     returned_data = {}
    #     for item in data:
    #         category, score = item.split("=")
    #         returned_data[category] = float(score)
    #     return returned_data

    # @classmethod
    # def get_user_liked_tags_by_email(cls, email):
    #     id = cls.get_user_id_by_email(email)
    #     return cls.get_user_liked_tags_by_id(id)

    # @classmethod
    # def add_tags_to_user_by_id(cls, id, tags, sent_score):
    #     """Add tags to user, tags is a dict documented in `get_user_liked_tags_by_id`
    #         Note that if a user already have a tag in `tags`, its score is just recalculated
    #         Params:
    #             id (str): The id of user
    #             tags (dict): Tags to be added to the user
    #             sent_score (float): sentiment score to be multiplied by each tag's score"""
    #     new_tags = defaultdict(float, cls.get_user_liked_tags_by_id(id))
    #     for category, score in tags.items():
    #         new_tags[category] += score * sent_score
    #     cls.set_user_tags(id, new_tags)
        
    # @classmethod
    # def set_user_tags(cls, id, tags):
    #     """Updates the `tags` of target user by `id`"""
    #     tags_text = ""
    #     for category, score in tags.items():
    #         tags_text += f"{category}:{score:.2f},"
    #     tags_text = tags_text.rstrip(",")
    #     cursor = cls.DATABASE.execute("UPDATE USER SET LIKED_TAGS=? WHERE ID=?", (tags_text, id))
    #     cursor.connection.commit()
    #     return True


    ### Product entity ###


    @classmethod
    def save_product(cls, **kwargs):
        id = kwargs.get("id")
        name = kwargs.get("name")
        price = kwargs.get("price")
        description = kwargs.get("description")
        image = kwargs.get("image")
        tags = kwargs.get("tags")
        score = kwargs.get("score")
        parameters = (id, name, price, description, image, tags, score)
        cls.DATABASE.execute("INSERT INTO PRODUCT VALUES (?, ?, ?, ?, ?, ?)", parameters)
        cls.DATABASE.commit()

    @classmethod
    def _get_product_by(cls, key, value):
        cursor = cls.DATABASE.execute(f"SELECT * FROM PRODUCT WHERE {key}=?", (value,))
        returned_data = cursor.fetchone()
        if returned_data is None:
            return None
        data = {}
        for i, field in enumerate(cls.PRODUCT_FIELDS):
            data[field.lower()] = returned_data[i]
        return data

    @classmethod
    def get_product_by_id(cls, id):
        return cls._get_product_by("ID", id)

    @classmethod
    def get_products_by_tag(cls, tag):
        """Returns all products tagged by `tag`
        Format is a list of dicts"""
        cursor = cls.DATABASE.execute("SELECT * FROM PRODUCT WHERE TAGS LIKE ? ORDER BY SCORE DESC", (f"%{tag}%",))
        returned_data = cursor.fetchall()
        # [(1, 'test1', 'test1'), (2, 'test2', 'test2')]
        if not returned_data:
            return None
        data = []
        for item in returned_data:
            d = {}
            for i, field in enumerate(cls.PRODUCT_FIELDS):
                d[field] = item[i]
            data.append(d)
        return data

    @classmethod
    def get_tags_by_product_id(cls, id):
        """Returns a list of tags for a product by id"""
        cursor = cls.DATABASE.execute("SELECT TAGS FROM PRODUCT WHERE ID=?", (id,))
        returned_data = cursor.fetchone()[0]
        if not returned_data:
            return None
        return returned_data.split(",")
        # returned_data = {}
        # for category, score in data.split("="):
        #     returned_data[category] = score
        # return returned_data

    @classmethod
    def product_increment_score(cls, product_id, rating):
        """Increments `SCORE` attribute by `rating`"""
        assert isinstance(rating, float) or isinstance(rating, int)
        cursor = cls.DATABASE.execute("UPDATE PRODUCT WHERE ID=? SET SCORE = SCORE+?", (product_id, rating))
        cursor.connection.commit()
        return True


    ### Rating entity ###

    @classmethod
    def add_rating(cls, user_id, product_id, review):
        cls.DATABASE.execute("INSERT INTO RATING VALUES ( ?, ?, ? )", (user_id, product_id, review))
        cls.DATABASE.commit()
        return True

    @classmethod
    def _get_ratings_by(cls, key, value):
        cursor = cls.DATABASE.execute(f"SELECT * FROM RATING WHERE {key}=?", (value,))
        returned_data = cursor.fetchall()
        if not returned_data:
            return None
        data = []
        for item in returned_data:
            d = {}
            for i, field in enumerate(cls.RATING_FIELDS):
                d[field] = item[i]
            data.append(d)
        return data

    @classmethod
    def get_ratings_by_user_id(cls, user_id):
        return cls._get_ratings_by("USER_ID", user_id)

    @classmethod
    def get_ratings_by_user_email(cls, email):
        user_id = cls.get_user_id_by_email(email)
        return cls.get_ratings_by_user_id(user_id)

    @classmethod
    def get_ratings_by_product_id(cls, product_id):
        return cls._get_ratings_by("PRODUCT_ID", product_id)

    

    ### UTILITIES ###

    # @classmethod
    # def update_user_tags_by_id(cls, product_id, user_id, sentiment_score):
    #     """This function does 3 tasks:
    #         - get all product tags for `product_id`
    #         - add those tags to the user by `user_id`
    #         - increment SCORE of product by `sentiment_score`"""
    #     product_tags = cls.get_tags_by_product_id(product_id)
    #     cls.add_tags_to_user_by_id(user_id, product_tags, sentiment_score)
    #     cls.product_increment_score(product_id, sentiment_score)