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


class sppasNumPolish(sppasNumEuropeanType):
    """Return an instance of sppasNumPolish

    :retruns: (sppasNumPolish)

    """
    # reference https://www.languagesandnumbers.com/comment-compter-en-polonais/fr/pol/
    def __init__(self, dictionary):
        # Very important if sppasNumEuropeanType.NUMBER_LIST has been modified before !
        sppasNumEuropeanType.NUMBER_LIST = (0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10,
                                            11, 12, 13, 14, 15, 16, 17, 18, 19, 20,
                                            30, 40, 50, 60, 70, 80, 90, 100, 1000, 1000000, 1000000000)
        super(sppasNumPolish, self).__init__('pol', dictionary)

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
            if int(str(number)[0]) * 100 != 100:
                mult = self._units(int(number / 100))

            if mult is None:
                if int(str(number)[1:]) == 0:
                    return self._lang_dict['100']
                else:
                    return self._lang_dict['100'] \
                           + self.separator \
                           + self._tenth(number % 100)
            else:
                if int(str(number)[1:]) == 0:
                    if 199 < number < 300:
                        return 'dwieście'
                    elif 399 < number < 500:
                        return mult + 'sta'
                    else:
                        return mult + 'set'
                else:
                    if 199 < number < 300:
                        return 'dwieście' \
                               + self.separator \
                               + self._tenth(number % 100)
                    elif 399 < number < 500:
                        return mult + 'sta' \
                               + self.separator \
                               + self._tenth(number % 100)
                    else:
                        return mult + 'set' \
                               + self.separator \
                               + self._tenth(number % 100)

    # ---------------------------------------------------------------------------

    def _thousands(self, number):
        if number < 1000:
            return self._hundreds(number)
        else:
            mult = None
            if number / 1000 * 1000 != 1000:
                mult = self._hundreds(int(number / 1000))

            if mult is None:
                if int(str(number)[1:]) == 0:
                    return self._lang_dict['1000']
                else:
                    return self._lang_dict['1000'] \
                           + self.separator \
                           + self._hundreds(number % 1000)
            else:
                if int(str(number)[1:]) == 0:
                    if 1000 < number < 2000:
                        return mult + self.separator \
                               + self._lang_dict['1000']
                    elif 1999 < number < 5000:
                        return mult + self.separator \
                               + 'tysiące'
                    else:
                        return mult + self.separator \
                               + 'tysięcy'
                else:
                    if 1000 < number < 2000:
                        return mult + self.separator \
                               + self._lang_dict['1000'] \
                               + self.separator \
                               + self._hundreds(number % 1000)
                    elif 1999 < number < 5000:
                        return mult + self.separator \
                               + 'tysiące' \
                               + self.separator \
                               + self._hundreds(number % 1000)
                    else:
                        return mult + self.separator \
                               + 'tysięcy' \
                               + self.separator \
                               + self._hundreds(number % 1000)

    # ---------------------------------------------------------------------------

    def _millions(self, number):
        """Return the "wordified" version of a million number.

        Returns the word corresponding to the given million number within the
        current language dictionary

        :param number: (int) number to convert in word
        :returns: (str)

        """
        if number < 1000000:
            return self._thousands(number)
        else:
            mult = None
            if int(number / 1000000) * 1000000 != 1000000:
                mult = self._hundreds(int(number / 1000000))

            if mult is None:
                if int(str(number)[1:]) == 0:
                    return self._lang_dict['1000000']
                else:
                    return self._lang_dict['1000000'] + self.separator \
                           + self._thousands(number % 1000000)
            else:
                if int(str(number)[1:]) == 0:
                    return mult + self.separator \
                           + self._lang_dict['1000000']
                else:
                    return mult + self.separator \
                           + self._lang_dict['1000000'] + self.separator \
                           + self._thousands(number % 1000000)

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
        elif number > 1000000000000:
            return None
        else:
            mult = None
            if int(number / 1000000000) * 1000000000 != 1000000000:
                mult = self._hundreds(int(number / 1000000000))

            if mult is None:
                if int(str(number)[1:]) == 0:
                    return self._lang_dict['1000000000']
                else:
                    return self._lang_dict['1000000000'] + self.separator \
                           + self._millions(number % 1000000000)
            else:
                if int(str(number)[1:]) == 0:
                    return mult + self.separator \
                           + self._lang_dict['1000000000']
                else:
                    return mult + self.separator \
                           + self._lang_dict['1000000000'] + self.separator \
                           + self._millions(number % 1000000000)

