import numpy as np
import pandas as pd
import sqlite3
from recommender.utils import low_rank_matrix_factorization
from common.database import Database



class Recommender:
    """Class of recommending products using both methods, content-based and collaborative filtering"""

    def __init__(self, num_features=15, regularization_amount={"content-based": 1.0, "col-filter": 0.1}):
        """Recommender constructor
        :param num_features: Number of latent features to generate for users and products
        :param regularization_amount: How much regularization to apply"""
        self.num_features = num_features
        self.regularization_amount = regularization_amount
        # user ratings
        self.df = None
        # products
        self.products_df = None
        # pivot rable of ratings
        self.ratings_df = None
        # user hidden feature matrices
        self.U_content_based = None
        self.U_col_filter = None
        # product hidden feature matrices
        self.P_content_based = None
        self.P_col_filter = None
        # ratings prediction
        self.predicted_ratings_cb = None
        self.predicted_ratings_cf = None
        # recommended dataframe for collaborative filtering method
        self.recommended_df = None
        # initialization of matrices
        self.update_matrices()

    def update_matrices(self):
        self.load_user_product_matrices("content-based")
        self.load_user_product_matrices("col-filter")
        self.load_predicted_ratings("content-based")
        self.load_predicted_ratings("col-filter")

    def load_user_product_matrices(self, method):
        """Loads user ratings and products, then use matrix factorization to return the factored latent
        feature arrays (user features and product features)
        Note that user ratings and products are retrieved from `RATING` and `PRODUCT` Tables respectively
        in SQLITE3 Database in db folder."""
        # load user ratings
        self.df = pd.read_sql_query("SELECT * FROM RATING", Database.DATABASE)
        # load products
        self.products_df = pd.read_sql_query("SELECT * FROM PRODUCT", Database.DATABASE)
        # convert the running list of user ratings into a matrix
        # if 2 ratings of the same user to the same product spotted
        # use the mean
        self.ratings_df = pd.pivot_table(self.df, index="USER_ID", columns="PRODUCT_ID", aggfunc=np.mean)
        # apply matrix factorization to find the hidden features
        if method == "col-filter":
            self.U_col_filter, self.P_col_filter = low_rank_matrix_factorization(self.ratings_df.as_matrix(),
                                        num_features=self.num_features,
                                        regularization_amount=self.regularization_amount[method])
        elif method == "content-based":
            self.U_content_based, self.P_content_based = low_rank_matrix_factorization(self.ratings_df.as_matrix(),
                                        num_features=self.num_features,
                                        regularization_amount=self.regularization_amount[method])
        else:
            raise TypeError("Recommendation System type not known. (use 'col-filter' or 'content-based')")

    def load_predicted_ratings(self, method):
        """Predicts all ratings by multiplying feature matrices"""
        if method == "col-filter":
            U = self.U_col_filter
            P = self.P_col_filter
        elif method == "content-based":
            U = self.U_content_based
            P = self.P_content_based
        else:
            raise TypeError("Recommendation System type not known. (use 'col-filter' or 'content-based')")

        predicted_ratings_tmp = np.matmul(U, P).T
        if method == "col-filter":
            self.predicted_ratings_cf = pd.DataFrame(predicted_ratings_tmp,
                                            index=self.ratings_df.columns,
                                            columns=self.ratings_df.index)
        elif method == "content-based":
            self.predicted_ratings_cb = pd.DataFrame(predicted_ratings_tmp,
                                            index=self.ratings_df.columns,
                                            columns=self.ratings_df.index)
    
    def get_recommended_products(self, user_id, n=None):
        """Returns recommended products for a specific user id
            Note that This method uses collaborative filtering to recommand products to a 
            Specific user.
            :param user_id (str): the target user id
            :param n (int): the top n recommended product ids to return,
                if n=None then return all products sorted in ascending order
                by difference score. Default is None"""
        # get predicted ratings for the user ( including viewed products )
        user_ratings = self.predicted_ratings_cf[user_id].copy()
        # get viewed products
        already_viewed = self.df[self.df['USER_ID'] == user_id]
        # get recommended products by user_ratings - already_viewed
        ratings = [ rating[1] for rating in user_ratings.index.values ]
        target_ids = set(ratings) - set(already_viewed.PRODUCT_ID.unique())

        user_ratings.index = ratings
        user_ratings = user_ratings[user_ratings.index.isin(target_ids)]

        return user_ratings.sort_values(0, ascending=False)

    def find_similar_products(self, product_id, n=None):
        """Gets the similar products for a product id based on `self.P` feature matrix
            Note that this method uses content-based recommendation to recommend similar products
            :param product_id (str): the target product id
            :param n (int): the top n similar product ids to return,
                if n=None then return all products sorted in ascending order
                by difference score. Default is None"""
        # associate each product id with its features
        labeled_P = pd.DataFrame(self.P_content_based, columns=self.predicted_ratings_cb.index.levels[1])
        # get a copy of products dataframe
        edited_products = self.products_df.copy()
        # get not-rated products
        not_rated = set(edited_products['ID']) - set(labeled_P.T.index)
        # add non-rated products
        for id in not_rated:
            labeled_P[id] = 0.5
        # get the features for the product
        product_features = np.array(labeled_P[product_id])
        # subtract the current product's features from every other product's features
        difference = labeled_P.T - product_features
        # take the absolute value of that difference
        difference = np.abs(difference)
        # each product have n features, sum those n features
        # to get a total difference score for each product
        difference = np.sum(difference, axis=1)
        # sort products by difference score, from least different to most different
        difference = difference.sort_values(0)
        if n is None:
            return difference[1:]
        else:
            return difference.iloc[1:n+1]

Database.init()
r = Recommender()