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

from sppas import sppasKeyError

from .num_base import sppasNumBase
from .num_jpn import sppasNumJapanese
from .num_fra import sppasNumFrench
from .num_spa import sppasNumSpanish
from .num_ita import sppasNumItalian
from .num_khm import sppasNumKhmer
from .num_vie import sppasNumVietnamese
from .num_cmn import sppasNumMandarinChinese
from .por_num import sppasNumPortuguese
from .num_pol import sppasNumPolish

from .num_asian_lang import sppasNumAsianType
from .num_und import sppasNumUnd
from .num_europ_lang import sppasNumEuropeanType

# ---------------------------------------------------------------------------


class sppasNumConstructor(object):

    LANGUAGES_DICT = {
        "fra": sppasNumFrench,
        "ita": sppasNumItalian,
        "spa": sppasNumSpanish,
        "khm": sppasNumKhmer,
        "vie": sppasNumVietnamese,
        "jpn": sppasNumJapanese,
        "cmn": sppasNumMandarinChinese,
        "por": sppasNumPortuguese,
        "pol": sppasNumPolish,
    }

    # ---------------------------------------------------------------------------

    @staticmethod
    def construct(lang="und", dictionary=None):
        """Return an instance of the correct object regarding the given language

        :returns: (sppasNumBase)
        :raises: sppasTypeError, sppasValueError

        """
        if lang == "und":
            # Instantiate with nothing
            instance = sppasNumUnd()

        elif lang in sppasNumConstructor.LANGUAGES_DICT:
            # Instantiate with only the dictionary
            instance = sppasNumConstructor.LANGUAGES_DICT[lang](dictionary)

        elif lang in sppasNumBase.ASIAN_TYPED_LANGUAGES:
            # Instantiate with the language and the dictionary
            instance = sppasNumAsianType(lang, dictionary)

        elif lang in sppasNumBase.EUROPEAN_TYPED_LANGUAGES:
            # Instantiate with the language and the dictionary
            instance = sppasNumEuropeanType(lang, dictionary)

        else:
            raise sppasKeyError(lang, "sppasNumConstructor")

        return instance
