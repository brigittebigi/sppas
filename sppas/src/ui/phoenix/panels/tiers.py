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

    src.ui.phoenix.panels.tiers.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""

import os
import wx
import json
import xml.etree.cElementTree as ET

from sppas.src.config import msg
from sppas.src.config import paths
from sppas.src.utils import u
from sppas.src.anndata import sppasTier
from sppas.src.anndata import sppasRW
from sppas.src.anndata.aio import sppasXRA
from sppas.src.anndata.aio.xra import sppasJRA

from ..windows import sppasToolbar
from ..windows import sppasPanel
from ..windows import sppasTextCtrl
from ..windows import sppasSplitterWindow
from ..windows import LineListCtrl
from ..windows.book import sppasNotebook

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------


DARK_GRAY = wx.Colour(35, 35, 35)
LIGHT_GRAY = wx.Colour(245, 245, 240)
LIGHT_BLUE = wx.Colour(230, 230, 250)
LIGHT_RED = wx.Colour(250, 230, 230)

UNLABELLED_FG_COLOUR = wx.Colour(190, 45, 45)
SILENCE_FG_COLOUR = wx.Colour(45, 45, 190)
SILENCE_BG_COLOUR = wx.Colour(230, 230, 250)
LAUGH_FG_COLOUR = wx.Colour(210, 150, 50)
LAUGH_BG_COLOUR = wx.Colour(250, 230, 230)
NOISE_FG_COLOUR = wx.Colour(45, 190, 45)
NOISE_BG_COLOUR = wx.Colour(230, 250, 230)

# --------------------------------------------------------------------------


def _(message):
    return u(msg(message, "ui"))


MSG_HEADER_TIERSVIEW = _("View annotations of tiers")
MSG_NO_TIER = _("No tier to view.")
MSG_BEGIN = _("Begin")
MSG_END = _("End")
MSG_LABELS = _("Serialized list of labels with alternative tags")
MSG_POINT = _("Midpoint")
MSG_RADIUS = _("Radius")
MSG_NB = _("Nb")
MSG_TYPE = _("Type")

# --------------------------------------------------------------------------


class sppasTierListCtrl(LineListCtrl):
    """List-view of a tier.

    """

    tag_types = {
        "str": "String",
        "int": "Integer",
        "float": "Float",
        "bool": "Boolean"
    }

    def __init__(self, parent, tier):
        super(sppasTierListCtrl, self).__init__(parent=parent, style=wx.LC_REPORT | wx.NO_BORDER)
        self._tier = tier
        self._create_content()

    # -----------------------------------------------------------------------

    def get_selected_annotation(self):
        """Return the annotation matching the selected line in the list.

        :return: (sppasAnnotation) None if no selected item in the list

        """
        index = self.GetFirstSelected()
        if index == -1:
            return None
        return self._tier[index]

    # -----------------------------------------------------------------------

    def _create_content(self):
        """Show a tier in a listctrl.

        """
        # create columns
        is_point_tier = self._tier.is_point()
        if not is_point_tier:
            cols = (MSG_BEGIN, MSG_END, MSG_LABELS, MSG_NB, MSG_TYPE)
        else:
            cols = (MSG_POINT, MSG_LABELS, MSG_NB, MSG_TYPE)
        for i, col in enumerate(cols):
            self.InsertColumn(i, col)
            self.SetColumnWidth(i, 100)

        # fill rows
        for i, a in enumerate(self._tier):

            # fix location
            if not is_point_tier:
                self.InsertItem(i, str(a.get_lowest_localization().get_midpoint()))
                self.SetItem(i, 1, str(a.get_highest_localization().get_midpoint()))
                labeli = 2
            else:
                self.InsertItem(i, str(a.get_highest_localization().get_midpoint()))
                labeli = 1

            # fix label
            if a.is_labelled():
                label_str = a.serialize_labels(separator=" - ")
                self.SetItem(i, labeli, label_str)

                # customize label look
                if label_str in ['#', 'sil']:
                    self.SetItemTextColour(i, SILENCE_FG_COLOUR)
                    self.SetItemBackgroundColour(i, SILENCE_BG_COLOUR)
                if label_str == '+':
                    self.SetItemTextColour(i, SILENCE_FG_COLOUR)
                if label_str in ['@', '@@', 'lg', 'laugh']:
                    self.SetItemTextColour(i, LAUGH_FG_COLOUR)
                    self.SetItemBackgroundColour(i, LAUGH_BG_COLOUR)
                if label_str in ['*', 'gb', 'noise', 'dummy']:
                    self.SetItemTextColour(i, NOISE_FG_COLOUR)
                    self.SetItemBackgroundColour(i, NOISE_BG_COLOUR)
            else:
                self.SetItemTextColour(i, UNLABELLED_FG_COLOUR)

            # properties of the labels
            self.SetItem(i, labeli+1, str(len(a.get_labels())))
            label_type = a.get_label_type()
            if label_type not in sppasTierListCtrl.tag_types:
                lt = "Unknown"
            else:
                lt = sppasTierListCtrl.tag_types[a.get_label_type()]
            self.SetItem(i, labeli+2, lt)

        self.SetColumnWidth(cols.index(MSG_LABELS), -1)

# ----------------------------------------------------------------------------


