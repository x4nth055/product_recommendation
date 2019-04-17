import os
import subprocess
from passlib.hash import pbkdf2_sha256
import base64
import time

from flask import request, url_for, redirect


def get_sent_file(attr_name):
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