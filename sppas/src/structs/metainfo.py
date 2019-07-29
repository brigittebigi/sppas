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

    structs.metainfo.py
    ~~~~~~~~~~~~~~~~~~~~

"""

import collections

from sppas.src.utils import u

from .structsexc import MetaKeyError

# ---------------------------------------------------------------------------


class sppasMetaInfo(object):
    """Meta information manager.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2019  Brigitte Bigi

    Meta-information is a sorted collection of pairs (key, value) where
    value is a tuple with first argument of type boolean to indicate the
    state of the key: enabled/disabled.

    Manage meta information of type (key,value). Allows to enable/disable
    each one. Keys are unicode strings, and values can be of any type.

    >>> m = sppasMetaInfo()
    >>> m.add_metainfo('author', 'Brigitte Bigi')
    >>> m.add_metainfo('version', (1,8,2))

    """

    def __init__(self):
        """Create a new sppasMetaInfo instance.

        """
        super(sppasMetaInfo, self).__init__()
        self._metainfo = collections.OrderedDict()

    # -----------------------------------------------------------------------

    def is_enable_metainfo(self, key):
        """Return the status of a given key.

        :param key: (str) The key of the meta-information
        :raises: MetaKeyError

        """
        if u(key) not in self._metainfo:
            raise MetaKeyError(key)

        return self._metainfo[u(key)][0]

    # -----------------------------------------------------------------------

    def get_metainfo(self, key):
        """Return the value of a given key.

        :param key: (str) The key of the meta-information
        :raises: MetaKeyError

        """
        if u(key) not in self._metainfo:
            raise MetaKeyError(key)

        return self._metainfo[u(key)][1]

    # -----------------------------------------------------------------------

    def enable_metainfo(self, key, value=True):
        """Enable/Disable a meta information.

        :param key: (str) The key of the meta-information
        :param value: (bool) Status of the meta-information
        :raises: MetaKeyError

        """
        if u(key) not in self._metainfo.keys():
            raise MetaKeyError(key)

        self._metainfo[u(key)][0] = bool(value)

    # -----------------------------------------------------------------------

    def add_metainfo(self, key, strv):
        """Fix a meta information or update it.

        :param key: (str) The key of the meta-information
        :param strv: (str)

        """
        self._metainfo[u(key)] = [True, strv]

    # -----------------------------------------------------------------------

    def pop_metainfo(self, key):
        """Pop a meta information.

        :param key: (str) The key of the meta-information
        :raises: MetaKeyError

        """
        if u(key) not in self._metainfo.keys():
            raise MetaKeyError(key)

        del self._metainfo[u(key)]

    # -----------------------------------------------------------------------

    def keys_enabled(self):
        """Return a list of the keys of enabled meta information.

        :returns: list of unicode strings

        """
        return [key for key in self._metainfo.keys()
                if self._metainfo[key][0] is True]

    # -----------------------------------------------------------------------
    # Overloads
    # -----------------------------------------------------------------------

    def __len__(self):
        """Return the number of meta info (enabled+disabled)."""
        return len(self._metainfo)
