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

    src.wkps.filedatafilters.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    A comparator must be implemented to define comparison functions. Then
    the method 'match' of the FileBase class can be invoked.
    The FileDataFilter() class is based on the use of this solution. It allows
    to combine results and is a simplified way to write a request.
    The use of the FileBase().match() is described in the next examples.

    :Example: Search if a FilePath() is exactly matching "my_path":

        >>> cmp = sppasFileBaseCompare()
        >>> fp.match([(cmp.exact, "my_path", False)])

    :Example: Search if a FilePath() is starting with "my_path" and is checked:

        >>> fp.match(
        >>>     [(cmp.startswith, "my_path", False),
        >>>      (cmp.state, True, False)],
        >>>     logic_bool="and")


    :Example: Search if a FileRoot() is exactly matching "my_path/toto":

        >>> cmp = sppasFileBaseCompare()
        >>> fr.match([(cmp.exact, "my_path", False)])

    :Example: Search if a FileRoot() is starting with "my_path/toto"
    and is checked:

        >>> fr.match(
        >>>     [(cmp.startswith, "my_path/toto", False),
        >>>      (cmp.state, True, False)],
        >>>     logic_bool="and")

    :Example: Search if a FileName() is starting with "toto" and is not
    a TextGrid and is checked:

        >>> cmpn = sppasNameCompare()
        >>> cmpe = sppasExtensionCompare()
        >>> cmpp = sppasFileBaseCompare()
        >>> fn.match(
        >>>    [(cmpn.startswith, "toto", False),
        >>>     (cmpe.iexact, "textgrid", True),
        >>>     (cmpp.state, True, False)],
        >>>    logic_bool="and")

