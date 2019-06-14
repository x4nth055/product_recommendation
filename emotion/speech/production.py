
import pickle
from common.utils import extract_feature, audio_config

regressor = pickle.load(open("emotion/speech/best_regressor.pickle", "rb"))
hns_model = pickle.load(open("emotion/speech/best_model_HNS.pickle", "rb"))
ahnps_model = pickle.load(open("emotion/speech/best_model_AHNPS.pickle", "rb"))

def get_review_stars(audio_path):
    feature = extract_feature(audio_path, **audio_config).reshape(1, -1)
    stars = regressor.predict(feature)[0]
    # convert 3-stars to 5-starss
    return stars * 5 / 3

def get_emotion(audio_path, emotions=['sad', 'neutral', 'happy']):
    if len(emotions) == 3:
        model = hns_model
    elif len(emotions) == 5:
        model = ahnps_model
    else:
        raise TypeError("Emotions not available")
    feature = extract_feature(audio_path, **audio_config).reshape(1, -1)
    return model.predict(feature)[0]


