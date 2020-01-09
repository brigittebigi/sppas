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

    src.ui.phoenix.dialogs.tiersfilters.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""

import sys
import wx
import wx.dataview

from sppas import sg
from sppas.src.anndata import sppasTier
from sppas.src.config import ui_translation

from ..windows import sppasDialog
from ..windows import sppasPanel
from ..windows import sppasToolbar
from ..windows import BitmapTextButton, CheckButton
from ..windows import sppasTextCtrl, sppasStaticText
from ..windows import sppasRadioBoxPanel
from ..dialogs import Information
from ..windows.book import sppasNotebook


# --------------------------------------------------------------------------

MSG_HEADER_TIERSFILTER = ui_translation.gettext("Filter annotations of tiers")

MSG_TAG_FILTER = ui_translation.gettext("Filter on tags of annotations")
MSG_LOC_FILTER = ui_translation.gettext("Filter on localization of annotations")
MSG_DUR_FILTER = ui_translation.gettext("Filter on duration of annotations")

MSG_LOC = ui_translation.gettext("The localization is:")
MSG_DUR = ui_translation.gettext("The duration is:")

MSG_TAG_TYPE_BOOL = ui_translation.gettext("Boolean value of the tag is:")
MSG_TAG_TYPE_INT = ui_translation.gettext("Integer value of the tag is:")
MSG_TAG_TYPE_FLOAT = ui_translation.gettext("Float value of the tag is:")
MSG_TAG_TYPE_STR = ui_translation.gettext("Patterns to find, "
                                          "separated by commas, are:")
DEFAULT_LABEL = "tag1, tag2..."
MSG_CASE = ui_translation.gettext("Case sensitive")

MSG_FALSE = ui_translation.gettext("False")
MSG_TRUE = ui_translation.gettext("True")

MSG_EQUAL = ui_translation.gettext("equal to")
MSG_NOT_EQUAL = ui_translation.gettext("not equal to")
MSG_GT = ui_translation.gettext("greater than")
MSG_LT = ui_translation.gettext("less than")
MSG_GE = ui_translation.gettext("greater or equal to")
MSG_LE = ui_translation.gettext("less or equal to")

MSG_EXACT = ui_translation.gettext("exact")
MSG_CONTAINS = ui_translation.gettext("contains")
MSG_STARTSWITH = ui_translation.gettext("starts with")
MSG_ENDSWITH = ui_translation.gettext("ends with")
MSG_REGEXP = ui_translation.gettext("match (regexp)")
MSG_NOT_EXACT = ui_translation.gettext("not exact")
MSG_NOT_CONTAINS = ui_translation.gettext("not contains")
MSG_NOT_STARTSWITH = ui_translation.gettext("not starts with")
MSG_NOT_ENDSWITH = ui_translation.gettext("not ends with")
MSG_NOT_REGEXP = ui_translation.gettext("not match (regexp)")
MSG_FROM = ui_translation.gettext("starting at")
MSG_TO = ui_translation.gettext("ending at")
MSG_VALUE = ui_translation.gettext("this value:")

# ---------------------------------------------------------------------------


