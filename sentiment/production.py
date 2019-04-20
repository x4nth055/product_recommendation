# to use CPU
import os
# os.environ["CUDA_DEVICE_ORDER"] = "PCI_BUS_ID"   # see issue #152
# os.environ["CUDA_VISIBLE_DEVICES"] = "-1"

# import tensorflow as tf
# graph = tf.get_default_graph() 

# config = tf.ConfigProto(intra_op_parallelism_threads=5,
#                         inter_op_parallelism_threads=5, 
#                         allow_soft_placement=True,
#                         device_count = {'CPU' : 1,
#                                         'GPU' : 0}
#                        )

from keras.models import Sequential
from keras.layers import Embedding, LSTM, Dense, Dropout, SpatialDropout1D
import numpy as np
from string import punctuation

# make it a set to accelerate tests
punc = set(punctuation)
embedding_size = 64
sequence_length = 500

def get_model_5stars(vocab_size, sequence_length, embedding_size):
    model=Sequential()
    model.add(Embedding(vocab_size, embedding_size, input_length=sequence_length))
    model.add(SpatialDropout1D(0.15))
    model.add(LSTM(128, recurrent_dropout=0.2))
    model.add(Dropout(0.3))
    model.add(Dense(1, activation="linear"))
    model.summary()
    return model


def clean_text(text):
    return ''.join([ c.lower() for c in text if c not in punc ])


def tokenize_words(words, vocab2int):
    words = words.split()
    tokenized_words = np.zeros((len(words),))
    for j in range(len(words)):
        try:
            tokenized_words[j] = vocab2int[words[j]]
        except KeyError:
            # didn't add any unk, just ignore
            pass
    return tokenized_words


from keras.preprocessing.sequence import pad_sequences
import pickle

print("Loading vocab2int")
vocab2int = pickle.load(open("sentiment/data/vocab2int.pickle", "rb"))

model = get_model_5stars(len(vocab2int), sequence_length=sequence_length, embedding_size=embedding_size)
model.load_weights("sentiment/results/model_V20_0.38_0.80.h5")


def get_review_stars(review):
    with graph.as_default():
        review = tokenize_words(clean_text(review), vocab2int)
        x = pad_sequences([review], maxlen=sequence_length)
        return model.predict(x)[0][0]


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Food Review evaluator")
    parser.add_argument("review", type=str, help="The review of the product in text")

    args = parser.parse_args()

    review_stars = get_review_stars(args.review)
    print(f"{review_stars:.2f}/5")

    # test = "I think you should improve the products price thats really expensive but the product in general is not that good too"
    # x = [ vocab2int[w.lower()] for w in test.split() ]

    # x = pad_sequences([x], maxlen=sequence_length)
    # print(model.predict(x))