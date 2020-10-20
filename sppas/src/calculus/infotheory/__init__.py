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

    src.calculus.infotheory.__init__.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Information Theory is a scientific fields that started with the Claude
Shannon's 1948 paper: *“A Mathematical  Theory  of  Communication”*
published in the Bell Systems Technical Journal.
There are several major concepts in this paper, including:

1. every communication channel has a speed limit, measured in binary
digits per second,
2. the architecture and design of communication systems,
3. source coding, i.e. the efficiency of the data representation
(remove redundancy in the information to make the message smaller)

"""

from .entropy import sppasEntropy
from .kullbackleibler import sppasKullbackLeibler
from .perplexity import sppasPerplexity
from .utilit import find_ngrams, symbols_to_items

__all__ = [
        "sppasEntropy",
        "sppasKullbackLeibler",
        "sppasPerplexity",
        "find_ngrams",
        "symbols_to_items"
]
