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

    ui.phoenix.page_annotate.annotaction.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""

import wx
import os

from sppas import msg, u
from sppas import annots, paths

from ..windows import sppasStaticLine
from ..windows import sppasToolbar
from ..windows import sppasPanel
from ..windows import sppasScrolledPanel
from ..windows import sppasStaticText
from ..windows import BitmapTextButton, CheckButton, RadioButton

from .annotevent import PageChangeEvent
from .annotselect import LANG_NONE


# ---------------------------------------------------------------------------
# List of displayed messages:


def _(message):
    return u(msg(message, "ui"))


MSG_STEP_FORMAT = _("STEP 1: choose an output file format")
MSG_STEP_LANG = _("STEP 2: fix the language(s)")
MSG_STEP_ANNCHOICE = _("STEP 3: select annotations")
MSG_STEP_RUN = _("STEP 4: perform the annotations")
MSG_STEP_REPORT = _("STEP 5: read the procedure outcome report")
MSG_BTN_RUN = _("Let's go!")
MSG_BTN_REPORT = _("Show report")

# ---------------------------------------------------------------------------


class sppasActionAnnotatePanel(sppasPanel):
    """Create a panel to configure then run automatic annotations.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2019  Brigitte Bigi

    TODO: Use a sppasSplitterWindow instead of a sppasPanel

    """

    def __init__(self, parent, param):
        super(sppasActionAnnotatePanel, self).__init__(
            parent=parent,
            name="page_annot_actions",
            style=wx.BORDER_NONE
        )
        self.__param = param

        self._create_content()
        self._setup_events()
        self.Layout()

    # -----------------------------------------------------------------------

    def SetBackgroundColour(self, colour):
        """Set the background of our panel to the given color."""
        wx.Panel.SetBackgroundColour(self, colour)
        hi_color = self.GetHighlightedBackgroundColour()

        for name in ("format", "lang", "annselect", "annot", "report"):
            w = self.FindWindow(name + "_panel")
            w.SetBackgroundColour(hi_color)

    # -----------------------------------------------------------------------

    def GetHighlightedBackgroundColour(self):
        """Return a color slightly different of the parent background one."""
        color = self.GetParent().GetBackgroundColour()
        r, g, b, a = color.Red(), color.Green(), color.Blue(), color.Alpha()
        return wx.Colour(r, g, b, a).ChangeLightness(90)

    # ------------------------------------------------------------------------

    def get_param(self):
        return self.__param

    def set_param(self, param):
        self.__param = param
        self.UpdateUI()

    # ------------------------------------------------------------------------
    # Private methods to construct the panel.
    # ------------------------------------------------------------------------

    def _create_content(self):
        """Create the main content."""
        reports = list()
        for f in os.listdir(paths.logs):
            if os.path.isfile(os.path.join(paths.logs, f)) and f.endswith('.txt'):
                reports.append(f)

        sizer = wx.BoxSizer(wx.HORIZONTAL)
        action_sizer = self._create_action_content()
        report_panel = ReportsPanel(self, reports, name="panel_reports")

        sizer.Add(action_sizer, 3, wx.EXPAND)
        sizer.Add(self.__create_vline(), 0, wx.EXPAND)
        sizer.Add(report_panel, 1, wx.EXPAND)
        self.SetSizer(sizer)

    # ------------------------------------------------------------------------

    def __create_vline(self):
        """Create an horizontal line, used to separate the panels."""
        line = sppasStaticLine(self, orient=wx.LI_VERTICAL)
        line.SetMinSize(wx.Size(-1, 20))
        line.SetPenStyle(wx.PENSTYLE_SOLID)
        line.SetDepth(1)
        return line

    # ------------------------------------------------------------------------

    def _create_action_content(self):
        """Create the left content with actions."""
        panel = sppasScrolledPanel(self)

        # Create all the objects
        pnl_fmt = self.__create_action_format(panel)
        pnl_lang = self.__create_action_lang(panel)
        pnl_select = self.__create_action_annselect(panel)
        pnl_run = self.__create_action_annot(panel)
        pnl_report = self.__create_action_report(panel)

        # Organize all the objects
        border = sppasPanel.fix_size(12)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(pnl_fmt, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, border)
        sizer.Add(pnl_lang, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, border)
        sizer.Add(pnl_select, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, border)
        sizer.Add(pnl_run, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, border)
        sizer.Add(pnl_report, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP | wx.BOTTOM, border)
        panel.SetSizerAndFit(sizer)

        panel.SetupScrolling(scroll_x=False, scroll_y=True)
        return panel

    # ------------------------------------------------------------------------

    def __create_action_format(self, parent):
        """The output file format (step 1)."""
        p = sppasPanel(parent, style=wx.BORDER_NONE, name="format_panel")

        st = sppasStaticText(p, label=MSG_STEP_FORMAT)
        all_formats = ['.xra', '.TextGrid', '.eaf', '.antx', '.mrk', '.csv']
        default = self.__param.get_output_format()
        wx.LogMessage("Default output format is {:s}".format(default))
        choice = wx.ComboBox(p, -1, choices=all_formats, name="format_choice")
        choice.SetSelection(choice.GetItems().index(default))
        choice.SetMinSize(wx.Size(sppasPanel.fix_size(80), -1))

        s = wx.BoxSizer(wx.HORIZONTAL)
        border = sppasPanel.fix_size(10)
        s.Add(st, 1, wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_LEFT | wx.ALL, border)
        s.Add(choice, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, border)
        p.SetSizer(s)
        return p

    # ------------------------------------------------------------------------

    def __create_action_lang(self, parent):
        """The language (step 2)."""
        p = sppasPanel(parent, style=wx.BORDER_NONE, name="lang_panel")

        st = sppasStaticText(p, label=MSG_STEP_LANG)
        all_langs = list()
        for i in range(self.__param.get_step_numbers()):
            a = self.__param.get_step(i)
            all_langs.extend(a.get_langlist())

        lang_list = list(set(all_langs))
        lang_list.append(LANG_NONE)
        choice = wx.ComboBox(p, -1, choices=sorted(lang_list), name="lang_choice")
        choice.SetSelection(choice.GetItems().index(LANG_NONE))
        choice.SetMinSize(wx.Size(sppasPanel.fix_size(80), -1))

        s = wx.BoxSizer(wx.HORIZONTAL)
        border = sppasPanel.fix_size(10)
        s.Add(st, 1, wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_LEFT | wx.ALL, border)
        s.Add(choice, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, border)
        p.SetSizer(s)
        return p

    # ------------------------------------------------------------------------

    def __create_action_annselect(self, parent):
        """The annotations to select (step 3)."""
        p = sppasPanel(parent, style=wx.BORDER_NONE, name="annselect_panel")
        st = sppasStaticText(p, label=MSG_STEP_ANNCHOICE)

        pbts = sppasPanel(p)
        sbts = wx.BoxSizer(wx.VERTICAL)
        border = sppasPanel.fix_size(3)
        for ann_type in annots.types:
            btn = self.__create_select_annot_btn(pbts, "{:s} annotations".format(ann_type))
            btn.SetName("btn_annot_" + ann_type)
            btn.SetImage("on-off-off")
            sbts.Add(btn, 1, wx.EXPAND | wx.LEFT | wx.TOP | wx.BOTTOM, border)
        pbts.SetSizer(sbts)

        s = wx.BoxSizer(wx.HORIZONTAL)
        border = sppasPanel.fix_size(10)
        s.Add(st, 1, wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_LEFT | wx.ALL, border)
        s.Add(pbts, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, border)
        p.SetSizer(s)
        return p

    # ------------------------------------------------------------------------

    def __create_action_annot(self, parent):
        """The button to run annotations (step 4)."""
        p = sppasPanel(parent, style=wx.BORDER_NONE, name="annot_panel")
        st = sppasStaticText(p, label=MSG_STEP_RUN)
        self.btn_run = self.__create_select_annot_btn(p, MSG_BTN_RUN)
        self.btn_run.SetName("wizard")
        self.btn_run.SetImage("wizard")
        self.btn_run.Enable(False)
        self.btn_run.BorderColour = wx.Colour(228, 24, 24, 128)

        s = wx.BoxSizer(wx.HORIZONTAL)
        border = sppasPanel.fix_size(10)
        s.Add(st, 1, wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_LEFT | wx.ALL, border)
        s.Add(self.btn_run, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, border)
        p.SetSizer(s)
        return p

    # ------------------------------------------------------------------------

    def __create_action_report(self, parent):
        """The button to show the report."""
        p = sppasPanel(parent, style=wx.BORDER_NONE, name="report_panel")
        st = sppasStaticText(p, label=MSG_STEP_REPORT)
        self.btn_por = self.__create_select_annot_btn(p, MSG_BTN_REPORT)
        self.btn_por.SetName("save_as")
        self.btn_por.SetImage("save_as")
        self.btn_por.Enable(False)
        self.btn_por.BorderColour = wx.Colour(228, 24, 24, 128)

        s = wx.BoxSizer(wx.HORIZONTAL)
        border = sppasPanel.fix_size(10)
        s.Add(st, 1, wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_LEFT | wx.ALL, border)
        s.Add(self.btn_por, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, border)
        p.SetSizer(s)
        return p

    # ------------------------------------------------------------------------

    def __create_select_annot_btn(self, parent, label):

        w = sppasPanel.fix_size(196)
        h = sppasPanel.fix_size(42)

        btn = BitmapTextButton(parent, label=label)
        btn.SetBorderWidth(2)
        btn.SetLabelPosition(wx.RIGHT)
        btn.SetSpacing(12)
        btn.SetBorderColour(wx.Colour(128, 128, 128, 128))
        btn.SetBitmapColour(self.GetForegroundColour())
        btn.SetMinSize(wx.Size(w, h))
        return btn

    # -----------------------------------------------------------------------
    # Events management
    # -----------------------------------------------------------------------

    def notify(self, destination, fct_name=""):
        """Send the EVT_PAGE_CHANGE to the parent."""
        if self.GetParent() is not None:
            evt = PageChangeEvent(from_page=self.GetName(),
                                  to_page=destination,
                                  fct=fct_name)
            evt.SetEventObject(self)
            wx.PostEvent(self.GetParent(), evt)

    # -----------------------------------------------------------------------

    def _setup_events(self):
        """Associate a handler function with the events.

        It means that when an event occurs then the process handler function
        will be called.

        """
        # Bind all events from our buttons
        self.Bind(wx.EVT_BUTTON, self._process_event)

        # Language choice changed
        self.FindWindow("lang_choice").Bind(wx.EVT_COMBOBOX, self._on_lang_changed)
        self.FindWindow("format_choice").Bind(wx.EVT_COMBOBOX, self._on_format_changed)

    # -----------------------------------------------------------------------

    def _process_event(self, event):
        """Process any kind of events.

        :param event: (wx.Event)

        """
        event_obj = event.GetEventObject()
        event_name = event_obj.GetName()

        for ann_type in annots.types:
            if event_name == "btn_annot_" + ann_type:
                self.notify("page_annot_{:s}".format(ann_type))
                event.Skip()
                return

        if event_name == "wizard":
            self.notify("page_annot_log", fct_name="run")

        elif event_name == "save_as":
            # we use the button save as but it only shows the text
            self.notify("page_annot_log")

        else:
            event.Skip()

    # -----------------------------------------------------------------------

    def _on_lang_changed(self, event):
        choice = event.GetEventObject()
        lang = choice.GetValue()
        if lang == LANG_NONE:
            lang = None

        for i in range(self.__param.get_step_numbers()):
            a = self.__param.get_step(i)
            if len(a.get_langlist()) > 0:
                if lang in a.get_langlist():
                    a.set_lang(lang)
                else:
                    a.set_lang(None)

        self.UpdateUI(update_lang=False)

    # -----------------------------------------------------------------------

    def _on_format_changed(self, event):
        choice = event.GetEventObject()
        new_format = choice.GetValue()
        self.__param.set_output_format(new_format)
        wx.LogDebug("New output format is {:s}".format(new_format))

    # -----------------------------------------------------------------------

    def UpdateUI(self,
                 update_lang=True,
                 update_annot=True,
                 update_run=True,
                 update_log=True):
        """Update the UI depending on the parameters."""

        # search for enabled annotations and fixed languages
        ann_enabled = [False] * len(annots.types)
        lang = list()

        for i in range(self.__param.get_step_numbers()):
            a = self.__param.get_step(i)
            if a.get_activate() is True:
                for x, ann_type in enumerate(annots.types):
                    if ann_type in a.get_types():
                        ann_enabled[x] = True
                # at least one annotation can be performed
                # (no need of the lang or lang is defined)
                if a.get_lang() is None or \
                        (len(a.get_langlist()) > 0 and len(a.get_lang()) > 0):
                    lang.append(a.get_lang())

        # update the button to set the language
        if update_lang is True:
            langs = list(set(lang))
            if None in langs:
                langs.remove(None)
            choice = self.FindWindow("lang_choice")
            if len(langs) <= 1:
                mix_item = choice.FindString("MIX")
                if mix_item != wx.NOT_FOUND:
                    choice.Delete(mix_item)
                if len(langs) == 0:
                    choice.SetSelection(choice.GetItems().index(LANG_NONE))
                else:
                    choice.SetSelection(choice.GetItems().index(langs[0]))
            else:
                # several languages
                i = choice.Append("MIX")
                choice.SetSelection(i)

        # update buttons to fix properties of annotations
        if update_annot is True:
            for i, ann_type in enumerate(annots.types):
                btn = self.FindWindow("btn_annot_" + ann_type)
                if ann_enabled[i] is True:
                    btn.SetImage("on-off-on")
                else:
                    btn.SetImage("on-off-off")

        # update the button to perform annotations
        # at least one annotation is enabled and lang is fixed.
        if update_run is True:
            if len(lang) == 0:
                self.btn_run.Enable(False)
                self.btn_run.BorderColour = wx.Colour(228, 24, 24, 128)
            else:
                self.btn_run.Enable(True)
                self.btn_run.BorderColour = wx.Colour(24, 228, 24, 128)

        # update the button to read log report
        report = self.__param.get_report_filename()
        if update_log is True:
            if report is None or os.path.exists(report) is False:
                self.btn_por.Enable(False)
                self.btn_por.BorderColour = wx.Colour(228, 24, 24, 128)
            else:
                name = os.path.basename(report)
                self.FindWindow("panel_reports").insert_report(name)
                self.FindWindow("panel_reports").switch_to_report(name)
                self.btn_por.Enable(True)
                self.btn_por.BorderColour = ReportsPanel.HIGHLIGHT_COLOR

