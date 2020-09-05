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

    wkps.filedatacompare.py
    ~~~~~~~~~~~~~~~~~~~~~~~~

    This file includes:

        - sppasPathCompare() to search for a value in a path id
          (FilePath.id, FilePath.state, FilePath.expand)

        - sppasRootCompare() to search for a value in a root id
          (FileRoot.id, FileRoot.state, FileRoot.expand)

        - sppasNameCompare() to search for a value in a file name
          (FileName.name)

        - sppasExtensionCompare() to search for a value in the extension of a
          file name (FileName.ext)

        - sppassppasCatReferenceCompare()

        - sppasRefAttributeCompare()

"""

import re

from sppas.src.exceptions import sppasTypeError

from sppas.src.utils.makeunicode import text_type
from sppas.src.structs import sppasBaseCompare

from .filebase import FileBase
from .filestructure import FilePath, FileName
from .fileref import sppasCatReference, sppasRefAttribute
from .filebase import States

# ---------------------------------------------------------------------------


class sppasFileBaseCompare(sppasBaseCompare):
    """Comparison methods for any FileBase.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2020  Brigitte Bigi

    :Example:
    Three different ways to compare a file data content to a given string

        >>> tc = sppasFileBaseCompare()
        >>> tc.exact(FilePath("c:\\Users"), u("c:\\Users"))
        >>> tc.methods['exact'](FilePath("c:\\Users"), u("c:\\Users"))
        >>> tc.get('exact')(FilePath("c:\\Users"), u("c:\\Users"))

    """

    def __init__(self):
        """Create a sppasFileBaseCompare instance."""
        super(sppasFileBaseCompare, self).__init__()

        # Compare the id to a text value
        self.methods['exact'] = sppasFileBaseCompare.exact
        self.methods['iexact'] = sppasFileBaseCompare.iexact
        self.methods['startswith'] = sppasFileBaseCompare.startswith
        self.methods['istartswith'] = sppasFileBaseCompare.istartswith
        self.methods['endswith'] = sppasFileBaseCompare.endswith
        self.methods['iendswith'] = sppasFileBaseCompare.iendswith
        self.methods['contains'] = sppasFileBaseCompare.contains
        self.methods['icontains'] = sppasFileBaseCompare.icontains
        self.methods['regexp'] = sppasFileBaseCompare.regexp

        # Compare state/expand to a boolean value
        self.methods['state'] = sppasFileBaseCompare.state
        self.methods['check'] = sppasFileBaseCompare.check
        self.methods['lock'] = sppasFileBaseCompare.lock

    # -----------------------------------------------------------------------
    # Identifier
    # -----------------------------------------------------------------------

    @staticmethod
    def exact(fb, value):
        """Test if fb strictly matches value.

        :param fb: (FileBase) Instance to compare.
        :param value: (unicode) Unicode string to be compared with.
        :returns: (bool)
        :raises: sppasTypeError

        """
        if isinstance(fb, FileBase) is False:
            raise sppasTypeError(fb, "FileBase")
        if isinstance(value, text_type) is False:
            raise sppasTypeError(value, text_type)

        # perhaps we should test with all systems separators ( '/' or '\' )
        return fb.id == value

    # -----------------------------------------------------------------------

    @staticmethod
    def iexact(fb, value):
        """Test if fb matches value without case sensitive.

        :param fb: (FileBase) Instance to compare.
        :param value: (unicode) Unicode string to be compared with.
        :returns: (bool)
        :raises: sppasTypeError

        """
        if isinstance(fb, FileBase) is False:
            raise sppasTypeError(fb, "FileBase")
        if isinstance(value, text_type) is False:
            raise sppasTypeError(value, text_type)

        return fb.id.lower() == value.lower()

    # -----------------------------------------------------------------------

    @staticmethod
    def startswith(fb, value):
        """Test if fb starts with the characters of the value.

        :param fb: (FileBase) Instance to compare.
        :param value: (unicode) Unicode string to be compared with.
        :returns: (bool)
        :raises: sppasTypeError

        """
        if isinstance(fb, FileBase) is False:
            raise sppasTypeError(fb, "FileBase")
        if isinstance(value, text_type) is False:
            raise sppasTypeError(value, text_type)

        return fb.id.startswith(value)

    # -----------------------------------------------------------------------

    @staticmethod
    def istartswith(fb, value):
        """Case-insensitive startswith.

        :param fb: (FileBase) Instance to compare.
        :param value: (unicode) Unicode string to be compared with.
        :returns: (bool)
        :raises: sppasTypeError

        """
        if isinstance(fb, FileBase) is False:
            raise sppasTypeError(fb, "FileBase")
        if isinstance(value, text_type) is False:
            raise sppasTypeError(value, text_type)

        return fb.id.lower().startswith(value.lower())

    # -----------------------------------------------------------------------

    @staticmethod
    def endswith(fb, value):
        """Test if fb ends with the characters of the value.

        :param fb: (FileBase) Instance to compare.
        :param value: (unicode) Unicode string to be compared with.
        :returns: (bool)
        :raises: sppasTypeError

        """
        if isinstance(fb, FileBase) is False:
            raise sppasTypeError(fb, "FileBase")
        if isinstance(value, text_type) is False:
            raise sppasTypeError(value, text_type)

        return fb.id.endswith(value)

    # -----------------------------------------------------------------------

    @staticmethod
    def iendswith(fb, value):
        """Case-insensitive endswith.

        :param fb: (FileBase) Instance to compare.
        :param value: (unicode) Unicode string to be compared with.
        :returns: (bool)
        :raises: sppasTypeError

        """
        if isinstance(fb, FileBase) is False:
            raise sppasTypeError(fb, "FileBase")
        if isinstance(value, text_type) is False:
            raise sppasTypeError(value, text_type)

        return fb.id.lower().endswith(value.lower())

    # -----------------------------------------------------------------------

    @staticmethod
    def contains(fb, value):
        """Test if fb contains the value.

        :param fb: (FileBase) Instance to compare.
        :param value: (unicode) Unicode string to be compared with.
        :returns: (bool)
        :raises: sppasTypeError

        """
        if isinstance(fb, FileBase) is False:
            raise sppasTypeError(fb, "FileBase")
        if isinstance(value, text_type) is False:
            raise sppasTypeError(value, text_type)

        return value in fb.id

    # -----------------------------------------------------------------------

    @staticmethod
    def icontains(fb, value):
        """Case-insensitive contains.

        :param fb: (FileBase) Instance to compare.
        :param value: (unicode) Unicode string to be compared with.
        :returns: (bool)
        :raises: sppasTypeError

        """
        if isinstance(fb, FileBase) is False:
            raise sppasTypeError(fb, "FileBase")
        if isinstance(value, text_type) is False:
            raise sppasTypeError(value, text_type)

        return value.lower() in fb.id.lower()

    # -----------------------------------------------------------------------

    @staticmethod
    def regexp(fb, pattern):
        """Test if text matches pattern.

        :param fb: (FileBase) Instance to compare.
        :param pattern: (unicode) Pattern to search.
        :returns: (bool)
        :raises: sppasTypeError

        """
        if isinstance(fb, FileBase) is False:
            raise sppasTypeError(fb, "FileBase")
        text = fb.id

        return True if re.match(pattern, text) else False

    # -----------------------------------------------------------------------
    # State
    # -----------------------------------------------------------------------

    @staticmethod
    def state(fb, state):
        if isinstance(fb, FileBase) is False:
            raise sppasTypeError(fb, "FileBase")
        if isinstance(state, int) is False:
            raise sppasTypeError(state, 'States')

        return fb.get_state() == state

    @staticmethod
    def check(fb, value):
        """Compare state member to the given value.

        :param fb: (FileBase) Instance to compare.
        :param value: (bool) Boolean to be compared with.
        :returns: (bool)
        :raises: sppasTypeError

        """
        if isinstance(fb, FileBase) is False:
            raise sppasTypeError(fb, "FileBase")

        #return (fb.state is States().CHECKED) == value
        return (fb.state in (States().CHECKED, States().AT_LEAST_ONE_CHECKED)) == value

    @staticmethod
    def lock(fb, value):
        """Compare state member to the given value.

        :param fb: (FileBase) Instance to compare.
        :param value: (bool) Boolean to be compared with.
        :returns: (bool)
        :raises: sppasTypeError

        """
        if isinstance(fb, FileBase) is False:
            raise sppasTypeError(fb, "FileBase")

        return (fb.state in (States().LOCKED, States().AT_LEAST_ONE_LOCKED)) == value

# ---------------------------------------------------------------------------


class sppasFileStateCompare(sppasBaseCompare):
    """Comparison methods for state of a FileBase.

    :author:       Barthélémy Drabczuk
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2020  Brigitte Bigi

    :Example: 
    
    Three different ways to compare a file data content to a given string

    >>> tc = sppasFileStateCompare()
    >>> tc.state(FileName("oriana1"), States().UNUSED)
    >>> tc.methods['state'](FileName("oriana1"), States().UNUSED)
    >>> tc.get('state')(FileName("oriana1"), States().UNUSED)

    """

    def __init__(self):
        """Create a sppasFileNameExtensionComparator instance."""
        super(sppasFileStateCompare, self).__init__()

        # Compare the state to a given value
        self.methods['state'] = sppasFileStateCompare.state

    @staticmethod
    def state(fb, state):
        if isinstance(fb, FileBase) is False:
            raise sppasTypeError(fb, "FileBase")
        if isinstance(state, int) is False:
            raise sppasTypeError(state, 'States')

        return fb.get_state() == state

# ---------------------------------------------------------------------------


class sppasFileNameCompare(sppasBaseCompare):
    """Comparison methods for FileName id.

    :author:       Barthélémy Drabczuk
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2020  Brigitte Bigi

    :Example: Three different ways to compare a file data content to a given string

    >>> tc = sppasFileNameCompare()
    >>> tc.exact(FileName("oriana1"), u("oriana1"))
    >>> tc.methods['exact'](FileName("oriana1"), u("oriana1"))
    >>> tc.get('exact')(FileName("oriana1"), u("oriana1"))

    """

    def __init__(self):
        """Create a sppasRootCompare instance."""
        super(sppasFileNameCompare, self).__init__()

        # Compare the id to a text value
        self.methods['exact'] = sppasFileNameCompare.exact
        self.methods['iexact'] = sppasFileNameCompare.iexact
        self.methods['startswith'] = sppasFileNameCompare.startswith
        self.methods['istartswith'] = sppasFileNameCompare.istartswith
        self.methods['endswith'] = sppasFileNameCompare.endswith
        self.methods['iendswith'] = sppasFileNameCompare.iendswith
        self.methods['contains'] = sppasFileNameCompare.contains
        self.methods['icontains'] = sppasFileNameCompare.icontains
        self.methods['regexp'] = sppasFileNameCompare.regexp

    # -----------------------------------------------------------------------
    # FileName name
    # -----------------------------------------------------------------------

    @staticmethod
    def exact(fn, value):
        """Test if name strictly matches value.

        :param fn: (FileName) Name to compare.
        :param value: (unicode) Unicode string to be compared with.
        :returns: (bool)
        :raises: sppasTypeError

        """
        if isinstance(fn, FileName) is False:
            raise sppasTypeError(fn, "FileName")
        if isinstance(value, text_type) is False:
            raise sppasTypeError(value, text_type)

        # perhaps we should test with all systems separators ( '/' or '\' )
        return fn.name == value

    # -----------------------------------------------------------------------

    @staticmethod
    def iexact(fn, value):
        """Test if name matches value without case sensitive.

        :param fn: (FileName) Name to compare.
        :param value: (unicode) Unicode string to be compared with.
        :returns: (bool)
        :raises: sppasTypeError

        """
        if isinstance(fn, FileName) is False:
            raise sppasTypeError(fn, "FileName")
        if isinstance(value, text_type) is False:
            raise sppasTypeError(value, text_type)

        return fn.name.lower() == value.lower()

    # -----------------------------------------------------------------------

    @staticmethod
    def startswith(fn, value):
        """Test if name starts with the characters of the value.

        :param fn: (FileName) Name to compare.
        :param value: (unicode) Unicode string to be compared with.
        :returns: (bool)
        :raises: sppasTypeError

        """
        if isinstance(fn, FileName) is False:
            raise sppasTypeError(fn, "FileName")
        if isinstance(value, text_type) is False:
            raise sppasTypeError(value, text_type)

        return fn.name.startswith(value)

    # -----------------------------------------------------------------------

    @staticmethod
    def istartswith(fn, value):
        """Case-insensitive startswith.

        :param fn: (FileName) Name to compare.
        :param value: (unicode) Unicode string to be compared with.
        :returns: (bool)
        :raises: sppasTypeError

        """
        if isinstance(fn, FileName) is False:
            raise sppasTypeError(fn, "FileName")
        if isinstance(value, text_type) is False:
            raise sppasTypeError(value, text_type)

        return fn.name.lower().startswith(value.lower())

    # -----------------------------------------------------------------------

    @staticmethod
    def endswith(fn, value):
        """Test if name ends with the characters of the value.

        :param fn: (FileName) Name to compare.
        :param value: (unicode) Unicode string to be compared with.
        :returns: (bool)
        :raises: sppasTypeError

        """
        if isinstance(fn, FileName) is False:
            raise sppasTypeError(fn, "FileName")
        if isinstance(value, text_type) is False:
            raise sppasTypeError(value, text_type)

        return fn.name.endswith(value)

    # -----------------------------------------------------------------------

    @staticmethod
    def iendswith(fn, value):
        """Case-insensitive endswith.

        :param fn: (FileName) Name to compare.
        :param value: (unicode) Unicode string to be compared with.
        :returns: (bool)
        :raises: sppasTypeError

        """
        if isinstance(fn, FileName) is False:
            raise sppasTypeError(fn, "FileName")
        if isinstance(value, text_type) is False:
            raise sppasTypeError(value, text_type)

        return fn.name.lower().endswith(value.lower())

    # -----------------------------------------------------------------------

    @staticmethod
    def contains(fn, value):
        """Test if the name contains the value.

        :param fn: (FileName) Name to compare.
        :param value: (unicode) Unicode string to be compared with.
        :returns: (bool)
        :raises: sppasTypeError

        """
        if isinstance(fn, FileName) is False:
            raise sppasTypeError(fn, "FileName")
        if isinstance(value, text_type) is False:
            raise sppasTypeError(value, text_type)

        return value in fn.name

    # -----------------------------------------------------------------------

    @staticmethod
    def icontains(fn, value):
        """Case-insensitive contains.

        :param fn: (FileName) Name to compare.
        :param value: (unicode) Unicode string to be compared with.
        :returns: (bool)
        :raises: sppasTypeError

        """
        if isinstance(fn, FileName) is False:
            raise sppasTypeError(fn, "FileName")
        if isinstance(value, text_type) is False:
            raise sppasTypeError(value, text_type)

        return value.lower() in fn.name.lower()

    # -----------------------------------------------------------------------

    @staticmethod
    def regexp(fn, pattern):
        """Test if text matches pattern.

        :param fn: (FileName) Name to compare.
        :param pattern: (unicode) Pattern to search.
        :returns: (bool)
        :raises: sppasTypeError

        """
        if isinstance(fn, FileName) is False:
            raise sppasTypeError(fn, "FileName")
        text = fn.name

        return True if re.match(pattern, text) else False

# ---------------------------------------------------------------------------


class sppasFileExtCompare(sppasBaseCompare):
    """Comparison methods for FileName extension.

    :author:       Barthélémy Drabczuk
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2020  Brigitte Bigi

    :Example:
    Three different ways to compare a file data content to a given string

    >>> tc = sppasFileExtCompare()
    >>> tc.exact(FileName("oriana1"), u("oriana1"))
    >>> tc.methods['exact'](FileName("oriana1"), u("oriana1"))
    >>> tc.get('exact')(FileName("oriana1"), u("oriana1"))

    """

    def __init__(self):
        """Create a sppasFileNameExtensionComparator instance."""
        super(sppasFileExtCompare, self).__init__()

        # Compare the id to a text value
        self.methods['exact'] = sppasFileExtCompare.exact
        self.methods['iexact'] = sppasFileExtCompare.iexact
        self.methods['startswith'] = sppasFileExtCompare.startswith
        self.methods['istartswith'] = sppasFileExtCompare.istartswith
        self.methods['endswith'] = sppasFileExtCompare.endswith
        self.methods['iendswith'] = sppasFileExtCompare.iendswith
        self.methods['contains'] = sppasFileExtCompare.contains
        self.methods['icontains'] = sppasFileExtCompare.icontains
        self.methods['regexp'] = sppasFileExtCompare.regexp

    # -----------------------------------------------------------------------
    # FileName Extension
    # -----------------------------------------------------------------------

    @staticmethod
    def exact(fn, value):
        """Test if name strictly matches value.

        :param fn: (FileName) 
        :param value: (unicode) Unicode string to be compared with.
        :returns: (bool)
        :raises: sppasTypeError

        """
        if isinstance(fn, FileName) is False:
            raise sppasTypeError(fn, "FileName")
        if isinstance(value, text_type) is False:
            raise sppasTypeError(value, text_type)

        # perhaps we should test with all systems separators ( '/' or '\' )
        return fn.extension == value

    # -----------------------------------------------------------------------

    @staticmethod
    def iexact(fn, value):
        """Test if extension matches value without case sensitive.

        :param fn: (FileName) 
        :param value: (unicode) Unicode string to be compared with.
        :returns: (bool)
        :raises: sppasTypeError

        """
        if isinstance(fn, FileName) is False:
            raise sppasTypeError(fn, "FileName")
        if isinstance(value, text_type) is False:
            raise sppasTypeError(value, text_type)

        return fn.extension.lower() == value.lower()

    # -----------------------------------------------------------------------

    @staticmethod
    def startswith(fn, value):
        """Test if extension starts with the characters of the value.

        :param fn: (FileName) 
        :param value: (unicode) Unicode string to be compared with.
        :returns: (bool)
        :raises: sppasTypeError

        """
        if isinstance(fn, FileName) is False:
            raise sppasTypeError(fn, "FileName")
        if isinstance(value, text_type) is False:
            raise sppasTypeError(value, text_type)

        return fn.extension.startswith(value)

    # -----------------------------------------------------------------------

    @staticmethod
    def istartswith(fn, value):
        """Case-insensitive startswith.

        :param fn: (FileName) 
        :param value: (unicode) Unicode string to be compared with.
        :returns: (bool)
        :raises: sppasTypeError

        """
        if isinstance(fn, FileName) is False:
            raise sppasTypeError(fn, "FileName")
        if isinstance(value, text_type) is False:
            raise sppasTypeError(value, text_type)

        return fn.extension.lower().startswith(value.lower())

    # -----------------------------------------------------------------------

    @staticmethod
    def endswith(fn, value):
        """Test if extension ends with the characters of the value.

        :param fn: (FileName) 
        :param value: (unicode) Unicode string to be compared with.
        :returns: (bool)
        :raises: sppasTypeError

        """
        if isinstance(fn, FileName) is False:
            raise sppasTypeError(fn, "FileName")
        if isinstance(value, text_type) is False:
            raise sppasTypeError(value, text_type)

        return fn.extension.endswith(value)

    # -----------------------------------------------------------------------

    @staticmethod
    def iendswith(fn, value):
        """Case-insensitive endswith.

        :param fn: (FileName) 
        :param value: (unicode) Unicode string to be compared with.
        :returns: (bool)
        :raises: sppasTypeError

        """
        if isinstance(fn, FileName) is False:
            raise sppasTypeError(fn, "FileName")
        if isinstance(value, text_type) is False:
            raise sppasTypeError(value, text_type)

        return fn.extension.lower().endswith(value.lower())

    # -----------------------------------------------------------------------

    @staticmethod
    def contains(fn, value):
        """Test if the name contains the value.

        :param fn: (FileName) 
        :param value: (unicode) Unicode string to be compared with.
        :returns: (bool)
        :raises: sppasTypeError

        """
        if isinstance(fn, FileName) is False:
            raise sppasTypeError(fn, "FileName")
        if isinstance(value, text_type) is False:
            raise sppasTypeError(value, text_type)

        return value in fn.extension

    # -----------------------------------------------------------------------

    @staticmethod
    def icontains(fn, value):
        """Case-insensitive contains.

        :param fn: (FileName) 
        :param value: (unicode) Unicode string to be compared with.
        :returns: (bool)
        :raises: sppasTypeError

        """
        if isinstance(fn, FileName) is False:
            raise sppasTypeError(fn, "FileName")
        if isinstance(value, text_type) is False:
            raise sppasTypeError(value, text_type)

        return value.lower() in fn.extension.lower()

    # -----------------------------------------------------------------------

    @staticmethod
    def regexp(fn, pattern):
        """Test if text matches pattern.

        :param fn: (FileName) 
        :param pattern: (unicode) Pattern to search.
        :returns: (bool)
        :raises: sppasTypeError

        """
        if isinstance(fn, FileName) is False:
            raise sppasTypeError(fn, "FileName")
        text = fn.extension

        return True if re.match(pattern, text) else False

# ---------------------------------------------------------------------------


class sppasFileRefCompare(sppasBaseCompare):
    """Comparison methods for sppasCatReference id.

    :author:       Barthélémy Drabczuk
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2020  Brigitte Bigi

    :Example:
    Three different ways to compare a file data content to a given string

    >>> tc = sppasFileRefCompare()
    >>> tc.exact(sppasCatReference("mic"), u("mic"))
    >>> tc.methods['exact'](sppasCatReference("mic"), u("mic"))
    >>> tc.get('exact')(sppasCatReference("mic"), u("mic"))

    """

    def __init__(self):
        """Create a sppasFileRefCompare instance."""
        super(sppasFileRefCompare, self).__init__()

        # Compare the id to a text value
        self.methods['exact'] = sppasFileRefCompare.exact
        self.methods['iexact'] = sppasFileRefCompare.iexact
        self.methods['startswith'] = sppasFileRefCompare.startswith
        self.methods['istartswith'] = sppasFileRefCompare.istartswith
        self.methods['endswith'] = sppasFileRefCompare.endswith
        self.methods['iendswith'] = sppasFileRefCompare.iendswith
        self.methods['contains'] = sppasFileRefCompare.contains
        self.methods['icontains'] = sppasFileRefCompare.icontains
        self.methods['regexp'] = sppasFileRefCompare.regexp

    # -----------------------------------------------------------------------
    # Reference Id
    # -----------------------------------------------------------------------

    @staticmethod
    def exact(cat, value):
        """Test if the id strictly matches value.

        :param cat: (sppasCatReference)
        :param value: (unicode) Unicode string to be compared with.
        :returns: (bool)
        :raises: sppasTypeError

        """
        if isinstance(cat, sppasCatReference) is False:
            raise sppasTypeError(cat, "Reference")
        if isinstance(value, text_type) is False:
            raise sppasTypeError(value, text_type)

        # perhaps we should test with all systems separators ( '/' or '\' )
        return cat.id == value

    # -----------------------------------------------------------------------

    @staticmethod
    def iexact(cat, value):
        """Test if the id matches value without case sensitive.

        :param cat: (sppasCatReference)
        :param value: (unicode) Unicode string to be compared with.
        :returns: (bool)
        :raises: sppasTypeError

        """
        if isinstance(cat, sppasCatReference) is False:
            raise sppasTypeError(cat, "Reference")
        if isinstance(value, text_type) is False:
            raise sppasTypeError(value, text_type)

        return cat.id.lower() == value.lower()

    # -----------------------------------------------------------------------

    @staticmethod
    def startswith(cat, value):
        """Test if the id starts with the characters of the value.

        :param cat: (sppasCatReference)
        :param value: (unicode) Unicode string to be compared with.
        :returns: (bool)
        :raises: sppasTypeError

        """
        if isinstance(cat, sppasCatReference) is False:
            raise sppasTypeError(cat, "Reference")
        if isinstance(value, text_type) is False:
            raise sppasTypeError(value, text_type)

        return cat.id.startswith(value)

    # -----------------------------------------------------------------------

    @staticmethod
    def istartswith(cat, value):
        """Case-insensitive startswith.

        :param cat: (sppasCatReference)
        :param value: (unicode) Unicode string to be compared with.
        :returns: (bool)
        :raises: sppasTypeError

        """
        if isinstance(cat, sppasCatReference) is False:
            raise sppasTypeError(cat, "Reference")
        if isinstance(value, text_type) is False:
            raise sppasTypeError(value, text_type)

        return cat.id.lower().startswith(value.lower())

    # -----------------------------------------------------------------------

    @staticmethod
    def endswith(cat, value):
        """Test if the id ends with the characters of the value.

        :param cat: (sppasCatReference)
        :param value: (unicode) Unicode string to be compared with.
        :returns: (bool)
        :raises: sppasTypeError

        """
        if isinstance(cat, sppasCatReference) is False:
            raise sppasTypeError(cat, "Reference")
        if isinstance(value, text_type) is False:
            raise sppasTypeError(value, text_type)

        return cat.id.endswith(value)

    # -----------------------------------------------------------------------

    @staticmethod
    def iendswith(cat, value):
        """Case-insensitive endswith.

        :param cat: (sppasCatReference)
        :param value: (unicode) Unicode string to be compared with.
        :returns: (bool)
        :raises: sppasTypeError

        """
        if isinstance(cat, sppasCatReference) is False:
            raise sppasTypeError(cat, "Reference")
        if isinstance(value, text_type) is False:
            raise sppasTypeError(value, text_type)

        return cat.id.lower().endswith(value.lower())

    # -----------------------------------------------------------------------

    @staticmethod
    def contains(cat, value):
        """Test if the id contains the value.

        :param cat: (sppasCatReference)
        :param value: (unicode) Unicode string to be compared with.
        :returns: (bool)
        :raises: sppasTypeError

        """
        if isinstance(cat, sppasCatReference) is False:
            raise sppasTypeError(cat, "Reference")
        if isinstance(value, text_type) is False:
            raise sppasTypeError(value, text_type)

        return value in cat.id

    # -----------------------------------------------------------------------

    @staticmethod
    def icontains(cat, value):
        """Case-insensitive contains.

        :param cat: (sppasCatReference)
        :param value: (unicode) Unicode string to be compared with.
        :returns: (bool)
        :raises: sppasTypeError

        """
        if isinstance(cat, sppasCatReference) is False:
            raise sppasTypeError(cat, "Reference")
        if isinstance(value, text_type) is False:
            raise sppasTypeError(value, text_type)

        return value.lower() in cat.id.lower()

    # -----------------------------------------------------------------------

    @staticmethod
    def regexp(cat, pattern):
        """Test if id matches pattern.

        :param cat: (sppasCatReference)
        :param pattern: (unicode) Pattern to search.
        :returns: (bool)
        :raises: sppasTypeError

        """
        if isinstance(cat, sppasCatReference) is False:
            raise sppasTypeError(cat, "FileName")
        text = cat.id

        return True if re.match(pattern, text) else False

# ---------------------------------------------------------------------------


class sppasRefAttributeCompare(sppasBaseCompare):
    """Comparison methods for sppasRefAttribute.

    :author:       Barthélémy Drabczuk
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2020  Brigitte Bigi

    """

    def __init__(self):
        """Create a sppassppasRefAttributeCompare instance."""
        super(sppasRefAttributeCompare, self).__init__()

        # Compare the value to a text value
        self.methods['exact'] = sppasRefAttributeCompare.exact
        self.methods['iexact'] = sppasRefAttributeCompare.iexact
        self.methods['startswith'] = sppasRefAttributeCompare.startswith
        self.methods['istartswith'] = sppasRefAttributeCompare.istartswith
        self.methods['endswith'] = sppasRefAttributeCompare.endswith
        self.methods['iendswith'] = sppasRefAttributeCompare.iendswith
        self.methods['contains'] = sppasRefAttributeCompare.contains
        self.methods['icontains'] = sppasRefAttributeCompare.icontains
        self.methods['regexp'] = sppasRefAttributeCompare.regexp

        # Compare the value to a numeric value
        self.methods['equal'] = sppasRefAttributeCompare.equals
        self.methods['iequal'] = sppasRefAttributeCompare.iequals
        self.methods['fequal'] = sppasRefAttributeCompare.fequals
        self.methods['gt'] = sppasRefAttributeCompare.gt
        self.methods['ge'] = sppasRefAttributeCompare.ge
        self.methods['lt'] = sppasRefAttributeCompare.lt
        self.methods['le'] = sppasRefAttributeCompare.le

    # -----------------------------------------------------------------------
    # Reference sppasRefAttribute
    # -----------------------------------------------------------------------

    @staticmethod
    def exact(att, value):
        """Test if the attribute value strictly matches value.

        :param att: (sppasRefAttribute)
        :param value: (str) Unicode string to be compared with.
        :returns: (bool)
        :raises: sppasTypeError

        """
        if isinstance(att, sppasRefAttribute) is False:
            raise sppasTypeError(att, "sppasRefAttribute")
        if not isinstance(value, text_type):
            raise sppasTypeError(value, text_type)

        return att.get_value() == value

    # -----------------------------------------------------------------------

    @staticmethod
    def iexact(att, value):
        """Test if the att matches value without case sensitive.

        :param att: (sppasRefAttribute)
        :param value: (unicode) Unicode string to be compared with.
        :returns: (bool)
        :raises: sppasTypeError

        """
        if isinstance(att, sppasRefAttribute) is False:
            raise sppasTypeError(att, "sppasRefAttribute")
        if not isinstance(value, text_type):
            raise sppasTypeError(value, text_type)

        return att.get_value().lower() == value.lower()

    # -----------------------------------------------------------------------

    @staticmethod
    def startswith(att, value):
        """Test if the att starts with the characters of the value.

        :param att: (sppasRefAttribute)
        :param value: (unicode) Unicode string to be compared with.
        :returns: (bool)
        :raises: sppasTypeError

        """
        if isinstance(att, sppasRefAttribute) is False:
            raise sppasTypeError(att, "sppasRefAttribute")
        if not isinstance(value, text_type):
            raise sppasTypeError(value, text_type)

        return att.get_value().startswith(value)

    # -----------------------------------------------------------------------

    @staticmethod
    def istartswith(att, value):
        """Case-insensitive startswith.

        :param att: (sppasRefAttribute)
        :param value: (unicode) Unicode string to be compared with.
        :returns: (bool)
        :raises: sppasTypeError

        """
        if isinstance(att, sppasRefAttribute) is False:
            raise sppasTypeError(att, "sppasRefAttribute")
        if not isinstance(value, text_type):
            raise sppasTypeError(value, text_type)

        return att.get_value().lower().startswith(value.lower())

    # -----------------------------------------------------------------------

    @staticmethod
    def endswith(att, value):
        """Test if the att ends with the characters of the value.

        :param att: (sppasRefAttribute)
        :param value: (unicode) Unicode string to be compared with.
        :returns: (bool)
        :raises: sppasTypeError

        """
        if isinstance(att, sppasRefAttribute) is False:
            raise sppasTypeError(att, "sppasRefAttribute")
        if not isinstance(value, text_type):
            raise sppasTypeError(value, text_type)

        return att.get_value().endswith(value)

    # -----------------------------------------------------------------------

    @staticmethod
    def iendswith(att, value):
        """Case-insensitive endswith.

        :param cat: (sppasCatReference)
        :param value: (unicode) Unicode string to be compared with.
        :returns: (bool)
        :raises: sppasTypeError

        """
        if isinstance(att, sppasRefAttribute) is False:
            raise sppasTypeError(att, "sppasRefAttribute")
        if not isinstance(value, text_type):
            raise sppasTypeError(value, text_type)

        return att.get_value().lower().endswith(value.lower())

    # -----------------------------------------------------------------------

    @staticmethod
    def contains(att, value):
        """Test if the att contains the value.

        :param att: (sppasRefAttribute)
        :param value: (unicode) Unicode string to be compared with.
        :returns: (bool)
        :raises: sppasTypeError

        """
        if isinstance(att, sppasRefAttribute) is False:
            raise sppasTypeError(att, "sppasRefAttribute")
        if not isinstance(value, text_type):
            raise sppasTypeError(value, text_type)

        return value in att.get_value()

    # -----------------------------------------------------------------------

    @staticmethod
    def icontains(att, value):
        """Case-insensitive contains.

        :param att: (sppasRefAttribute)
        :param value: (unicode) Unicode string to be compared with.
        :returns: (bool)
        :raises: sppasTypeError

        """
        if isinstance(att, sppasRefAttribute) is False:
            raise sppasTypeError(att, "sppasRefAttribute")
        if not isinstance(value, text_type):
            raise sppasTypeError(value, text_type)

        return value.lower() in att.get_value().lower()

    # -----------------------------------------------------------------------

    @staticmethod
    def regexp(att, pattern):
        """Test if att matches pattern.

        :param att: (sppasRefAttribute)
        :param pattern: (unicode) Pattern to search.
        :returns: (bool)
        :raises: sppasTypeError

        """
        if isinstance(att, sppasRefAttribute) is False:
            raise sppasTypeError(att, "sppasRefAttribute")
        text = att.get_value()

        return True if re.match(pattern, text) else False

    # -----------------------------------------------------------------------

    @staticmethod
    def equals(att, value):
        """Test if att equals the given value.

        :param att: (sppasRefAttribute)
        :param value: (number) Pattern to search.
        :returns: (bool)
        :raises: sppasTypeError

        """
        if isinstance(att, sppasRefAttribute) is False:
            raise sppasTypeError(att, "sppasRefAttribute")
        if isinstance(value, (int, float)) is False:
            raise sppasTypeError(value, "int, float")

        return att.get_typed_value() == value

    # -----------------------------------------------------------------------

    @staticmethod
    def iequals(att, value):
        """Test if att equals the given value.

        :param att: (sppasRefAttribute)
        :param value: (number) Pattern to search.
        :returns: (bool)
        :raises: sppasTypeError

        """
        if isinstance(att, sppasRefAttribute) is False:
            raise sppasTypeError(att, "sppasRefAttribute")
        if isinstance(value, int) is False:
            raise sppasTypeError(value, "int")

        return att.get_typed_value() == value

    # -----------------------------------------------------------------------

    @staticmethod
    def fequals(att, value, precision=0.):
        """Test if att equals the given value.

        :param att: (sppasRefAttribute)
        :param value: (number) Pattern to search.
        :param precision: (number) Vagueness around the value
        :returns: (bool)
        :raises: sppasTypeError

        """
        if isinstance(att, sppasRefAttribute) is False:
            raise sppasTypeError(att, "sppasRefAttribute")
        if isinstance(value, float) is False:
            raise sppasTypeError(value, "float")

        return value - precision < att.get_typed_value() < value + precision

    # -----------------------------------------------------------------------

    @staticmethod
    def gt(att, value):
        """Test if att is strictly greater than the given value.

        :param att: (sppasRefAttribute)
        :param value: (number) Pattern to search.
        :returns: (bool)
        :raises: sppasTypeError

        """
        if isinstance(att, sppasRefAttribute) is False:
            raise sppasTypeError(att, "sppasRefAttribute")
        if isinstance(value, (int, float)) is False:
            raise sppasTypeError(value, "int, float")

        return att.get_typed_value() > value

    # -----------------------------------------------------------------------

    @staticmethod
    def ge(att, value):
        """Test if att is greater than or equal to the given value.

        :param att: (sppasRefAttribute)
        :param value: (number) Pattern to search.
        :returns: (bool)
        :raises: sppasTypeError

        """
        if isinstance(att, sppasRefAttribute) is False:
            raise sppasTypeError(att, "sppasRefAttribute")
        if isinstance(value, (int, float)) is False:
            raise sppasTypeError(value, "int, float")

        return att.get_typed_value() >= value

    # -----------------------------------------------------------------------

    @staticmethod
    def lt(att, value):
        """Test if att is less than the given value.

        :param att: (sppasRefAttribute)
        :param value: (number) Pattern to search.
        :returns: (bool)
        :raises: sppasTypeError

        """
        if isinstance(att, sppasRefAttribute) is False:
            raise sppasTypeError(att, "sppasRefAttribute")
        if isinstance(value, (int, float)) is False:
            raise sppasTypeError(value, "int, float")

        return att.get_typed_value() < value

    # -----------------------------------------------------------------------

    @staticmethod
    def le(att, value):
        """Test if att is less than or equal to the given value.

        :param att: (sppasRefAttribute)
        :param value: (number) Pattern to search.
        :returns: (bool)
        :raises: sppasTypeError

        """
        if isinstance(att, sppasRefAttribute) is False:
            raise sppasTypeError(att, "sppasRefAttribute")
        if isinstance(value, (int, float)) is False:
            raise sppasTypeError(value, "int, float")

        return att.get_typed_value() <= value