class sppasTiersSingleFilterDialog(sppasDialog):
    """A dialog to filter annotations of tiers.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2020  Brigitte Bigi

    Returns wx.ID_OK if ShowModal().

    """

    def __init__(self, parent, tiers):
        """Create a dialog to fix settings.

        :param parent: (wx.Window)
        :param tiers: dictionary with key=filename, value=list of selected tiers

        """
        super(sppasTiersSingleFilterDialog, self).__init__(
            parent=parent,
            title="Tiers Filter",
            style=wx.CAPTION | wx.RESIZE_BORDER | wx.CLOSE_BOX | wx.MAXIMIZE_BOX | wx.STAY_ON_TOP,
            name="tierfilter-dialog")

        self.CreateHeader(MSG_HEADER_TIERSFILTER, "tier_ann_view")
        self._create_content()
        self._create_buttons()
        self.Bind(wx.EVT_BUTTON, self._process_event)

        self.LayoutComponents()
        self.GetSizer().Fit(self)
        self.CenterOnParent()
        self.FadeIn(deltaN=-8)

    # -----------------------------------------------------------------------
    # Public methods
    # -----------------------------------------------------------------------

    def get_filters(self):
        """Return a list of (filter, function, values)."""
        filters = list()
        for i in range(self.listctrl.GetItemCount()):
            filter_name = self.listctrl.GetValue(i, 0)
            fct_name = self.listctrl.GetValue(i, 1)
            values = self.listctrl.GetValue(i, 2)
            filters.append((filter_name, fct_name, values))
        return filters

    # -----------------------------------------------------------------------
    # Construct the GUI
    # -----------------------------------------------------------------------

    def _create_content(self):
        """Create the content of the message dialog."""
        panel = sppasPanel(self, name="content")
        tb = self.__create_toolbar(panel)
        self.listctrl = wx.dataview.DataViewListCtrl(panel, wx.ID_ANY)
        self.listctrl.AppendTextColumn("filter", width=80)
        self.listctrl.AppendTextColumn("function", width=90)
        self.listctrl.AppendTextColumn("value", width=120)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(tb, proportion=0, flag=wx.EXPAND, border=0)
        sizer.Add(self.listctrl, proportion=1, flag=wx.EXPAND | wx.LEFT | wx.RIGHT, border=5)
        panel.SetSizer(sizer)

        self.SetMinSize(wx.Size(320, 200))
        panel.SetAutoLayout(True)
        self.SetContent(panel)

    # -----------------------------------------------------------------------

    def __create_toolbar(self, parent):
        """Create the toolbar."""
        tb = sppasToolbar(parent)
        tb.set_focus_color(wx.Colour(196, 196, 96, 128))
        tb.AddTextButton("tier_filter_add_tag", "+ Tag")
        tb.AddTextButton("tier_filter_add_loc", "+ Loc")
        tb.AddTextButton("tier_filter_add_dur", "+ Dur")
        tb.AddSpacer()
        #tb.AddTextButton(None, "- Remove")
        return tb

    # -----------------------------------------------------------------------

    def _create_buttons(self):
        """Create the buttons and bind events."""
        panel = sppasPanel(self, name="actions")
        # panel.SetMinSize(wx.Size(-1, wx.GetApp().settings.action_height))
        sizer = wx.BoxSizer(wx.HORIZONTAL)

        # Create the buttons
        cancel_btn = self.__create_action_button(panel, "Cancel", "cancel")
        apply_or_btn = self.__create_action_button(panel, "Apply - OR", "window-apply")
        apply_and_btn = self.__create_action_button(panel, "Apply - AND", "ok")
        apply_and_btn.SetFocus()

        sizer.Add(cancel_btn, 1, wx.ALL | wx.EXPAND, 0)
        sizer.Add(self.VertLine(parent=panel), 0, wx.ALL | wx.EXPAND, 0)
        sizer.Add(apply_or_btn, 1, wx.ALL | wx.EXPAND, 0)
        sizer.Add(self.VertLine(parent=panel), 0, wx.ALL | wx.EXPAND, 0)
        sizer.Add(apply_and_btn, 1, wx.ALL | wx.EXPAND, 0)

        panel.SetSizer(sizer)
        self.SetActions(panel)

    # -----------------------------------------------------------------------

    def __create_action_button(self, parent, text, icon):
        btn = BitmapTextButton(parent, label=text, name=icon)
        btn.LabelPosition = wx.RIGHT
        btn.Spacing = sppasDialog.fix_size(12)
        btn.BorderWidth = 0
        btn.BitmapColour = self.GetForegroundColour()
        btn.SetMinSize(wx.Size(sppasDialog.fix_size(32),
                               sppasDialog.fix_size(32)))

        return btn

    # ------------------------------------------------------------------------
    # Callback to events
    # ------------------------------------------------------------------------

    def _process_event(self, event):
        """Process any kind of events.

        :param event: (wx.Event)

        """
        event_obj = event.GetEventObject()
        event_name = event_obj.GetName()

        if event_name == "tier_filter_add_tag":
            self.__append_filter("tag")

        elif event_name == "tier_filter_add_loc":
            self.__append_filter("loc")

        elif event_name == "tier_filter_add_dur":
            self.__append_filter("dur")

        elif event_name == "cancel":
            self.SetReturnCode(wx.ID_CANCEL)
            self.Close()

        elif event_name == "window-apply":
            self.match_all = False
            self.EndModal(wx.ID_APPLY)

        elif event_name == "ok":
            self.match_all = True
            self.EndModal(wx.ID_OK)

        else:
            event.Skip()

    # ------------------------------------------------------------------------

    def __append_filter(self, fct):
        if fct == "loc":
            dlg = sppasLocFilterDialog(self)
        elif fct == "dur":
            dlg = sppasDurFilterDialog(self)
        else:
            dlg = sppasTagFilterDialog(self)
        response = dlg.ShowModal()
        if response == wx.ID_OK:
            f = dlg.get_data()
            if len(f[1].strip()) > 0:
                self.listctrl.AppendItem([fct, f[0], f[1].strip()])
            else:
                wx.LogError("Empty input pattern.")
        dlg.Destroy()

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

        self.SetSize(wx.Size(sppasPanel.fix_size(380),
                             sppasPanel.fix_size(300)))
        self.LayoutComponents()
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

        notebook.SetMinSize(wx.Size(sppasPanel.fix_size(320),
                                    sppasPanel.fix_size(200)))
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
        self.text = sppasTextCtrl(self, value=DEFAULT_LABEL)

        functions = [row[0] for row in sppasTagStringPanel.choices]
        self.radiobox = sppasRadioBoxPanel(
            self,
            choices=functions,
            majorDimension=2,
            style=wx.RA_SPECIFY_COLS)
        self.radiobox.SetSelection(1)

        self.checkbox = CheckButton(self, label=MSG_CASE)
        self.checkbox.SetValue(True)

        # Layout
        sizer = wx.BoxSizer(wx.VERTICAL)
        b = sppasPanel.fix_size(6)
        sizer.Add(top_label, 0, flag=wx.EXPAND | wx.ALL, border=b)
        sizer.Add(self.text, 0, flag=wx.EXPAND | wx.ALL, border=b)
        sizer.Add(self.radiobox, 0, flag=wx.EXPAND | wx.ALL,border=b*2)
        sizer.Add(self.checkbox, 0, flag=wx.EXPAND | wx.ALL, border=b)
        self.SetSizer(sizer)

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
        self.SetSizer(sizer)

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
        self.SetSizer(sizer)

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
        self.SetSizer(sizer)

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

        self.SetSize(wx.Size(sppasPanel.fix_size(380),
                             sppasPanel.fix_size(300)))
        self.LayoutComponents()
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

        notebook.SetMinSize(wx.Size(sppasPanel.fix_size(320),
                                    sppasPanel.fix_size(200)))
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
        sizer.Add(hbox, 0, flag=wx.EXPAND | wx.ALL, border=0)

        self.SetSizer(sizer)

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
        sizer.Add(hbox, 0, flag=wx.EXPAND | wx.ALL, border=0)

        self.SetSizer(sizer)

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


