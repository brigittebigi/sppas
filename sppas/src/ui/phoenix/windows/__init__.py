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

from .splitter import sppasSplitterWindow
from .splitter import sppasMultiSplitterPanel

from .listctrl import CheckListCtrl
from .listctrl import SortListCtrl
from .listctrl import LineListCtrl
from .listctrl import sppasListCtrl

from .image import sppasStaticBitmap

from .popup import LabelPopup

from .text import sppasStaticText
from .text import sppasSimpleText
from .text import sppasMessageText
from .text import sppasTitleText
from .text import sppasTextCtrl
from .text import NotEmptyTextValidator

from .basedcwindow import sppasDCWindow
from .basedcwindow import sppasWindowEvent

# basewindow requires basedcwindow
from .basewindow import WindowState
from .basewindow import sppasWindow

# line requires sppasDCWindow
from .line import sppasStaticLine

# frame requires sppasStaticLine
from .frame import sppasTopFrame
from .frame import sppasFrame

# buttons package requires sppasWindow/WindowState
from .buttons import BaseButton
from .buttons import TextButton
from .buttons import BitmapButton
from .buttons import BitmapTextButton
from .buttons import ToggleButton
from .buttons import CheckButton
from .buttons import RadioButton

# panels package requires buttons
from .panels import sppasPanel
from .panels import sppasTransparentPanel
from .panels import sppasImgBgPanel
from .panels import sppasScrolledPanel
from .panels import sppasCollapsiblePanel

# dialogs package requires panels and buttons
from .dialogs import sppasDialog
from .dialogs import sppasChoiceDialog
from .dialogs import sppasFileDialog
from .dialogs import sppasTextEntryDialog
from .dialogs import Information
from .dialogs import Confirm
from .dialogs import Warn
from .dialogs import Error
from .dialogs import YesNoQuestion
from .dialogs import sppasProgressDialog

# buttonbox package requires panels and buttons
from .buttonbox import sppasRadioBoxPanel
from .buttonbox import sppasToggleBoxPanel

# toolbar requires panels, buttons and text
from .toolbar import sppasToolbar

# combobox requires panels, buttons and buttonbox
from .combobox import sppasComboBox

from .media import MediaType
from .media import MediaEvents
from .media import sppasMediaCtrl
from .media import sppasPlayerControlsPanel
from .media import sppasMultiPlayerPanel

__all__ = (
    "sppasDialog",
    "sppasChoiceDialog",
    "sppasFileDialog",
    "sppasTextEntryDialog",
    "Information",
    "Confirm",
    "Warn",
    "Error",
    "YesNoQuestion",
    "sppasStaticLine",
    "WindowState",
    "BaseButton",
    'TextButton',
    'BitmapTextButton',
    "BitmapButton",
    "sppasRadioBoxPanel",
    "CheckButton",
    "RadioButton",
    "ToggleButton",
    "sppasMediaCtrl",
    "MediaType",
    "MediaEvents",
    "sppasPlayerControlsPanel",
    "sppasMultiPlayerPanel",
    "sppasSplitterWindow",
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
    "sppasToolbar",
    "sppasComboBox",
    "sppasListCtrl",
    "LineListCtrl",
    "CheckListCtrl",
    "SortListCtrl"
)
