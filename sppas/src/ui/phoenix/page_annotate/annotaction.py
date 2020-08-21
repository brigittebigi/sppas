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
import logging
import os

from sppas.src.config import msg
from sppas.src.config import annots, paths
from sppas.src.utils import u

from ..windows.dialogs import Error
from ..windows import sppasStaticLine
from ..windows import sppasToolbar
from ..windows import sppasPanel
from ..windows import sppasScrolledPanel
from ..windows import sppasStaticText
from ..windows import BitmapTextButton, RadioButton
from ..windows import sppasComboBox  # todo: implement FindString() and Delete()

from .annotevent import PageChangeEvent
from .annotselect import LANG_NONE

# ---------------------------------------------------------------------------
# List of displayed messages:


def _(message):
    return u(msg(message, "ui"))


MSG_STEP_FORMAT = _("STEP 1: choose the output file format(s)")
MSG_STEP_LANG = _("STEP 2: fix the language(s)")
MSG_STEP_ANNCHOICE = _("STEP 3: select and configure annotations")
MSG_STEP_RUN = _("STEP 4: perform the annotations")
MSG_STEP_REPORT = _("STEP 5: read the procedure outcome report")
MSG_BTN_RUN = _("Let's go!")
MSG_BTN_REPORT = _("Show report")
MSG_TITLE_REPORTS = _("Reports:")
MSG_BTN_DEL_CHECK = _("Del checked")
MSG_BTN_DEL_ALL = _("Del all")

# ---------------------------------------------------------------------------


