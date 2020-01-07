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

import wx
import wx.dataview

try:
    from agw import floatspin as FS
except ImportError:
    import wx.lib.agw.floatspin as FS

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
        tb.AddTextButton("filter_tag", "+ Tag")
        tb.AddTextButton("filter_loc", "+ Loc")
        tb.AddTextButton("filter_dur", "+ Dur")
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

        if event_name == "filter_tag":
            self.__append_filter("tag")

        elif event_name == "filter_loc":
            self.__append_filter("loc")

        elif event_name == "filter_dur":
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

    TODO: a notebook witn "String", "Number", "Boolean" pages.
    
    """

    choices = (
               ("exact", "exact"),
               ("contains", "contains"),
               ("starts with", "startswith"),
               ("ends with", "endswith"),
               ("match (regexp)", "regexp"),

               ("not exact", "exact"),
               ("not contains", "contains"),
               ("not starts with", "startswith"),
               ("not ends with", "endswith"),
               ("not match", "regexp"),
              )

    def __init__(self, parent, show_case_sensitive=True):
        """Create a string filter dialog.

        :param parent: (wx.Window)

        """
        super(sppasTagFilterDialog, self).__init__(
            parent=parent,
            title='{:s} filter'.format(sg.__name__),
            style=wx.DEFAULT_FRAME_STYLE)

        self._create_content(show_case_sensitive)
        self.CreateActions([wx.ID_CANCEL, wx.ID_OK])

        self.SetSize(wx.Size(380, 320))
        self.LayoutComponents()
        self.CenterOnParent()

    # -----------------------------------------------------------------------

    def get_data(self):
        """Return the data defined by the user.

        Returns: (tuple) with:

               - function (str): one of the methods in Compare
               - values (list): patterns to find separated by commas

        """
        idx = self.radiobox.GetSelection()
        label = self.radiobox.GetStringSelection()
        given_fct = self.choices[idx][1]

        # Fill the resulting dict
        prepend_fct = ""

        if given_fct != "regexp":
            # prepend "not_" if reverse
            if "not" in label:
                prepend_fct += "not_"
            # prepend "i" if case-insensitive
            if self.checkbox.GetValue() is False:
                prepend_fct += "i"

        return prepend_fct+given_fct, self.text.GetValue()

    # -----------------------------------------------------------------------
    # Methods to construct the GUI
    # -----------------------------------------------------------------------

    def _create_content(self, show_case_sensitive):
        """Create the content of the message dialog."""
        panel = sppasPanel(self, name="content")

        label = sppasStaticText(panel, label="Search for pattern(s): ")
        self.text = sppasTextCtrl(panel, value="")

        choices = [row[0] for row in self.choices]
        self.radiobox = sppasRadioBoxPanel(
            panel,
            choices=choices,
            majorDimension=2,
            style=wx.RA_SPECIFY_COLS)
        self.radiobox.SetSelection(1)
        self.checkbox = CheckButton(panel, label="Case sensitive")
        self.checkbox.SetValue(False)
        if show_case_sensitive is False:
            self.checkbox.Hide()

        # Layout
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(label, 0, flag=wx.EXPAND | wx.ALL, border=4)
        sizer.Add(self.text, 0, flag=wx.EXPAND | wx.ALL, border=4)
        sizer.Add(self.radiobox, 1, flag=wx.EXPAND | wx.ALL, border=4)
        sizer.Add(self.checkbox, 0, flag=wx.EXPAND | wx.ALL, border=4)

        panel.SetSizer(sizer)
        panel.SetMinSize(wx.Size(240, 160))
        panel.SetAutoLayout(True)
        self.SetContent(panel)

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
        (" is starting at...", "rangefrom"),
        (" is ending at...", "rangeto")
    )

    def __init__(self, parent):
        """Create a duration filter dialog.

        :param parent: (wx.Window)

        """
        super(sppasLocFilterDialog, self).__init__(
            parent=parent,
            title='{:s} filter'.format(sg.__name__),
            style=wx.DEFAULT_FRAME_STYLE)

        self._create_content()
        self.CreateActions([wx.ID_CANCEL, wx.ID_OK])

        self.SetSize(wx.Size(380, 320))
        self.LayoutComponents()
        self.CenterOnParent()

    # -----------------------------------------------------------------------

    def get_data(self):
        """Return the data defined by the user.

        :returns: (tuple) with
               type (str): loc
               function (str): "rangefrom" or "rangeto"
               values (list): time value (represented by a 'str')

        """
        idx = self.radiobox.GetSelection()
        given_fct = sppasLocFilterDialog.choices[idx][1]
        value = self.ctrl.GetValue()
        return "loc", given_fct, [value]

    # -----------------------------------------------------------------------
    # Method to construct the GUI
    # -----------------------------------------------------------------------

    def _create_content(self):
        """Create the content of the message dialog."""
        panel = sppasPanel(self, name="content")

        top_label = sppasStaticText(panel, label="The time ")
        bottom_label = sppasStaticText(panel, label="... this value in seconds: ")

        choices = [row[0] for row in sppasLocFilterDialog.choices]
        self.radiobox = sppasRadioBoxPanel(
            panel,
            choices=choices,
            majorDimension=1,
            style=wx.RA_SPECIFY_COLS)
        self.radiobox.SetSelection(1)

        self.ctrl = FS.FloatSpin(self, min_val=0.0,
                                 increment=0.001,
                                 value=0,
                                 digits=3)

        # Layout
        b = sppasPanel.fix_size(4)

        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.Add(bottom_label, flag=wx.EXPAND | wx.ALL, border=b)
        hbox.Add(self.ctrl, flag=wx.EXPAND | wx.ALL, border=b)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(top_label, flag=wx.EXPAND | wx.ALL, border=b)
        sizer.Add(self.radiobox, 1, flag=wx.EXPAND | wx.ALL, border=0)
        sizer.Add(hbox, 0, flag=wx.EXPAND | wx.ALL, border=0)

        panel.SetSizer(sizer)
        panel.SetMinSize(wx.Size(240, 160))
        panel.SetAutoLayout(True)
        self.SetContent(panel)


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
        (" is equal to...", "eq"),
        (" is not equal to...", "ne"),
        (" is greater than...", "gt"),
        (" is less than...", "lt"),
        (" is greater or equal to...", "ge"),
        (" is lesser or equal to...", "le")
    )

    def __init__(self, parent):
        """Create a duration filter dialog.

        :param parent: (wx.Window)

        """
        super(sppasDurFilterDialog, self).__init__(
            parent=parent,
            title='{:s} filter'.format(sg.__name__),
            style=wx.DEFAULT_FRAME_STYLE)

        self._create_content()
        self.CreateActions([wx.ID_CANCEL, wx.ID_OK])

        self.SetSize(wx.Size(380, 320))
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

        top_label = sppasStaticText(panel, label="The duration ")
        bottom_label = sppasStaticText(panel, label="... this value in seconds: ")

        choices = [row[0] for row in sppasDurFilterDialog.choices]
        self.radiobox = sppasRadioBoxPanel(
            panel,
            choices=choices,
            majorDimension=1,
            style=wx.RA_SPECIFY_COLS)
        self.radiobox.SetSelection(1)

        self.ctrl = FS.FloatSpin(panel,
                                 min_val=0.0,
                                 increment=0.01,
                                 value=0,
                                 digits=3)

        # Layout
        b = sppasPanel.fix_size(4)

        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.Add(bottom_label, flag=wx.EXPAND | wx.ALL, border=b)
        hbox.Add(self.ctrl, flag=wx.EXPAND | wx.ALL, border=b)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(top_label, 0, flag=wx.EXPAND | wx.ALL, border=b)
        sizer.Add(self.radiobox, 1, flag=wx.EXPAND | wx.ALL, border=0)
        sizer.Add(hbox, 0, flag=wx.EXPAND | wx.ALL, border=0)

        panel.SetSizer(sizer)
        panel.SetMinSize(wx.Size(240, 160))
        panel.SetAutoLayout(True)
        self.SetContent(panel)


# ----------------------------------------------------------------------------
# Panel tested by test_glob.py
# ----------------------------------------------------------------------------


class TestPanel(sppasPanel):

    def __init__(self, parent):
        super(TestPanel, self).__init__(parent, name="TestPanel-tiersfilter")

        btn = wx.Button(self,
                        pos=(200, 10),
                        size=(384, 128),
                        label="Tag filter",
                        name="tag_btn")
        self.Bind(wx.EVT_BUTTON, self._process_event)

    def _process_event(self, event):
        """Process any kind of events.

        :param event: (wx.Event)

        """
        event_obj = event.GetEventObject()
        event_name = event_obj.GetName()

        if event_name == "tag_btn":
            dlg = sppasTagFilterDialog()
            response = dlg.ShowModal()
            if response == wx.ID_OK:
                f = dlg.get_data()
                if len(f[1].strip()) > 0:
                    wx.LogMessage("function tag; filter {:s}; value {!s:s}".format(f[0], f[1].strip()))
                else:
                    wx.LogError("Empty input pattern.")
            dlg.Destroy()

