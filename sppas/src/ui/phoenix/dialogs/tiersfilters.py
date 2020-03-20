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
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    A dialog to fix a list of filters and any parameter needed. DO NOT APPLY
    THE FILTERS ON TIERS.

"""

import sys
import wx
import wx.dataview
try:
    from agw import floatspin as FS
    import agw.ultimatelistctrl as ulc
except ImportError:
    import wx.lib.agw.floatspin as FS
    import wx.lib.agw.ultimatelistctrl as ulc

from sppas import sg
from sppas.src.config import msg
from sppas.src.utils import u

from ..windows import sppasDialog
from ..windows import sppasPanel
from ..windows import sppasToolbar
from ..windows import BitmapTextButton
from ..windows import CheckButton
from ..windows import sppasTextCtrl, sppasStaticText
from ..windows import sppasRadioBoxPanel
from ..windows.book import sppasNotebook

# --------------------------------------------------------------------------


def _(message):
    return u(msg(message, "ui"))


MSG_HEADER_TIERSFILTER = _("Filter annotations of tiers")

MSG_TAG_FILTER = _("Filter on tags of annotations")
MSG_LOC_FILTER =_("Filter on localization of annotations")
MSG_DUR_FILTER = _("Filter on duration of annotations")

MSG_LOC = _("The localization is:")
MSG_DUR = _("The duration is:")

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

MSG_ANNOT_FORMAT = _("Replace the tag by the name of the filter")
MSG_NAME = _("Name")
MSG_OPT = _("Option")

# ---------------------------------------------------------------------------

Relations = (
               ('equals', ' Equals', '', '', ''),
               ('before', ' Before', 'Max delay\nin seconds: ', 3.0, 'max_delay'),
               ('after', ' After', 'Max delay\nin seconds: ', 3.0, 'max_delay'),
               ('meets', ' Meets', '', '', ''),
               ('metby', ' Met by', '', '', ''),
               ('overlaps', ' Overlaps', 'Min overlap\n in seconds: ', 0.030, 'overlap_min'),
               ('overlappedby', ' Overlapped by', 'Min overlap\n in seconds: ', 0.030, 'overlap_min'),
               ('starts', ' Starts', '', '', ''),
               ('startedby', ' Started by', '', '', ''),
               ('finishes', ' Finishes', '', '', ''),
               ('finishedby', ' Finished by', '', '', ''),
               ('during', ' During', '', '', ''),
               ('contains', ' Contains', '', '', '')
            )

Illustrations = (
               # equals
               ('X |-----|\nY |-----|',
                'Non efficient',
                'Non efficient',
                'X |\nY |'),
               # before
               ('X |-----|\nY' + ' ' * 15 + '|-----|',
                'X |-----|\nY' + ' ' * 15 + '|',
                'X |\nY   |-----|',
                'X |\nY   |'),
               # after
               ('X' + ' ' * 15 + '|-----|\nY |-----|',
                'X' + ' ' * 15 + '|\nY |-----|',
                'X   |-----|\nY |',
                'X   |\nY |'),
               # meets
               ('X |-----|\nY' + ' ' * 8 + '|-----|',
                'Non efficient',
                'Non efficient',
                'Non efficient'),
               # metby
               ('X' + ' ' * 8 + '|-----|\nY |-----|',
                'Non efficient',
                'Non efficient',
                'Non efficient'),
               # overlaps
               ('X |-----|\nY ' + ' ' * 5 + '|-----|',
                'Non efficient',
                'Non efficient',
                'Non efficient'),
               # overlappedby
               ('X' + ' ' * 5 + '|-----|\nY |-----|',
                'Non efficient',
                'Non efficient',
                'Non efficient'),
               # starts
               ('X |---|\nY |-----|',
                'Non efficient',
                'Non efficient',
                'Non efficient'),
               # startedby
               ('X |-----|\nY |---|',
                'Non efficient',
                'Non efficient',
                'Non efficient'),
               # finishes
               ('X |---|\nY    |------|',
                'Non efficient',
                'Non efficient',
                'Non efficient'),
               # finishedby
               ('X |------|\nY    |---|',
                'Non efficient',
                'Non efficient',
                'Non efficient'),
               # during
               ('X    |---|\nY |------|',
                'Non efficient',
                'X      |\nY |------|',
                'Non efficient'),
               # contains
               ('X |------|\nY    |---|',
                'X |-----|\nY     |',
                'Non efficient',
                'Non efficient'),
               )

ALLEN_RELATIONS = tuple(row + Illustrations[i] for i, row in enumerate(Relations))

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

    def __init__(self, parent):
        """Create a dialog to fix settings.

        :param parent: (wx.Window)
        :param tiers: dictionary with key=filename, value=list of selected tiers

        """
        super(sppasTiersSingleFilterDialog, self).__init__(
            parent=parent,
            title="Tiers Single Filter",
            style=wx.CAPTION | wx.RESIZE_BORDER | wx.CLOSE_BOX | wx.MAXIMIZE_BOX | wx.STAY_ON_TOP,
            name="tierfilter-dialog")

        self.__filters = list()
        self.match_all = True

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
        """Return a list of tuples (filter, function, [typed values])."""
        return self.__filters

    # -----------------------------------------------------------------------

    def get_tiername(self):
        """Return the expected name of the filtered tier."""
        w = self.FindWindow("tiername_textctrl")
        return w.GetValue()

    # -----------------------------------------------------------------------

    def get_annot_format(self):
        """Return True if the label has to be replaced by the filter name."""
        w = self.FindWindow("annotformat_checkbutton")
        return w.GetValue()

    # -----------------------------------------------------------------------
    # Construct the GUI
    # -----------------------------------------------------------------------

    def _create_content(self):
        """Create the content of the message dialog."""
        b = sppasPanel.fix_size(6)
        panel = sppasPanel(self, name="content")
        tb = self.__create_toolbar(panel)
        lst = self.__create_list_filters(panel)
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        st = sppasStaticText(self, label="Name of the filtered tier:")
        nt = sppasTextCtrl(self, value="Filtered", name="tiername_textctrl")
        hbox.Add(st, 0, wx.ALIGN_CENTRE_VERTICAL | wx.ALL, b)
        hbox.Add(nt, 1, wx.EXPAND | wx.ALL, b)
        an_box = CheckButton(self, label=MSG_ANNOT_FORMAT)
        an_box.SetValue(False)
        an_box.SetName("annotformat_checkbutton")

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(tb, 0, wx.EXPAND, 0)
        sizer.Add(lst, 1, wx.EXPAND | wx.ALL, b)
        sizer.Add(hbox, 0)
        sizer.Add(an_box, 0, wx.EXPAND | wx.ALL, b)

        panel.SetSizer(sizer)
        panel.SetAutoLayout(True)
        self.SetContent(panel)

    # -----------------------------------------------------------------------

    def __create_toolbar(self, parent):
        """Create the toolbar."""
        tb = sppasToolbar(parent)
        tb.set_focus_color(wx.Colour(180, 230, 255))
        tb.AddTextButton("tier_filter_add_tag", "+ Tag")
        tb.AddTextButton("tier_filter_add_loc", "+ Loc")
        tb.AddTextButton("tier_filter_add_dur", "+ Dur")
        tb.AddSpacer()
        tb.AddTextButton("tier_filter_delete", "- Remove")
        return tb

    # -----------------------------------------------------------------------

    def __create_list_filters(self, parent):
        style = wx.BORDER_NONE | wx.LC_REPORT | wx.LC_SINGLE_SEL | wx.LC_HRULES
        lst = wx.ListCtrl(parent, style=style, name="filters_listctrl")
        lst.AppendColumn("filter name",
                         format=wx.LIST_FORMAT_LEFT,
                         width=sppasPanel.fix_size(80))
        lst.AppendColumn("function",
                         format=wx.LIST_FORMAT_LEFT,
                         width=sppasPanel.fix_size(90))
        lst.AppendColumn("value",
                         format=wx.LIST_FORMAT_LEFT,
                         width=sppasPanel.fix_size(120))

        return lst

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
        btn.SetLabelPosition(wx.RIGHT)
        btn.SetSpacing(sppasDialog.fix_size(12))
        btn.SetBitmapColour(self.GetForegroundColour())
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

        elif event_name == "tier_filter_delete":
            self.__remove_filter()

        elif event_name == "cancel":
            self.__action("cancel")

        elif event_name == "window-apply":
            self.__action("or")

        elif event_name == "ok":
            self.__action("and")

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
            str_values = " ".join([str(v) for v in f[2]])
            if len(str_values) > 0:
                self.__filters.append(f)
                listctrl = self.FindWindow("filters_listctrl")
                str_values = " ".join(str(v) for v in f[2])
                listctrl.Append([f[0], f[1], str_values])
                self.Layout()
            else:
                wx.LogError("Empty input pattern.")
        dlg.Destroy()

    # ------------------------------------------------------------------------

    def __remove_filter(self):
        listctrl = self.FindWindow("filters_listctrl")
        if listctrl.GetSelectedItemCount() > 0:
            index = listctrl.GetFirstSelected()
            wx.LogDebug("Remove item selected at index {:d}".format(index))
            self.__filters.pop(index)
            listctrl.DeleteItem(index)
            self.Layout()
        else:
            wx.LogDebug("No filter selected to be removed.")

    # ------------------------------------------------------------------------

    def __action(self, name="cancel"):
        """Close the dialog."""
        if len(self.__filters) == 0 or name == "cancel":
            self.SetReturnCode(wx.ID_CANCEL)
            self.Close()
        else:
            if name == "and":
                self.match_all = True
                self.EndModal(wx.ID_OK)
            elif name == "or":
                self.match_all = False
                self.EndModal(wx.ID_APPLY)

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

        self.LayoutComponents()
        self.SetSizerAndFit(self.GetSizer())
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
        top_label.SetMinSize(wx.Size(sppasPanel.fix_size(320), -1))
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


# ---------------------------------------------------------------------------


class sppasTiersRelationFilterDialog(sppasDialog):
    """A dialog to filter annotations of tiers.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2020  Brigitte Bigi

    Returns wx.ID_OK if ShowModal().

    """

    Relations = (
        ('equals', 'Equals', '', '', ''),
        ('before', 'Before', 'Max delay\nin seconds:', 3.0, 'max_delay'),
        ('after', 'After', 'Max delay\nin seconds:', 3.0, 'max_delay'),
        ('meets', 'Meets', '', '', ''),
        ('metby', 'Met by', '', '', ''),
        ('overlaps', 'Overlaps', 'Min overlap\n in seconds', 0.030, 'overlap_min'),
        ('overlappedby', 'Overlapped by', 'Min overlap\n in seconds', 0.030, 'overlap_min'),
        ('starts', 'Starts', '', '', ''),
        ('startedby', 'Started by', '', '', ''),
        ('finishes', 'Finishes', '', '', ''),
        ('finishedby', 'Finished by', '', '', ''),
        ('during', 'During', '', '', ''),
        ('contains', 'Contains', '', '', '')
    )

    Illustrations = (
        # equals
        ('X |-----|\nY |-----|',
         'Non efficient',
         'Non efficient',
         'X |\nY |'),
        # before
        ('X |-----|\nY' + ' ' * 15 + '|-----|',
         'X |-----|\nY' + ' ' * 15 + '|',
         'X |\nY   |-----|',
         'X |\nY   |'),
        # after
        ('X' + ' ' * 15 + '|-----|\nY |-----|',
         'X' + ' ' * 15 + '|\nY |-----|',
         'X   |-----|\nY |',
         'X   |\nY |'),
        # meets
        ('X |-----|\nY' + ' ' * 8 + '|-----|',
         'Non efficient',
         'Non efficient',
         'Non efficient'),
        # metby
        ('X' + ' ' * 8 + '|-----|\nY |-----|',
         'Non efficient',
         'Non efficient',
         'Non efficient'),
        # overlaps
        ('X |-----|\nY ' + ' ' * 5 + '|-----|',
         'Non efficient',
         'Non efficient',
         'Non efficient'),
        # overlappedby
        ('X' + ' ' * 5 + '|-----|\nY |-----|',
         'Non efficient',
         'Non efficient',
         'Non efficient'),
        # starts
        ('X |---|\nY |-----|',
         'Non efficient',
         'Non efficient',
         'Non efficient'),
        # startedby
        ('X |-----|\nY |---|',
         'Non efficient',
         'Non efficient',
         'Non efficient'),
        # finishes
        ('X |---|\nY    |------|',
         'Non efficient',
         'Non efficient',
         'Non efficient'),
        # finishedby
        ('X |------|\nY    |---|',
         'Non efficient',
         'Non efficient',
         'Non efficient'),
        # during
        ('X    |---|\nY |------|',
         'Non efficient',
         'X      |\nY |------|',
         'Non efficient'),
        # contains
        ('X |------|\nY    |---|',
         'X |-----|\nY     |',
         'Non efficient',
         'Non efficient'),
    )

    AllenTable = tuple(row + Illustrations[i] for i, row in enumerate(Relations))

    def __init__(self, parent):
        """Create a dialog to fix settings.

        :param parent: (wx.Window)
        :param tiers: dictionary with key=filename, value=list of selected tiers

        """
        super(sppasTiersRelationFilterDialog, self).__init__(
            parent=parent,
            title="Tiers Relation Filter",
            style=wx.CAPTION | wx.RESIZE_BORDER | wx.CLOSE_BOX | wx.MAXIMIZE_BOX | wx.STAY_ON_TOP,
            name="tierfilter_dialog")

        self.CreateHeader(MSG_HEADER_TIERSFILTER, "tier_ann_view")
        self._create_content()
        self.CreateActions([wx.ID_CANCEL, wx.ID_OK])

        self.LayoutComponents()
        self.GetSizer().Fit(self)
        self.CenterOnParent()
        self.FadeIn(deltaN=-8)

    # -----------------------------------------------------------------------
    # Public methods
    # -----------------------------------------------------------------------

    def get_filters(self):
        """Return a tuple ([list of functions], [list of options])."""
        w = self.FindWindow("listctrl")
        return w.get_selected_relations()

    # -----------------------------------------------------------------------

    def get_tiername(self):
        """Return the expected name of the filtered tier."""
        w = self.FindWindow("tiername_textctrl")
        return w.GetValue()

    # -----------------------------------------------------------------------

    def get_relation_tiername(self):
        """Return the tier Y."""
        w = self.FindWindow("y_tier_textctrl")
        return w.GetValue()

    # -----------------------------------------------------------------------

    def get_annot_format(self):
        """Return True if the label has to be replaced by the filter name."""
        w = self.FindWindow("annotformat_checkbutton")
        return w.GetValue()

    # -----------------------------------------------------------------------
    # Construct the GUI
    # -----------------------------------------------------------------------

    def _create_content(self):
        """Create the content of the message dialog."""
        b = sppasPanel.fix_size(6)
        panel = sppasPanel(self, name="content")

        # The list of relations and their options
        lst = AllensRelationsTable(panel, name="listctrl")

        # The name of the filtered tier
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        st = sppasStaticText(panel, label="Name of the filtered tier:")
        nt = sppasTextCtrl(panel, value="Filtered", name="tiername_textctrl")
        hbox.Add(st, 0, wx.ALIGN_CENTRE_VERTICAL | wx.ALL, b)
        hbox.Add(nt, 1, wx.EXPAND | wx.ALL, b)

        # The annot_format option (replace label by the name of the relation)
        an_box = CheckButton(panel, label=MSG_ANNOT_FORMAT)
        an_box.SetValue(False)
        an_box.SetName("annotformat_checkbutton")

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(lst, 1, wx.EXPAND | wx.ALL, b)
        sizer.Add(hbox, 0)
        sizer.Add(an_box, 0, wx.EXPAND | wx.ALL, b)

        panel.SetSizer(sizer)
        panel.SetAutoLayout(True)
        self.SetContent(panel)

# ---------------------------------------------------------------------------


class AllensRelationsTable(ulc.UltimateListCtrl):

    def __init__(self, parent, *args, **kwargs):
        agw_style = ulc.ULC_REPORT | ulc.ULC_VRULES | ulc.ULC_HRULES |\
                    ulc.ULC_HAS_VARIABLE_ROW_HEIGHT | ulc.ULC_NO_HEADER
        ulc.UltimateListCtrl.__init__(self, parent, agwStyle=agw_style, *args, **kwargs)
        self._optionCtrlList = []
        self.InitUI()
        try:
            self.SetFont(wx.GetApp().settings.mono_font)
        except:
            mono_font = wx.Font(12,  # point size
                                wx.FONTFAMILY_TELETYPE,  # family,
                                wx.FONTSTYLE_NORMAL,   # style,
                                wx.FONTWEIGHT_NORMAL,  # weight,
                                underline=False,
                                encoding=wx.FONTENCODING_SYSTEM)
            self.SetFont(mono_font)

    # -----------------------------------------------------------------------

    def SetFont(self, font):
        """Sets a new font size, but not the font itself."""
        s = font.GetPointSize()
        self.GetFont().SetPointSize(s)

    # -----------------------------------------------------------------------

    def InitUI(self):
        headers = ('Name',
                   'Option',
                   'X: Interval \nY: Interval',
                   'X: Interval \nY: Point',
                   'X: Point \nY: Interval',
                   'X: Point \nY: Point'
                   )
        # Create columns
        for i, col in enumerate(headers):
            self.InsertColumn(col=i, heading=col)

        p = sppasPanel()
        self.SetColumnWidth(col=0, width=p.fix_size(150))
        self.SetColumnWidth(col=1, width=p.fix_size(180))
        self.SetColumnWidth(col=2, width=p.fix_size(150))
        self.SetColumnWidth(col=3, width=p.fix_size(100))
        self.SetColumnWidth(col=4, width=p.fix_size(100))
        self.SetColumnWidth(col=5, width=p.fix_size(100))

        # Create first row, used as an header.
        index = self.InsertStringItem(0, headers[0])
        for i, col in enumerate(headers[1:], 1):
            self.SetStringItem(index, i, col)

        # Add rows for relations
        for i, row in enumerate(ALLEN_RELATIONS, 1):
            func, name, opt_label, opt_value, opt_name, desc1, desc2, desc3, desc4 = row

            opt_panel = wx.Panel(self)
            opt_sizer = wx.BoxSizer(wx.HORIZONTAL)

            if isinstance(opt_value, float):
                opt_ctrl = FS.FloatSpin(opt_panel,
                                        min_val=0.005,
                                        increment=0.010,
                                        value=opt_value,
                                        digits=3)
            elif isinstance(opt_value, int):
                opt_ctrl = wx.SpinCtrl(opt_panel, min=1, value=str(opt_value))
            else:
                opt_ctrl = wx.StaticText(opt_panel, label="")

            self._optionCtrlList.append(opt_ctrl)
            opt_text = wx.StaticText(opt_panel, label=opt_label)
            opt_sizer.Add(opt_text)
            opt_sizer.Add(opt_ctrl)
            opt_panel.SetSizer(opt_sizer)

            index = self.InsertStringItem(i, name, 1)
            self.SetItemWindow(index, 1, opt_panel, expand=True)
            self.SetStringItem(index, 2, desc1)
            self.SetStringItem(index, 3, desc2)
            self.SetStringItem(index, 4, desc3)
            self.SetStringItem(index, 5, desc4)

        item = self.GetItem(1)
        self._mainWin.CheckItem(item)
        self.SetMinSize(wx.Size(
            p.fix_size(780),
            p.fix_size(520)
        ))

    # -----------------------------------------------------------------------

    def get_selected_relations(self):
        """Return a tuple with a list of functions and a list of options."""
        fcts = list()
        opts = list()

        for i, option in enumerate(self._optionCtrlList, 1):
            if self.IsItemChecked(i, col=0):
                func_name = ALLEN_RELATIONS[i-1][0]
                fcts.append(func_name)

                try:
                    option_value = option.GetValue()
                    option_name = ALLEN_RELATIONS[i-1][4]
                    opts.append((option_name, option_value))
                except:
                    pass

        return fcts, opts


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
        btn_sgl = wx.Button(self,
                            pos=(10, 100),
                            size=(260, 70),
                            label="Single filter",
                            name="sgl_btn")
        btn_rel = wx.Button(self,
                            pos=(310, 100),
                            size=(260, 70),
                            label="Relation filter",
                            name="rel_btn")
        self.Bind(wx.EVT_BUTTON, self._process_event)

    # -----------------------------------------------------------------------

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

        elif event_name == "sgl_btn":
            dlg = sppasTiersSingleFilterDialog(self)
            response = dlg.ShowModal()
            if response in (wx.ID_OK, wx.ID_APPLY):
                filters = dlg.get_filters()
                wx.LogError("Filters {:s}:\n{:s}".format(
                    str(dlg.match_all),
                    "\n".join([str(f) for f in filters])
                ))
            dlg.Destroy()

        elif event_name == "rel_btn":
            dlg = sppasTiersRelationFilterDialog(self)
            response = dlg.ShowModal()
            if response in (wx.ID_OK, wx.ID_APPLY):
                filters = dlg.get_filters()
                wx.LogError("Filters {:s}:\n".format("\n".join([str(f) for f in filters])))
            dlg.Destroy()
