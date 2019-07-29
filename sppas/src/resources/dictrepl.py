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

    src.resources.dictrepl.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~

"""
import codecs
import logging

from sppas.src.config import sg
from sppas.src.utils import sppasUnicode, u

from .dumpfile import sppasDumpFile
from .resourcesexc import FileUnicodeError

# ----------------------------------------------------------------------------


class sppasDictRepl(object):
    """A dictionary to manage automated replacements.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2017  Brigitte Bigi

    A dictionary with specific features for language resources.
    The main feature is that values are "accumulated".

    >>>d = sppasDictRepl()
    >>>d.add("key", "v1")
    >>>d.add("key", "v2")
    >>>d.get("key")
    >>>v1|v2
    >>>d.is_value("v1")
    >>>True
    >>>d.is_value("v1|v2")
    >>>False

    """

    REPLACE_SEPARATOR = "|"

    # -----------------------------------------------------------------------

    def __init__(self, dict_filename=None, nodump=False):
        """Create a sppasDictRepl instance.

        :param dict_filename: (str) The dictionary file name (2 columns)
        :param nodump: (bool) Disable the creation of a dump file
        A dump file is a binary version of the dictionary. Its size is greater
        than the original ASCII dictionary but the time to load it is divided
        by two or three.

        """
        self._dict = dict()
        self._filename = ""

        if dict_filename is not None:

            self._filename = dict_filename
            data = None
            dp = sppasDumpFile(dict_filename)

            # Try first to get the dict from a dump file
            # (at least 2 times faster)
            if nodump is False:
                data = dp.load_from_dump()

            # Load from ascii if: 1st load,
            # or dump load error,
            # or dump older than ascii
            if data is None:
                self.load_from_ascii(dict_filename)
                if nodump is False:
                    dp.save_as_dump(self._dict)
            else:
                self._dict = data

    # -----------------------------------------------------------------------

    def get_filename(self):
        """Return the name of the file from which the vocab comes from."""
        return self._filename

    # -----------------------------------------------------------------------
    # Getters
    # -----------------------------------------------------------------------

    def is_key(self, entry):
        """Return True if entry is exactly a key in the dictionary.

        :param entry: (str) Unicode string.

        """

        return u(entry) in self._dict

    # -----------------------------------------------------------------------

    def is_value(self, entry):
        """Return True if entry is a value in the dictionary.

        :param entry: (str) Unicode string.

        """
        s = sppasDictRepl.format_token(entry)

        for v in self._dict.values():
            values = v.split(sppasDictRepl.REPLACE_SEPARATOR)
            for val in values:
                if val == s:
                    return True

        return False

    # -----------------------------------------------------------------------

    def is_value_of(self, key, entry):
        """Return True if entry is a value of a given key in the dictionary.

        :param key: (str) Unicode string.
        :param entry: (str) Unicode string.

        """
        s = sppasDictRepl.format_token(entry)
        v = self.get(key, "")
        values = v.split(sppasDictRepl.REPLACE_SEPARATOR)
        for val in values:
            if val == s:
                return True

        return False

    # -----------------------------------------------------------------------

    def is_unk(self, entry):
        """Return True if entry is not a key in the dictionary.

        :param entry: (str) Unicode string.

        """
        s = sppasDictRepl.format_token(entry)
        return s not in self._dict

    # -----------------------------------------------------------------------

    def is_empty(self):
        """Return True if there is no entry in the dictionary."""
        return len(self._dict) == 0

    # -----------------------------------------------------------------------

    def get(self, entry, substitution=""):
        """Return the value of a key of the dictionary or substitution.

        :param entry: (str) A token to find in the dictionary
        :param substitution: (str) String to return if token is missing of the dict
        :returns: unicode of the replacement or the substitution.

        """
        s = sppasDictRepl.format_token(entry)
        return self._dict.get(s, substitution)

    # -----------------------------------------------------------------------

    def replace(self, key):
        """Return the value of a key or None if key has no replacement."""
        return self.get(key)

    # -----------------------------------------------------------------------

    def replace_reversed(self, value):
        """Return the key(s) of a value or an empty string.

        :param value: (str) value to search
        :returns: a unicode string with all keys, separated by '_', or an empty string if value does not exists.

        """
        s = sppasDictRepl.format_token(value)
        # hum... of course, a value can have more than 1 key!
        keys = []
        for k, v in self._dict.items():
            values = v.split(sppasDictRepl.REPLACE_SEPARATOR)
            for val in values:
                if val == s:
                    keys.append(k)

        if len(keys) == 0:
            return ""

        return sppasDictRepl.REPLACE_SEPARATOR.join(keys)

    # -----------------------------------------------------------------------

    @staticmethod
    def format_token(entry):
        """Remove the CR/LF, tabs, multiple spaces and others... and lower.

        :param entry: (str) a token
        :returns: formatted token

        """
        return sppasUnicode(entry).to_strip()

    # -----------------------------------------------------------------------
    # Setters
    # -----------------------------------------------------------------------

    def add(self, token, repl):
        """Add a new key,value into the dict.

        Add as a new pair or append the value to the existing one with
        a "|" used as separator.

        :param token: (str) string of the token to add
        :param repl: (str) the replacement token

        Both token and repl are converted to unicode (if any) and strip.

        """
        key = sppasDictRepl.format_token(token)
        value = sppasDictRepl.format_token(repl)

        # Check key,value in the dict
        if key in self._dict:
            if self.is_value_of(key, value) is False:
                value = "{0}|{1}".format(self._dict.get(key), value)

        # Append
        self._dict[key] = value

    # -----------------------------------------------------------------------

    def pop(self, entry):
        """Remove an entry, as key.

        :param entry: (str) unicode string of the entry to remove

        """
        s = sppasDictRepl.format_token(entry)
        if s in self._dict:
            self._dict.pop(s)

    # -----------------------------------------------------------------------

    def remove(self, entry):
        """Remove an entry, as key or value.

        :param entry: (str) unicode string of the entry to remove

        """
        s = sppasDictRepl.format_token(entry)
        to_pop = list()
        for k in self._dict.keys():
            if k == s or self.is_value_of(k, entry):
                to_pop.append(k)

        for k in to_pop:
            self._dict.pop(k)

    # -----------------------------------------------------------------------
    # File
    # -----------------------------------------------------------------------

    def load_from_ascii(self, filename):
        """Load a replacement dictionary from an ascii file.

        :param filename: (str) Replacement dictionary file name

        """
        with codecs.open(filename, 'r', sg.__encoding__) as fd:
            try:
                lines = fd.readlines()
            except UnicodeDecodeError:
                raise FileUnicodeError(filename=filename)
            fd.close()

        self._filename = filename
        for line in lines:
            line = " ".join(line.split())
            if len(line) == 0:
                continue

            tab_line = line.split()
            if len(tab_line) < 2:
                continue

            # Add (or modify) the entry in the dict
            key = tab_line[0]
            value = sppasDictRepl.REPLACE_SEPARATOR.join(tab_line[1:])
            self.add(key, value)

    # -----------------------------------------------------------------------

    def save_as_ascii(self, filename):
        """Save the replacement dictionary.

        :param filename: (str)
        :returns: (bool)

        """
        try:
            with codecs.open(filename, 'w', encoding=sg.__encoding__) as output:

                for entry, value in sorted(self._dict.items(),
                                           key=lambda x: x[0]):
                    values = value.split(sppasDictRepl.REPLACE_SEPARATOR)
                    for v in values:
                        output.write("{:s} {:s}\n".format(entry, v.strip()))

        except Exception as e:
            logging.info('Saving file failed due to the following error: {:s}'
                         ''.format(str(e)))
            return False

        return True

    # -----------------------------------------------------------------------
    # Overloads
    # -----------------------------------------------------------------------

    def __str__(self):
        return str(self._dict)

    # -----------------------------------------------------------------------

    def __len__(self):
        return len(self._dict)

    # -----------------------------------------------------------------------

    def __contains__(self, item):
        s = sppasDictRepl.format_token(item)
        return s in self._dict

    # ------------------------------------------------------------------------

    def __iter__(self):
        for a in self._dict:
            yield a

    # ------------------------------------------------------------------------

    def __getitem__(self, item):
        s = sppasDictRepl.format_token(str(item))
        return self._dict[s]
