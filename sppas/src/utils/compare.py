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

    utils.sppasCompare.py
    ~~~~~~~~~~~~~~~~~~~~~~

"""

import logging

from .makeunicode import u
from .makeunicode import text_type
from .makeunicode import binary_type
from .datatype import sppasType

# ---------------------------------------------------------------------------


class sppasCompare(object):
    """Utility class to compare data.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      contact@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2018  Brigitte Bigi

    >>> sc = sppasCompare()
    >>> d1 = {1:"one", 2:"two"}
    >>> d2 = {2:"TWO", 1:"ONE"}
    >>> sc.equals(d1, d2)
    >>> True
    >>> sc.equals_lists(d1.keys(), d2.keys())
    >>> False
    >>> sc.set_case_sensitive(True)
    >>> sc.equals(d1, d2)
    >>> False

    """

    def __init__(self, verbose=False, case_sensitive=False):
        """Create a sppasCompare instance and set options.

        :param verbose: (bool) Print comparison results on stdout
        :param case_sensitive: (bool) Only to compare strings

        """
        self._verbose = verbose
        self._case_sensitive = case_sensitive

    # -----------------------------------------------------------------------

    def set_verbose(self, v):
        """Print comparison results on stdout or not.

        :param v: (bool) Enable or disable verbosity

        """
        self._verbose = bool(v)

    # -----------------------------------------------------------------------

    def set_case_sensitive(self, v):
        """Compare strings with lower/upper case.

        :param v: (bool) Enable or not the case sensitive comparison of strings

        """
        self._case_sensitive = bool(v)

    # -----------------------------------------------------------------------

    def equals(self, data1, data2):
        """Compare two data sets of any type.

        :param data1 (any) The data to compare.
        :param data2 (any) The data to be compared with.
        :returns: (bool) whether the 2 data sets are equals or not

        """
        if data1 is None or data2 is None:
            if self._verbose:
                logging.info("TypeError: None instead of data.")
            return False

        if type(data1) is list:
            return self.equals_lists(data1, data2)

        if sppasType.is_dict(data1) is True:
            return self.equals_dictionaries(data1, data2)

        return self.equals_items(data1, data2)

    # -----------------------------------------------------------------------

    def equals_lists(self, list1, list2):
        """Compare two lists.

        :param list1 (list) The list to compare.
        :param list2 (list) The list to be compared with.
        :returns: (bool) whether the 2 lists are equals or not

        """
        if list1 is None or list2 is None:
            if self._verbose is True:
                logging.info("TypeError: None instead of lists.")
            return False

        if type(list1) != type(list2) or \
           type(list1) is not list or \
           type(list2) is not list:
            if self._verbose is True:
                logging.info("TypeError: Not same types (expected 2 lists).")
            return False

        if len(list1) != len(list2):
            if self._verbose is True:
                logging.info("FALSE: Not the same number of items: {0} {1}."
                             "".format(len(list1), len(list2)))
            return False

        for item1, item2 in zip(list1, list2):

            if sppasType.is_dict(item1) is True:
                items_are_equals = self.equals_dictionaries(item1, item2)
            elif type(item1) is list:
                items_are_equals = self.equals_lists(item1, item2)
            else:
                items_are_equals = self.equals_items(item1, item2)

            if items_are_equals is False:
                return False

        return True

    # -----------------------------------------------------------------------

    def equals_dictionaries(self, dict1, dict2):
        """Compare two dictionaries.

        :param dict1: (dict or collection) The dict to compare.
        :param dict2: (dict or collection) The dict to be compared with.
        :returns: (bool) whether the 2 dictionaries are equals or not

        """
        if dict1 is None or dict2 is None:
            if self._verbose is True:
                logging.info("TypeError: None instead of lists.")
            return False

        if sppasType.is_dict(dict1) is False or \
           sppasType.is_dict(dict2) is False:
            if self._verbose is True:
                logging.info("TypeError: "
                             "Not same types (expected two dictionaries).")
            return False

        shared_keys = set(dict2.keys()) & set(dict2.keys())

        if not len(shared_keys) == len(dict1.keys()) or \
           not len(shared_keys) == len(dict2.keys()):
            if self._verbose is True:
                logging.info("FALSE: not shared keys: {0} vs {1}"
                             "".format(dict1.keys(), dict2.keys()))
            return False

        for key in dict1:

            if sppasType.is_dict(dict1[key]) is True:
                items_are_equals = self.equals_dictionaries(dict1[key],
                                                            dict2[key])
            elif type(dict1[key]) is list:
                items_are_equals = self.equals_lists(dict1[key],
                                                     dict2[key])
            else:
                items_are_equals = self.equals_items(dict1[key],
                                                     dict2[key])

            if items_are_equals is False:
                return False

        return True

    # -----------------------------------------------------------------------

    def equals_items(self, item1, item2):
        """Compare 2 items of type string or numeric.

        :param item1: The string or numeric to compare
        :param item2: The string or numeric to be compared with
        :returns: (bool) whether the 2 items are equals or not

        """
        if isinstance(item1, (text_type, binary_type)) is True:
            return self.equals_strings(item1, item2)

        if type(item1) is float or type(item2) is float:
            if round(item1, 4) != round(item2, 4):
                if self._verbose is True:
                    logging.info("Float values rounded to "
                                 "4 digits are not equals: "
                                 "{:0.4f} != {:0.4f}".format(item1, item2))
                return False
            return True

        if item1 != item2:
            if self._verbose is True:
                logging.info("Not equals: {0} {1}".format(item1, item2))
            return False

        return True

    # -----------------------------------------------------------------------

    def equals_strings(self, item1, item2):
        """Compare 2 data of type string or unicode.

        :param item1: The string to compare
        :param item2: The string to be compared with
        :returns: (bool) whether the 2 items are equals or not

        """
        if isinstance(item1, (text_type, binary_type)) is False or \
           isinstance(item2, (text_type, binary_type)) is False:
            if self._verbose is True:
                logging.info("TypeError: Not same types "
                             "(expected two strings).")
            return False

        if isinstance(item1, binary_type):
            item1 = u(item1)
        if isinstance(item2, binary_type):
            item2 = u(item2)
        if self._case_sensitive is False:
            return item1.lower() == item2.lower()

        return item1 == item2
