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
from emotion.text.model import get_model_emotions
from emotion.text.utils import clean_text, tokenize_words
from emotion.text.config import embedding_size, sequence_length
from keras.preprocessing.sequence import pad_sequences

import pickle

categories = {
    0: "neutral",
    1: "anger",
    2: "happiness",
    3: "surprise",
    4: "sadness"
}

print("Loading vocab2int")
vocab2int = pickle.load(open("emotion/text/results/vocab2int.pickle", "rb"))

model = get_model_emotions(len(vocab2int), sequence_length=sequence_length, embedding_size=embedding_size)
model.load_weights("emotion/text/results/model_v1_0.68_0.74.h5")


def get_emotions(text, proba=True):
    text = tokenize_words(clean_text(text), vocab2int)
    x = pad_sequences([text], maxlen=sequence_length)
    with graph.as_default():
        if proba:
            probs = {}
            p = model.predict(x)[0]
            for i, category in categories.items():
                probs[category] = p[i]*100
            return probs
        else:
            prediction = model.predict_classes(x)[0]
            return categories[prediction]


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Emotion classifier using text")  
    parser.add_argument("text", type=str, help="The text you want to analyze")

    args = parser.parse_args()
    
    text = tokenize_words(clean_text(args.text), vocab2int)
    x = pad_sequences([text], maxlen=sequence_length)
    prediction = model.predict_classes(x)[0]
    
    probs = model.predict(x)[0]
    print("Probs:")
    for i, category in categories.items():
        print(f"{category.capitalize()}: {probs[i]*100:.2f}%")
    print("The most dominant:", categories[prediction])