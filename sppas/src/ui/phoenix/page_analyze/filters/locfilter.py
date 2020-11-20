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

    src.ui.phoenix.page_analyze.filters.locfilter.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    A dialog to fix filters on localization of annotations of a tier.

"""

import sys
import wx

from sppas.src.config import msg
from sppas.src.utils import u

from sppas.src.ui.phoenix.windows import sppasDialog
from sppas.src.ui.phoenix.windows import sppasPanel
from sppas.src.ui.phoenix.windows import sppasStaticText
from sppas.src.ui.phoenix.windows import sppasRadioBoxPanel
from sppas.src.ui.phoenix.windows.book import sppasNotebook

# --------------------------------------------------------------------------


def _(message):
    return u(msg(message, "ui"))


MSG_LOC_FILTER = _("Filter on localization of annotations")

MSG_LOC = _("The localization is:")
MSG_FROM = _("starting at")
MSG_TO = _("ending at")
MSG_VALUE = _("this value:")

# ---------------------------------------------------------------------------


class sppasLocFilterDialog(sppasDialog):
    """Dialog to get a filter on a sppasLocalization.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2020  Brigitte Bigi

    """

    choices = (
        (MSG_FROM, "rangefrom"),
        (MSG_TO, "rangeto")
    )

    def __init__(self, parent):
        """Create a localization filter dialog.

        :param parent: (wx.Window)

        """
        super(sppasLocFilterDialog, self).__init__(
            parent=parent,
            title="+ Loc filter",
            style=wx.DEFAULT_FRAME_STYLE)

        self.CreateHeader(MSG_LOC_FILTER, "tier_filter_add_loc")
        self._create_content()
        self.CreateActions([wx.ID_CANCEL, wx.ID_OK])

        self.LayoutComponents()
        self.SetSizerAndFit(self.GetSizer())
        self.CenterOnParent()

    # -----------------------------------------------------------------------

    def get_data(self):
        """Return the data defined by the user.

        :returns: (tuple) with:
               - type (str): tag
               - function (str): one of the methods in Compare
               - values (list): patterns to find

        """
        notebook = self.FindWindow("content")
        page_idx = notebook.GetSelection()
        data = notebook.GetPage(page_idx).get_data()
        return data

    # -----------------------------------------------------------------------
    # Methods to construct the GUI
    # -----------------------------------------------------------------------

    def _create_content(self):
        """Create the content of the message dialog.

        notebook.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED, ...) not used because it
        is bugged under MacOS (do not display the page content).

        """
        # Make the notebook to show each possible type of tag
        notebook = sppasNotebook(self, name="content")

        # Create and add the pages to the notebook
        page1 = sppasLocFloatPanel(notebook)
        notebook.AddPage(page1, " Float ")
        page2 = sppasLocIntegerPanel(notebook)
        notebook.AddPage(page2, " Integer ")

        w, h = page1.GetMinSize()
        notebook.SetMinSize(wx.Size(w, h + (sppasPanel().get_font_height()*4)))
        self.SetContent(notebook)


# ---------------------------------------------------------------------------


class sppasLocFloatPanel(sppasPanel):
    """Panel to get a filter on a sppasLocalization if its type is 'float'.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2020  Brigitte Bigi

    """

    def __init__(self, parent):
        """Create a loc filter panel, for localizations of type float.

        :param parent: (wx.Window)

        """
        super(sppasLocFloatPanel, self).__init__(parent)
        top_label = sppasStaticText(self, label=MSG_LOC)
        top_label.SetMinSize(wx.Size(sppasPanel.fix_size(320), -1))
        bottom_label = sppasStaticText(self, label=MSG_VALUE)

        choices = [row[0] for row in sppasLocFilterDialog.choices]
        self.radiobox = sppasRadioBoxPanel(
            self,
            choices=choices,
            style=wx.RA_SPECIFY_COLS)
        self.radiobox.SetSelection(1)

        self.ctrl = wx.SpinCtrlDouble(
            self, value="", min=0.0, max=sys.float_info.max,
            inc=0.01, initial=0.)
        self.ctrl.SetDigits(3)

        # Layout
        b = sppasPanel.fix_size(6)

        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.Add(bottom_label, 0, flag=wx.ALIGN_CENTER_VERTICAL | wx.ALL, border=b)
        hbox.Add(self.ctrl, 1, flag=wx.EXPAND | wx.ALL, border=b)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(top_label, 0, flag=wx.EXPAND | wx.ALL, border=b)
        sizer.Add(self.radiobox, 0, flag=wx.EXPAND | wx.ALL, border=b*2)
        sizer.Add(hbox, 0, flag=wx.EXPAND | wx.BOTTOM, border=b)

        self.SetSizerAndFit(sizer)

    # -----------------------------------------------------------------------

    def get_data(self):
        """Return the data defined by the user.

        :returns: (tuple) with
               type (str): loc
               function (str): "rangefrom" or "rangeto"
               values (list): time value (represented by a float)

        """
        idx = self.radiobox.GetSelection()
        given_fct = sppasLocFilterDialog.choices[idx][1]
        str_value = self.ctrl.GetValue()
        try:
            value = float(str_value)
        except ValueError:
            wx.LogError("{:s} can't be converted to a float"
                        "".format(str_value))
            value = 0.

        return "loc", given_fct, [value]

# ---------------------------------------------------------------------------


class sppasLocIntegerPanel(sppasPanel):
    """Panel to get a filter on a sppasLocalization if its type is 'int'.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2020  Brigitte Bigi

    """

    def __init__(self, parent):
        """Create a loc filter panel, for localizations of type int.

        :param parent: (wx.Window)

        """
        super(sppasLocIntegerPanel, self).__init__(parent)
        top_label = sppasStaticText(self, label=MSG_LOC)
        bottom_label = sppasStaticText(self, label=MSG_VALUE)

        choices = [row[0] for row in sppasLocFilterDialog.choices]
        self.radiobox = sppasRadioBoxPanel(
            self,
            choices=choices,
            style=wx.RA_SPECIFY_COLS)
        self.radiobox.SetSelection(1)

        self.ctrl = wx.SpinCtrl(self, value="", min=0, max=sys.maxsize//100,
                                initial=0)

        # Layout
        b = sppasPanel.fix_size(6)

        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.Add(bottom_label, 0, flag=wx.ALIGN_CENTER_VERTICAL | wx.ALL, border=b)
        hbox.Add(self.ctrl, 1, flag=wx.EXPAND | wx.ALL, border=b)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(top_label, 0, flag=wx.EXPAND | wx.ALL, border=b)
        sizer.Add(self.radiobox, 0, flag=wx.EXPAND | wx.ALL, border=b*2)
        sizer.Add(hbox, 0, flag=wx.EXPAND | wx.BOTTOM, border=b)

        self.SetSizerAndFit(sizer)

    # -----------------------------------------------------------------------

    def get_data(self):
        """Return the data defined by the user.

        :returns: (tuple) with
               type (str): loc
               function (str): "rangefrom" or "rangeto"
               values (list): loc value (represented by an int)

        """
        idx = self.radiobox.GetSelection()
        given_fct = sppasLocFilterDialog.choices[idx][1]
        str_value = self.ctrl.GetValue()
        try:
            value = int(str_value)
        except ValueError:
            wx.LogError("{:s} can't be converted to an integer"
                        "".format(str_value))
            value = 0

        return "loc", given_fct, [value]

# ---------------------------------------------------------------------------


class TestPanel(sppasPanel):

    def __init__(self, parent, pos=wx.DefaultPosition, size=wx.DefaultSize):
        super(TestPanel, self).__init__(parent, pos=pos, size=size,
                                        name="Loc Filter")

        btn = wx.Button(self, label="Loc filter")
        btn.SetMinSize(wx.Size(150, 40))
        btn.SetPosition(wx.Point(10, 10))
        self.Bind(wx.EVT_BUTTON, self._process_event)

    # -----------------------------------------------------------------------

    def _process_event(self, event):
        """Process any kind of events.

        :param event: (wx.Event)

        """
        dlg = sppasLocFilterDialog(self)
        response = dlg.ShowModal()
        if response == wx.ID_OK:
            f = dlg.get_data()
            if len(f[1].strip()) > 0:
                wx.LogMessage("'loc': filter='{:s}'; value='{:s}'"
                              "".format(f[1], str(f[2])))
            else:
                wx.LogError("Empty input pattern.")
        dlg.Destroy()
