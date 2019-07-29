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
"""

from .num_asian_lang import sppasNumAsianType

# ---------------------------------------------------------------------------


class sppasNumJapanese(sppasNumAsianType):
    """Return an instance of sppasNumJapanese.

    :returns: (sppasNumJapanese)

    """

    def __init__(self, dictionary):
        sppasNumAsianType.NUMBER_LIST = (0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10,
                                         20, 30, 40, 50, 60, 70, 80, 90,
                                         100, 1000, 10000, 100000000)

        super(sppasNumJapanese, self).__init__('jpn', dictionary)
