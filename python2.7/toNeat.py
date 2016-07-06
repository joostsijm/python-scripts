#!/usr/bin/env python2.7

import re
import sys

# Maps a string such as 'The Beatles' to 'the-beatles'.
def toNeat(s, args):
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
