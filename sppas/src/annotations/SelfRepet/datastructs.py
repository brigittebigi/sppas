"""
    ..
        ---------------------------------------------------------------------
         ___   __    __    __    ___
        /     |  \  |  \  |  \  /              the automatic
        \__   |__/  |__/  |___| \__             annotation and
           \  |     |     |   |    \             analysis
        ___/  |     |     |   | ___/              of speech

        http://www.sppas.org/

        Use of this software is governed by the GNU Public License, version 3.

        SPPAS is free software: you can redistribute it and/or modify
        it under the terms of the GNU General Public License as published by
        the Free Software Foundation, either version 3 of the License, or
        (at your option) any later version.

        SPPAS is distributed in the hope that it will be useful,
        but WITHOUT ANY WARRANTY; without even the implied warranty of
        MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
        GNU General Public License for more details.

        You should have received a copy of the GNU General Public License
        along with SPPAS. If not, see <http://www.gnu.org/licenses/>.

        This banner notice must not be removed.

        ---------------------------------------------------------------------

    src.annotations.SelfRepet.datastructs.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Data structures to store repetitions.

"""

import re

from sppas.src.config import symbols
from sppas.src.exceptions import RangeBoundsException
from sppas.src.exceptions import IndexRangeException
from sppas.src.utils import sppasUnicode

# ---------------------------------------------------------------------------


class DataRepetition(object):
    """Class to store one repetition (the source and the echos).

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2018  Brigitte Bigi

    The source of a repetition is represented as a tuple (start, end).
    The echos of this latter are stored as a list of tuples (start, end).

    """

    def __init__(self, s1=None, s2=None, r1=None, r2=None):
        """Create a DataRepetition data structure.

        :param s1: start position of the source.
        :param s2: end position of the source.
        :param r1: start position of an echo
        :param r2: end position of an echo

        """
        self.__source = None
        self.set_source(s1, s2)

        self.__echos = list()
        if r1 is not None and r2 is not None:
            self.add_echo(r1, r2)

    # -----------------------------------------------------------------------

    def reset(self):
        """Fix the source to None and the echos to an empty list."""
        self.__source = None
        self.__echos = list()

    # -----------------------------------------------------------------------

    def set_source(self, start, end):
        """Set the position of the source.

        Setting the position of the source automatically resets the echos
        because it's not correct to change the source of existing echos.

        :param start: Start position of the source
        :param end: End position of the source
        :raises: ValueError, IndexError

        """
        if start is None or end is None:
            self.reset()
            return

        s1 = int(start)
        s2 = int(end)
        if s1 > s2:
            raise RangeBoundsException(s1, s2)
        if s1 < 0 or s2 < 0:
            raise ValueError

        self.__source = (s1, s2)
        self.__echos = list()

    # -----------------------------------------------------------------------

    def get_source(self):
        """Return the tuple (start, end) of the source."""
        return self.__source

    # -----------------------------------------------------------------------

    def get_echos(self):
        """Return the list of echos."""
        return self.__echos

    # -----------------------------------------------------------------------

    def add_echo(self, start, end):
        """Add an entry in the list of echos.

        :param start: Start position of the echo.
        :param end: End position of the source.
        :raises: ValueError

        """
        if self.__source is None:
            raise Exception('No source defined.')

        if start is None or end is None:
            return 0

        r1 = int(start)
        r2 = int(end)
        if r1 > r2:
            raise RangeBoundsException(r1, r2)
        if r1 < 0 or r2 < 0:
            raise ValueError

        if (r1, r2) not in self.__echos:
            self.__echos.append((r1, r2))
            return 1
        return 0

    # -----------------------------------------------------------------------
    # Overloads
    # -----------------------------------------------------------------------

    def __str__(self):
        print("source: ({:d}, {:d})"
              "".format(self.__source[0], self.__source[1]))
        print("echos: ")
        for rep in self.__echos:
            print("  ({:d}, {:d}) ".format(rep[0], rep[1]))

# ---------------------------------------------------------------------------


