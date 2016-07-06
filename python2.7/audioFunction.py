#!/usr/bin/env python2.7

from mutagen.easyid3 import EasyID3
from mutagen.oggvorbis import OggVorbis 
import os

def returnAudio(path):
    ext = os.path.splitext(path)[1]
    if ext == ".mp3":
        audio = EasyID3(path)
    elif ext == ".ogg":
        audio = OggVorbis(path)
    return audio