class sppasDurFilterDialog(sppasDialog):
    """Dialog to get a filter on a sppasDuration.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2020  Brigitte Bigi

    """

    choices = (
        (MSG_EQUAL, "eq"),
        (MSG_NOT_EQUAL, "ne"),
        (MSG_GT, "gt"),
        (MSG_LT, "lt"),
        (MSG_GE, "ge"),
        (MSG_LE, "le")
    )

    def __init__(self, parent):
        """Create a duration filter dialog.

        :param parent: (wx.Window)

        """
        super(sppasDurFilterDialog, self).__init__(
            parent=parent,
            title='{:s} filter'.format(sg.__name__),
            style=wx.DEFAULT_FRAME_STYLE)

        self.CreateHeader(MSG_DUR_FILTER, "tier_filter_add_dur")
        self._create_content()
        self.CreateActions([wx.ID_CANCEL, wx.ID_OK])

        self.SetSize(wx.Size(sppasPanel.fix_size(380),
                             sppasPanel.fix_size(320)))
        self.LayoutComponents()
        self.CenterOnParent()

    # -----------------------------------------------------------------------

    def get_data(self):
        """Return the data defined by the user.

        :returns: (tuple) with
               type (str): dur
               function (str): one of the choices
               values (list): time value (represented by a 'str')

        """
        idx = self.radiobox.GetSelection()
        given_fct = sppasDurFilterDialog.choices[idx][1]
        value = self.ctrl.GetValue()
        return "dur", given_fct, [value]

    # -----------------------------------------------------------------------
    # Method to construct the GUI
    # -----------------------------------------------------------------------

    def _create_content(self):
        """Create the content of the message dialog."""
        panel = sppasPanel(self, name="content")

        top_label = sppasStaticText(panel, label=MSG_DUR)
        bottom_label = sppasStaticText(panel, label=MSG_VALUE)

        choices = [row[0] for row in sppasDurFilterDialog.choices]
        self.radiobox = sppasRadioBoxPanel(
            panel,
            choices=choices,
            style=wx.RA_SPECIFY_COLS)
        self.radiobox.SetSelection(0)

        self.ctrl = wx.SpinCtrlDouble(
            panel, value="", min=0.0, inc=0.01, initial=0.)
        self.ctrl.SetDigits(3)

        # Layout
        b = sppasPanel.fix_size(6)

        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.Add(bottom_label, 0, flag=wx.ALIGN_CENTER_VERTICAL | wx.ALL, border=b)
        hbox.Add(self.ctrl, 1, flag=wx.EXPAND | wx.ALL, border=b)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(top_label, 0, flag=wx.EXPAND | wx.ALL, border=b)
        sizer.Add(self.radiobox, 0, flag=wx.EXPAND | wx.ALL, border=2*b)
        sizer.Add(hbox, 0, flag=wx.EXPAND | wx.ALL, border=0)

        panel.SetSizer(sizer)
        panel.SetAutoLayout(True)
        self.SetContent(panel)