# ----------------------------------------------------------------------------
# Panel to display the existing log reports
# ----------------------------------------------------------------------------


class ReportsPanel(sppasScrolledPanel):
    """Manager of the list of available reports in the software.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      contact@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2019  Brigitte Bigi

    todo: The parent has to handle EVT_REPORT_CHANGED event to be informed that a report changed.

    """
    
    HIGHLIGHT_COLOR = wx.Colour(196, 196, 24, 128)
    
    # -----------------------------------------------------------------------

    def __init__(self, parent, reports, name=wx.PanelNameStr):
        super(ReportsPanel, self).__init__(
            parent,
            id=wx.ID_ANY,
            pos=wx.DefaultPosition,
            size=wx.DefaultSize,
            style=wx.BORDER_NONE | wx.NO_FULL_REPAINT_ON_RESIZE,
            name=name)

        self.SetBackgroundColour(wx.GetApp().settings.bg_color)
        self.SetForegroundColour(wx.GetApp().settings.fg_color)
        self.SetFont(wx.GetApp().settings.text_font)

        self._create_content(reports)
        self.SetupScrolling(scroll_x=True, scroll_y=True)
        self.Layout()

    # -----------------------------------------------------------------------

    def switch_to_report(self, name):
        """Check the button of the given report.

        :param name: (str)

        """
        for i, child in enumerate(self.GetChildren()):
            if isinstance(child, CheckButton):
                if child.GetLabel() == name:
                    child.SetValue(True)
                    self.__set_active_btn_style(child)
                else:
                    if child.GetValue() is True:
                        child.SetValue(False)
                        self.__set_normal_btn_style(child)

    # -----------------------------------------------------------------------

    def insert_report(self, name):
        """Add a button corresponding to the name of a report.

        Add the button at the top of the list.

        :param name: (str)
        :returns: (bool) the button was inserted or not

        """
        # Do not insert the same report twice
        for i, child in enumerate(self.GetChildren()):
            if child.GetLabel() == name:
                return False

        # Create a new button and insert at the top of the list
        btn = RadioButton(self, label=name, name="checkbox_"+name)
        btn.SetSpacing(self.get_font_height())
        btn.SetMinSize(wx.Size(-1, self.get_font_height()*2))
        self.__set_normal_btn_style(btn)
        btn.SetValue(False)
        btn.Enable(False)   # ================================

        self.GetSizer().Insert(1, btn, 0, wx.EXPAND | wx.ALL, 2)
        return True

    # -----------------------------------------------------------------------
    # Private methods to construct the panel.
    # -----------------------------------------------------------------------

    def __create_toolbar(self):
        tb = sppasToolbar(self, orient=wx.VERTICAL)
        tb.set_focus_color(wx.Colour(196, 196, 24, 128))

        tb.AddTitleText("Reports: ", color=ReportsPanel.HIGHLIGHT_COLOR)
        return tb

    # -----------------------------------------------------------------------

    def _create_content(self, reports):
        """Create the main content."""
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.__create_toolbar(), 0, wx.EXPAND, 0)
        self.SetSizer(sizer)

        for r in reports:
            self.insert_report(r)
        self.SetMinSize(wx.Size(sppasPanel.fix_size(196),
                                sppasPanel.fix_size(24)*len(self.GetChildren())))

    # -----------------------------------------------------------------------

    def __set_normal_btn_style(self, button):
        """Set a normal style to a button."""
        button.SetBorderWidth(0)
        button.SetBorderColour(self.GetForegroundColour())
        button.SetBorderStyle(wx.PENSTYLE_SOLID)
        button.SetFocusColour(wx.Colour(128, 128, 128, 128))

    # -----------------------------------------------------------------------

    def __set_active_btn_style(self, button):
        """Set a highlight style to the button."""
        button.SetBorderWidth(1)
        button.SetBorderColour(ReportsPanel.HIGHLIGHT_COLOR)
        button.SetBorderStyle(wx.PENSTYLE_SOLID)
        button.SetFocusColour(self.GetForegroundColour())

    # -----------------------------------------------------------------------
    # Private methods
    # -----------------------------------------------------------------------

    def __btn_set_state(self, btn, state):
        if state is True:
            self.__set_active_btn_style(btn)
        else:
            self.__set_normal_btn_style(btn)
        btn.SetValue(state)
        btn.Refresh()
        wx.LogDebug('Report {:s} is checked: {:s}'
                      ''.format(btn.GetLabel(), str(state)))

