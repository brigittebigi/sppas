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

    src.resources.mapping.py
    ~~~~~~~~~~~~~~~~~~~~~~~

"""

import re
import logging

from .dictrepl import sppasDictRepl

# ----------------------------------------------------------------------------


class sppasMapping(sppasDictRepl):
    """Class to manage mapping tables.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2019  Brigitte Bigi

    A mapping is an extended replacement dictionary.
    sppasMapping is used for the management of a mapping table of any set
    of strings.

    """

    DEFAULT_SEP = (";", ",", "\n", " ", ".", "|", "+", "-")

    def __init__(self, dict_name=None):
        """Create a new sppasMapping instance.

        :param dict_name: (str) file name with the mapping data (2 columns)

        """
        super(sppasMapping, self).__init__(dict_name, nodump=True)

        self._keep_miss = True  # remove or not missing values
        self._reverse = False   # will replace value by key instead of by value
        self._miss_symbol = ""  # Symbol to be used if keep_miss is False

    # -----------------------------------------------------------------------

    def get_reverse(self):
        """Return the boolean value of reverse member."""
        return self._reverse

    # -----------------------------------------------------------------------

    def get_miss_symbol(self):
        """Return the boolean value of reverse member."""
        return self._miss_symbol

    # -----------------------------------------------------------------------
    # Methods to fix options
    # -----------------------------------------------------------------------

    def set_keep_miss(self, keep_miss):
        """Fix the keep_miss option.

        :param keep_miss: (bool) If keep_miss is set to True, each missing
        entry is kept without change; instead each missing entry is replaced
        by a specific symbol.

        """
        self._keep_miss = keep_miss

    # -----------------------------------------------------------------------

    def set_reverse(self, reverse):
        """Fix the reverse option.

        :param reverse: (bool) If replace is set to True, the mapping will
        replace value by key instead of replacing key by value.

        """
        self._reverse = reverse

    # -----------------------------------------------------------------------

    def set_miss_symbol(self, symbol):
        """Fix the symbol to be used if keep_miss is False.

        :param symbol: (str) US-ASCII symbol to be used in case of a symbol
        is missing of the mapping table.

        """
        self._miss_symbol = str(symbol)

    # -----------------------------------------------------------------------
    # Mapping entries
    # -----------------------------------------------------------------------

    def map_entry(self, entry):
        """Map an entry (a key or a value).

        :param entry: (str) input string to map
        :returns: mapped entry is a string

        """
        if self.is_empty() is True:
            return entry

        if self._reverse is False:
            if self.is_key(entry):
                return self.get(entry)
        else:
            s = self.replace_reversed(entry)
            if len(s) > 0:
                return s

        if self._keep_miss is False:
            return self._miss_symbol

        return entry

    # -----------------------------------------------------------------------

    def map(self, mstr, delimiters=DEFAULT_SEP, separator=""):
        """Run the Mapping process on an input string.

        :param mstr: input string to map
        :param delimiters: (list) list of character delimiters. Default is:\
               [';', ',', ' ', '.', '|', '+', '-']
        :param separator: (char) used to separate parts of the mapped result
        (when longest matching algorithm was used to map a string)
        :returns: a string

        """
        if self.is_empty() is True:
            return mstr

        tab = []
        if len(delimiters) > 0:
            # Suppose that some punctuation are like a separator
            # and we have to replace all strings between them
            pattern = "|".join(map(re.escape, delimiters))
            pattern = "(" + pattern + ")\s*"
            tab = re.split(pattern, mstr)

        else:
            # No delimiters: we apply a longest matching to map.
            # save the current members values to restore them later
            s = self._miss_symbol
            k = self._keep_miss
            # fix values these members to work properly with them
            self._miss_symbol = "UNKNOWN"
            self._keep_miss = False
            # longest matching to map
            i = 0
            j = 0
            maxi = len(mstr)
            while i < maxi:
                i = maxi
                mapped = self.map_entry(mstr[j:i])
                while mapped == self._miss_symbol and j < (i-1):
                    i -= 1
                    mapped = self.map_entry(mstr[j:i])
                tab.append(mstr[j:i])
                j = i
            # restore initial members
            self._miss_symbol = s
            self._keep_miss = k

        map_tab = []
        for v in tab:
            if v in delimiters:
                map_tab.append(v)
            else:
                mapped = self.map_entry(v)
                if mapped == self._miss_symbol:
                    logging.debug('In {:s}, missing symbol {:s}. '
                                  'Mapped into {:s}.'
                                  ''.format(mstr, v, mapped))
                map_tab.append(mapped)

        return separator.join(map_tab)
