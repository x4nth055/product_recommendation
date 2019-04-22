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
    def delete_user(cls, id):
        cls.DATABASE.execute("DELETE FROM USER WHERE ID=?", (id,))
        cls.DATABASE.commit()
        return True

    @classmethod
    def edit_user(cls, id, **kwargs):
        query = "UPDATE USER SET "
        parameters = []
        for field, value in kwargs.items():
            if field not in cls.USER_FIELDS:
                raise TypeError("Table Column not found:" + field)
            query += f"{field} = ?"
            parameters.append(value)
        query += " WHERE ID=?"
        parameters.append(id)
        cls.DATABASE.execute(query, parameters)
        cls.DATABASE.commit()
        return True

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

    @classmethod
    def get_all_users(cls, formalize=True):
        cursor = cls.DATABASE.execute("SELECT * FROM USER")
        returned_data = cursor.fetchall()
        if not formalize:
            return returned_data
        data = []
        for item in returned_data:
            d = {}
            for i, field in enumerate(cls.USER_FIELDS):
                d[field.lower()] = item[i]
            data.append(d)
        return data

    ### Product entity ###

    @classmethod
    def get_all_products(cls, formalize=True):
        cursor = cls.DATABASE.execute("SELECT * FROM PRODUCT ORDER BY SCORE DESC")
        returned_data = cursor.fetchall()
        if not returned_data:
            return None
        if not formalize:
            return returned_data
        data = []
        for item in returned_data:
            d = {}
            for i, field in enumerate(cls.PRODUCT_FIELDS):
                d[field.lower()] = item[i]
            data.append(d)
        return data

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
        cls.DATABASE.execute("INSERT INTO PRODUCT VALUES (?, ?, ?, ?, ?, ?, ?)", parameters)
        cls.DATABASE.commit()

    @classmethod
    def delete_product(cls, id):
        cls.DATABASE.execute("DELETE FROM PRODUCT WHERE ID=?", (id,))
        cls.DATABASE.commit()
        return True

    @classmethod
    def edit_product(cls, id, **kwargs):
        query = "UPDATE PRODUCT SET "
        paramaters = []
        for field, value in kwargs.items():
            if field not in cls.PRODUCT_FIELDS:
                raise TypeError("Table column not found:" + field)
            query += f"{field} = ?"
            paramaters.append(value)
        query += " WHERE ID=?"
        paramaters.append(id)
        cls.DATABASE.execute(query, paramaters)
        cls.DATABASE.commit()
        return True

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
                d[field.lower()] = item[i]
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
    def product_increment_score(cls, user_id, product_id, rating):
        """Increments `SCORE` attribute by `rating`"""
        assert isinstance(rating, float) or isinstance(rating, int)
        if not cls.get_ratings_by_both(user_id=user_id, product_id=product_id):
            cursor = cls.DATABASE.execute("UPDATE PRODUCT SET SCORE = SCORE+? WHERE ID=? ", (rating, product_id))
            cursor.connection.commit()
            return True
        else:
            return False

    @classmethod
    def get_product_tags(cls):
        data = cls.get_all_products()
        return sorted({ d['tags'] for d in data })


    ### Rating entity ###

    @classmethod
    def add_rating(cls, user_id, product_id, review):
        cls.DATABASE.execute("INSERT INTO RATING VALUES ( ?, ?, ? )", (user_id, product_id, review))
        cls.DATABASE.commit()
        return True

    @classmethod
    def _delete_rating_by(cls, key, id):
        cls.DATABASE.execute(f"DELETE FROM RATING WHERE {key}=?", (id,))
        cls.DATABASE.commit()
        return True

    @classmethod
    def delete_rating_by_user_id(cls, user_id):
        return cls._delete_rating_by("USER_ID", user_id)

    @classmethod
    def delete_rating_by_product_id(cls, product_id):
        return cls._delete_rating_by("PRODUCT_ID", product_id)

    @classmethod
    def delete_rating_by_both(cls, user_id, product_id):
        cls.DATABASE.execute(f"DELETE FROM RATING WHERE USER_ID=? AND PRODUCT_ID=?", (user_id, product_id))
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
                d[field.lower()] = item[i]
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

    @classmethod
    def get_ratings_by_both(cls, user_id, product_id):
        cursor = cls.DATABASE.execute(f"SELECT * FROM RATING WHERE USER_ID=? AND PRODUCT_ID=?", (user_id, product_id))
        returned_data = cursor.fetchall()
        if not returned_data:
            return None
        data = []
        for item in returned_data:
            d = {}
            for i, field in enumerate(cls.RATING_FIELDS):
                d[field.lower()] = item[i]
            data.append(d)
        return data

    @classmethod
    def get_all_ratings(cls, formalize=True):
        cursor = cls.DATABASE.execute("SELECT * FROM RATING")
        returned_data = cursor.fetchall()
        if not formalize:
            return returned_data
        data = []
        for item in returned_data:
            d = {}
            for i, field in enumerate(cls.RATING_FIELDS):
                d[field.lower()] = item[i]
            data.append(d)
        return data

    @classmethod
    def get_number_of_ratings_by_user_id(cls, user_id):
        data = cls.get_ratings_by_user_id(user_id)
        if data is None:
            return 0
        else:
            return len(data)

    

    ### UTILITIES ###

    @classmethod
    def get_user_ratings_joined_by_products(cls, user_id):
        cursor = cls.DATABASE.execute("""SELECT RATING.PRODUCT_ID,
                                        USER.NAME, PRODUCT.NAME, PRODUCT.IMAGE, RATING.REVIEW
                                        FROM USER, PRODUCT, RATING
                                        WHERE RATING.USER_ID = USER.ID
                                        AND RATING.PRODUCT_ID = PRODUCT.ID
                                        AND USER.ID = ?""", (user_id,))
        returned_data = cursor.fetchall()
        return [ field[0] for field in cursor.description ], returned_data
        