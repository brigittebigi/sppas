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

    src.structs.basefilters.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""

from sppas import sppasValueError
from sppas import sppasKeyError

# ---------------------------------------------------------------------------


class sppasBaseFilters(object):
    """Base class for any filter system.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2019  Brigitte Bigi

    """

    def __init__(self, obj):
        """Create a sppasBaseFilters instance.

        :param obj: (object) The object to be filtered.

        """
        self.obj = obj

    # -----------------------------------------------------------------------

    @staticmethod
    def test_args(comparator, **kwargs):
        """Raise an exception if any of the args is not correct.

        :param comparator: (sppasBaseComparator)

        """
        names = ["logic_bool"] + comparator.get_function_names()
        for func_name, value in kwargs.items():
            if func_name.startswith("not_"):
                func_name = func_name[4:]

            if func_name not in names:
                raise sppasKeyError("kwargs function name", func_name)

    # -----------------------------------------------------------------------

    @staticmethod
    def fix_logic_bool(**kwargs):
        """Return the value of a logic boolean predicate.

        """
        for func_name, value in kwargs.items():
            if func_name == "logic_bool":
                if value not in ['and', 'or']:
                    raise sppasValueError(value, "logic bool")
                return value
        return "and"

    # -----------------------------------------------------------------------

    @staticmethod
    def fix_function_values(comparator, **kwargs):
        """Return the list of function names and the expected value.

        :param comparator: (sppasBaseComparator)

        """
        fct_values = list()
        for func_name, value in kwargs.items():
            if func_name in comparator.get_function_names():
                fct_values.append("{:s} = {!s:s}".format(func_name, value))

        return fct_values

    # -----------------------------------------------------------------------

    @staticmethod
    def fix_functions(comparator, **kwargs):
        """Parse the args to get the list of function/value/complement.

        :param comparator: (sppasBaseComparator)

        """
        f_functions = list()
        for func_name, value in kwargs.items():

            logical_not = False
            if func_name.startswith("not_"):
                logical_not = True
                func_name = func_name[4:]

            if func_name in comparator.get_function_names():
                f_functions.append((comparator.get(func_name),
                                    value,
                                    logical_not))

        return f_functions