class sppasActionAnnotatePanel(sppasPanel):
    """Create a panel to configure then run automatic annotations.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2020  Brigitte Bigi

    1st page of the "page_annotate". Displays the steps to perform
    automatic annotations and the list of reports.

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
        self.UpdateUI()
        self.Layout()

    # -----------------------------------------------------------------------

    def SetBackgroundColour(self, colour):
        """Set the background of our panel to the given color."""
        wx.Panel.SetBackgroundColour(self, colour)
        hi_color = self.GetHighlightedBackgroundColour()

        for name in ("format", "lang", "annselect", "annot", "show_report"):
            w = self.FindWindow(name + "_panel")
            w.SetBackgroundColour(hi_color)

        self._reports.SetBackgroundColour(colour)

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
        report = self.__param.get_report_filename()
        if report is not None:
            self._reports.insert_report(os.path.basename(report))
        self.UpdateUI()

    # ------------------------------------------------------------------------
    # Private methods to construct the panel.
    # ------------------------------------------------------------------------

    def _create_content(self):
        """Create the main content."""
        reports = list()
        for f in os.listdir(paths.logs):
            if os.path.isfile(os.path.join(paths.logs, f)):
                if f.endswith('.txt') and "report" in f:
                    reports.append(f)

        sizer = wx.BoxSizer(wx.HORIZONTAL)
        action_panel = self._create_action_content()
        reports_panel = ReportsPanel(self, reports, name="reports_panel")

        sizer.Add(action_panel, 3, wx.EXPAND)
        sizer.Add(self.__create_vline(), 0, wx.EXPAND)
        sizer.Add(reports_panel, 1, wx.EXPAND)

        self.SetSizer(sizer)

    # ------------------------------------------------------------------------

    @property
    def _reports(self):
        return self.FindWindow("reports_panel")

    # ------------------------------------------------------------------------

    def __create_vline(self):
        """Create an horizontal line, used to separate the anz_panels."""
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
        """The output file formats (step 1). """
        border = sppasPanel.fix_size(10)
        p = sppasPanel(parent, style=wx.BORDER_NONE, name="format_panel")
        s = wx.BoxSizer(wx.HORIZONTAL)
        st = sppasStaticText(p, label=MSG_STEP_FORMAT)
        s.Add(st, 1, wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_LEFT | wx.ALL, border)

        for out_format in annots.outformat:
            all_formats = self.__param.get_outformat_extensions(out_format)
            if len(all_formats) == 0:
                continue
            default = self.__param.get_default_outformat_extension(out_format)
            box = sppasComboBox(p, -1, choices=all_formats, name="format_choice_"+out_format)
            box.SetSelection(box.GetItems().index(default))
            box.SetMinSize(wx.Size(sppasPanel.fix_size(80), -1))
            s.Add(box, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, border)

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
        btn_run = self.__create_select_annot_btn(p, MSG_BTN_RUN)
        btn_run.SetName("run_btn")
        btn_run.SetImage("wizard")

        s = wx.BoxSizer(wx.HORIZONTAL)
        border = sppasPanel.fix_size(10)
        s.Add(st, 1, wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_LEFT | wx.ALL, border)
        s.Add(btn_run, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, border)
        p.SetSizer(s)
        return p

    @property
    def btn_run(self):
        return self.FindWindow("run_btn")

    # ------------------------------------------------------------------------

    def __create_action_report(self, parent):
        """The button to show the report."""
        p = sppasPanel(parent, style=wx.BORDER_NONE, name="show_report_panel")
        st = sppasStaticText(p, label=MSG_STEP_REPORT)
        btn_por = self.__create_select_annot_btn(p, MSG_BTN_REPORT)
        btn_por.SetName("report_btn")
        btn_por.SetImage("report_clip")

        s = wx.BoxSizer(wx.HORIZONTAL)
        border = sppasPanel.fix_size(10)
        s.Add(st, 1, wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_LEFT | wx.ALL, border)
        s.Add(btn_por, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, border)
        p.SetSizer(s)
        return p

    @property
    def btn_por(self):
        return self.FindWindow("report_btn")

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
        self._reports.Bind(wx.EVT_RADIOBUTTON, self._process_radio_event)

        # Language choice changed
        self.FindWindow("lang_choice").Bind(wx.EVT_COMBOBOX, self._on_lang_changed)

        # Output format changed
        for out_format in annots.outformat:
            box = self.FindWindow("format_choice_"+out_format)
            if box is not None:
                box.Bind(wx.EVT_COMBOBOX, self._on_format_changed)

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

        if event_name == "report_delete_checked":
            self._reports.delete_checked()
            self.__param.set_report_filename(None)
            self.UpdateUI(update_log=True)

        elif event_name == "report_delete_unchecked":
            self._reports.delete_unchecked()

        elif event_name == "run_btn":
            self.notify("page_annot_log", fct_name="run")

        elif event_name == "report_btn":
            # Get the name of the checked report
            report = self._reports.get_checked_report()
            if report is not None:
                report = os.path.join(paths.logs, report)
            # Set it to the param
            self.__param.set_report_filename(report)
            # Ask parent to show the report
            self.notify("page_annot_log", fct_name="show")

        else:
            event.Skip()

    # -----------------------------------------------------------------------

    def _process_radio_event(self, event):
        """Process a click on a report.

        :param event: (wx.Event)

        """
        event_obj = event.GetEventObject()
        # The button was selected
        if event_obj.GetValue() is True:
            name = event_obj.GetLabel()
            self._reports.switch_to_report(name)
            self.__param.set_report_filename(os.path.join(paths.logs, name))
        else:
            # The button was de-selected
            self.__param.set_report_filename(None)

        self.UpdateUI(update_log=True)

    # -----------------------------------------------------------------------

    def _on_lang_changed(self, event):
        choice = event.GetEventObject()
        lang = choice.GetStringSelection()
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
        new_ext = choice.GetStringSelection()
        out_format = choice.GetName().replace("format_choice_", "")
        self.__param.set_output_extension(new_ext, out_format)

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
                logging.debug("Annotation activated: {}".format(a.get_key()))
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
        report = self._reports.get_checked_report()
        if report is not None:
            report = os.path.join(paths.logs, report)
        if update_log is True:
            if report is None or os.path.exists(report) is False:
                self.btn_por.Enable(False)
                self.btn_por.SetBorderColour(wx.Colour(228, 24, 24, 128))
            else:
                name = os.path.basename(report)
                self._reports.switch_to_report(name)
                self.btn_por.Enable(True)
                self.btn_por.SetBorderColour(ReportsPanel.HIGHLIGHT_COLOR)

# ----------------------------------------------------------------------------
# Panel to display the existing log reports
# ----------------------------------------------------------------------------


class ReportsPanel(sppasScrolledPanel):
    """Manager of the list of available reports in the software.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      contact@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2020 Brigitte Bigi

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

        self._create_content(reports)
        self.SetupScrolling(scroll_x=True, scroll_y=True)

        self.SetBackgroundColour(wx.GetApp().settings.bg_color)
        self.SetForegroundColour(wx.GetApp().settings.fg_color)
        self.SetFont(wx.GetApp().settings.text_font)

        self.Layout()

    # -----------------------------------------------------------------------

    def get_checked_report(self):
        """Return the name of the currently checked report or None."""
        for i, child in enumerate(self.GetChildren()):
            if isinstance(child, RadioButton):
                if child.GetValue() is True:
                    return child.GetLabel()

        return None

    # -----------------------------------------------------------------------

    def switch_to_report(self, name):
        """Check the button of the given report.

        :param name: (str)

        """
        for i, child in enumerate(self.GetChildren()):
            if isinstance(child, RadioButton):
                if child.GetLabel() == name:
                    child.SetValue(True)
                    self.__set_active_btn_style(child)
                else:
                    if child.GetValue() is True:
                        child.SetValue(False)
                        self.__set_normal_btn_style(child)

    # -----------------------------------------------------------------------

    def insert_report(self, name):
        """Add a button corresponding to the name of a report or select it.

        Add the button at the top of the list and check it, or only check it
        if it is already existing.

        :param name: (str)
        :returns: (bool) the button was inserted or not

        """
        # Do not insert the same report twice
        for i, child in enumerate(self.GetChildren()):
            if child.GetLabel() == name:
                self.switch_to_report(name)
                return False

        # Create a new button and insert at the top of the list
        btn = RadioButton(self, label=name, name="checkbox_"+name)
        btn.SetSpacing(self.get_font_height())
        btn.SetMinSize(wx.Size(-1, self.get_font_height()*2))
        self.switch_to_report(name)

        self.GetSizer().Insert(1, btn, 0, wx.EXPAND | wx.ALL, 2)
        return True

    # -----------------------------------------------------------------------

    def delete_report(self, name):
        """Delete the report of the given name.

        :param name: (str)

        """
        rm_child = None
        for i, child in enumerate(self.GetChildren()):
            if isinstance(child, RadioButton):
                if child.GetLabel() == name:
                    rm_child = child
                    break

        if rm_child is not None:
            try:
                self.__delete_report(name)
            except Exception as e:
                Error(str(e))
            else:
                self.GetSizer().Detach(rm_child)
                rm_child.Destroy()
                self.Layout()

    # -----------------------------------------------------------------------

    def delete_checked(self):
        rm_child = None
        for child in self.GetChildren():
            if isinstance(child, RadioButton):
                if child.GetValue() is True:
                    child.SetValue(True)
                    rm_child = child
                    break
        if rm_child is not None:
            try:
                self.__delete_report(rm_child.GetLabel())
            except Exception as e:
                Error(str(e))
            else:
                self.GetSizer().Detach(rm_child)
                rm_child.Destroy()
                self.Layout()

    # -----------------------------------------------------------------------

    def delete_unchecked(self):
        rm_child = list()
        for child in self.GetChildren():
            if isinstance(child, RadioButton):
                if child.GetValue() is False:
                    rm_child.append(child)

        for child in reversed(rm_child):
            try:
                self.__delete_report(child.GetLabel())
            except Exception as e:
                Error(str(e))
            else:
                self.GetSizer().Detach(child)
                child.Destroy()

        self.Layout()

    # -----------------------------------------------------------------------
    # Private methods to construct the panel.
    # -----------------------------------------------------------------------

    def __create_toolbar(self):
        tb = sppasToolbar(self, orient=wx.HORIZONTAL)
        tb.set_focus_color(wx.Colour(196, 196, 24, 128))

        tb.AddTitleText(MSG_TITLE_REPORTS, color=ReportsPanel.HIGHLIGHT_COLOR)
        del_checked = tb.AddButton("report_delete_checked", text=MSG_BTN_DEL_CHECK)
        self.__set_normal_btn_style(del_checked)

        del_unchecked = tb.AddButton("report_delete_unchecked", text=MSG_BTN_DEL_ALL)
        self.__set_normal_btn_style(del_unchecked)

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

    # -----------------------------------------------------------------------

    @staticmethod
    def __delete_report(name):
        if os.path.exists(name) is False:
            fullname = os.path.join(paths.logs, name)
        else:
            fullname = name
        os.remove(fullname)

