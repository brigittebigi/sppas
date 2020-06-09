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

from sppas.src.exceptions import sppasValueError, sppasTypeError
from sppas.src.resources import sppasDictRepl

# ---------------------------------------------------------------------------


class sppasNumBase(object):

    ASIAN_TYPED_LANGUAGES = ("yue", "cmn", "jpn", "pcm")
    EUROPEAN_TYPED_LANGUAGES = ("fra", "ita", "eng", "spa", "pol", "por", "vie", "khm")

    # ---------------------------------------------------------------------------

    def __init__(self, lang=None, dictionary=None):
        """Create an instance of sppasNumBase.

        :param lang: (str) name of the language
        :raises: (sppasValueError)

        """
        self.languages = ("und", "yue", "cmn", "fra", "ita", "eng", "spa",
                          "khm", "vie", "jpn", "pol", "por", "pcm")
        self.separator = '_'

        if lang is None or lang not in self.languages:
            self.__lang = "und"
        else:
            self.__lang = lang

        self._lang_dict = sppasDictRepl()
        if self.__lang != "und":
            if dictionary is None or isinstance(dictionary, sppasDictRepl) is False:
                raise sppasTypeError(dictionary, "sppasDictRepl")

            if dictionary is not None:
                has_tenth_of_thousand = False
                lang_except = ('vie', 'khm')
                if dictionary.is_key('10000') and lang not in lang_except:
                    has_tenth_of_thousand = True

                if has_tenth_of_thousand is True\
                        and self.__lang not in sppasNumBase.ASIAN_TYPED_LANGUAGES:
                    raise sppasValueError(dictionary, str(sppasNumBase.ASIAN_TYPED_LANGUAGES))
                elif has_tenth_of_thousand is False\
                        and self.__lang in sppasNumBase.ASIAN_TYPED_LANGUAGES:
                    raise sppasValueError(dictionary, str(sppasNumBase.EUROPEAN_TYPED_LANGUAGES))

                self._lang_dict = dictionary

    # ---------------------------------------------------------------------------

    def get_lang(self):
        """Return the current language.

        :returns: (str)

        """
        return self.__lang

    # ---------------------------------------------------------------------------

    def set_lang(self, lang):
        """Set the language to a new one and update the dictionary.

        :param lang: (str) new language
        :raises: sppasValueError

        """
        if lang in self.languages:
            self.__lang = lang
            self._lang_dict = sppasDictRepl(self.__lang)
        else:
            raise sppasValueError(lang, str(self.languages))

    # ---------------------------------------------------------------------------

    def _get_lang_dict(self):
        """Return the current language dictionary.

        :returns: (list) current language dictionary

        """
        return self._lang_dict

    # ---------------------------------------------------------------------------

    def _units(self, number):
        """Return the "wordified" version of a unit number.

        Returns the word corresponding to the given unit within the current
        language dictionary

        :param number: (int) number to convert in word
        :returns: (str)

        """
        if number == 0:
            return self._lang_dict['0']
        if 0 < number < 10:
            return self._lang_dict[str(number)]

    # ---------------------------------------------------------------------------

    def _tenth(self, number):
        """Return the "wordified" version of a tenth number.

        Returns the word corresponding to the given tenth within the current
        language dictionary

        :param number: (int) number to convert in word
        :returns: (str)

        """
        if number < 10:
            return self._units(number)
        else:
            if self._lang_dict.is_key(number):
                return self._lang_dict[str(number)]
            else:
                if self._lang_dict.is_key(int(number/10)*10):
                    if int(str(number)[1:]) == 0:
                        return self._lang_dict[str(number)]
                    else:
                        if self.__lang in sppasNumBase.ASIAN_TYPED_LANGUAGES:
                            return self._lang_dict[str(int(number/10)*10)] \
                                   + self._units(number % 10)
                        else:
                            return self._lang_dict[str(int(number/10)*10)] \
                                   + self.separator \
                                   + self._units(number % 10)

    # ---------------------------------------------------------------------------

    def _hundreds(self, number):
        """Return the "wordified" version of a hundred number.

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
                    return self._lang_dict['100']
                else:
                    if self.__lang in sppasNumBase.ASIAN_TYPED_LANGUAGES:
                        return self._lang_dict['100'] \
                               + self._tenth(number % 100)
                    else:
                        return self._lang_dict['100']\
                               + self.separator \
                               + self._tenth(number % 100)
            else:
                if int(str(number)[1:]) == 0:
                    if self.__lang in sppasNumBase.ASIAN_TYPED_LANGUAGES:
                        return mult + self._lang_dict['100']\
                               + self._tenth(number % 100)
                    else:
                        return mult + self.separator\
                               + self._lang_dict['100']
                else:
                    if self.__lang in sppasNumBase.ASIAN_TYPED_LANGUAGES:
                        return mult + self._lang_dict['100']\
                               + self._tenth(number % 100)
                    else:
                        return mult + self.separator\
                               + self._lang_dict['100']\
                               + self.separator\
                               + self._tenth(number % 100)

    # ---------------------------------------------------------------------------

    def _thousands(self, number):
        """Return the "wordified" version of a thousand number.

        Returns the word corresponding to the given thousand number within the
        current language dictionary

        :param number: (int) number to convert in word
        :returns: (str)

        """
        if number < 1000:
            return self._hundreds(number)
        else:
            mult = None
            if number/1000*1000 != 1000:
                mult = self._hundreds(int(number/1000))

            if mult is None:
                if int(str(number)[1:]) == 0:
                    if self.__lang in sppasNumBase.ASIAN_TYPED_LANGUAGES:
                        return self._lang_dict['1']\
                               + self._lang_dict['1000']
                    else:
                        return self._lang_dict['1']\
                               + self.separator\
                               + self._lang_dict['1000']
                else:
                    if self.__lang in sppasNumBase.ASIAN_TYPED_LANGUAGES:
                        return self._lang_dict['1']\
                               + self._lang_dict['1000'] \
                               + self._hundreds(number % 1000)
                    else:
                        return self._lang_dict['1000'] \
                                + self.separator\
                                + self._hundreds(number % 1000)
            else:
                if int(str(number)[1:]) == 0:
                    if self.__lang in sppasNumBase.ASIAN_TYPED_LANGUAGES:
                        return mult + self._lang_dict['1000'] \
                                + self._hundreds(number % 1000)
                    else:
                        return mult + self.separator\
                                + self._lang_dict['1000']
                else:
                    if self.__lang in sppasNumBase.ASIAN_TYPED_LANGUAGES:
                        return mult + self._lang_dict['1000'] \
                                + self._hundreds(number % 1000)
                    else:
                        return mult + self.separator\
                                + self._lang_dict['1000'] \
                                + self.separator\
                                + self._hundreds(number % 1000)

    # ---------------------------------------------------------------------------

    def _billions(self, number):
        """Return the "wordified" version of a billion number

        Returns the word corresponding to the given billion number within the
        current language dictionary

        :param number: (int) number to convert in word
        :returns: (str)

        """
        raise NotImplementedError

    # ---------------------------------------------------------------------------

    def convert(self, number):
        """Return the whole "wordified" given number.

        Returns the entire number given in parameter in a "wordified" state
        it calls recursively the sub functions within the instance and more
        specifics ones in the sub-classes

        :param number: (int) number to convert into word
        :returns: (str)

        """
        stringyfied_number = str(number)
        if stringyfied_number.isdigit() is False:
            raise sppasValueError(number, "int")

        res = ''
        if len(stringyfied_number) > 1:
            if stringyfied_number.startswith('0'):
                while '0' == stringyfied_number[0]:
                    res += self._lang_dict['0'] + self.separator
                    stringyfied_number = stringyfied_number[1:]

        res += self._billions(int(number))
        return res if res is not None else number
