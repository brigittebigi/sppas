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


class sppasNumMandarinChinese(sppasNumAsianType):

    def __init__(self, dictionary):
        """Create an instance of sppasNumMandarinChinese.

        :returns: (sppasNumMandarinChinese)

        """
        # Very important if sppasNumAsianType.NUMBER_LIST has been modified before !
        sppasNumAsianType.NUMBER_LIST = (0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10,
                                         20, 30, 40, 50, 60, 70, 80, 90,
                                         100, 1000, 10000,)
        super(sppasNumMandarinChinese, self).__init__('cmn', dictionary)

    # ---------------------------------------------------------------------------

    def _hundreds(self, number):
        """"Return the "wordified" version of a hundred number.

        Returns the word corresponding to the given hundred number within the
        current language dictionary

        :param number: (int) number to convert in word
        :returns: (str)

        """
        if number < 100:
            return self._tenth(number)
        else:
            mult = None
            if int(str(number)[0])*100 != 100:
                mult = self._units(int(number/100))

            if mult is None:
                if int(str(number)[1:]) == 0:
                    return self._lang_dict['1']\
                           + self._lang_dict['100']
                else:
                    return self._lang_dict['1']\
                           + self._lang_dict['100'] \
                           + self._lang_dict['0'] \
                           + self._tenth(number % 100)
            else:
                if int(str(number)[1:]) == 0:
                    return mult + self._lang_dict['100'] \
                           + self._lang_dict['0'] \
                           + self._tenth(number % 100)
                else:
                    return mult + self._lang_dict['100'] \
                           + self._lang_dict['0'] \
                           + self._tenth(number % 100)

    # ---------------------------------------------------------------------------

    def _billions(self, number):
        if number < 100000000:
            return self._tenth_of_thousands(number)
        else:
            mult = None
            if int(number/1000000000)*1000000000 != 1000000000:
                mult = self._thousands(int(number/1000000000))

            if mult is None:
                if int(str(number)[1:]) == 0:
                    return self._lang_dict['1000000000']
                else:
                    return self._lang_dict['1000000000'] \
                           + self._tenth_of_thousands(number % 1000000000)
            else:
                if int(str(number)[1:]) == 0:
                    return mult + self._lang_dict['1000000000']
                else:
                    return mult + self._lang_dict['1000000000'] \
                            + self._tenth_of_thousands(number % 1000000000)
