from pocketsphinx import Pocketsphinx
import os

config = {
    "hmm": "asr/pocketsphinx/cmusphinx-en-us-8khz-5.2",
    "lm": "asr/pocketsphinx/en-70k-0.1.lm",
}

print(" * Loading HMM pocketsphinx model")
speech = Pocketsphinx(**config)

def get_transcription(audio_file):
    speech.decode(audio_file=audio_file)
    return speech.hypothesis()

if __name__ == "__main__":
    audio_file = "audio_uploads/20190416_155703.wav"
    print(get_transcription(audio_file))