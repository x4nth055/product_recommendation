from pocketsphinx import Pocketsphinx

config = {
    "hmm": "emotion/sphinx/emotion.ci_cont",
    "dict": "emotion/sphinx/emotion.dic",
    "lm": "emotion/sphinx/emotion.lm"
}

model = Pocketsphinx(**config)

def get_emotion(audio_file):
    return model.decode(audio_file).hypothesis()