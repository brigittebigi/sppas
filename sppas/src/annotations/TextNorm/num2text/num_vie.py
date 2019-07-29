
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


class sppasNumVietnamese(sppasNumEuropeanType):

    def __init__(self, dictionary):
        """Create an instance of sppasNumVietnamese.

        :returns: (sppasNumVietnamese)

        """
        sppasNumEuropeanType.NUMBER_LIST = (0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10,
                                         20, 30, 40, 50, 60, 70, 80, 90,
                                         100, 1000, 1000000, 1000000000,)
        super(sppasNumVietnamese, self).__init__('vie', dictionary)

    # -----------------------------------------------------------------------

    def _thousands(self, number):
        """Return the "wordified" version of a tenth of a thousand number.

        Returns the word corresponding to the given tenth of a thousand number
        within the current language dictionary

        :param number: (int) number to convert in word
        :returns: (str)

        """
        if number < 1000:
            return self._hundreds(number)
        else:
            mult = None
            if int(number / 1000) * 1000 != 1000:
                mult = self._hundreds(int(number / 1000))

            if mult is None:
                if int(str(number)[1:]) == 0:
                    return self._lang_dict['1'] \
                           + self.separator \
                           + self._lang_dict['1000']
                else:
                    return self._lang_dict['1'] \
                           + self.separator \
                           + self._lang_dict['1000'] \
                           + self.separator \
                           + self._hundreds(number % 1000)
            else:
                if int(str(number)[1:]) == 0:
                    return mult + self.separator \
                           + 'nghìn'
                else:
                    return mult + self.separator \
                           + 'nghìn' \
                           + self.separator \
                           + self._hundreds(number % 1000)

    # ---------------------------------------------------------------------------

    def _billions(self, number):
        """Return the "wordified" version of a billion number.

        Returns the word corresponding to the given billion number within the
        current language dictionary

        :param number: (int) number to convert in word
        :returns: (str)

        """
        if number < 1000000000:
            return self._millions(number)
        else:
            mult = None
            if int(number / 1000000000) * 1000000000 != 1000000000:
                mult = self._thousands(int(number / 100000000))

            if mult is None:
                if int(str(number)[1:]) == 0:
                    return self._lang_dict['1'] \
                           + self.separator \
                           + self._lang_dict['1000000000']
                else:
                    return self._lang_dict['1'] \
                           + self.separator \
                           + self._lang_dict['1000000000'] \
                           + self.separator \
                           + self._millions(number % 100000000)
            else:
                if int(str(number)[1:]) == 0:
                    return mult + self.separator \
                           + self._lang_dict['1000000000']
                else:
                    return mult + self.separator \
                           + self._lang_dict['1000000000'] \
                           + self.separator \
                           + self._millions(number % 100000000)
