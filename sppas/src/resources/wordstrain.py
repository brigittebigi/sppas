# -*- coding: UTF-8 -*-
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

    src.resources.wordstrain.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""
import codecs

from sppas.src.config import sg

from .dictrepl import sppasDictRepl
from .resourcesexc import FileUnicodeError

# ---------------------------------------------------------------------------


class sppasWordStrain(sppasDictRepl):
    """Sort of basic lemmatization.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2018  Brigitte Bigi

    """

    def __init__(self, filename=None):
        """Create a WordStain instance.

        :param filename: (str) 2 or 3 columns file with word/freq/wordstrain

        """
        super(sppasWordStrain, self).__init__(dict_filename=None, nodump=True)
        self.load(filename)

    # -----------------------------------------------------------------------

    def load(self, filename):
        """Load word substitutions from a file.

        Replace the existing substitutions.

        :param filename: (str) 2 or 3 columns file with word/freq/replacement

        """
        if filename is None:
            return

        with codecs.open(filename, 'r', sg.__encoding__) as fd:
            try:
                line = fd.readline()
            except UnicodeDecodeError:
                raise FileUnicodeError(filename=filename)
            fd.close()

        content = line.split()
        if len(content) < 3:
            self.load_from_ascii(filename)
        else:
            self.__load_with_freq(filename)

    # -----------------------------------------------------------------------

    def __load_with_freq(self, filename):
        """Load a replacement dictionary from a 3-columns ascii file.

        :param filename: (str) Replacement dictionary file name

        """
        with codecs.open(filename, 'r', sg.__encoding__) as fd:
            try:
                lines = fd.readlines()
            except UnicodeDecodeError:
                raise FileUnicodeError(filename=filename)
            fd.close()

        self.__filename = filename
        frequency = {}
        for line in lines:
            line = " ".join(line.split())
            if len(line) == 0:
                continue

            tab_line = line.split()
            if len(tab_line) < 2:
                continue

            # To add (or modify) the entry in the dict:
            # Search for a previous token in the dictionary...
            key = tab_line[0].lower()
            freq = int(tab_line[1])
            value = sppasDictRepl.REPLACE_SEPARATOR.join(tab_line[2:])

            # does such entry already exists?
            if key in frequency:
                # does the new one is more frequent?
                if freq > frequency[key]:
                    # replace the old one by the new one
                    frequency[key] = freq
                    self.pop(key)
                    self.add(key, value)
            else:
                # add the new entry
                frequency[key] = freq
                self.add(key, value)
