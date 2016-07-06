#!/usr/bin/env python2.7

__author__ = ['[Brandon Amos](http://bamos.github.io)']
__date__ = '2014.04.19'

"""
This script (music-organizer.py) organizes my music collection for
iTunes and [mpv](http://mpv.io) using tag information.
The directory structure is `<artist>/<track>`, where `<artist>` and `<track>`
are lower case strings separated by dashes.

See my blog post
[Using Python to organize a music directory](http://bamos.github.io/2014/07/05/music-organizer/)
for a more detailed overview of this script.
"""

import argparse
import glob
import os
import re
import shutil
import sys
import toNeat
from mutagen.easyid3 import EasyID3
from mutagen.oggvorbis import OggVorbis

parser = argparse.ArgumentParser(
        description='''Organizes a music collection using tag information.
    The directory format is that the music collection consists of
    artist subdirectories, and there are 2 modes to operate on
    the entire collection or a single artist.
    All names are made lowercase and separated by dashes for easier
    navigation in a Linux filesystem.'''
    )
parser.add_argument('-d','--delete-conflicts', action='store_true',
        dest='delete_conflicts',
        help='''If an artist has duplicate tracks with the same name,
                    delete them. Note this might always be best in case an
                    artist has multiple versions. To keep multiple versions,
                    fix the tag information.''')
parser.add_argument('-e','--delete-unrecognized-extensions', action='store_true',
        dest='delete_unrecognized')
parser.add_argument('-A','--album', action='store_true',
        dest='album',
        help='''Adds album folder inside the artist folder to sort out
                    albums''')
parser.add_argument('-n','--numbering', action='store_true',
        dest='numbering',
        help='''Adds numbering in front of sorted songs''')
parser.add_argument('-C','--capital', action='store_true',
        dest='capital',
        help='''Makes the first letter of a song capital''')
args = parser.parse_args()

def artist():
    print("Organizing artist")
    delete_dirs = []
    for dirname, dirnames, filenames in os.walk("."):
        # Move all the files to the root directory.
        for filename in filenames:
            fullPath = os.path.join(dirname, filename)
            # formating song
            returned = song(fullPath)
            if returned is "succes":
                print("succesful formated")
            elif returned is "delete":
                print"deleted remaining files in folder"
            else:
                returnedlist = returned.split('/')
                for extdir in returnedlist:
                    if extdir in delete_dirs:
                        delete_dirs.remove(extdir)

        # Add subdirectories to a list 
        for subdirname in dirnames:
            delete_dirs.append(subdirname)

    # deletes subdirectories
    for d in delete_dirs:
        shutil.rmtree(os.path.join(".", d), ignore_errors=True)

def song(filename):
#    if filename[0] == '.':
#       print("Ignoring dotfile: '{}'".format(filename))
#       return
    ext = os.path.splitext(filename)[1]
    if ext in (".mp3" , ".ogg"):
        print("Organizing song '" + filename + "'.")
        try:
            if ext == ".mp3":
                audio = EasyID3(filename)
            elif ext == ".ogg":
                audio = OggVorbis(filename)
            artist = audio['artist'][0].encode('ascii', 'ignore')
            title = audio['title'][0].encode('ascii', 'ignore')
            if args.album:
                album = audio['album'][0].encode('ascii', 'ignore')
            if args.numbering:
                try:
                    tracknumber = audio['tracknumber'][0].encode('ascii', 'ignore')
                except:
                    try:
                        tracknumber = re.findall(r'\d+', os.path.basename(filename).split(' ')[0])[0]
                    except:
                        tracknumber = "error"
                neatTracknumber = tracknumber.split('/')[0].zfill(2)
            print("    artist: " + artist)
            print("    title: " + title)
            if args.album:
                print("    album: " + album)
        except:
            artist = None
            title = None
            if args.album:
                album = None
            if args.numbering:
                tracknumber = None
        
        neatArtist = toNeat.toNeat(artist, args)
        if args.numbering:
            neatTitle = neatTracknumber + "." + toNeat.toNeat(title, args)
        else:
            neatTitle = toNeat.toNeat(title, args)
        if args.album:
            neatAlbum = toNeat.toNeat(album, args)
        print("    neatArtist: " + neatArtist)
        print("    neatTitle: " + neatTitle)
        if args.album:
            print("    neatAlbum: " + neatAlbum)
        if not os.path.isdir(neatArtist):
            os.mkdir(neatArtist)
        if args.album:
            if not os.path.isdir(neatArtist + "/" + neatAlbum):
                os.mkdir(neatArtist + "/" + neatAlbum)
            newFullPath = os.path.join(neatArtist, neatAlbum, neatTitle + ext)
        else:
            newFullPath = os.path.join(neatArtist, neatTitle + ext)

        if newFullPath != filename:
            if os.path.isfile(newFullPath):
                if args.delete_conflicts:
                    os.remove(filename)
                    print("File exists: '" + newFullPath + "'")
                    print("Deleted: '" + filename + "'")
                else:
                    print("Error: File exists: '" + newFullPath + "'")
                    return os.path.split(newFullPath)[0]
            else:
                os.rename(filename, newFullPath)
                return "succes"

    else:
        if not args.delete_unrecognized:
            print("Error: Unrecognized file extension in '{}'.".format(filename))
            sys.exit(-42)
        else:
            return "delete"
 

def collection():
    for f in glob.glob('*'):
        if os.path.isdir(f):
            if f != 'iTunes' and f != 'playlists':
                artist()
        elif os.path.isfile(f):
            song(f)

collection()
print("\nComplete!")