class Entry(object):
    """Class to store a formatted unicode entry.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2018  Brigitte Bigi

    """

    def __init__(self, entry):
        """Create an Entry instance.

        :param entry: (str, unicode)

        """
        self.__entry = None
        self.set(entry)

    # -----------------------------------------------------------------------

    def get(self):
        """Return the formatted unicode entry."""
        return self.__entry

    # -----------------------------------------------------------------------

    def set(self, entry):
        """Fix the entry.

        :param entry: (str, unicode) entry to store.

        """
        if entry is None:
            self.__entry = sppasUnicode("").to_strip()
        else:
            self.__entry = sppasUnicode(entry).to_strip()
        self.__clean()

    # -----------------------------------------------------------------------
    # Private
    # -----------------------------------------------------------------------

    def __clean(self):
        """Remove some punctuations (they can be due to the EOT)."""
        self.__entry = re.sub("\~$", "", self.__entry)
        self.__entry = re.sub("\-+$", "", self.__entry)
        self.__entry = re.sub(">$", "", self.__entry)
        self.__entry = re.sub("^<", "", self.__entry)

# ---------------------------------------------------------------------------


class DataSpeaker(object):
    """Class to store data of a speaker.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2018  Brigitte Bigi

    Stored data are a list of formatted unicode strings.

    """

    def __init__(self, tokens):
        """Create a DataSpeaker instance.

        :param tokens: (list) List of tokens.

        """
        self.__entries = list()
        for tok in tokens:
            self.__entries.append(Entry(tok).get())

    # -----------------------------------------------------------------------

    def is_word(self, idx):
        """Return true if the entry at the given index is a word.

        An empty entry is not a word.
        Symbols (silences, laughs...) are not words.
        Hesitations are considered words.

        Return False if the given index is wrong.

        :param idx: (int) Index of the entry to get
        :returns: (bool)

        """
        if idx < 0:
            return False
        if idx >= len(self.__entries):
            return False

        # An empty string
        if len(self.__entries[idx]) == 0:
            return False

        # Symbols used by SPPAS to represent an event
        if self.__entries[idx] in symbols.all:
            return False

        return True

    # -----------------------------------------------------------------------

    def get_next_word(self, current):
        """Ask for the index of the next word in entries.

        :param current (int) Current position to search for the next word
        :returns: (int) Index of the next word or -1 if no next word can
        be found.

        """
        # check if current is a correct value
        self.__get_entry(current)

        # search for the next word after the current index
        c_next = current + 1
        while c_next < len(self.__entries):
            if self.is_word(c_next) is True:
                return c_next
            c_next += 1

        return -1

    # -----------------------------------------------------------------------

    def is_word_repeated(self, current, other_current, other_speaker):
        """Ask for a token to be a repeated word.

        :param current: (int) From index, in current speaker
        :param other_current: (int) From index, in the other speaker
        :param other_speaker: (DataSpeaker) Data of the other speaker
        :returns: index of the echo or -1

        """
        # Does the current entry is a word?
        if self.is_word(current) is False:
            return -1

        # Search for this word in the other speaker data
        word = self.__entries[current]
        while 0 <= other_current < len(other_speaker):
            other_token = other_speaker[other_current]
            if word == other_token:
                return other_current
            # not found. try next one
            other_current = other_speaker.get_next_word(other_current)

        return -1

    # -----------------------------------------------------------------------
    # Private
    # -----------------------------------------------------------------------

    def __get_entry(self, idx):
        """Return the formatted "token" at the given index.

        Raise exception if index is wrong.

        :param idx: (int) Index of the entry to get
        :returns: (str) unicode formatted entry

        """
        if idx < 0:
            raise IndexRangeException(idx, 0, len(self.__entries))
        if idx >= len(self.__entries):
            raise IndexRangeException(idx, 0, len(self.__entries))

        return self.__entries[idx]

    # -----------------------------------------------------------------------
    # Overloads
    # -----------------------------------------------------------------------

    def __str__(self):
        return " ".join([e for e in self.__entries])

    def __iter__(self):
        for a in self.__entries:
            yield a

    def __getitem__(self, i):
        return self.__get_entry(i)

    def __len__(self):
        return len(self.__entries)
