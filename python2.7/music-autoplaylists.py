#!/usr/bin/env python2.7

__author__ = ['[Brandon Amos](http://bamos.github.io)']
__date__ = '2015.04.09'

"""
This script (music-autoplaylists.py) automatically creates
M3U playlists from the genre ID3 tags of songs in a directory.
"""

import argparse
import os
import re
import shutil
import sys
from mutagen.easyid3 import EasyID3
from collections import defaultdict
import toNeat

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--musicDir', type=str, default='.')
    parser.add_argument('--playlistDir', type=str, default='./playlists/auto')
    parser.add_argument('-a','--album', action='store_true', help='''Album mode''')
    parser.add_argument('-g','--genre', action='store_true', help='''Genre mode''')
    parser.add_argument('-C','--capital', action='store_true', help='''Changes names to capital''')
    args = parser.parse_args()

    titleList = defaultdict(list)
    
    for dpath, dnames, fnames in os.walk(args.musicDir):
        if '.git' in dpath:
            continue
        for fname in fnames:
            if os.path.splitext(fname)[1] != '.mp3':
                continue
            p = os.path.abspath(os.path.join(dpath, fname))
            audio = EasyID3(p)
            if args.genre:
                if 'genre' in audio:
                    assert(len(audio['genre']) == 1)
                    title = toNeat.toNeat(str(audio['genre'][0]), args)
                else:
                    title = 'Unknown'
                titleList[title].append(p)
            elif args.album:
                if 'album' in audio:
                    assert(len(audio['album']) == 1)
                    title = toNeat.toNeat(str(audio['album'][0]), args) 
                else:
                    title = 'Unknown'
                titleList[title].append(p)

    if os.path.exists(args.playlistDir):
        shutil.rmtree(args.playlistDir)
    os.makedirs(args.playlistDir)

    for titleList, songs in titleList.items():
        p = os.path.join(args.playlistDir, title + '.m3u')
        print("Creating playlist: {}".format(p))
        with open(p, 'w') as f:
            f.write("#EXTM3U\n")
            f.write("\n".join(sorted(songs)) + "\n")

if __name__ == '__main__':
    main()
