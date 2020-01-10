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

    ui.phoenix.page_analyze.errview.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    ErrorViewPanel to display an error message instead of the content.

"""

import wx

from sppas import msg
from sppas.src.utils import u

from ..windows import sppasPanel
from ..windows import sppasTextCtrl

from .baseview import sppasBaseViewPanel


# ----------------------------------------------------------------------------
# List of displayed messages:


def _(message):
    return u(msg(message, "ui"))


MSG_ERROR = _("The file {:s} can't be loaded by this view.")
MSG_UNK = _("Unknown error.")

# ---------------------------------------------------------------------------


class ErrorViewPanel(sppasBaseViewPanel):
    """Display the content of a file into an editable TextCtrl.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      contact@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2019  Brigitte Bigi

    The object does not create an object.

    """

    def __init__(self, parent, filename, name="errorview-panel"):
        super(ErrorViewPanel, self).__init__(parent, filename, name)

    # -----------------------------------------------------------------------
    # Override from the parent
    # -----------------------------------------------------------------------

    def load_text(self):
        """Load the file content into an object.

        Raise an exception if the file is not supported or can't be read.

        """
        pass

    # ------------------------------------------------------------------------

    def _create_content(self):
        """Create the content of the panel."""
        self.AddButton("close")
        self._create_child_panel()
        self.Collapse(True)

    # -----------------------------------------------------------------------

    def _create_child_panel(self):
        """Override. Create the child panel."""
        style = wx.NO_BORDER | wx.TE_MULTILINE | wx.TE_RICH | \
                wx.TE_PROCESS_ENTER | wx.TE_BESTWRAP | wx.TE_NO_VSCROLL
        txtview = sppasTextCtrl(self, style=style)
        txtview.SetFont(wx.GetApp().settings.mono_text_font)
        txtview.SetEditable(False)
        self.SetPane(txtview)

        self.set_error_message(MSG_UNK)

    # -----------------------------------------------------------------------

    def set_error_message(self, error_message):
        """Set the error message to be displayed.

        :param error_message: (str)

        """
        message = MSG_ERROR.format(self._filename) + "\n" + error_message
        txtview = self.GetPane()
        txtview.SetValue(message)

        # required under Windows
        txtview.SetStyle(0, len(message), txtview.GetDefaultStyle())

        # Search for the height of the text
        nblines = len(error_message.split()) + 1
        view_height = float(self.get_font_height()) * 1.1 * nblines
        txtview.SetMinSize(wx.Size(sppasPanel.fix_size(420), view_height))
