#!/usr/bin python
"""

:author:       Fix Me
:date:         Now
:contact:      me@me.org
:license:      GPL, v3
:copyright:    Copyright (C) 2017  Fixme

:summary:      Simple script to get how many vowels are in a list of phonemes.

In this script, we also introduce the way to re-use the functions we already
have done in another script. There's no reason to re-write!!!
The other script must be in the same directory.

"""
import sys
from ex05_reading_file import read_file

# ----------------------------------------------------------------------------
# Variables
# ----------------------------------------------------------------------------

#myfile="C:\phonemes.csv"
myfile = "phonemes.csv"

# ----------------------------------------------------------------------------


def extract_list_from_lines(lines, pattern):
    """ Extract a list from lines if lines match with pattern.

    :param lines: (list of str)
    :param pattern: (str)

    """
    my_list = list()
    for line in lines:
        columns = line.split(';')
        if columns[0].strip() == pattern:
            my_list.append(columns[1].strip())

    return my_list

# ----------------------------------------------------------------------------


def count_elements(reference, to_count):
    """ Return how many elements of a list are in the reference list.

    :param reference: (list)
    :param to_count: (list)
    :returns: (int)

    """
    n = 0
    for x in to_count:
        if x in reference:
            n += 1
    return n

# ----------------------------------------------------------------------------

if __name__ == '__main__':

    # get the content of my file
    lines = read_file(myfile)

    # before doing something, check the data!
    if len(lines) == 0:
        print('Hum... the file was empty!')
        sys.exit(0)

    vowels = extract_list_from_lines(lines, "vowels")
    my_list = ['a', 'b', 'c', 'd', 'e', 'f', 'E', 'g', 'a~', 'S']

    nb_items = count_elements(vowels, my_list)
    nb_fric = count_elements(extract_list_from_lines(lines, "fricatives"), my_list)
    print("In my list, there are {:d} vowels.".format(nb_items))
    print("In my list, there are {:d} fricatives.".format(nb_fric))
