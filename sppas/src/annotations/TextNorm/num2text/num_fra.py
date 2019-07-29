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

from .num_europ_lang import sppasNumEuropeanType

# ---------------------------------------------------------------------------


class sppasNumFrench(sppasNumEuropeanType):
    """

    :author:       Barthélémy Drabczuk
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2019  Brigitte Bigi

    """

    def __init__(self, dictionary):
        """Return an instance of sppasNumFrench.

        :returns: (sppasNumFrench)

        """
        sppasNumEuropeanType.NUMBER_LIST = (0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10,
                                            11, 12, 13, 14, 15, 16, 17, 18, 19, 20,
                                            30, 40, 50, 60, 70, 80, 90, 100, 1000, 1000000, 1000000000)
        super(sppasNumFrench, self).__init__('fra', dictionary)

    # ---------------------------------------------------------------------------

    def _tenth(self, number):
        """Return the "wordified" version of a tenth number.

        Returns the word corresponding to the given tenth within the current
        language dictionary

        :param number: (int) number to convert in word
        :returns: (str)

        """
        if 70 <= number < 80:
            return self._tenth(60) + self.separator \
                   + self._tenth(number - 60) if number - 60 > 0 else ''
        elif 80 <= number < 90:
            return self._units(4) + '-' \
                   + self._tenth(20) + self.separator \
                   + self._units(int(str(number)[1:]))
        elif 90 <= number < 100:
            return self._units(4) + self.separator \
                   + self._tenth(20) + self.separator \
                   + self._tenth(number - 80) if number - 80 > 0 else ''

        elif number > 11 and number % 10 == 1:
            return sppasNumEuropeanType._get_lang_dict(self)[int(str(number)[0])*10] \
                    + '-et-' + self._units(int(str(number)[1:]))

        else:
            return sppasNumEuropeanType._tenth(self, number)
