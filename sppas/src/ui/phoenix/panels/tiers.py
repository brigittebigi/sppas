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
from ..windows.dialogs import Error, Confirm
from ..windows.book import sppasNotebook
from ..main_events import ViewEvent, EVT_VIEW

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
ERR_ANN_SET_LABELS = _("Invalid annotation labels.")
MSG_CANCEL = _("Cancel changes?")

# --------------------------------------------------------------------------


def serialize_labels(labels):
    if len(labels) == 1:
        return labels[0].serialize("", alt=True)
    c = list()
    for label in labels:
        c.append(label.serialize("", alt=True))
    return "\n".join(c)

# --------------------------------------------------------------------------


class sppasTierListCtrl(LineListCtrl):
    """List-view of annotations of a tier.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2020  Brigitte Bigi

    A ListCtrl to represent annotations of a tier.
     - Only the best localization is displayed.
     - Labels are serialized.

    """

    tag_types = {
        "str": "String",
        "int": "Integer",
        "float": "Float",
        "bool": "Boolean"
    }

    # -----------------------------------------------------------------------

    def __init__(self, parent, tier, filename):
        """Create a sppasTierListCtrl and select the first annotation.

        :param parent: (wx.Window)
        :param tier: (sppasTier)
        :param filename: (str) The file this tier was extracted from.

        """
        super(sppasTierListCtrl, self).__init__(parent=parent, style=wx.LC_REPORT | wx.NO_BORDER)

        self._tier = tier
        self.__filename = filename
        self._dirty = False
        self._create_content()

        # select the first annotation. Under MacOS, the first annotation
        # is systematically selected but not under the other platforms.
        # So, we have to select it... to be consistent.
        if len(self._tier) > 0:
            self.Select(0, on=1)

    # -----------------------------------------------------------------------

    def get_tiername(self):
        """Return the name of the tier this listctrl is displaying."""
        return self._tier.get_name()

    # -----------------------------------------------------------------------

    def get_filename(self):
        """Return the name of the file this listctrl is displaying a tier."""
        return self.__filename

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

    def set_annotation_labels(self, idx, labels):
        """Set the labels of an annotation.

        :param idx: (int) Index of the annotation in the list
        :param labels: (list) List of labels

        """
        annotation = self._tier[idx]
        old = serialize_labels(annotation.get_labels())
        new = serialize_labels(labels)
        if old != new:
            annotation.set_labels(labels)
            self._dirty = True

    # -----------------------------------------------------------------------
    # Construct the window
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

    # ---------------------------------------------------------------------

    def Select(self, idx, on):
        """Override. Selects/deselects an item.

        Highlight the selected item with a Bigger & Bold font (the native
        system can't be disabled and is different on each system).

        """
        wx.ListCtrl.Select(self, idx, on)
        font = self.GetFont()
        if on:
            bold = wx.Font(int(float(font.GetPointSize())*1.3),
                           font.GetFamily(),
                           font.GetStyle(),
                           wx.FONTWEIGHT_BOLD,  # weight,
                           underline=False,
                           faceName=font.GetFaceName(),
                           encoding=wx.FONTENCODING_SYSTEM)
            self.SetItemFont(idx, bold)
        else:
            self.SetItemFont(idx, font)

# ----------------------------------------------------------------------------


