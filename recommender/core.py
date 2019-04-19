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

    def load_user_product_matrices(self, method):
        """Loads user ratings and products, then use matrix factorization to return the factored latent
        feature arrays (user features and product features)
        Note that user ratings and products are retrieved from `RATING` and `PRODUCT` Tables respectively
        in SQLITE3 Database in db folder."""
        # load user ratings
        self.df = pd.read_sql_query("SELECT * FROM RATING", Database.DATABASE)
        # load products
        self.products_df = pd.read_sql_query("SELECT ID FROM PRODUCT", Database.DATABASE)
        # convert the running list of user ratings into a matrix
        # if 2 ratings of the same user to the same product spotted
        # use the mean
        self.ratings_df = pd.pivot_table(self.df, index="user_id", columns="product_id", aggfunc=np.mean)
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
        elif method == "content-based":
            U = self.U_content_based
        else:
            raise TypeError("Recommendation System type not known. (use 'col-filter' or 'content-based')")
        if not U:
            # in other words, self.load_user_product_matrices isn't called yet.
            # load the matrices then
            self.load_user_product_matrices(method)

        # reload vars
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
        if self.predicted_ratings_cf is None:
            self.load_predicted_ratings("col-filter")
        # get predicted ratings for the user ( including viewed products )
        user_ratings = self.predicted_ratings_cf[user_id]
        # get viewed products
        already_viewed = self.df[self.df['user_id'] == user_id]['product_id']
        # get recommended products by user_ratings - already_viewed
        edited_products = self.products_df.copy()
        edited_products['rating'] = np.array(user_ratings)
        recommended_df = edited_products[edited_products.index.isin(already_viewed) == False]
        recommended_df = recommended_df.sort_values(["rating"], ascending=False)
        return recommended_df

    def find_similar_products(self, product_id, n=None):
        """Gets the similar products for a product id based on `self.P` feature matrix
            Note that this method uses content-based recommendation to recommend similar products
            :param product_id (str): the target product id
            :param n (int): the top n similar product ids to return,
                if n=None then return all products sorted in ascending order
                by difference score. Default is None"""
        if self.P_content_based is None:
            self.load_predicted_ratings("content-based")
        # associate each product id with its features
        labeled_P = pd.DataFrame(self.P_content_based, columns=self.predicted_ratings_cb.index.levels[1])
        # get the features for the product
        product_features = np.array(labeled_P[product_id])
        # subtract the current product's features from every other product's features
        difference = np.transpose(self.P_content_based) - product_features
        # take the absolute value of that difference
        difference = np.abs(difference)
        # each product have n features, sum those n features
        # to get a total difference score for each product
        difference = np.sum(difference, axis=1)
        # get a copy of products dataframe
        edited_products = self.products_df.copy()
        # add new column to the product list with difference score of each product
        edited_products['DIFFERENCE_SCORE'] = difference
        # sort products by difference score, from least different to most different
        edited_products = edited_products.sort_values("DIFFERENCE_SCORE")
        if n is None:
            return edited_products
        else:
            return edited_products.iloc[:n]


r = Recommender()