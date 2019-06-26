import os
import subprocess
from passlib.hash import pbkdf2_sha256
import base64
import time
import numpy as np
import librosa
import soundfile

from flask import request, url_for, redirect
from string import digits
import urllib.request as urllib


def internet_on():
    try:
        urllib.urlopen('http://www.google.com', timeout=1)
        return True
    except urllib.URLError: 
        return False


def get_sent_audio_file(attr_name):
    """This function does:
        - Gets audio file from AJAX request sent from JS
        - Saves it to `audio_uploads` folder
        - Convert it to 16000Hz mono"""
    # get audio file from AJAX request
    name = request.form[attr_name]
    split = name.split(".")
    audio = request.files['data']
    time_now = time.strftime("%Y%m%d_%H%M%S")
    tmp_file = f"audio_uploads/{time_now}_temp.{split[1]}"
    target_file = f"audio_uploads/{time_now}.{split[1]}"
    audio.save(tmp_file)
    convert_audio(tmp_file, target_file, remove=True)
    target_file = os.path.join(os.getcwd(), target_file)
    return target_file


def get_sent_image_file(attr_name, id=None):
    print(request.files)
    image = request.files[attr_name]
    if id is None:
        id = get_unique_id(16)
    target_file = f"static/img/products/{id}.jpeg"
    image.save(target_file)
    return target_file


def convert_audio(audio_path, target_path, remove=False):
    """This function sets the audio `audio_path` to:
        - 16000Hz Sampling rate
        - one number of audio channels ( mono )
            Params:
                audio_path (str): the path of audio wav file you want to convert
                target_path (str): target path to save your new converted wav file
                remove (bool): whether to remove the old file after converting
        Note that this function requires ffmpeg installed in your system."""

    # os.system(f"ffmpeg -i {audio_path} -ac 1 -ar 16000 {target_path}")
    NULL = subprocess.DEVNULL
    subprocess.Popen(f"ffmpeg -i {audio_path} -ac 1 -ar 16000 {target_path}", shell=True, stdout=NULL, stderr=NULL).communicate()
    if remove:
        os.remove(audio_path)


def get_query(tablename, fields):
    query = f"CREATE TABLE IF NOT EXISTS {tablename.upper()} ("
    for name, datatype in fields.items():
        query += f"{name} {datatype}, "
    return query.rstrip(", ") + ")"


def get_unique_id(length=8):
    """Generates random secure unique ID that is urlsafe ( i.e can be on url )"""
    return base64.urlsafe_b64encode(os.urandom(length)).decode().strip('=')


def is_pw_correct(password, hashed_password):
    """Test whether `password` that is not hashed is the same as `hashed_password`"""
    return pbkdf2_sha256.verify(password, hashed_password)


def hash_pw(password):
    """Returns hashed version of `password`"""
    return pbkdf2_sha256.hash(password)


def email_valid(email):
    # TODO
    return True


def redirect_previous_url(default='home'):
    return redirect(request.args.get('next') or request.referrer or url_for(default))


def remove_starting_digits(string):
    """This function is useful for html id attribute"""
    return string.lstrip(digits)

            
audio_config = {
    'mfcc': True,
    'chroma': True,
    'mel': True,
    'contrast': False,
    'tonnetz': False
}

def extract_feature(file_name, **kwargs):
    """Extract feature from audio file `file_name`
        Features supported:
            - MFCC (mfcc)
            - Chroma (chroma)
            - MEL Spectrogram Frequency (mel)
            - Contrast (contrast)
            - Tonnetz (tonnetz)
        e.g:
        `features = extract_feature(path, mel=True, mfcc=True)`"""
    mfcc = kwargs.get("mfcc")
    chroma = kwargs.get("chroma")
    mel = kwargs.get("mel")
    contrast = kwargs.get("contrast")
    tonnetz = kwargs.get("tonnetz")
    with soundfile.SoundFile(file_name) as sound_file:
        X = sound_file.read(dtype="float32")
        sample_rate = sound_file.samplerate
        if chroma or contrast:
            stft = np.abs(librosa.stft(X))
        result = np.array([])
        if mfcc:
            mfccs = np.mean(librosa.feature.mfcc(y=X, sr=sample_rate, n_mfcc=40).T, axis=0)
            result = np.hstack((result, mfccs))
        if chroma:
            chroma = np.mean(librosa.feature.chroma_stft(S=stft, sr=sample_rate).T,axis=0)
            result = np.hstack((result, chroma))
        if mel:
            mel = np.mean(librosa.feature.melspectrogram(X, sr=sample_rate).T,axis=0)
            result = np.hstack((result, mel))
        if contrast:
            contrast = np.mean(librosa.feature.spectral_contrast(S=stft, sr=sample_rate).T,axis=0)
            result = np.hstack((result, contrast))
        if tonnetz:
            tonnetz = np.mean(librosa.feature.tonnetz(y=librosa.effects.harmonic(X), sr=sample_rate).T,axis=0)
            result = np.hstack((result, tonnetz))
    return result
            