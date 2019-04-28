# to use CPU
import os
os.environ["CUDA_DEVICE_ORDER"] = "PCI_BUS_ID"   # see issue #152
os.environ["CUDA_VISIBLE_DEVICES"] = "-1"

import tensorflow as tf
graph = tf.get_default_graph() 
config = tf.ConfigProto(intra_op_parallelism_threads=5,
                        inter_op_parallelism_threads=5, 
                        allow_soft_placement=True,
                        device_count = {'CPU' : 1,
                                        'GPU' : 0}
                       )

from emotion.speech.models import first_model
from emotion.speech.utils import categories_reversed, extract_feature, categories

import numpy as np

audio_config = {
    "mfcc": True,
    "chroma": False,
    "mel": True,
    "contrast": False,
    "tonnetz": False
}

model = first_model(168, len(categories_reversed))
model.load_weights("emotion/speech/results/first_model_v2_0.38.h5")

def get_emotions(audio_file, proba=True):
    X = extract_feature(audio_file, **audio_config)
    X = np.expand_dims(X, axis=1)
    X = X.reshape((1, X.shape[1], X.shape[0]))
    with graph.as_default():
        if proba:
            probs = {}
            for i, x in enumerate(model.predict(X)[0]):
                probs[categories[i]] = x*100
            return probs
        else:
            return categories[model.predict_classes(X)[0]]
