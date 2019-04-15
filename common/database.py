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
        "TYPE": "VARCHAR"
    }

    PRODUCT_FIELDS = {
        "ID": "VARCHAR",
        "NAME": "VARCHAR",
        "PRICE": "INTEGER",
        "DESCRIPTION": "TEXT",
        "IMAGE": "TEXT", # absolute path of the image associated with this product
        "TAGS": "TEXT", # categories separated by '/' (e.g adventure/thiller/action) 
    }

    # all table queries need to be here
    TABLE_QUERIES = [
        get_query("USER", USER_FIELDS),
        get_query("PRODUCT", PRODUCT_FIELDS)
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


    ### Product entity ###
    @classmethod
    def save_product(cls, **kwargs):
        id = kwargs.get("id")
        name = kwargs.get("name")
        price = kwargs.get("price")
        description = kwargs.get("description")
        image = kwargs.get("image")
        tags = kwargs.get("tags")
        parameters = (id, name, price, description, image, tags)
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
        cursor = cls.DATABASE.execute("SELECT * FROM PRODUCT WHERE TAGS LIKE ?", (f"%{tag}%",))
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
        
    