#!/usr/bin/env python2.7

from mutagen.easyid3 import EasyID3
from mutagen.oggvorbis import OggVorbis
import audioFunction
import os
import re

def fixTracknumber(fname):
    print("fixTracknumber")
    audio = audioFunction.returnAudio(fname)
    try:
        tracknumber = re.findall(r'\d+', os.path.basename(fname).split(' ')[0])[0]
    except:
        tracknumber = "0"
    audio['tracknumber'] = tracknumber.zfill(2)
    return formatNumber(audio)

def formatNumber(fname):
    audio = audioFunction.returnAudio(fname)
    if 'tracknumber' not in audio:
        fixTracknumber(fname)
    if '/' in audio['tracknumber'][0]:
        audio['tracknumber'] = audio['tracknumber'][0].split('/')[0]
    audio['tracknumber'][0]
    audio.save()
    return audio

def getTracknumber(fname):
    audio = formatNumber(fname)
    return audio['tracknumber'][0].encode('ascii', 'ignore')
