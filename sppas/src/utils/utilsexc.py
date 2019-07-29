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

    utils.utilsexc.py
    ~~~~~~~~~~~~~~~~~

"""

from sppas.src.config import error

# -----------------------------------------------------------------------


class UtilsDataTypeError(TypeError):
    """:ERROR 7010:.

    Expected a {data_name} of type {expected_type}. Got {data_type} instead.

    """

    def __init__(self, data_name, expected_type, data_type):
        self.parameter = error(7010) + \
                         (error(7010, "utils")).format(
                             data_name=data_name,
                             expected_type=expected_type,
                             data_type=data_type)

    def __str__(self):
        return repr(self.parameter)
