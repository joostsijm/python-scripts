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
parser.add_argument('-m','--ignore-multiple-artists', action='store_true',
        dest='ignore_multiple_artists',
        help='''This script will prompt for confirmation if an artist
                    directory has songs with more than 2 different tags.
                    This flag disables the confirmation and won't perform
                    this check.''')
parser.add_argument('-c','--collection', action='store_true',
        help='''Operate in 'collection' mode and run 'artist' mode
                    on every subdirectory.''')
parser.add_argument('-a', '--artist', action='store_true',
        help='''Operate in 'artist' mode and copy all songs to the
                    root of the directory and cleanly format the names to
                    be easily typed and navigated in a shell.''')
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

if args.collection and args.artist:
    print("Error: Only provide 1 of '--collection' or '--artist'.")
    sys.exit(-1)
elif not (args.collection or args.artist):
    print("Error: Mode '--collection' or '--artist' not provided.")
    sys.exit(-1)


# Maps a string such as 'The Beatles' to 'the-beatles'.
def toNeat(s):
    if args.capital:
        s = s.title().replace("&", "and")
    else:
        s = s.lower().replace("&", "and")

    # Put spaces between and remove blank characters.
    blankCharsPad = r"()\[\],.\\\?\#/\!\$\:\;"
    blankCharsNoPad = r"'\""
    s = re.sub(r"([" + blankCharsPad + r"])([^ ])", "\\1 \\2", s)
    s = re.sub("[" + blankCharsPad + blankCharsNoPad + "]", "", s)

    # Replace spaces with a single dash.
    s = re.sub(r"[ \*\_]+", "-", s)
    s = re.sub("-+", "-", s)
    s = re.sub("^-*", "", s)
    s = re.sub("-*$", "", s)

    # Ensure the string is only alphanumeric with '-', '+', and '='.
    if args.capital:
        search = re.search("[^0-9a-zA-Z\-\+\=]", s)
    else:
        search = re.search("[^0-9a-z\-\+\=]", s)
    if search:
        print("Error: Unrecognized character in '" + s + "'")
        sys.exit(-42)
    return s


def artist():
    print("Organizing artist")
    if not args.ignore_multiple_artists:
        artists = set()
        for dirname, dirnames, filenames in os.walk("."):
            # Make sure there aren't a lot of different artists
            # in case this was called from the wrong directory.
            for filename in filenames:
                try:
                    audio = EasyID3(os.path.join(dirname, filename))
                    artist = audio['artist'][0].decode()
                    artists.add(artist)
                except:
                    pass

        if len(artists) > 2:
            while True:
                print("Warning: More than 2 artists found in '{}'.".format("."))
                print("This will move all songs to the '{}' directory.".format("."))
                print("Continue? yes/no")
                choice = raw_input().lower()
                valid = {"yes": True, "y": True, "no": False, "n": False}
                if choice in valid:
                    if valid[choice]:
                        break
                    else:
                        print("Exiting.")
                        sys.exit(-1)

    delete_dirs = []
    for dirname, dirnames, filenames in os.walk("."):
        # Move all the files to the root directory.
        for filename in filenames:
            fullPath = os.path.join(dirname, filename)
            song(fullPath)
            '''
            if ext in (".mp3" , ".ogg"):
                print("file: " + str(fullPath))

                try:
                    if ext == ".mp3":
                        audio = EasyID3(fullPath)
                    elif ext == ".ogg":
                        audio = OggVorbis(fullPath)
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
                    print("    title: " + title)
                except:
                    title = None
                    if args.album:
                        album = None

                if not title:
                    print("Error: title not found for '" + filename + "'")
                    sys.exit(-42)

                if args.numbering and tracknumber is not "error":
                     neatTitle = tracknumber + ".-" + toNeat(title)
                else:
                    neatTitle = toNeat(title)
                
                print("    neatTitle: " + neatTitle)

                if args.album:
                    neatAlbum = toNeat(album)
                    print("    neatAlbum: " + neatAlbum)
                    newFullPath = os.path.join(artistDir, neatAlbum, neatTitle + ext)
                
                else:
                    newFullPath = os.path.join(artistDir, neatTitle + ext)
                print("    newFullPath: " + newFullPath)

                if newFullPath != fullPath:
                    if os.path.isfile(newFullPath):
                        if args.delete_conflicts:
                            os.remove(fullPath)
                            print("File exists: '" + newFullPath + "'")
                            print("Deleted: '" + fullPath + "'")
                        else:
                            print("Error: File exists: '" + newFullPath + "'")
                            sys.exit(-42)
                    else:
                        os.rename(fullPath, newFullPath)
            elif ext == ".pdf":
                pass
           '''

        # Delete all subdirectories.
        for subdirname in dirnames:
            delete_dirs.append(subdirname)

    for d in delete_dirs:
        shutil.rmtree(os.path.join(".", d), ignore_errors=True)

def song(filename):
#    if filename[0] == '.':
 #       print("Ignoring dotfile: '{}'".format(filename))
  #      return
    print("Organizing song '" + filename + "'.")
    ext = os.path.splitext(filename)[1]
    if ext in (".mp3" , ".ogg"):
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
        neatArtist = toNeat(artist)
        if args.numbering:
            neatTitle = tracknumber + "." + toNeat(title)
        else:
            neatTitle = toNeat(title)
        if args.album:
            neatAlbum = toNeat(album)
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
        os.rename(filename, newFullPath)
    else:
        if not args.delete_unrecognized:
            print("Error: Unrecognized file extension in '{}'.".format(filename))
            sys.exit(-42)
 

def collection():
    for f in glob.glob('*'):
        if os.path.isdir(f):
            if f != 'iTunes' and f != 'playlists':
                artist()
        elif os.path.isfile(f):
            song(f)

if args.artist:
    artist()
else:
    collection()
print("\nComplete!")