class sppasTiersEditWindow(sppasSplitterWindow):
    """

    """

    def __init__(self, parent, name="tiers_edit_splitter"):
        super(sppasTiersEditWindow, self).__init__(parent, name=name)

        # Window 1 of the splitter: a ListCtrl of each tier in a notebook
        p1 = sppasNotebook(self, style=wx.BORDER_SIMPLE, name="tiers_notebook")
        # p1.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGING, self._on_page_changing)
        p1.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED, self._on_page_changed)

        # Window 2 of the splitter: an annotation editor
        p2 = self.__create_annotation_editor()

        # Fix size&layout
        self.SetMinimumPaneSize(sppasPanel.fix_size(128))
        self.SplitHorizontally(p1, p2, sppasPanel.fix_size(512))
        self.SetSashGravity(0.9)

    # -----------------------------------------------------------------------

    def __create_annotation_editor(self):
        """"""
        panel = sppasPanel(self, style=wx.BORDER_SIMPLE)

        toolbar = sppasToolbar(panel, name="ann_toolbar")
        toolbar.set_height(24)
        toolbar.AddButton("way_up_down")
        toolbar.AddSpacer(1)
        toolbar.AddToggleButton("code_review", value=True, group_name="view_mode")
        toolbar.AddToggleButton("code_xml", group_name="view_mode")
        btn = toolbar.AddToggleButton("code_json", group_name="view_mode")
        # btn.Enable(False)
        toolbar.AddSpacer(1)
        self.Bind(wx.EVT_BUTTON, self._process_toolbar_event)
        self.Bind(wx.EVT_TOGGLEBUTTON, self._process_toolbar_event)

        body_style = wx.TAB_TRAVERSAL | wx.TE_BESTWRAP | \
                     wx.TE_MULTILINE | wx.BORDER_STATIC
        text = sppasTextCtrl(panel, style=body_style, name="ann_textctrl")
        text.Bind(wx.EVT_CHAR, self._on_char, text)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(toolbar, 0, wx.EXPAND)
        sizer.Add(text, 1, wx.EXPAND)

        panel.SetSizer(sizer)
        return panel

    # -----------------------------------------------------------------------

    def add_tiers(self, tiers):
        notebook = self.FindWindow("tiers_notebook")
        for tier in tiers:
            page = sppasTierListCtrl(notebook, tier)
            page.Bind(wx.EVT_LIST_ITEM_SELECTED, self._on_annotation_selected)
            notebook.AddPage(page, tier.get_name())

    # -----------------------------------------------------------------------

    def refresh_annotation(self):
        notebook = self.FindWindow("tiers_notebook")
        textctrl = self.FindWindow("ann_textctrl")
        tb = self.FindWindow("ann_toolbar")

        page_index = notebook.GetSelection()
        listctrl = notebook.GetPage(page_index)
        ann = listctrl.get_selected_annotation()
        if ann is None:
            textctrl.SetValue("")
        else:
            # Which view is currently toggled?
            textctrl.SetFocus()
            if tb.get_button("code_xml", "view_mode").IsPressed():
                root = ET.Element('Annotation')
                for label in ann.get_labels():
                    label_root = ET.SubElement(root, 'Label')
                    sppasXRA.format_label(label_root, label)
                sppasXRA.indent(root)
                xml_text = ET.tostring(root, encoding="utf-8", method="xml")
                textctrl.SetValue(xml_text)

            elif tb.get_button("code_json", "view_mode").IsPressed():
                root = list()
                for label in ann.get_labels():
                    sppasJRA.format_label(root, label)
                json_text = json.dumps(root, indent=4, separators=(',', ': '))
                textctrl.SetValue(json_text)

            elif tb.get_button("code_review", "view_mode").IsPressed():
                textctrl.SetValue(ann.serialize_labels())

    # -----------------------------------------------------------------------

    def swap_top_down_panels(self):
        win_1 = self.GetWindow1()
        win_2 = self.GetWindow2()
        w, h = win_2.GetSize()
        self.Unsplit(toRemove=win_1)
        self.Unsplit(toRemove=win_2)
        self.SplitHorizontally(win_2, win_1, h)

        if win_1.GetName() == "tiers_notebook":
            self.SetSashGravity(0.9)
        else:
            self.SetSashGravity(0.1)

        self.UpdateSize()

    # -----------------------------------------------------------------------
    # Events management
    # -----------------------------------------------------------------------

    def _process_toolbar_event(self, event):
        """Process a button of the toolbar event.

        :param event: (wx.Event)

        """
        wx.LogDebug("Toolbar Event received by {:s}".format(self.GetName()))
        btn = event.GetEventObject()
        btn_name = btn.GetName()

        if btn_name == "way_up_down":
            self.swap_top_down_panels()

        elif btn_name in ("code_review", "code_xml", "code_json"):
            self.refresh_annotation()

        else:
            event.Skip()

    # -----------------------------------------------------------------------

    def _on_char(self, evt):
        text = evt.GetEventObject()
        if evt.ControlDown() and evt.KeyCode == 1:
            # Ctrl+A
            text.SelectAll()

        else:
            evt.Skip()

    # -----------------------------------------------------------------------

    def _on_annotation_selected(self, evt):
        """An annotation is selected in the list."""
        self.refresh_annotation()

    # -----------------------------------------------------------------------

    def _on_page_changing(self, evt):
        """The notebook is being to change page."""
        pass

    # -----------------------------------------------------------------------

    def _on_page_changed(self, evt):
        """The notebook is being to change page."""
        if not self:
            return
        wx.LogDebug("THE PAGE OF THE NOTEBOOK CHANGED.")
        self.refresh_annotation()


# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------


class TestPanel(sppasTiersEditWindow):
    def __init__(self, parent):
        f1 = os.path.join(paths.samples, "annotation-results",
                          "samples-fra", "F_F_B003-P8-palign.xra")
        f2 = os.path.join(paths.samples, "annotation-results",
                          "samples-fra", "F_F_B003-P8-phon.xra")

        parser = sppasRW(f1)
        trs1 = parser.read()
        parser.set_filename(f2)
        trs2 = parser.read()
        super(TestPanel, self).__init__(parent)
        self.add_tiers(trs1.get_tier_list())
        self.add_tiers(trs2.get_tier_list())