# ----------------------------------------------------------------------------
# Panel tested by test_glob.py
# ----------------------------------------------------------------------------


class TestPanel(sppasPanel):

    def __init__(self, parent):
        super(TestPanel, self).__init__(parent, name="TestPanel-tiersfilter")

        btn_tag = wx.Button(self,
                            pos=(10, 10),
                            size=(180, 70),
                            label="+ Tag filter",
                            name="tag_btn")
        btn_loc = wx.Button(self,
                            pos=(200, 10),
                            size=(180, 70),
                            label="+ Loc filter",
                            name="loc_btn")
        btn_dur = wx.Button(self,
                            pos=(390, 10),
                            size=(180, 70),
                            label="+ Dur filter",
                            name="dur_btn")
        self.Bind(wx.EVT_BUTTON, self._process_event)

    def _process_event(self, event):
        """Process any kind of events.

        :param event: (wx.Event)

        """
        event_obj = event.GetEventObject()
        event_name = event_obj.GetName()

        if event_name == "tag_btn":
            dlg = sppasTagFilterDialog(self)
            response = dlg.ShowModal()
            if response == wx.ID_OK:
                f = dlg.get_data()
                if len(f[1].strip()) > 0:
                    wx.LogMessage("'tag': filter='{:s}'; values='{!s:s}'"
                                  "".format(f[1], str(f[2])))
                else:
                    wx.LogError("Empty input pattern.")
            dlg.Destroy()

        elif event_name == "loc_btn":
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

        elif event_name == "dur_btn":
            dlg = sppasDurFilterDialog(self)
            response = dlg.ShowModal()
            if response == wx.ID_OK:
                f = dlg.get_data()
                if len(f[1].strip()) > 0:
                    wx.LogMessage("'dur': filter='{:s}'; value='{:s}'"
                                  "".format(f[1], str(f[2])))
                else:
                    wx.LogError("Empty input pattern.")
            dlg.Destroy()

