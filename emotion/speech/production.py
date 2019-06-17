
import os
os.environ["CUDA_DEVICE_ORDER"] = "PCI_BUS_ID"   # see issue #152
os.environ["CUDA_VISIBLE_DEVICES"] = "-1"

import tensorflow as tf

config = tf.ConfigProto(intra_op_parallelism_threads=5,
                        inter_op_parallelism_threads=5, 
                        allow_soft_placement=True,
                        device_count = {'CPU' : 1,
                                        'GPU' : 0}
                       )

graph = tf.get_default_graph()

import pickle
from common.utils import extract_feature, audio_config

from keras.layers import Dense, Dropout, LSTM
from keras.models import Sequential, load_model

def create_model():
    # parameters
    input_length = 180
    n_rnn_layers = 2
    n_dense_layers = 2
    cell = LSTM
    rnn_units = 128
    dense_units = 128
    dropout = [0.25]*4
    classification = False
    output_dim = 3

    loss = "mean_absolute_error"
    optimizer = "adam"

    model = Sequential()
    for i in range(n_rnn_layers):
        if i == 0:
            # first layer
            model.add(cell(rnn_units, return_sequences=True, input_shape=(None, input_length)))
            model.add(Dropout(dropout[i]))
        else:
            # middle layers
            model.add(cell(rnn_units, return_sequences=True))
            model.add(Dropout(dropout[i]))

        if n_rnn_layers == 0:
            i = 0

        # dense layers
        for j in range(n_dense_layers):
            # if n_rnn_layers = 0, only dense
            if n_rnn_layers == 0 and j == 0:
                model.add(Dense(dense_units, input_shape=(None, input_length)))
                model.add(Dropout(dropout[i+j]))
            else:
                model.add(Dense(dense_units))
                model.add(Dropout(dropout[i+j]))
                
        if classification:
            model.add(Dense(output_dim, activation="softmax"))
            model.compile(loss=loss, metrics=["accuracy"], optimizer=optimizer)
        else:
            model.add(Dense(1, activation="linear"))
            model.compile(loss="mean_absolute_error", metrics=["mean_absolute_error"], optimizer=optimizer)
        
        return model

# regressor = pickle.load(open("emotion/speech/HNS-r-LSTM-layers-2-2-units-128-128-dropout-0.25_0.25_0.25_0.25.h5", "rb"))
# regressor = create_model()
# regressor.load_weights("emotion/speech/HNS-r-LSTM-layers-2-2-units-128-128-dropout-0.25_0.25_0.25_0.25.h5")
regressor = load_model("emotion/speech/HNS-r-LSTM-layers-2-2-units-128-128-dropout-0.25_0.25_0.25_0.25.h5")
hns_model = pickle.load(open("emotion/speech/best_model_HNS.pickle", "rb"))
ahnps_model = pickle.load(open("emotion/speech/best_model_AHNPS.pickle", "rb"))
hn_model = pickle.load(open("emotion/speech/best_model_HN.pickle", "rb"))
hs_model = pickle.load(open("emotion/speech/best_model_HS.pickle", "rb"))

def get_review_stars(audio_path):
    feature = extract_feature(audio_path, **audio_config)
    # reshape
    feature = feature.reshape((1, 1, feature.shape[0]))
    with graph.as_default():
        stars = regressor.predict(feature)[0][0][0]
    # convert 3-stars to 5-starss
    if stars <= 0:
        stars = 0.05
    elif stars > 3:
        stars = 3
    return stars * 5 / 3

def get_emotion(audio_path, emotions=['sad', 'neutral', 'happy']):
    if len(emotions) == 2:
        if 'sad' in emotions and 'happy' in emotions:
            model = hs_model
        else:
            model = hn_model
    elif len(emotions) == 3:
        model = hns_model
    elif len(emotions) == 5:
        model = ahnps_model
    else:
        raise TypeError("Emotions not available")
    feature = extract_feature(audio_path, **audio_config).reshape(1, -1)
    return model.predict(feature)[0]