"""

from sppas.src.structs import sppasBaseFilters
from sppas.src.structs import sppasBaseSet

from .fileref import sppasAttribute
from .filedatacompare import sppasFileBaseCompare
from .filedatacompare import sppasFileNameCompare
from .filedatacompare import sppasFileExtCompare
from .filedatacompare import sppasFileRefCompare
from .filedatacompare import sppasAttributeCompare

# ---------------------------------------------------------------------------


class sppasFileDataFilters(sppasBaseFilters):
    """This class implements the 'SPPAS file data filter system'.

    :author:       Brigitte Bigi, Barthélémy Drabczuk
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2019  Brigitte Bigi

    Search in file data.

    :Example:

        >>> # Search for all checked TextGrid files in a path containing 'corpus'
        >>> f = sppasFileDataFilters(data)
        >>> f.path(contains='corpus') & f.file(state=True) & f.extension(iexact='textgrid')

    """

    def __init__(self, obj):
        """Create a sppasFileDataFilters instance.

        :param obj: (sppasWorkspace) The object to be filtered.

        """
        super(sppasFileDataFilters, self).__init__(obj)

    # -----------------------------------------------------------------------
    # Paths/Roots/Files
    # -----------------------------------------------------------------------

    def path(self, **kwargs):
        """Apply functions on all paths of the object.

        Each argument is made of a function name and its expected value.
        Each function can be prefixed with 'not_', like in the next example.

        :Example:

            >>> f.path(startswith="c:\\users\myname", not_endswith='a', logic_bool="and")
            >>> f.path(startswith="c:\\users\myname") & f.path(not_endswith='a')
            >>> f.path(startswith="c:\\users\myname") | f.path(startswith="ta")

        :param kwargs: logic_bool/any sppasPathCompare() method.
        :returns: (sppasDataSet) Set of FileName() instances

        """
        comparator = sppasFileBaseCompare()

        # extract the information from the arguments
        sppasBaseFilters.test_args(comparator, **kwargs)
        logic_bool = sppasBaseFilters.fix_logic_bool(**kwargs)
        path_fct_values = sppasBaseFilters.fix_function_values(comparator, **kwargs)
        path_functions = sppasBaseFilters.fix_functions(comparator, **kwargs)

        # the set of results
        data = sppasBaseSet()

        # search for the data to be returned:
        for path in self.obj:

            is_matching = path.match(path_functions, logic_bool)
            if is_matching is True:
                # append all files of the path
                for fr in path:
                    for fn in fr:
                        data.append(fn, path_fct_values)

        return data

    # -----------------------------------------------------------------------

    def root(self, **kwargs):
        """Apply functions on all roots of the object.

        Each argument is made of a function name and its expected value.
        Each function can be prefixed with 'not_', like in the next example.

        :Example:

            >>> f.root(startswith="myfile", not_endswith='a', logic_bool="and")
            >>> f.root(startswith="myfile") & f.root(not_endswith='a')
            >>> f.root(startswith="myfile") | f.root(startswith="ta")

        :param kwargs: logic_bool/any sppasRootCompare() method.
        :returns: (sppasDataSet) Set of FileName() instances

        """
        comparator = sppasFileBaseCompare()

        # extract the information from the arguments
        sppasBaseFilters.test_args(comparator, **kwargs)
        logic_bool = sppasBaseFilters.fix_logic_bool(**kwargs)
        path_fct_values = sppasBaseFilters.fix_function_values(comparator, **kwargs)
        path_functions = sppasBaseFilters.fix_functions(comparator, **kwargs)

        # the set of results
        data = sppasBaseSet()

        # search for the data to be returned:
        for path in self.obj:
            for root in path:
                is_matching = root.match(path_functions, logic_bool)
                if is_matching is True:
                    # append all files of the path
                    for fn in root:
                        data.append(fn, path_fct_values)

        return data

    # -----------------------------------------------------------------------

    def __search_fn(self, comparator, **kwargs):
        """Apply functions on files.

        Each argument is made of a function name and its expected value.
        Each function can be prefixed with 'not_', like in the next example.

        :param comparator: (sppasBaseCompare)
        :param kwargs: logic_bool/any sppasFileNameCompare() method.
        :returns: (sppasDataSet) Set of FileName() instances

        """
        # extract the information from the arguments
        sppasBaseFilters.test_args(comparator, **kwargs)
        logic_bool = sppasBaseFilters.fix_logic_bool(**kwargs)
        path_fct_values = sppasBaseFilters.fix_function_values(comparator, **kwargs)
        path_functions = sppasBaseFilters.fix_functions(comparator, **kwargs)

        # the set of results
        data = sppasBaseSet()

        # search for the data to be returned:
        for path in self.obj:
            # append all files of the path
            for fr in path:
                for fn in fr:
                    is_matching = fn.match(path_functions, logic_bool)
                    if is_matching is True:
                        data.append(fn, path_fct_values)

        return data

    # -----------------------------------------------------------------------

    def file(self, **kwargs):
        """Apply functions on all files of the object.

        Each argument is made of a function name and its expected value.
        Each function can be prefixed with 'not_', like in the next example.

        :Examples:

            >>> f.file(state=State().UNUSED)
            >>> f.file(contains="dlg")

        :param kwargs: logic_bool/any sppasFileStateCompare() method.
        :returns: (sppasDataSet)

        """
        comparator = sppasFileBaseCompare()
        return self.__search_fn(comparator, **kwargs)

    # -----------------------------------------------------------------------

    def name(self, **kwargs):
        """Apply functions on all names of the files of the object.

        Each argument is made of a function name and its expected value.
        Each function can be prefixed with 'not_', like in the next example.

        :Example:

            >>> f.name(iexact="myfile-phon", not_startswith='a', logic_bool="and")
            >>> f.name(iexact="myfile-phon") & f.name(not_startswith='a')
            >>> f.name(iexact="myfile-phon") | f.name(startswith="ta")

        :param kwargs: logic_bool/any sppasFileNameCompare() method.
        :returns: (sppasDataSet) Set of FileName() instances

        """
        comparator = sppasFileNameCompare()
        return self.__search_fn(comparator, **kwargs)

    # -----------------------------------------------------------------------

    def extension(self, **kwargs):
        """Apply functions on all extensions of the files of the object.

        Each argument is made of a function name and its expected value.
        Each function can be prefixed with 'not_', like in the next example.

        :Example:

            >>> f.extension(startswith=".TEXT", not_endswith='a', logic_bool="and")
            >>> f.extension(startswith=".TEXT") & f.extension(not_endswith='a')
            >>> f.extension(startswith=".TEXT") | f.extension(startswith="ta")

        :param kwargs: logic_bool/any sppasFileExtCompare() method.
        :returns: (sppasDataSet)

        """
        comparator = sppasFileExtCompare()
        return self.__search_fn(comparator, **kwargs)

    # -----------------------------------------------------------------------
    # References/Attributes
    # -----------------------------------------------------------------------

    def ref(self, **kwargs):
        """Apply functions on all file properties of the object.

        Each argument is made of a function name and its expected value.
        Each function can be prefixed with 'not_', like in the next example.

        :Example:

            >>> f.ref(startswith="toto", not_endswith="tutu", logic_bool="and")
            >>> f.ref(startswith="toto") & f.ref(not_endswith="tutu")
            >>> f.ref(startswith="toto") | f.ref(startswith="tutu")

        :param kwargs: logic_bool/any sppasFileStateCompare() method.
        :returns: (sppasDataSet) Set of FileName() instances

        """
        comparator = sppasFileRefCompare()

        # extract the information from the arguments
        sppasBaseFilters.test_args(comparator, **kwargs)
        logic_bool = sppasBaseFilters.fix_logic_bool(**kwargs)
        ref_fct_values = sppasBaseFilters.fix_function_values(comparator, **kwargs)
        ref_functions = sppasBaseFilters.fix_functions(comparator, **kwargs)

        # the set of results
        data = sppasBaseSet()

        # search for the data to be returned:
        for path in self.obj:
            # append all files of the path
            for fr in path:
                for ref in fr.references:
                    is_matching = ref.match(ref_functions, logic_bool)
                    if is_matching is True:
                        for fn in fr:
                            data.append(fn, ref_fct_values)

        return data

    # -----------------------------------------------------------------------

    def att(self, **kwargs):
        """Apply functions on attributes of references of files of the object.

        Each argument is made of a function name and its expected value.
        Each function can be prefixed with 'not_', like in the next example.

        The given value is a tuple with (identifier, value) of the attribute.

        :Example:

        >>> f.att(equals=("age", "14"))

        :param kwargs: logic_bool/any sppasAttCompare() method.
        :returns: (sppasDataSet) Set of FileName() instances

        """
        comparator = sppasAttributeCompare()

        # extract the information from the arguments
        sppasBaseFilters.test_args(comparator, **kwargs)
        logic_bool = sppasBaseFilters.fix_logic_bool(**kwargs)
        att_fct_values = sppasBaseFilters.fix_function_values(comparator, **kwargs)
        att_functions = sppasBaseFilters.fix_functions(comparator, **kwargs)

        # the set of results
        data = sppasBaseSet()

        # search for the data to be returned:
        for fp in self.obj:
            # does this root have references with all/any attributes matching the given ones?
            for fr in fp:

                # each given att is False until we really know!
                matches = [False]*len(att_functions)

                for ref in fr.get_references():
                    # Find if one of the attributes of this reference is matching one
                    # of the requested attributes
                    for i, a in enumerate(att_functions):
                        func, value, logical_not = a
                        for att in ref:
                            mm = False
                            try:
                                searched = sppasAttribute(value[0], value[1], att.get_value_type())
                                if att.get_id() == searched.get_id():
                                    if logical_not is True:
                                        mm = not func(att, searched.get_typed_value())
                                    else:
                                        mm = func(att, searched.get_typed_value())
                                if mm is True:
                                    matches[i] = True
                                    break
                            except ValueError:
                                continue

                if logic_bool == "and":
                    is_matching = all(matches)
                else:
                    is_matching = any(matches)

                if is_matching is True:
                    for fn in fr:
                        data.append(fn, att_fct_values)

        return data
