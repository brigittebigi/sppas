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

    src.ui.phoenix.page_files.fileutils.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""

import wx

from sppas.src.wkps import sppasAttribute

# ----------------------------------------------------------------------------


class IdentifierTextValidator(wx.Validator):
    """Check if the TextCtrl is valid for an identifier.

    If the TextCtrl is not valid, the background becomes pinky.

    """

    def __init__(self):
        super(IdentifierTextValidator, self).__init__()

    def Clone(self):
        # Required method for validator
        return IdentifierTextValidator()

    def TransferToWindow(self):
        # Prevent wxDialog from complaining.
        return True

    def TransferFromWindow(self):
        # Prevent wxDialog from complaining.
        return True

    def Validate(self, win=None):
        text_ctrl = self.GetWindow()
        text = text_ctrl.GetValue().strip()
        if sppasAttribute.validate(text) is False:
            text_ctrl.SetBackgroundColour("pink")
            text_ctrl.SetFocus()
            text_ctrl.Refresh()
            return False

        try:
            text_ctrl.SetBackgroundColour(wx.GetApp().settings.bg_color)
        except:
            text_ctrl.SetBackgroundColour(wx.SystemSettings.GetColour(wx.SYS_COLOUR_WINDOW))

        text_ctrl.Refresh()
        return True

