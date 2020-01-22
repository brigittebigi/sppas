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

    src.resources.unigram.py
    ~~~~~~~~~~~~~~~~~~~~~~~~

"""

import codecs
import logging

from sppas.src.config import sg
from sppas.src.utils import sppasUnicode

from .dumpfile import sppasDumpFile
from .resourcesexc import PositiveValueError

# ----------------------------------------------------------------------------


class sppasUnigram(object):
    """Class to represent a simple unigram: a set of token/count.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2018  Brigitte Bigi

    An unigram is commonly a data structure with tokens and their
    probabilities, and a back-off value. Is is a statistical language model.
    This class is a simplified version with only tokens and their occurrences.

    Notice that tokens are case-sensitive.

    """

    def __init__(self, filename=None, nodump=True):
        """Create a sppasUnigram instance.

        :param filename: (str) Name of the file with words and counts \
        (2 columns)
        :param nodump: (bool) Disable the creation of a dump file

        """
        self.__sum = 0
        self.__entries = dict()

        if filename is not None:

            data = None
            dp = sppasDumpFile(filename)

            # Try first to get the dict from a dump file
            # (at least 2 times faster)
            if nodump is False:
                data = dp.load_from_dump()

            # Load from ascii if: 1st load,
            # or, dump load error,
            # or dump older than ascii
            if data is None:
                self.load_from_ascii(filename)
                if nodump is False:
                    dp.save_as_dump(self.__entries)
            else:
                self.__entries = data

    # -------------------------------------------------------------------------

    def add(self, entry, value=1):
        """Add or increment a token in the unigram.

        :param entry: (str) String of the token to add
        :param value: (int) Value to increment the count
        :raises: PositiveValueError

        """
        entry = sppasUnicode(entry).to_strip()

        value = int(value)
        if value <= 0:
            raise PositiveValueError(count=value)
        count = self.__entries.get(entry, 0) + value

        self.__entries[entry] = count
        self.__sum += value

    # -------------------------------------------------------------------------

    def get_count(self, token):
        """Return the count of a token.

        :param token: (str) The string of the token

        """
        s = sppasUnicode(token).to_strip()
        return self.__entries.get(s, 0)

    # -------------------------------------------------------------------------

    def get_sum(self):
        """Return the sum of all counts (of all tokens)."""
        return self.__sum

    # -------------------------------------------------------------------------

    def get_tokens(self):
        """Return a list with all tokens."""
        return self.__entries.keys()

    # ------------------------------------------------------------------------
    # File
    # ------------------------------------------------------------------------

    def load_from_ascii(self, filename):
        """Load a unigram from a file with two columns: word count.

        :param filename: (str) Name of the unigram ASCII file to read

        """
        with codecs.open(filename, 'r', sg.__encoding__) as fd:
            lines = fd.readlines()

        for line in lines:
            line = " ".join(line.split())
            if len(line) == 0:
                continue

            tabline = line.split()
            if len(tabline) < 2:
                continue

            # Add (or modify) the entry in the dict
            key = tabline[0]
            value = int(tabline[1])
            self.add(key, value)

    # -------------------------------------------------------------------------

    def save_as_ascii(self, filename):
        """Save a unigram into a file with two columns: word freq.

        :param filename: (str) Name of the unigram ASCII file to write
        :returns: (bool)

        """
        try:
            with codecs.open(filename, 'w', encoding=sg.__encoding__) as output:

                for entry, value in sorted(self.__entries.items(),
                                           key=lambda x: x[0]):
                    output.write("{:s} {:d}\n".format(entry, value))

        except Exception as e:
            logging.info('Save file failed due to the following error: {:s}'
                         ''.format(str(e)))
            return False

        return True

    # -----------------------------------------------------------------------
    # Overloads
    # -----------------------------------------------------------------------

    def __len__(self):
        return len(self.__entries)

    # ------------------------------------------------------------------------

    def __contains__(self, item):
        s = sppasUnicode(item).to_strip()
        return s in self.__entries
