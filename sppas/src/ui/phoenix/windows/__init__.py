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

    src.ui.phoenix.windows.__init__.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""

from .line import sppasStaticLine

from .button import TextButton
from .button import BitmapTextButton
from .button import CheckButton
from .button import RadioButton
from .button import ToggleButton
from .button import sppasBitmapTextButton
from .button import sppasTextButton
from .button import sppasBitmapButton

from .buttonbox import sppasRadioBoxPanel

from .text import sppasStaticText
from .text import sppasSimpleText
from .text import sppasMessageText
from .text import sppasTitleText
from .text import sppasTextCtrl
from .text import NotEmptyTextValidator

from .image import sppasStaticBitmap

from .media import MediaType
from .media import MediaEvents
from .media import sppasMediaPanel
from .media import sppasPlayerControlsPanel

from .panel import sppasPanel
from .panel import sppasTransparentPanel
from .panel import sppasImgBgPanel
from .panel import sppasScrolledPanel
from .panel import sppasCollapsiblePanel

from .splitter import sppasMultiSplitterPanel

from .progress import sppasProgressDialog
from .dialog import sppasDialog
from .frame import sppasTopFrame
from .frame import sppasFrame

from .toolbar import sppasToolbar

__all__ = (
    "sppasStaticLine",
    'TextButton',
    'BitmapTextButton',
    'sppasBitmapTextButton',
    "sppasTextButton",
    "sppasBitmapButton",
    "sppasRadioBoxPanel",
    "CheckButton",
    "RadioButton",
    "ToggleButton",
    "sppasMediaPanel",
    "MediaType",
    "MediaEvents",
    "sppasPlayerControlsPanel",
    "sppasMultiSplitterPanel",
    "sppasStaticText",
    "sppasTitleText",
    "sppasMessageText",
    "sppasSimpleText",
    "sppasTextCtrl",
    "NotEmptyTextValidator",
    "sppasStaticBitmap",
    "sppasProgressDialog",
    "sppasPanel",
    "sppasTransparentPanel",
    "sppasImgBgPanel",
    "sppasScrolledPanel",
    "sppasCollapsiblePanel",
    "sppasDialog",
    "sppasTopFrame",
    "sppasFrame",
    "sppasToolbar"
)
