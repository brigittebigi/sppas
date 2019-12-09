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

    ui.phoenix.page_analyze.listview.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    ListViewPanel displays the content of an annotated file as a list ctrl.

"""

import os
import wx
import wx.dataview
import wx.lib.newevent

from sppas import paths

from sppas.src.anndata import sppasRW
from sppas.src.anndata import sppasTranscription
from sppas.src.anndata import sppasTier
from sppas.src.anndata import sppasMedia
from sppas.src.anndata import sppasHierarchy
from sppas.src.anndata import sppasCtrlVocab
from sppas.src.anndata import sppasMetaData
from sppas.src.config import ui_translation

from ..windows import sppasScrolledPanel
from ..windows import sppasCollapsiblePanel
from ..tools import sppasSwissKnife
from .baseview import sppasBaseViewPanel


# ---------------------------------------------------------------------------
# Internal use of an event, when an item is clicked.

ItemClickedEvent, EVT_ITEM_CLICKED = wx.lib.newevent.NewEvent()
ItemClickedCommandEvent, EVT_ITEM_CLICKED_COMMAND = wx.lib.newevent.NewCommandEvent()

# ---------------------------------------------------------------------------

STATES_ICON_NAMES = {
    "False": "choice_checkbox",
    "True": "choice_checked",
}

# ---------------------------------------------------------------------------


class TrsListViewPanel(sppasBaseViewPanel):
    """A panel to display the content of a sppasTranscription as a list.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      contact@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2019  Brigitte Bigi

    """

    def __init__(self, parent, filename, name="listview-panel"):
        self.__trs = sppasTranscription()
        self.__dirty = False
        super(TrsListViewPanel, self).__init__(parent, filename, name)

    # -----------------------------------------------------------------------
    # Override from the parent
    # -----------------------------------------------------------------------

    def is_modified(self):
        """Return True if the content of the file has changed."""
        return self.__dirty

    # -----------------------------------------------------------------------

    def get_object(self):
        """Return the object created from the opened file.

        :return: (sppasTranscription)

        """
        return self.__trs

    # -----------------------------------------------------------------------

    def load_text(self):
        """Override. Load filename in a sppasTranscription.

        Add the appropriate metadata.
        The tiers, medias and controlled vocab lists are collapsed if empty.

        """
        parser = sppasRW(self._filename)
        self.__trs = parser.read()

        if self.__trs.get_meta("checked", None) is None:
            self.__trs.set_meta("checked", "False")
        if self.__trs.get_meta("collapsed", None) is None:
            self.__trs.set_meta("collapsed", "False")

        for tier in self.__trs.get_tier_list():
            if tier.get_meta("checked", None) is None:
                tier.set_meta("checked", "False")
        self.__trs.set_meta("tiers_collapsed", str(len(self.__trs.get_tier_list()) == 0))

        for media in self.__trs.get_media_list():
            if media.get_meta("checked", None) is None:
                media.set_meta("checked", "False")
        self.__trs.set_meta("media_collapsed", str(len(self.__trs.get_media_list()) == 0))

        for vocab in self.__trs.get_ctrl_vocab_list():
            if vocab.get_meta("checked", None) is None:
                vocab.set_meta("checked", "False")
        self.__trs.set_meta("vocabs_collapsed", str(len(self.__trs.get_ctrl_vocab_list()) == 0))

    # -----------------------------------------------------------------------

    def save(self):
        """Save the displayed transcription into a file."""
        if self.__dirty is True:
            # the writer will increase the file version
            parser = sppasRW(self._filename)
            parser.write(self.__trs)
            self.__dirty = False
            return True
        return False

    # -----------------------------------------------------------------------

    def _create_content(self):
        """Override. Create the content of the panel."""
        self.AddButton("save")
        self.AddButton("close")
        self._create_child_panel()
        self.Collapse(self.str_to_bool(self.__trs.get_meta("collapsed")))

    # ------------------------------------------------------------------------

    def _create_child_panel(self):
        """Override. Create the child panel."""
        child_panel = self.GetPane()

        # todo: add metadata
        # todo: add hierarchy

        tier_ctrl = TiersCollapsiblePanel(child_panel, self.__trs.get_tier_list())
        tier_ctrl.Collapse(self.str_to_bool(self.__trs.get_meta("tiers_collapsed")))
        self.Bind(wx.EVT_COLLAPSIBLEPANE_CHANGED, self.OnCollapseChanged, tier_ctrl)

        media_ctrl = MediaCollapsiblePanel(child_panel, self.__trs.get_media_list())
        media_ctrl.Collapse(self.str_to_bool(self.__trs.get_meta("media_collapsed")))
        self.Bind(wx.EVT_COLLAPSIBLEPANE_CHANGED, self.OnCollapseChanged, media_ctrl)

        vocab_ctrl = CtrlVocabCollapsiblePanel(child_panel, self.__trs.get_ctrl_vocab_list())
        vocab_ctrl.Collapse(self.str_to_bool(self.__trs.get_meta("vocabs_collapsed")))
        self.Bind(wx.EVT_COLLAPSIBLEPANE_CHANGED, self.OnCollapseChanged, vocab_ctrl)

        # y_ctrl = self.__create_hyctrl()

        s = wx.BoxSizer(wx.VERTICAL)
        # s.Add(meta_ctrl, 0, wx.EXPAND)
        s.Add(tier_ctrl, 0, wx.EXPAND)
        s.Add(media_ctrl, 0, wx.EXPAND)
        s.Add(vocab_ctrl, 0, wx.EXPAND)
        # s.Add(hy_ctrl, 0, wx.EXPAND)
        child_panel.SetSizerAndFit(s)

        # The user clicked an item
        child_panel.Bind(EVT_ITEM_CLICKED, self._process_item_clicked)

    # ------------------------------------------------------------------------
    # Events management
    # -----------------------------------------------------------------------

    def _process_item_clicked(self, event):
        """Process an action event: an item was clicked.

        The sender of the event is a Collapsible Panel.

        :param event: (wx.Event)

        """
        # the object is a FileBase (path, root or file)
        object_id = event.id
        obj = self.get_object_in_trs(object_id)

        # change state of the item
        current_state = obj.get_meta("checked")
        new_state = "False"
        if current_state == "False":
            new_state = "True"
        obj.set_meta("checked", new_state)

        # update the corresponding panel(s)
        panel = event.GetEventObject()
        panel.change_state(object_id, new_state)

    # ------------------------------------------------------------------------

    def get_object_in_trs(self, identifier):
        obj = self.__trs.get_tier_from_id(identifier)
        if obj is not None:
            return obj

        obj = self.__trs.get_media_from_id(identifier)
        if obj is not None:
            return obj

        obj = self.__trs.get_ctrl_vocab_from_id(identifier)
        if obj is not None:
            return obj

        return None

    # ------------------------------------------------------------------------

    def OnCollapseChanged(self, evt=None):
        """One of the list child panel was collapsed/expanded."""
        panel = evt.GetEventObject()
        if panel.GetName() == "tiers-panel":
            self.__trs.set_meta("tiers_expanded", str(panel.IsExpanded()))
        elif panel.GetName() == "media-panel":
            self.__trs.set_meta("media_expanded", str(panel.IsExpanded()))
        elif panel.GetName() == "vocabs-panel":
            self.__trs.set_meta("vocab_expanded", str(panel.IsExpanded()))
        else:
            return

        self.Layout()
        self.GetParent().SendSizeEvent()

    # ------------------------------------------------------------------------

    @staticmethod
    def str_to_bool(value):
        if value.lower() == "true":
            return True
        try:
            if value.isdigit() and int(value) > 0:
                return True
        except AttributeError:
            pass
        return False

    # -----------------------------------------------------------------------

    def update(self):
        """Update the controls to match the data."""
        panel = self.FindWindow("tierctrl_panel")
        for i, tier in enumerate(self.__trs.get_tier_list()):
            #self.__update_tier(tier, i)
            panel.add_item(tier)

# ---------------------------------------------------------------------------


class BaseObjectCollapsiblePanel(sppasCollapsiblePanel):
    """A panel to display a list of tiers.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      contact@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2019  Brigitte Bigi

    """

    def __init__(self, parent, objects, label="", name="objects-panel"):
        super(BaseObjectCollapsiblePanel, self).__init__(
            parent, label=label, name=name)

        self.__ils = list()
        self._create_content()
        self._create_columns()
        # self._setup_events()

        # For convenience, objects identifiers are stored into a list.
        self._objects = list()

        # Look&feel
        self.SetBackgroundColour(self.GetParent().GetBackgroundColour())
        self.SetForegroundColour(wx.GetApp().settings.fg_color)
        self.SetFont(wx.GetApp().settings.text_font)

        # Fill in the controls with the data
        self.update(objects)

    # -----------------------------------------------------------------------
    # Public methods
    # -----------------------------------------------------------------------

    def SetBackgroundColour(self, color):
        """Calculate a lightness or darkness background color."""
        r, g, b = color.Red(), color.Green(), color.Blue()
        delta = 10
        if (r + g + b) > 384:
            color = wx.Colour(r, g, b, 50).ChangeLightness(100 - delta)
        else:
            color = wx.Colour(r, g, b, 50).ChangeLightness(100 + delta)

        wx.Window.SetBackgroundColour(self, color)
        for c in self.GetChildren():
            c.SetBackgroundColour(color)

    # -----------------------------------------------------------------------

    def SetFont(self, font):
        """Override."""
        f = wx.Font(font.GetPointSize(),
                    font.GetFamily(),
                    wx.FONTSTYLE_ITALIC,
                    wx.FONTWEIGHT_NORMAL,
                    font.GetUnderlined(),
                    font.GetFaceName())
        sppasCollapsiblePanel.SetFont(self, f)
        self.GetPane().SetFont(font)

        # The change of font implies to re-draw all proportional objects
        self.__il = self.__create_image_list()
        self.FindWindow("listctrl").SetImageList(self.__il, wx.IMAGE_LIST_SMALL)
        self.__set_pane_size()
        self.Layout()

    # ----------------------------------------------------------------------

    def add(self, obj):
        """Add an object in the listctrl child panel.

        :param obj:

        """
        if obj.get_meta("id") in self._objects:
            return False

        self.__add_item(obj)
        return True

    # ----------------------------------------------------------------------

    def remove(self, identifier):
        """Remove an item of the listctrl child panel.

        :param identifier: (str)
        :return: (bool)

        """
        if identifier not in self._objects:
            return False

        self.__remove_item(identifier)
        return True

    # ------------------------------------------------------------------------

    def change_state(self, identifier, state):
        """Update the state of the given identifier.

        :param identifier: (str)
        :param state: (str) True or False

        """
        icon_name = STATES_ICON_NAMES[state]

        listctrl = self.FindWindow("listctrl")
        idx = self._objects.index(identifier)
        listctrl.SetItem(idx, 0, "", imageId=self.__ils.index(icon_name))

    # ------------------------------------------------------------------------

    def update(self, lst_obj):
        """Update each object of a given list.

        :param lst_obj: (list of sppasTier)

        """
        for obj in lst_obj:
            if obj.get_meta("id") not in self._objects:
                self.__add_item(obj)
            else:
                #self.change_state(obj.get_meta("id"), obj.get_state())
                self.update_item(obj)

    # ------------------------------------------------------------------------
    # Construct the GUI
    # ------------------------------------------------------------------------

    def _create_content(self):
        style = wx.BORDER_NONE | wx.LC_REPORT | wx.LC_NO_HEADER | wx.LC_SINGLE_SEL | wx.LC_HRULES
        lst = wx.ListCtrl(self, style=style, name="listctrl")
        lst.Bind(wx.EVT_LIST_ITEM_SELECTED, self.__item_selected)
        self.SetPane(lst)

        info = wx.ListItem()
        info.Mask = wx.LIST_MASK_TEXT | wx.LIST_MASK_IMAGE | wx.LIST_MASK_FORMAT
        info.Image = -1
        info.Align = 0
        lst.InsertColumn(0, info)
        lst.SetColumnWidth(0, sppasScrolledPanel.fix_size(24))

    # ------------------------------------------------------------------------

    def _create_columns(self):
        """Create the columns to display the objects."""
        raise NotImplementedError

    # ------------------------------------------------------------------------

    def __create_image_list(self):
        """Create a list of images to be displayed in the listctrl.

        :return: (wx.ImageList)

        """
        font = self.GetFont()
        lh = int(float(font.GetPixelSize()[1]))
        icon_size = int(float(lh * 1.4))

        il = wx.ImageList(icon_size, icon_size)
        self.__ils = list()

        icon_name = "choice_checkbox"
        bitmap = sppasSwissKnife.get_bmp_icon(icon_name, icon_size)
        il.Add(bitmap)
        self.__ils.append(icon_name)

        icon_name = "choice_checked"
        bitmap = sppasSwissKnife.get_bmp_icon(icon_name, icon_size)
        il.Add(bitmap)
        self.__ils.append(icon_name)

        return il

    # ------------------------------------------------------------------------

    def __set_pane_size(self):
        """Fix the size of the child panel."""
        listctrl = self.GetPane()  # self.FindWindow("listctrl")

        pxh = self.GetFont().GetPixelSize()[1]
        n = listctrl.GetItemCount()
        h = int(pxh * 2.)
        listctrl.SetMinSize(wx.Size(-1, n * h))
        listctrl.SetMaxSize(wx.Size(-1, (n * h) + pxh))

    # ------------------------------------------------------------------------
    # Management the list of files
    # ------------------------------------------------------------------------

    def __add_item(self, obj):
        """Append an object."""
        listctrl = self.FindWindow("listctrl")
        icon_name = STATES_ICON_NAMES[obj.get_meta("checked")]
        img_index = self.__ils.index(icon_name)
        listctrl.InsertItem(listctrl.GetItemCount(), img_index)

        self._objects.append(obj.get_meta("id"))
        self.update_item(obj)

        self.__set_pane_size()
        self.Layout()

    # ------------------------------------------------------------------------

    def __remove_item(self, identifier):
        """Remove an object of the listctrl."""
        listctrl = self.FindWindow("listctrl")
        idx = self._objects.index(identifier)
        listctrl.DeleteItem(idx)

        self._objects.pop(idx)
        self.__set_pane_size()
        self.Layout()

    # ------------------------------------------------------------------------

    def update_item(self, obj):
        """Update information of an object, except its state."""
        raise NotImplementedError

    # ------------------------------------------------------------------------
    # Management of the events
    # ------------------------------------------------------------------------

    def notify(self, identifier):
        """The parent has to be informed of a change of content."""
        evt = ItemClickedEvent(id=identifier)
        evt.SetEventObject(self)
        wx.PostEvent(self.GetParent(), evt)

    # ------------------------------------------------------------------------

    def __item_selected(self, event):
        listctrl = self.FindWindow("listctrl")
        index = listctrl.GetFirstSelected()
        listctrl.Select(index, on=False)

        # notify parent to decide what has to be done
        self.notify(self._objects[index])

# ---------------------------------------------------------------------------


class TiersCollapsiblePanel(BaseObjectCollapsiblePanel):
    """A panel to display a list of tiers.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      contact@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2019  Brigitte Bigi

    """

    def __init__(self, parent, objects):
        super(TiersCollapsiblePanel, self).__init__(
            parent, objects, label="Tiers", name="tiers-panel")

    # ------------------------------------------------------------------------

    def _create_columns(self):
        """Create a listctrl to display the objects."""
        listctrl = self.FindWindow("listctrl")
        listctrl.AppendColumn("name",
                              format=wx.LIST_FORMAT_LEFT,
                              width=sppasScrolledPanel.fix_size(200))
        listctrl.AppendColumn("len",
                              format=wx.LIST_FORMAT_LEFT,
                              width=sppasScrolledPanel.fix_size(80))

    # ------------------------------------------------------------------------

    def update_item(self, obj):
        """Update information of an object, except its state."""
        listctrl = self.FindWindow("listctrl")
        if obj.get_meta("id") in self._objects:
            index = self._objects.index(obj.get_meta("id"))
            listctrl.SetItem(index, 1, obj.get_name())
            listctrl.SetItem(index, 2, str(len(obj)))
            listctrl.RefreshItem(index)

# ---------------------------------------------------------------------------


class CtrlVocabCollapsiblePanel(BaseObjectCollapsiblePanel):
    """A panel to display a list of controlled vocabs.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      contact@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2019  Brigitte Bigi

    """

    def __init__(self, parent, objects):
        super(CtrlVocabCollapsiblePanel, self).__init__(
            parent, objects, label="Controlled vocabularies", name="vocabs-panel")

    # ------------------------------------------------------------------------

    def _create_columns(self):
        """Create a listctrl to display the objects."""
        listctrl = self.FindWindow("listctrl")
        listctrl.AppendColumn("name",
                              format=wx.LIST_FORMAT_LEFT,
                              width=sppasScrolledPanel.fix_size(200))
        listctrl.AppendColumn("description",
                              format=wx.LIST_FORMAT_LEFT,
                              width=sppasScrolledPanel.fix_size(80))

    # ------------------------------------------------------------------------

    def update_item(self, obj):
        """Update information of an object, except its state."""
        listctrl = self.FindWindow("listctrl")
        if obj.get_meta("id") in self._objects:
            index = self._objects.index(obj.get_meta("id"))
            listctrl.SetItem(index, 1, obj.get_name())
            listctrl.SetItem(index, 2, obj.get_description())
            listctrl.RefreshItem(index)

# ---------------------------------------------------------------------------


class MediaCollapsiblePanel(BaseObjectCollapsiblePanel):
    """A panel to display a list of metadata.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      contact@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2019  Brigitte Bigi

    """

    def __init__(self, parent, objects):
        super(MediaCollapsiblePanel, self).__init__(
            parent, objects, label="Media", name="media-panel")

    # ------------------------------------------------------------------------

    def _create_columns(self):
        """Create a listctrl to display the objects."""
        listctrl = self.FindWindow("listctrl")
        listctrl.AppendColumn("filename",
                              format=wx.LIST_FORMAT_LEFT,
                              width=sppasScrolledPanel.fix_size(200))
        listctrl.AppendColumn("mime",
                              format=wx.LIST_FORMAT_LEFT,
                              width=sppasScrolledPanel.fix_size(80))

    # ------------------------------------------------------------------------

    def update_item(self, obj):
        """Update information of an object, except its state."""
        listctrl = self.FindWindow("listctrl")
        if obj.get_meta("id") in self._objects:
            index = self._objects.index(obj.get_meta("id"))
            listctrl.SetItem(index, 1, obj.get_filename())
            listctrl.SetItem(index, 2, obj.get_mime_type())
            listctrl.RefreshItem(index)

# ----------------------------------------------------------------------------
# Panel tested by test_glob.py
# ----------------------------------------------------------------------------


class TestPanel(sppasScrolledPanel):

    def __init__(self, parent):
        super(TestPanel, self).__init__(parent, name="TestPanel-listview")

        f1 = os.path.join(paths.samples, "annotation-results", "samples-fra", "F_F_B003-P8-palign.xra")
        f2 = os.path.join(paths.samples, "annotation-results", "samples-fra", "F_F_B003-P8-salign.xra")
        p1 = TrsListViewPanel(self, f1)
        p2 = TrsListViewPanel(self, f2)
        self.Bind(wx.EVT_COLLAPSIBLEPANE_CHANGED, self.OnCollapseChanged, p1)
        self.Bind(wx.EVT_COLLAPSIBLEPANE_CHANGED, self.OnCollapseChanged, p2)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(p1, 0, wx.EXPAND)
        sizer.Add(p2, 0, wx.EXPAND)

        self.SetBackgroundColour(wx.Colour(28, 28, 28))
        self.SetForegroundColour(wx.Colour(228, 228, 228))

        self.SetSizer(sizer)
        # self.FitInside()
        self.SetAutoLayout(True)
        self.Layout()
        self.SetupScrolling(scroll_x=True, scroll_y=True)

    def OnCollapseChanged(self, evt=None):
        panel = evt.GetEventObject()
        panel.SetFocus()
        self.Layout()
