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

    src.ui.phoenix.page_analyze.filters.relation.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    A dialog to fix a list of filters and any parameter needed.
    The dialog only allows to fix and format properly the filters, it doesn't
    apply them on any data.

"""

import wx
import wx.dataview
try:
    from agw import floatspin as FS
    import agw.ultimatelistctrl as ulc
except ImportError:
    import wx.lib.agw.floatspin as FS
    import wx.lib.agw.ultimatelistctrl as ulc

from sppas.src.config import msg
from sppas.src.utils import u

from sppas.src.ui.phoenix.windows import sppasDialog
from sppas.src.ui.phoenix.windows import sppasPanel
from sppas.src.ui.phoenix.windows import sppasToolbar
from sppas.src.ui.phoenix.windows import BitmapTextButton
from sppas.src.ui.phoenix.windows import CheckButton
from sppas.src.ui.phoenix.windows import sppasTextCtrl, sppasStaticText
from sppas.src.ui.phoenix.windows.listctrl import sppasListCtrl

from .tagfilter import sppasTagFilterDialog
from .locfilter import sppasLocFilterDialog
from .durfilter import sppasDurFilterDialog

# --------------------------------------------------------------------------


def _(message):
    return u(msg(message, "ui"))


MSG_HEADER_TIERSFILTER = _("Filter annotations of tiers")
MSG_ANNOT_FORMAT = _("Replace the tag by the name of the filter")

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
        self.FadeIn()

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
        b = sppasPanel.fix_size(4)
        panel = sppasPanel(self, name="content")
        tb = self.__create_toolbar(panel)
        lst = self.__create_list_filters(panel)

        hbox = wx.BoxSizer(wx.HORIZONTAL)
        st = sppasStaticText(panel, label="Name of the filtered tier:")
        nt = sppasTextCtrl(panel, value="Filtered", name="tiername_textctrl")
        hbox.Add(st, 1, wx.EXPAND | wx.ALL, b)
        hbox.Add(nt, 2, wx.EXPAND | wx.ALL, b)

        an_box = CheckButton(panel, label=MSG_ANNOT_FORMAT)
        an_box.SetMinSize(wx.Size(-1, panel.get_font_height()*2))
        an_box.SetFocusWidth(0)
        an_box.SetValue(False)
        an_box.SetName("annotformat_checkbutton")

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(tb, 0, wx.EXPAND, 0)
        sizer.Add(lst, 1, wx.EXPAND | wx.ALL, b)
        sizer.Add(hbox, 0, wx.EXPAND)
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
        style = wx.BORDER_SIMPLE | wx.LC_REPORT | wx.LC_SINGLE_SEL
        lst = sppasListCtrl(parent, style=style, name="filters_listctrl")
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
        # btn.SetBitmapColour(self.GetForegroundColour())
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


class TestPanel(sppasPanel):

    def __init__(self, parent, pos=wx.DefaultPosition, size=wx.DefaultSize):
        super(TestPanel, self).__init__(parent, pos=pos, size=size,
                                        name="Single Filters")

        btn = wx.Button(self, label="Single filter")
        btn.SetMinSize(wx.Size(150, 40))
        btn.SetPosition(wx.Point(10, 10))
        self.Bind(wx.EVT_BUTTON, self._process_event)

    # -----------------------------------------------------------------------

    def _process_event(self, event):
        """Process any kind of events.

        :param event: (wx.Event)

        """
        dlg = sppasTiersSingleFilterDialog(self)
        response = dlg.ShowModal()
        if response in (wx.ID_OK, wx.ID_APPLY):
            filters = dlg.get_filters()
            wx.LogError("Filters {:s}:\n{:s}".format(
                str(dlg.match_all),
                "\n".join([str(f) for f in filters])
            ))
        dlg.Destroy()
