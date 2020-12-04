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

    src.ui.phoenix.page_analyze.filters.tagfilter.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    A dialog to fix filters on tags of annotations of a tier.

"""

import wx

from sppas.src.config import msg
from sppas.src.utils import u

from sppas.src.ui.phoenix.windows.dialogs import sppasDialog
from sppas.src.ui.phoenix.windows.panels import sppasPanel
from sppas.src.ui.phoenix.windows.text import sppasStaticText
from sppas.src.ui.phoenix.windows.text import sppasTextCtrl
from sppas.src.ui.phoenix.windows import sppasRadioBoxPanel
from sppas.src.ui.phoenix.windows.book import sppasNotebook
from sppas.src.ui.phoenix.windows.buttons import CheckButton

# --------------------------------------------------------------------------


def _(message):
    return u(msg(message, "ui"))


MSG_TAG_FILTER = _("Filter on tags of annotations")

MSG_TAG_TYPE_BOOL = _("Boolean value of the tag is:")
MSG_TAG_TYPE_INT = _("Integer value of the tag is:")
MSG_TAG_TYPE_FLOAT = _("Float value of the tag is:")
MSG_TAG_TYPE_STR = _("Patterns to find, separated by commas, are:")
DEFAULT_LABEL = "tag1, tag2..."
MSG_CASE = _("Case sensitive")

MSG_FALSE = _("False")
MSG_TRUE = _("True")

MSG_EQUAL = _("equal to")
MSG_NOT_EQUAL = _("not equal to")
MSG_GT = _("greater than")
MSG_LT = _("less than")
MSG_GE = _("greater or equal to")
MSG_LE = _("less or equal to")

MSG_EXACT = _("exact")
MSG_CONTAINS = _("contains")
MSG_STARTSWITH = _("starts with")
MSG_ENDSWITH = _("ends with")
MSG_REGEXP = _("match (regexp)")
MSG_NOT_EXACT = _("not exact")
MSG_NOT_CONTAINS = _("not contains")
MSG_NOT_STARTSWITH = _("not starts with")
MSG_NOT_ENDSWITH = _("not ends with")
MSG_NOT_REGEXP = _("not match (regexp)")
MSG_FROM = _("starting at")
MSG_TO = _("ending at")
MSG_VALUE = _("this value:")

# ---------------------------------------------------------------------------


class sppasTagFilterDialog(sppasDialog):
    """Dialog to get a filter on a sppasTag.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2020  Brigitte Bigi

    """

    def __init__(self, parent):
        """Create a string filter dialog.

        :param parent: (wx.Window)

        """
        super(sppasTagFilterDialog, self).__init__(
            parent=parent,
            title="+ Tag filter",
            style=wx.DEFAULT_FRAME_STYLE)

        self.CreateHeader(MSG_TAG_FILTER, "tier_filter_add_tag")
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
        page1 = sppasTagStringPanel(notebook)
        notebook.AddPage(page1, " String ")
        page2 = sppasTagIntegerPanel(notebook)
        notebook.AddPage(page2, " Integer ")
        page3 = sppasTagFloatPanel(notebook)
        notebook.AddPage(page3, " Float ")
        page4 = sppasTagBooleanPanel(notebook)
        notebook.AddPage(page4, " Boolean ")

        w, h = page1.GetMinSize()
        notebook.SetMinSize(wx.Size(w, h+(sppasPanel().get_font_height()*4)))
        self.SetContent(notebook)

# ---------------------------------------------------------------------------


class sppasTagStringPanel(sppasPanel):
    """Panel to get a filter on a sppasTag if its type is 'str'.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2020  Brigitte Bigi

    """

    choices = (
               (MSG_EXACT, "exact"),
               (MSG_CONTAINS, "contains"),
               (MSG_STARTSWITH, "startswith"),
               (MSG_ENDSWITH, "endswith"),
               (MSG_REGEXP, "regexp"),

               (MSG_NOT_EXACT, "exact"),
               (MSG_NOT_CONTAINS, "contains"),
               (MSG_NOT_STARTSWITH, "startswith"),
               (MSG_NOT_ENDSWITH, "endswith"),
               (MSG_NOT_REGEXP, "regexp"),
              )

    def __init__(self, parent):
        super(sppasTagStringPanel, self).__init__(parent)
        top_label = sppasStaticText(self, label=MSG_TAG_TYPE_STR)
        top_label.SetMinSize(wx.Size(sppasPanel.fix_size(320), -1))
        self.text = sppasTextCtrl(self, value=DEFAULT_LABEL)

        functions = [row[0] for row in sppasTagStringPanel.choices]
        self.radiobox = sppasRadioBoxPanel(
            self,
            choices=functions,
            majorDimension=2,
            style=wx.RA_SPECIFY_COLS)
        self.radiobox.SetSelection(1)

        self.checkbox = CheckButton(self, label=MSG_CASE)
        self.checkbox.SetMinSize(wx.Size(-1, self.get_font_height()*2))
        self.checkbox.SetFocusWidth(0)
        self.checkbox.SetValue(True)

        # Layout
        sizer = wx.BoxSizer(wx.VERTICAL)
        b = sppasPanel.fix_size(6)
        sizer.Add(top_label, 0, flag=wx.EXPAND | wx.ALL, border=b)
        sizer.Add(self.text, 0, flag=wx.EXPAND | wx.ALL, border=b)
        sizer.Add(self.radiobox, 0, flag=wx.EXPAND | wx.ALL,border=b*2)
        sizer.Add(self.checkbox, 0, flag=wx.EXPAND | wx.ALL, border=b)

        self.SetSizerAndFit(sizer)

    # -----------------------------------------------------------------------

    def get_data(self):
        """Return the data defined by the user.

        :returns: (tuple) with:
               - type (str): tag
               - function (str): one of the methods in Compare
               - values (list): patterns to find

        """
        idx = self.radiobox.GetSelection()
        label = self.radiobox.GetStringSelection()
        given_fct = sppasTagStringPanel.choices[idx][1]

        # Fill the resulting dict
        prepend_fct = ""

        if given_fct != "regexp":
            # prepend "not_" if reverse
            if "not" in label:
                prepend_fct += "not_"
            # prepend "i" if case-insensitive
            if self.checkbox.GetValue() is False:
                prepend_fct += "i"

            # fix the value to find (one or several with the same function)
            given_patterns = self.text.GetValue()
            values = given_patterns.split(',')
            values = [" ".join(p.split()) for p in values]
        else:
            values = [self.text.GetValue()]

        return "tag", prepend_fct+given_fct, values

# ---------------------------------------------------------------------------


class sppasTagIntegerPanel(sppasPanel):
    """Panel to get a filter on a sppasTag if its type is 'int'.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2020  Brigitte Bigi

    """

    choices = (
               (MSG_EQUAL, "equal"),
               (MSG_GT, "greater"),
               (MSG_LT, "lower"),
             )

    def __init__(self, parent):
        super(sppasTagIntegerPanel, self).__init__(parent)
        top_label = sppasStaticText(self, label=MSG_TAG_TYPE_INT)

        functions = [row[0] for row in sppasTagIntegerPanel.choices]
        self.radiobox = sppasRadioBoxPanel(
            self,
            choices=functions,
            style=wx.RA_SPECIFY_COLS)
        self.radiobox.SetSelection(1)

        self.text = sppasTextCtrl(self, value="0")

        # Layout
        sizer = wx.BoxSizer(wx.VERTICAL)
        b = sppasPanel.fix_size(6)
        sizer.Add(top_label, 0, flag=wx.EXPAND | wx.ALL, border=b)
        sizer.Add(self.radiobox, 0, flag=wx.EXPAND | wx.ALL, border=b*2)
        sizer.Add(self.text, 0, flag=wx.EXPAND | wx.ALL, border=b)
        self.SetSizerAndFit(sizer)

    # -----------------------------------------------------------------------

    def get_data(self):
        """Return the data defined by the user.

        :returns: (tuple) with:
               - type (str): tag
               - function (str): one of the methods in Compare
               - values (list): integer to compare

        """
        idx = self.radiobox.GetSelection()
        given_fct = sppasTagIntegerPanel.choices[idx][1]
        str_value = self.text.GetValue()
        try:
            value = int(str_value)
        except ValueError:
            wx.LogError("{:s} can't be converted to an integer"
                        "".format(str_value))
            value = 0

        return "tag", given_fct, [value]

# ---------------------------------------------------------------------------


class sppasTagFloatPanel(sppasPanel):
    """Panel to get a filter on a sppasTag if its type is 'float'.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2020  Brigitte Bigi

    """

    choices = (
               (MSG_EQUAL, "equal"),
               (MSG_GT, "greater"),
               (MSG_LT, "lower"),
             )

    def __init__(self, parent):
        """Create a tag filter panel, for tags of type float.

         :param parent: (wx.Window)

         """
        super(sppasTagFloatPanel, self).__init__(parent)
        top_label = sppasStaticText(self, label=MSG_TAG_TYPE_FLOAT)

        functions = [row[0] for row in sppasTagIntegerPanel.choices]
        self.radiobox = sppasRadioBoxPanel(
            self,
            choices=functions,
            style=wx.RA_SPECIFY_COLS)
        self.radiobox.SetSelection(0)

        self.text = sppasTextCtrl(self, value="0.")

        # Layout
        sizer = wx.BoxSizer(wx.VERTICAL)
        b = sppasPanel.fix_size(6)
        sizer.Add(top_label, 0, flag=wx.EXPAND | wx.ALL, border=b)
        sizer.Add(self.radiobox, 0, flag=wx.EXPAND | wx.ALL, border=b*2)
        sizer.Add(self.text, 0, flag=wx.EXPAND | wx.ALL, border=b)
        self.SetSizerAndFit(sizer)

    # -----------------------------------------------------------------------

    def get_data(self):
        """Return the data defined by the user.

        :returns: (tuple) with:
               - type (str): tag
               - function (str): one of the methods in Compare
               - values (list): patterns to find

        """
        idx = self.radiobox.GetSelection()
        given_fct = sppasTagIntegerPanel.choices[idx][1]
        str_value = self.text.GetValue()
        try:
            value = float(str_value)
        except ValueError:
            wx.LogError("{:s} can't be converted to a float"
                        "".format(str_value))
            value = 0.

        return "tag", given_fct, [value]

# ---------------------------------------------------------------------------


class sppasTagBooleanPanel(sppasPanel):
    """Panel to get a filter on a sppasTag if its type is 'boolean'.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2020  Brigitte Bigi

    """

    def __init__(self, parent):
        """Create a tag filter panel, for tags of type boolean.

        :param parent: (wx.Window)

        """
        super(sppasTagBooleanPanel, self).__init__(parent)
        top_label = sppasStaticText(self, label=MSG_TAG_TYPE_BOOL)

        self.radiobox = sppasRadioBoxPanel(
            self, choices=[MSG_FALSE, MSG_TRUE], style=wx.RA_SPECIFY_COLS)
        self.radiobox.SetSelection(1)

        # Layout
        sizer = wx.BoxSizer(wx.VERTICAL)
        b = sppasPanel.fix_size(6)
        sizer.Add(top_label, 0, flag=wx.EXPAND | wx.ALL, border=b)
        sizer.Add(self.radiobox, 0, flag=wx.EXPAND | wx.ALL, border=b*2)
        self.SetSizerAndFit(sizer)

    # -----------------------------------------------------------------------

    def get_data(self):
        """Return the data defined by the user.

        :returns: (tuple) with:
               - type (str): tag
               - function (str): bool
               - values (list): patterns to find

        """
        # False is at index 0 so that bool(index) gives the value
        idx = self.radiobox.GetSelection()
        return "tag", "bool", [bool(idx)]

# ---------------------------------------------------------------------------


class TestPanel(sppasPanel):

    def __init__(self, parent, pos=wx.DefaultPosition, size=wx.DefaultSize):
        super(TestPanel, self).__init__(parent, pos=pos, size=size,
                                        name="Tag Filter")

        btn = wx.Button(self, label="Tag filter")
        btn.SetMinSize(wx.Size(150, 40))
        btn.SetPosition(wx.Point(10, 10))
        self.Bind(wx.EVT_BUTTON, self._process_event)

    # -----------------------------------------------------------------------

    def _process_event(self, event):
        """Process any kind of events.

        :param event: (wx.Event)

        """
        dlg = sppasTagFilterDialog(self)
        response = dlg.ShowModal()
        if response == wx.ID_OK:
            f = dlg.get_data()
            if len(f[1].strip()) > 0:
                wx.LogMessage("'tag': filter='{:s}'; value='{:s}'"
                              "".format(f[1], str(f[2])))
            else:
                wx.LogError("Empty input pattern.")
        dlg.Destroy()
