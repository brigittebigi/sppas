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
import re
import wx
import wx.dataview
import wx.lib.newevent

from sppas import paths

from sppas.src.anndata import sppasRW
from sppas.src.anndata import sppasTranscription
from sppas.src.anndata.anndataexc import TrsAddError, AnnDataTypeError

from sppas.src.anndata import sppasTier
from sppas.src.anndata import sppasMedia
from sppas.src.anndata import sppasHierarchy
from sppas.src.anndata import sppasCtrlVocab
from sppas.src.anndata import sppasMetaData
from sppas.src.config import ui_translation

from ..windows import sppasPanel
from ..windows import sppasCollapsiblePanel
from ..tools import sppasSwissKnife
from .baseview import sppasBaseViewPanel

TIER_BG_COLOUR = wx.Colour(180, 230, 255)

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
    """A panel to display the content of a file as a list.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      contact@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2019  Brigitte Bigi

    The object this class is displaying is a sppasTranscription.

    """

    def __init__(self, parent, filename, name="listview-panel"):
        self._object = sppasTranscription()
        self.__dirty = False
        self._hicolor = wx.Colour(200, 200, 180)

        super(TrsListViewPanel, self).__init__(parent, filename, name)
        self._bgcolor = self.GetBackgroundColour()
        self.__set_selected(self._object.get_meta("selected"))

    # -----------------------------------------------------------------------

    def SetHighLightColor(self, color):
        """Set a color to highlight the filename if selected."""
        self._hicolor = color
        self.SetBackgroundColour(self._bgcolor)
        self.Refresh()

    # -----------------------------------------------------------------------

    def is_selected(self):
        """Return True is this file is selected."""
        return self.str_to_bool(self._object.get_meta("selected", "False"))

    # -----------------------------------------------------------------------

    def get_checked_tier(self):
        """Return the number of checked tiers."""
        checked = list()
        for tier in self._object.get_tier_list():
            if tier.get_meta("checked") == "True":
                checked.append(tier)

        return checked

    # -----------------------------------------------------------------------

    def get_nb_checked_tier(self):
        """Return the number of checked tiers."""
        nb = 0
        for tier in self._object.get_tier_list():
            if tier.get_meta("checked") == "True":
                nb += 1
                wx.LogDebug("Tier {:s} is checked.".format(tier.get_name()))
            else:
                wx.LogDebug("Tier {:s} is not checked.".format(tier.get_name()))

        return nb

    # -----------------------------------------------------------------------

    def check_tier(self, name):
        """Check tier matching the given regexp. Uncheck the others."""
        panel = self.FindWindow("tiers-panel")
        for tier in self._object.get_tier_list():
            is_matching = re.match(name, tier.get_name())
            if is_matching is not None:
                if tier.get_meta("checked") == "False":
                    tier.set_meta("checked", "True")
                    panel.change_state(tier.get_id(), "True")
                    self.__dirty = True
            else:
                if tier.get_meta("checked") == "True":
                    tier.set_meta("checked", "False")
                    panel.change_state(tier.get_id(), "False")
                    self.__dirty = True

    # -----------------------------------------------------------------------

    def uncheck_tier(self):
        """Uncheck tiers."""
        panel = self.FindWindow("tiers-panel")
        for tier in self._object.get_tier_list():
            if tier.get_meta("checked") == "True":
                tier.set_meta("checked", "False")
                panel.change_state(tier.get_id(), "False")
                self.__dirty = True

    # -----------------------------------------------------------------------

    def rename_tier(self, new_name):
        """Rename the checked tier.

        :param new_name: (str)

        """
        if len(new_name) == 0:
            new_name = None
        panel = self.FindWindow("tiers-panel")
        for tier in self._object.get_tier_list():
            if tier.get_meta("checked") == "True":
                old_name = tier.get_name()
                if old_name != new_name:
                    tier.set_name(new_name)
                    new_name = tier.get_name()
                    panel.update_item(tier)
                    wx.LogMessage("Tier {:s} renamed to {:s}"
                                  "".format(old_name, new_name))
                    self.__dirty = True

    # -----------------------------------------------------------------------

    def delete_tier(self, tier_id=None):
        """Delete all checked tiers or the tier which name is exactly matching.

        :param tier_id: (str or None)

        """
        panel = self.FindWindow("tiers-panel")
        if tier_id is not None:
            tier = self._object.find_id(tier_id)
            if tier is not None:
                panel.remove(tier.get_id())
                i = self._object.get_tier_index_id(tier.get_id())
                self._object.pop(i)

        else:
            i = len(self._object)
            for tier in reversed(self._object.get_tier_list()):
                i -= 1
                if tier.get_meta("checked") == "True":
                    panel.remove(tier.get_id())
                    self._object.pop(i)

        self.Layout()

    # -----------------------------------------------------------------------

    def cut_tier(self):
        """Remove checked tiers of the transcription and return them.

        :return: (list of sppasTier)

        """
        clipboard = list()
        for tier in self._object.get_tier_list():
            if tier.get_meta("checked") == "True":
                # Copy the tier to the clipboard
                new_tier = tier.copy()
                clipboard.append(new_tier)

        if len(clipboard) > 0:
            self.delete_tier()
            self.__dirty = True

        return clipboard

    # -----------------------------------------------------------------------

    def copy_tier(self):
        """Copy checked tiers to the clipboard.

        :return: (list of sppasTier)

        """
        clipboard = list()
        for tier in self._object.get_tier_list():
            if tier.get_meta("checked") == "True":
                # Copy the tier to the clipboard
                new_tier = tier.copy()
                clipboard.append(new_tier)

        return clipboard

    # -----------------------------------------------------------------------

    def paste_tier(self, clipboard):
        """Paste the clipboard tier(s) to the current page.

        :param clipboard: (list of tiers, or None)
        :return: (int) Number of tiers added

        """
        added = 0
        panel = self.FindWindow("tiers-panel")

        # Append clipboard tiers to the transcription
        for tier in clipboard:
            copied_tier = tier.copy()
            # copied_tier.gen_id()
            try:
                self._object.append(copied_tier)
                # The tier comes from another Transcription... must update infos.
                if not (copied_tier.get_parent() is self._object):
                    copied_tier.set_parent(self._object)
                panel.add(copied_tier)
                added += 1
                self.__dirty = True
            except TrsAddError as e:
                wx.LogError("Paste tier error: {:s}".format(str(e)))

        return added

    # -----------------------------------------------------------------------

    def duplicate_tier(self):
        """Duplicate the checked tiers."""
        panel = self.FindWindow("tiers-panel")

        nb = 0
        for tier in reversed(self._object.get_tier_list()):
            if tier.get_meta("checked") == "True":
                new_tier = tier.copy()
                new_tier.gen_id()
                new_tier.set_meta("checked", "False")
                new_tier.set_meta("tier_was_duplicated_from_id", tier.get_meta('id'))
                new_tier.set_meta("tier_was_duplicated_from_name", tier.get_name())
                self._object.append(new_tier)
                panel.add(new_tier)
                nb += 1
                self.__dirty = True

        return nb

    # -----------------------------------------------------------------------

    def move_up_tier(self):
        """Move up the checked tiers (except for the first one)."""
        panel = self.FindWindow("tiers-panel")

        for i, tier in enumerate(self._object.get_tier_list()):
            if tier.get_meta("checked") == "True" and i > 0:
                # move up into the transcription
                self._object.set_tier_index_id(tier.get_id(), i - 1)
                wx.LogDebug("Tier {:s} moved to index {:d}".format(tier.get_name(), i-1))

                # move up into the panel
                panel.remove(tier.get_id())
                panel.add(tier, i-1)
                self.__dirty = True

    # ------------------------------------------------------------------------

    def move_down_tier(self):
        """Move down the checked tiers (except for the last one)."""
        panel = self.FindWindow("tiers-panel")

        i = len(self._object.get_tier_list())
        for tier in reversed(self._object.get_tier_list()):
            i = i - 1
            if tier.get_meta("checked") == "True" and (i+1) < len(tier):
                # move down into the transcription
                self._object.set_tier_index_id(tier.get_id(), i + 1)
                wx.LogDebug("Tier {:s} moved to index {:d}".format(tier.get_name(), i+1))

                # move down into the panel
                panel.remove(tier.get_id())
                panel.add(tier, i+1)
                self.__dirty = True

    # -----------------------------------------------------------------------

    def radius(self, r, tier_id=None):
        """Fix a new radius value to the given tier or the checked tiers.

        :param r: (int or float) Value of the vagueness
        :param tier_id: (str or None)

        """
        if tier_id is not None:
            tier = self._object.find_id(tier_id)
            if tier is not None:
                tier.set_radius(r)
        else:
            for tier in self._object.get_tier_list():
                p = tier.get_first_point()
                if p is None:
                    continue
                if tier.get_meta("checked") == "True":
                    try:
                        radius = r
                        if p.is_float() is True:
                            radius = float(r)
                        tier.set_radius(radius)
                        self.__dirty = True
                        wx.LogMessage(
                            "Radius set to tier {:s} of file {:s}: {:s}"
                            "".format(tier.get_name(), self._filename, str(r)))
                    except Exception as e:
                        wx.LogError(
                            "Radius not set to tier {:s} of file {:s}: {:s}"
                            "".format(tier.get_name(), self._filename, str(e)))

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
        return self._object

    # -----------------------------------------------------------------------

    def load_text(self):
        """Override. Load filename in a sppasTranscription.

        Add the appropriate metadata.
        The tiers, medias and controlled vocab lists are collapsed if empty.

        :raises: AioFileExtensionError

        """
        parser = sppasRW(self._filename)
        self._object = parser.read()

        if self._object.get_meta("selected", None) is None:
            self._object.set_meta("selected", "False")

        if self._object.get_meta("checked", None) is None:
            self._object.set_meta("checked", "False")
        if self._object.get_meta("collapsed", None) is None:
            self._object.set_meta("collapsed", "False")

        for tier in self._object.get_tier_list():
            if tier.get_meta("checked", None) is None:
                tier.set_meta("checked", "False")
        self._object.set_meta("tiers_collapsed", str(len(self._object.get_tier_list()) == 0))

        for media in self._object.get_media_list():
            if media.get_meta("checked", None) is None:
                media.set_meta("checked", "False")
        self._object.set_meta("media_collapsed", str(len(self._object.get_media_list()) == 0))

        for vocab in self._object.get_ctrl_vocab_list():
            if vocab.get_meta("checked", None) is None:
                vocab.set_meta("checked", "False")
        self._object.set_meta("vocabs_collapsed", str(len(self._object.get_ctrl_vocab_list()) == 0))

    # -----------------------------------------------------------------------

    def save(self, filename=None):
        """Save the displayed transcription into a file.

        :param filename: (str) To be used to "save as..."

        """
        parser = None
        if filename is None and self.__dirty is True:
            # the writer will increase the file version
            parser = sppasRW(self._filename)
            self.__dirty = False
        if filename is not None:
            parser = sppasRW(filename)

        if parser is not None:
            parser.write(self._object)
            return True
        return False

    # -----------------------------------------------------------------------

    def _create_content(self):
        """Override. Create the content of the panel."""
        self.AddButton("select")
        self.AddButton("save")
        self.AddButton("close")

        self._create_child_panel()
        self.Collapse(self.str_to_bool(self._object.get_meta("collapsed")))

    # ------------------------------------------------------------------------

    def _create_child_panel(self):
        """Override. Create the child panel."""
        child_panel = self.GetPane()

        # todo: add metadata
        # todo: add hierarchy

        tier_ctrl = TiersCollapsiblePanel(child_panel, self._object.get_tier_list())
        tier_ctrl.Collapse(self.str_to_bool(self._object.get_meta("tiers_collapsed")))
        self.Bind(wx.EVT_COLLAPSIBLEPANE_CHANGED, self.OnCollapseChanged, tier_ctrl)

        media_ctrl = MediaCollapsiblePanel(child_panel, self._object.get_media_list())
        media_ctrl.Collapse(self.str_to_bool(self._object.get_meta("media_collapsed")))
        self.Bind(wx.EVT_COLLAPSIBLEPANE_CHANGED, self.OnCollapseChanged, media_ctrl)

        vocab_ctrl = CtrlVocabCollapsiblePanel(child_panel, self._object.get_ctrl_vocab_list())
        vocab_ctrl.Collapse(self.str_to_bool(self._object.get_meta("vocabs_collapsed")))
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
        object_id = event.id
        obj = self.get_object_in_trs(object_id)

        # change state of the item
        current_state = obj.get_meta("checked")
        new_state = "False"
        if current_state == "False":
            new_state = "True"
        obj.set_meta("checked", new_state)
        self.__dirty = True

        # update the corresponding panel(s)
        panel = event.GetEventObject()
        panel.change_state(object_id, new_state)

    # -----------------------------------------------------------------------

    def _process_event(self, event):
        """Process any kind of event.

        :param event: (wx.Event)

        """
        event_obj = event.GetButtonObj()
        event_name = event_obj.GetName()

        if event_name == "select":
            self.__set_selected()

        else:
            sppasBaseViewPanel._process_event(self, event)

    # ------------------------------------------------------------------------

    def __set_selected(self, value=None):
        """Force to set the given selected value or reverse the existing one."""
        if value is None:
            is_selected = self._object.get_meta("selected", "True")
            if is_selected is "False":
                value = "True"
            else:
                value = "False"

        if value != self._object.get_meta("selected", "x"):
            self._object.set_meta("selected", value)
            self.__dirty = True
            wx.LogDebug("File {:s} selected: {:s}".format(self._filename, value))
        self.SetBackgroundColour(self._bgcolor)
        self.Refresh()

    # ------------------------------------------------------------------------

    def get_object_in_trs(self, identifier):
        obj = self._object.get_tier_from_id(identifier)
        if obj is not None:
            return obj

        obj = self._object.get_media_from_id(identifier)
        if obj is not None:
            return obj

        obj = self._object.get_ctrl_vocab_from_id(identifier)
        if obj is not None:
            return obj

        return None

    # ------------------------------------------------------------------------

    def OnCollapseChanged(self, evt=None):
        """One of the list child panel was collapsed/expanded."""
        panel = evt.GetEventObject()
        if panel.GetName() == "tiers-panel":
            self._object.set_meta("tiers_expanded", str(panel.IsExpanded()))
        elif panel.GetName() == "media-panel":
            self._object.set_meta("media_expanded", str(panel.IsExpanded()))
        elif panel.GetName() == "vocabs-panel":
            self._object.set_meta("vocab_expanded", str(panel.IsExpanded()))
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
        panel = self.FindWindow("tiers-panel")
        for i, tier in enumerate(self._object.get_tier_list()):
            #self.__update_tier(tier, i)
            panel.add_item(tier)

    # -----------------------------------------------------------------------

    def SetBackgroundColour(self, colour):
        """Override."""
        self._bgcolor = colour
        wx.Panel.SetBackgroundColour(self, self._bgcolor)
        for c in self.GetChildren():
            c.SetBackgroundColour(colour)

        if self._object.get_meta("selected", "False") == "True":
            self.GetToolsPane().SetBackgroundColour(self._hicolor)

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

        self._ils = list()
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

    def SetBackgroundColour(self, colour):
        r, g, b = colour.Red(), colour.Green(), colour.Blue()
        delta = 10
        if (r + g + b) > 384:
            cc = wx.Colour(r, g, b, 50).ChangeLightness(100 - delta)
        else:
            cc = wx.Colour(r, g, b, 50).ChangeLightness(100 + delta)

        sppasCollapsiblePanel.SetBackgroundColour(self, cc)

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

    def add(self, obj, index=None):
        """Add an object in the listctrl child panel.

        :param obj:
        :param index: Position of the object in the list. If None, append.

        """
        if obj.get_id() in self._objects:
            return False

        self.__add_item(obj, index)
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
        listctrl.SetItem(idx, 0, "", imageId=self._ils.index(icon_name))

    # ------------------------------------------------------------------------

    def update(self, lst_obj):
        """Update each object of a given list.

        :param lst_obj: (list of sppasTier)

        """
        for obj in lst_obj:
            if obj.get_id() not in self._objects:
                self.__add_item(obj)
            else:
                #self.change_state(obj.get_id(), obj.get_state())
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
        lst.SetColumnWidth(0, sppasPanel.fix_size(24))

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
        self._ils = list()

        icon_name = "choice_checkbox"
        bitmap = sppasSwissKnife.get_bmp_icon(icon_name, icon_size)
        il.Add(bitmap)
        self._ils.append(icon_name)

        icon_name = "choice_checked"
        bitmap = sppasSwissKnife.get_bmp_icon(icon_name, icon_size)
        il.Add(bitmap)
        self._ils.append(icon_name)

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
    # Management the list of tiers
    # ------------------------------------------------------------------------

    def __add_item(self, obj, index=None):
        """Append an object."""
        listctrl = self.FindWindow("listctrl")
        icon_name = STATES_ICON_NAMES[obj.get_meta("checked", "False")]
        img_index = self._ils.index(icon_name)

        if index is None or index < 0 or index > listctrl.GetItemCount():
            # Append
            index = listctrl.InsertItem(listctrl.GetItemCount(), img_index)
        else:
            index = listctrl.InsertItem(index, img_index)

        self._objects.insert(index, obj.get_id())
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
                              width=sppasPanel.fix_size(160))
        listctrl.AppendColumn("len",
                              format=wx.LIST_FORMAT_LEFT,
                              width=sppasPanel.fix_size(30))
        listctrl.AppendColumn("loctype",
                              format=wx.LIST_FORMAT_LEFT,
                              width=sppasPanel.fix_size(50))
        listctrl.AppendColumn("begin",
                              format=wx.LIST_FORMAT_LEFT,
                              width=sppasPanel.fix_size(40))
        listctrl.AppendColumn("end",
                              format=wx.LIST_FORMAT_LEFT,
                              width=sppasPanel.fix_size(40))
        listctrl.AppendColumn("tagtype",
                              format=wx.LIST_FORMAT_LEFT,
                              width=sppasPanel.fix_size(40))
        listctrl.AppendColumn("tagged",
                              format=wx.LIST_FORMAT_LEFT,
                              width=sppasPanel.fix_size(30))
        listctrl.AppendColumn("id",
                              format=wx.LIST_FORMAT_LEFT,
                              width=sppasPanel.fix_size(220))

    # ------------------------------------------------------------------------

    def update_item(self, obj):
        """Update information of an object, except its state.

        :param obj: (sppasTier)

        """
        if obj.is_point() is True:
            tier_type = "Point"
        elif obj.is_interval():
            tier_type = "Interval"
        elif obj.is_disjoint():
            tier_type = "Disjoint"
        else:  # probably an empty tier
            tier_type = "Unknown"

        if obj.is_empty() is True:
            begin = " ... "
            end = " ... "
        else:
            begin = str(obj.get_first_point().get_midpoint())
            end = str(obj.get_last_point().get_midpoint())

        if obj.is_string() is True:
            tier_tag_type = "String"
        elif obj.is_int() is True:
            tier_tag_type = "Integer"
        elif obj.is_float() is True:
            tier_tag_type = "Float"
        elif obj.is_bool() is True:
            tier_tag_type = "Bool"
        else:
            tier_tag_type = "Unknown"

        listctrl = self.FindWindow("listctrl")
        if obj.get_id() in self._objects:
            index = self._objects.index(obj.get_id())
            listctrl.SetItem(index, 1, obj.get_name())
            listctrl.SetItem(index, 2, str(len(obj)))
            listctrl.SetItem(index, 3, tier_type)
            listctrl.SetItem(index, 4, begin)
            listctrl.SetItem(index, 5, end)
            listctrl.SetItem(index, 6, tier_tag_type)
            listctrl.SetItem(index, 7, str(obj.get_nb_filled_labels()))
            listctrl.SetItem(index, 8, obj.get_id())
            listctrl.RefreshItem(index)

            state = obj.get_meta("checked", "False")
            if state == "True":
                listctrl.SetItemBackgroundColour(index, TIER_BG_COLOUR)

    # ------------------------------------------------------------------------

    def change_state(self, identifier, state):
        """Update the state of the given identifier.

        :param identifier: (str)
        :param state: (str) True or False

        """
        icon_name = STATES_ICON_NAMES[state]

        listctrl = self.FindWindow("listctrl")
        idx = self._objects.index(identifier)
        listctrl.SetItem(idx, 0, "", imageId=self._ils.index(icon_name))

        if state == "True":
            listctrl.SetItemBackgroundColour(idx, TIER_BG_COLOUR)
        else:
            listctrl.SetItemBackgroundColour(idx, self.GetBackgroundColour())

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
                              width=sppasPanel.fix_size(200))
        listctrl.AppendColumn("description",
                              format=wx.LIST_FORMAT_LEFT,
                              width=sppasPanel.fix_size(80))
        listctrl.AppendColumn("id",
                              format=wx.LIST_FORMAT_LEFT,
                              width=sppasPanel.fix_size(220))

    # ------------------------------------------------------------------------

    def update_item(self, obj):
        """Update information of an object, except its state."""
        listctrl = self.FindWindow("listctrl")
        if obj.get_id() in self._objects:
            index = self._objects.index(obj.get_id())
            listctrl.SetItem(index, 1, obj.get_name())
            listctrl.SetItem(index, 2, obj.get_description())
            listctrl.SetItem(index, 3, obj.get_id())
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
                              width=sppasPanel.fix_size(300))
        listctrl.AppendColumn("mimeheader",
                              format=wx.LIST_FORMAT_LEFT,
                              width=sppasPanel.fix_size(80))
        listctrl.AppendColumn("id",
                              format=wx.LIST_FORMAT_LEFT,
                              width=sppasPanel.fix_size(220))

    # ------------------------------------------------------------------------

    def update_item(self, obj):
        """Update information of an object, except its state."""
        listctrl = self.FindWindow("listctrl")
        if obj.get_id() in self._objects:
            index = self._objects.index(obj.get_id())
            listctrl.SetItem(index, 1, obj.get_filename())
            listctrl.SetItem(index, 2, obj.get_mime_type())
            listctrl.SetItem(index, 3, obj.get_id())
            listctrl.RefreshItem(index)

# ----------------------------------------------------------------------------
# Panel tested by test_glob.py
# ----------------------------------------------------------------------------


class TestPanel(sppasPanel):

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

    def OnCollapseChanged(self, evt=None):
        panel = evt.GetEventObject()
        panel.SetFocus()
        self.Layout()