class sppasTiersEditWindow(sppasSplitterWindow):
    """

    """

    def __init__(self, parent, name="tiers_edit_splitter"):
        super(sppasTiersEditWindow, self).__init__(parent, name=name)

        # Window 1 of the splitter: a ListCtrl of each tier in a notebook
        p1 = sppasNotebook(self, style=wx.BORDER_SIMPLE, name="tiers_notebook")
        # p1.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGING, self._on_page_changing)
        self.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED, self._on_page_changed)

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

    def get_filename(self):
        """Return the name of the file of the current page."""
        notebook = self.FindWindow("tiers_notebook")
        page_index = notebook.GetSelection()
        listctrl = notebook.GetPage(page_index)
        return listctrl.get_filename()

    # -----------------------------------------------------------------------

    def get_tiername(self):
        """Return the name of the tier of the current page."""
        notebook = self.FindWindow("tiers_notebook")
        page_index = notebook.GetSelection()
        listctrl = notebook.GetPage(page_index)
        return listctrl.get_tiername()

    # -----------------------------------------------------------------------

    def set_selected_tier(self, filename, tier_name):
        """Change page selection of the notebook to match given data."""
        notebook = self.FindWindow("tiers_notebook")

        # Currently selected annotation is deselected in a proper way!
        page_index = notebook.GetSelection()
        listctrl = notebook.GetPage(page_index)
        cur_index = listctrl.GetFirstSelected()
        if cur_index != -1:
            self.__annotation_deselected(cur_index)

        # Select requested tier (... and an annotation)
        for i in range(notebook.GetPageCount()):
            page = notebook.GetPage(i)
            if page.get_filename() == filename and page.get_tiername() == tier_name:
                notebook.ChangeSelection(i)
                listctrl = notebook.GetPage(i)
                cur_index = listctrl.GetFirstSelected()
                if cur_index == -1:
                    cur_index = 0
                start, end = self.__annotation_selected(cur_index)
                self.Notify(action="period_selected", value=(start, end))

    # -----------------------------------------------------------------------

    def add_tiers(self, filename, tiers):
        """Add a set of tiers of the file.

        Select the first annotation of the first given tier and notify parent.

        :param filename: (str)
        :param tiers: (list of sppasTier)

        """
        notebook = self.FindWindow("tiers_notebook")
        for tier in tiers:
            if len(tier) > 0:
                page = sppasTierListCtrl(notebook, tier, filename)
                page.Bind(wx.EVT_LIST_ITEM_SELECTED, self._on_annotation_selected)
                page.Bind(wx.EVT_LIST_ITEM_DESELECTED, self._on_annotation_deselected)
                notebook.AddPage(page, tier.get_name())
            else:
                wx.LogError("Page not created. "
                            "No annotation in tier: {:s}".format(tier.get_name()))
        self.Layout()
        self.set_selected_tier(filename, tiers[0])

    # -----------------------------------------------------------------------

    def set_selected_annotation(self, idx):
        """Change the selected annotation.

        :param idx: (int) Index of the annotation to select.

        """
        notebook = self.FindWindow("tiers_notebook")
        page_index = notebook.GetSelection()
        listctrl = notebook.GetPage(page_index)
        cur_index = listctrl.GetFirstSelected()
        if cur_index != -1:
            self.__annotation_deselected(cur_index)
        self.__annotation_selected(idx)

    # -----------------------------------------------------------------------

    def text_to_labels(self):
        """Return the labels created from the text content.

        :return (list of sppasLabel)

        """
        tb = self.FindWindow("ann_toolbar")

        # The text is in XML (.xra) format
        if tb.get_button("code_xml", "view_mode").IsPressed():
            pass

        # The text is in JSON (.jra) format
        if tb.get_button("code_json", "view_mode").IsPressed():
            pass

        # The text is serialized
        if tb.get_button("code_review", "view_mode").IsPressed():
            pass

        return ""

    # -----------------------------------------------------------------------

    def labels_to_text(self, labels):
        if len(labels) == 0:
            return ""

        tb = self.FindWindow("ann_toolbar")

        # The annotation labels are to be displayed in XML (.xra) format
        if tb.get_button("code_xml", "view_mode").IsPressed():
            root = ET.Element('Annotation')
            for label in labels:
                label_root = ET.SubElement(root, 'Label')
                sppasXRA.format_label(label_root, label)
            sppasXRA.indent(root)
            xml_text = ET.tostring(root, encoding="utf-8", method="xml")
            return xml_text

        # The annotation labels are to be displayed in JSON (.jra) format
        if tb.get_button("code_json", "view_mode").IsPressed():
            root = list()
            for label in labels:
                sppasJRA.format_label(root, label)
            json_text = json.dumps(root, indent=4, separators=(',', ': '))
            return json_text

        # The annotation labels are to be displayed in text
        if tb.get_button("code_review", "view_mode").IsPressed():
            return serialize_labels(labels)

        return ""

    # -----------------------------------------------------------------------

    def refresh_annotation(self):
        notebook = self.FindWindow("tiers_notebook")
        textctrl = self.FindWindow("ann_textctrl")
        page_index = notebook.GetSelection()
        listctrl = notebook.GetPage(page_index)

        ann = listctrl.get_selected_annotation()

        if ann is None:
            textctrl.SetValue("")
        else:
            # Which view is currently toggled?
            textctrl.SetFocus()
            textctrl.SetValue(self.labels_to_text(ann.get_labels()))

        return ann

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

    def Notify(self, action, value):
        """Sends a EVT_VIEW event to the listener (if any)."""
        evt = ViewEvent(action=action, value=value)
        evt.SetEventObject(self)
        wx.PostEvent(self.GetParent(), evt)
        wx.LogDebug("Notify parent {:s} of view event".format(self.GetParent().GetName()))

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

    def _on_annotation_deselected(self, evt):
        """An annotation is de-selected in the list.

        If the content was modified, we have to push the text content into
        the annotation of the tier.

        """
        index = evt.GetIndex()
        wx.LogMessage("DESELECTED = {}".format(index))
        self.__annotation_deselected(evt.GetIndex())

    def __annotation_deselected(self, idx):
        notebook = self.FindWindow("tiers_notebook")
        page_index = notebook.GetSelection()
        listctrl = notebook.GetPage(page_index)
        try:
            labels = self.text_to_labels()
            # listctrl.set_annotation_labels(labels)
        except Exception as e:
            msg = ERR_ANN_SET_LABELS + "{:s}".format(str(e)) + MSG_CANCEL
            response = Confirm(msg)

        listctrl.Select(idx, on=0)

    # -----------------------------------------------------------------------

    def _on_annotation_selected(self, evt):
        """An annotation is selected in the list."""
        index = evt.GetIndex()
        wx.LogMessage("SELECTED = {}".format(index))
        start, end = self.__annotation_selected(evt.GetIndex())
        self.Notify(action="period_selected", value=(start, end))

    def __annotation_selected(self, idx):
        notebook = self.FindWindow("tiers_notebook")
        page_index = notebook.GetSelection()
        listctrl = notebook.GetPage(page_index)
        listctrl.Select(idx, on=1)

        ann = self.refresh_annotation()
        if ann is not None:
            start_point = ann.get_lowest_localization()
            start = start_point.get_midpoint()
            r = start_point.get_radius()
            if r is not None:
                start -= r
            end_point = ann.get_highest_localization()
            end = end_point.get_midpoint()
            r = end_point.get_radius()
            if r is not None:
                end += r
        return start, end

    # -----------------------------------------------------------------------

    def _on_page_changing(self, evt):
        """The notebook is being to change page."""

        notebook = self.FindWindow("tiers_notebook")
        page_index = notebook.GetSelection()
        listctrl = notebook.GetPage(page_index)
        cur_index = listctrl.GetFirstSelected()
        if cur_index != -1:
            self.__annotation_deselected(cur_index)

    # -----------------------------------------------------------------------

    def _on_page_changed(self, evt):
        """The notebook changed its page."""
        if not self:
            return
        self.Notify(action="tier_selected", value=None)

        notebook = self.FindWindow("tiers_notebook")
        page_index = notebook.GetSelection()
        listctrl = notebook.GetPage(page_index)
        cur_index = listctrl.GetFirstSelected()
        if cur_index != -1:
            cur_index = 0
        self.__annotation_selected(cur_index)

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
        self.add_tiers(f1, trs1.get_tier_list())
        self.add_tiers(f2, trs2.get_tier_list())

