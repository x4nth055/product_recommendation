# Requirements
- **Flask 1.0.2**
- **passlib 1.7.1** for hashing passwords
- **pocketsphinx** for ASR HMM model
- **FFmpeg** for converting wav files to 16000Hz sample rate (install [here](http://ffmpeg.org/download.html))
- **SciPy**
- **NumPy**
- **Pandas**
```
pip3 install -r requirements.txt
```
## Automatic Speech Recognition
### Pocketsphinx
- Download HMM model [here](https://sourceforge.net/projects/cmusphinx/files/Acoustic%20and%20Language%20Models/.US%20English/cmusphinx-en-us-8khz-5.2.tar.gz/download)
- Download Language Model [here](https://sourceforge.net/projects/cmusphinx/files/Acoustic%20and%20Language%20Models/US%20English/en-70k-0.1.lm.gz/download).
- Extract them and put them in asr/pocketsphinx folder.