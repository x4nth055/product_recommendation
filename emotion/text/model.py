from keras.models import Sequential
from keras.layers import Embedding, LSTM, Dense, Activation, LeakyReLU, Dropout, TimeDistributed
from keras.layers import SpatialDropout1D
from emotion.text.config import LSTM_units

def get_model_emotions(vocab_size, sequence_length, embedding_size):
    model=Sequential()
    model.add(Embedding(vocab_size, embedding_size, input_length=sequence_length))
    model.add(SpatialDropout1D(0.15))
    model.add(LSTM(LSTM_units, recurrent_dropout=0.2))
    model.add(Dropout(0.3))
    model.add(Dense(5, activation="softmax"))
    # model.summary()
    return model