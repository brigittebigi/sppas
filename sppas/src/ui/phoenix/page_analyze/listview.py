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

import sppas.src.audiodata.aio
from sppas.src.anndata import sppasRW
from sppas.src.anndata import sppasTranscription
from sppas.src.anndata.aio.basetrs import sppasBaseIO
from sppas.src.anndata.anndataexc import TrsAddError
from sppas.src.analysis.tierfilters import SingleFilterTier
from sppas.src.analysis.tierfilters import RelationFilterTier

from sppas.src.anndata import sppasTier
from sppas.src.anndata import sppasMedia
from sppas.src.anndata import sppasHierarchy
from sppas.src.anndata import sppasCtrlVocab
from sppas.src.anndata import sppasMetaData

from ..dialogs import AudioRoamer
from ..windows.listctrl import CheckListCtrl, sppasListCtrl
from ..windows.text import sppasStaticText, sppasTextCtrl
from ..windows.panel import sppasPanel
from ..windows.panel import sppasCollapsiblePanel
from ..windows.dialogs import MetaDataEdit

from .baseview import sppasBaseViewPanel

# ---------------------------------------------------------------------------
# Internal use of an event, when an item is clicked.

ItemClickedEvent, EVT_ITEM_CLICKED = wx.lib.newevent.NewEvent()
ItemClickedCommandEvent, EVT_ITEM_CLICKED_COMMAND = wx.lib.newevent.NewCommandEvent()

# ---------------------------------------------------------------------------

LABEL_LIST = {"duration": "Duration (seconds): ",
              "framerate": "Frame rate (Hz): ",
              "sampwidth": "Sample width (bits): ",
              "channels": "Channels: "}

NO_INFO_LABEL = " ... "

ERROR_COLOUR = wx.Colour(220, 30, 10, 128)     # red
WARNING_COLOUR = wx.Colour(240, 190, 45, 128)  # orange

# ---------------------------------------------------------------------------


class AudioListViewPanel(sppasBaseViewPanel):
    """A panel to display the content of an audio as a list.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      contact@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2020  Brigitte Bigi

    The object this class is displaying is a sppasAudio.
    Can not be constructed if the file is not supported and/or if an error
    occurred when opening or reading.

    """

    def __init__(self, parent, filename, name="listview-panel"):
        self._object = None
        self._dirty = False
        self._labels = dict()
        self._values = dict()

        super(AudioListViewPanel, self).__init__(parent, filename, name)
        self.fix_values()
        if self._object.get_duration() > 300.:
            self.FindWindow("window-more").Enable(False)
            wx.LogWarning("Audio Roamer is disabled: the audio file {} "
                          "is too long.".format(filename))

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

        sppasCollapsiblePanel.SetBackgroundColour(self, colour)
        self.GetPane().SetBackgroundColour(cc)

    # -----------------------------------------------------------------------

    def SetForegroundColour(self, colour):
        sppasCollapsiblePanel.SetForegroundColour(self, colour)
        if self._object is not None and len(self._values) > 0:
            self.fix_values()

    # -----------------------------------------------------------------------

    def fix_values(self):
        """Display information of a sound file. """
        self.__fix_duration()
        self.__fix_framerate()
        self.__fix_sampwidth()
        self.__fix_nchannels()

    # -----------------------------------------------------------------------

    def cancel_values(self):
        """Reset displayed information. """
        for v in self._values:
            v.ChangeValue(NO_INFO_LABEL)
            v.SetForegroundColour(self.GetForegroundColour())

    # -----------------------------------------------------------------------
    # Override from the parent
    # -----------------------------------------------------------------------

    def Destroy(self):
        self._object.close()
        wx.Window.Destroy(self)

    # -----------------------------------------------------------------------

    def get_object(self):
        """Return the object created from the opened file.

        :return: (sppasTranscription)

        """
        return self._object

    # -----------------------------------------------------------------------

    def load_text(self):
        """Override. Load audio filename in the object.

        :raises: IOError

        """
        self._object = sppas.src.audiodata.aio.open(self._filename)

    # -----------------------------------------------------------------------

    def _create_content(self):
        """Override. Create the content of the panel."""
        self.AddButton("window-more")
        self.AddButton("close")

        self._create_child_panel()
        self.Expand()

    # -----------------------------------------------------------------------

    def _create_child_panel(self):
        child_panel = self.GetPane()
        gbs = wx.GridBagSizer()

        for i, label in enumerate(LABEL_LIST):
            static_tx = sppasStaticText(child_panel, label=LABEL_LIST[label])
            self._labels[label] = static_tx
            gbs.Add(static_tx, (i, 0), flag=wx.ALIGN_CENTER_VERTICAL | wx.ALL, border=sppasPanel.fix_size(6))

            # tx = sppasTextCtrl(child_panel, value=NO_INFO_LABEL, style=wx.TE_READONLY | wx.BORDER_NONE)
            tx = sppasStaticText(child_panel, label=NO_INFO_LABEL)
            tx.SetMinSize(wx.Size(sppasPanel.fix_size(200), -1))
            self._values[label] = tx
            gbs.Add(tx, (i, 1), flag=wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, border=sppasPanel.fix_size(6))

        gbs.AddGrowableCol(1)
        child_panel.SetSizer(gbs)

    # -----------------------------------------------------------------------

    def __fix_duration(self):
        duration = self._object.get_duration()
        # self._values["duration"].ChangeValue(str(round(float(duration), 3)))
        self._values["duration"].SetLabel(str(round(float(duration), 3)))
        self._values["duration"].SetForegroundColour(self.GetForegroundColour())

    def __fix_framerate(self):
        framerate = self._object.get_framerate()
        # self._values["framerate"].ChangeValue(str(framerate))
        self._values["framerate"].SetLabel(str(framerate))
        if framerate < 16000:
            self._values["framerate"].SetForegroundColour(ERROR_COLOUR)
        elif framerate in [16000, 32000, 48000]:
            self._values["framerate"].SetForegroundColour(self.GetForegroundColour())
        else:
            self._values["framerate"].SetForegroundColour(WARNING_COLOUR)

    def __fix_sampwidth(self):
        sampwidth = self._object.get_sampwidth()
        # self._values["sampwidth"].ChangeValue(str(sampwidth*8))
        self._values["sampwidth"].SetLabel(str(sampwidth*8))
        if sampwidth == 1:
            self._values["sampwidth"].SetForegroundColour(ERROR_COLOUR)
        elif sampwidth == 2:
            self._values["sampwidth"].SetForegroundColour(self.GetForegroundColour())
        else:
            self._values["sampwidth"].SetForegroundColour(WARNING_COLOUR)

    def __fix_nchannels(self):
        nchannels = self._object.get_nchannels()
        # self._values["channels"].ChangeValue(str(nchannels))
        self._values["channels"].SetLabel(str(nchannels))
        if nchannels == 1:
            self._values["channels"].SetForegroundColour(self.GetForegroundColour())
        else:
            self._values["channels"].SetForegroundColour(ERROR_COLOUR)

    # -----------------------------------------------------------------------

    def _process_event(self, event):
        """Process any kind of event.

        :param event: (wx.Event)

        """
        event_obj = event.GetButtonObj()
        event_name = event_obj.GetName()

        if event_name == "window-more":
            AudioRoamer(self, self._object)

        else:
            sppasBaseViewPanel._process_event(self, event)

# ---------------------------------------------------------------------------


class TrsListViewPanel(sppasBaseViewPanel):
    """A panel to display the content of a file as a list.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      contact@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2019  Brigitte Bigi

    The object this class is displaying is a sppasTranscription.
    Can not be constructed if the file is not supported and/or if an error
    occurred when opening or reading.

    """

    def __init__(self, parent, filename, name="listview-panel"):
        self._object = sppasTranscription("NewDocument")
        self._dirty = False
        self._hicolor = wx.Colour(200, 200, 180)

        super(TrsListViewPanel, self).__init__(parent, filename, name)
        self.__set_metadata()
        self.__set_selected(self._object.get_meta("private_selected"))

    # -----------------------------------------------------------------------

    def SetHighLightColor(self, color):
        """Set a color to highlight the filename if selected."""
        self._hicolor = color
        if self._object.get_meta("private_selected", "False") == "True":
            self.GetToolsPane().SetBackgroundColour(self._hicolor)
        else:
            self.GetToolsPane().SetBackgroundColour(self.GetBackgroundColour())
        self.Refresh()

    # -----------------------------------------------------------------------

    def is_selected(self):
        """Return True is this file is selected."""
        return self.str_to_bool(self._object.get_meta("private_selected", "False"))

    # -----------------------------------------------------------------------

    def get_tiernames(self):
        """Return the list of all tier names."""
        return [tier.get_name() for tier in self._object.get_tier_list()]

    # -----------------------------------------------------------------------

    def get_checked_tier(self):
        """Return the list of checked tiers."""
        checked = list()
        for tier in self._object.get_tier_list():
            if tier.get_meta("private_checked") == "True":
                checked.append(tier)

        return checked

    # -----------------------------------------------------------------------

    def get_nb_checked_tier(self):
        """Return the number of checked tiers."""
        nb = 0
        for tier in self._object.get_tier_list():
            if tier.get_meta("private_checked") == "True":
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
                if tier.get_meta("private_checked") == "False":
                    tier.set_meta("private_checked", "True")
                    panel.change_state(tier.get_id(), "True")
                    self._dirty = True
            else:
                if tier.get_meta("private_checked") == "True":
                    tier.set_meta("private_checked", "False")
                    panel.change_state(tier.get_id(), "False")
                    self._dirty = True

    # -----------------------------------------------------------------------

    def uncheck_tier(self):
        """Uncheck tiers."""
        panel = self.FindWindow("tiers-panel")
        for tier in self._object.get_tier_list():
            if tier.get_meta("private_checked") == "True":
                tier.set_meta("private_checked", "False")
                panel.change_state(tier.get_id(), "False")
                self._dirty = True

    # -----------------------------------------------------------------------

    def rename_tier(self, new_name):
        """Rename the checked tier.

        :param new_name: (str)

        """
        if len(new_name) == 0:
            new_name = None
        panel = self.FindWindow("tiers-panel")
        for tier in self._object.get_tier_list():
            if tier.get_meta("private_checked") == "True":
                old_name = tier.get_name()
                if old_name != new_name:
                    tier.set_name(new_name)
                    new_name = tier.get_name()
                    panel.update_item(tier)
                    wx.LogMessage("Tier {:s} renamed to {:s}"
                                  "".format(old_name, new_name))
                    self._dirty = True

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
                if tier.get_meta("private_checked") == "True":
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
            if tier.get_meta("private_checked") == "True":
                # Copy the tier to the clipboard
                new_tier = tier.copy()
                clipboard.append(new_tier)

        if len(clipboard) > 0:
            self.delete_tier()
            self._dirty = True

        return clipboard

    # -----------------------------------------------------------------------

    def copy_tier(self):
        """Copy checked tiers to the clipboard.

        :return: (list of sppasTier)

        """
        clipboard = list()
        for tier in self._object.get_tier_list():
            if tier.get_meta("private_checked") == "True":
                # Copy the tier to the clipboard
                new_tier = tier.copy()

                # Invalidate its links to other data of its transcription
                new_tier.set_ctrl_vocab(None)
                new_tier.set_media(None)
                new_tier.set_parent(None)

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
                self._dirty = True
            except TrsAddError as e:
                wx.LogError("Paste tier error: {:s}".format(str(e)))

        return added

    # -----------------------------------------------------------------------

    def duplicate_tier(self):
        """Duplicate the checked tiers."""
        panel = self.FindWindow("tiers-panel")

        nb = 0
        for tier in reversed(self._object.get_tier_list()):
            if tier.get_meta("private_checked") == "True":
                new_tier = tier.copy()
                new_tier.gen_id()
                new_tier.set_meta("private_checked", "False")
                new_tier.set_meta("tier_was_duplicated_from_id", tier.get_meta('id'))
                new_tier.set_meta("tier_was_duplicated_from_name", tier.get_name())
                self._object.append(new_tier)
                panel.add(new_tier)
                nb += 1
                self._dirty = True

        return nb

    # -----------------------------------------------------------------------

    def move_up_tier(self):
        """Move up the checked tiers (except for the first one)."""
        panel = self.FindWindow("tiers-panel")

        for i, tier in enumerate(self._object.get_tier_list()):
            if tier.get_meta("private_checked") == "True" and i > 0:
                # move up into the transcription
                self._object.set_tier_index_id(tier.get_id(), i - 1)
                wx.LogDebug("Tier {:s} moved to index {:d}".format(tier.get_name(), i-1))

                # move up into the panel
                panel.remove(tier.get_id())
                panel.add(tier, i-1)
                self._dirty = True

    # ------------------------------------------------------------------------

    def move_down_tier(self):
        """Move down the checked tiers (except for the last one)."""
        panel = self.FindWindow("tiers-panel")

        i = len(self._object.get_tier_list())
        for tier in reversed(self._object.get_tier_list()):
            i = i - 1
            if tier.get_meta("private_checked") == "True" and (i+1) < len(tier):
                # move down into the transcription
                self._object.set_tier_index_id(tier.get_id(), i + 1)
                wx.LogDebug("Tier {:s} moved to index {:d}".format(tier.get_name(), i+1))

                # move down into the panel
                panel.remove(tier.get_id())
                panel.add(tier, i+1)
                self._dirty = True

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
                if tier.get_meta("private_checked") == "True":
                    try:
                        radius = r
                        if p.is_float() is True:
                            radius = float(r)
                        tier.set_radius(radius)
                        self._dirty = True
                        wx.LogMessage(
                            "Radius set to tier {:s} of file {:s}: {:s}"
                            "".format(tier.get_name(), self._filename, str(r)))
                    except Exception as e:
                        wx.LogError(
                            "Radius not set to tier {:s} of file {:s}: {:s}"
                            "".format(tier.get_name(), self._filename, str(e)))

    # -----------------------------------------------------------------------

    def single_filter(self, filters,
                      match_all=False,
                      annot_format=False,
                      out_tiername="Filtered"):
        """Apply filters on the checked tiers.

        :param filters: (list of tuples)
        :param match_all: (bool)
        :param annot_format: (bool) Replace the label by the name of the filter
        :param out_tiername: (str)

        """
        panel = self.FindWindow("tiers-panel")
        nb = 0

        ft = SingleFilterTier(filters, annot_format, match_all)
        for tier in self._object.get_tier_list():
            if tier.get_meta("private_checked") == "True":
                new_tier = ft.filter_tier(tier, out_tiername)
                if new_tier is not None:
                    self._object.append(new_tier)
                    self._dirty = True
                    panel.add(new_tier, len(self._object))
                    nb += 1

        return nb

    # -----------------------------------------------------------------------

    def relation_filter(self, filters,
                        y_tiername,
                        annot_format=False,
                        out_tiername="Filtered"):
        """Apply 'rel' filters on the checked tiers.

        :param filters: (list)
        :param y_tiername: (str) Name of the tier to be in relation with.
        :param annot_format: (bool) Replace the label by the name of the filter
        :param out_tiername: (str)

        """
        panel = self.FindWindow("tiers-panel")
        if self.get_nb_checked_tier() == 0:
            return 0
        y_tier = self._object.find(y_tiername)
        if y_tier is None:
            wx.LogWarning("No tier with name {:s} in {:s}."
                          "".format(y_tiername, self._filename))
            return 0

        nb = 0
        ft = RelationFilterTier(filters, annot_format)
        for tier in self._object.get_tier_list():
            if tier.get_meta("private_checked") == "True":
                new_tier = ft.filter_tier(tier, y_tier, out_tiername)
                if new_tier is not None:
                    self._object.append(new_tier)
                    self._dirty = True
                    panel.add(new_tier, len(self._object))
                    nb += 1

        return nb

    # -----------------------------------------------------------------------
    # Override from the parent
    # -----------------------------------------------------------------------

    def get_object(self):
        """Return the object created from the opened file.

        :return: (sppasTranscription)

        """
        return self._object

    # -----------------------------------------------------------------------

    def load_text(self):
        """Override. Load filename in a sppasBaseIO.

        Add the appropriate metadata.
        The tiers, medias and controlled vocab lists are collapsed if empty.

        :raises: AioFileExtensionError

        """
        parser = sppasRW(self._filename)
        self._object = parser.read()

    # -----------------------------------------------------------------------

    def __set_metadata(self):
        """Set metadata to the object about checked or selected items."""
        if self._object.get_meta("private_selected", None) is None:
            self._object.set_meta("private_selected", "False")

        if self._object.get_meta("private_checked", None) is None:
            self._object.set_meta("private_checked", "False")
        if self._object.get_meta("private_collapsed", None) is None:
            self._object.set_meta("private_collapsed", "False")

        for tier in self._object.get_tier_list():
            if tier.get_meta("private_checked", None) is None:
                tier.set_meta("private_checked", "False")
        self._object.set_meta("private_tiers_collapsed", str(len(self._object.get_tier_list()) == 0))

        for media in self._object.get_media_list():
            if media.get_meta("private_checked", None) is None:
                media.set_meta("private_checked", "False")
        self._object.set_meta("private_media_collapsed", str(len(self._object.get_media_list()) == 0))

        for vocab in self._object.get_ctrl_vocab_list():
            if vocab.get_meta("private_checked", None) is None:
                vocab.set_meta("private_checked", "False")
        self._object.set_meta("private_vocabs_collapsed", str(len(self._object.get_ctrl_vocab_list()) == 0))

    # -----------------------------------------------------------------------

    def save(self, filename=None):
        """Save the displayed transcription into a file.

        :param filename: (str) To be used to "save as..."

        """
        parser = None
        if filename is None and self._dirty is True:
            # the writer will increase the file version
            parser = sppasRW(self._filename)
            self._dirty = False
        if filename is not None:
            parser = sppasRW(filename)

        if parser is not None:
            parser.write(self._object)
            return True
        return False

    # -----------------------------------------------------------------------

    def _create_content(self):
        """Override. Create the content of the panel."""
        self.AddButton("tags")
        self.AddButton("select")
        self.AddButton("save")
        self.AddButton("close")

        self._create_child_panel()
        self.Collapse(self.str_to_bool(self._object.get_meta("private_collapsed")))

    # ------------------------------------------------------------------------

    def _create_child_panel(self):
        """Override. Create the child panel."""
        child_panel = self.GetPane()

        # todo: add hierarchy

        tier_ctrl = TiersCollapsiblePanel(child_panel, self._object.get_tier_list())
        tier_ctrl.Collapse(self.str_to_bool(self._object.get_meta("private_tiers_collapsed")))
        self.Bind(wx.EVT_COLLAPSIBLEPANE_CHANGED, self.OnCollapseChanged, tier_ctrl)

        media_ctrl = MediaCollapsiblePanel(child_panel, self._object.get_media_list())
        media_ctrl.Collapse(self.str_to_bool(self._object.get_meta("private_media_collapsed")))
        self.Bind(wx.EVT_COLLAPSIBLEPANE_CHANGED, self.OnCollapseChanged, media_ctrl)
        if isinstance(self._object, sppasBaseIO) is False:
            media_ctrl.Hide()
        else:
            if self._object.media_support() is False:
                media_ctrl.Hide()

        vocab_ctrl = CtrlVocabCollapsiblePanel(child_panel, self._object.get_ctrl_vocab_list())
        vocab_ctrl.Collapse(self.str_to_bool(self._object.get_meta("private_vocabs_collapsed")))
        self.Bind(wx.EVT_COLLAPSIBLEPANE_CHANGED, self.OnCollapseChanged, vocab_ctrl)
        if isinstance(self._object, sppasBaseIO) is False:
            vocab_ctrl.Hide()
        else:
            if self._object.ctrl_vocab_support() is False:
                vocab_ctrl.Hide()

        # y_ctrl = self.__create_hyctrl()

        s = wx.BoxSizer(wx.VERTICAL)
        # s.Add(meta_ctrl, 0, wx.EXPAND)
        s.Add(tier_ctrl, 0, wx.EXPAND)
        s.Add(media_ctrl, 0, wx.EXPAND)
        s.Add(vocab_ctrl, 0, wx.EXPAND)
        # s.Add(hy_ctrl, 0, wx.EXPAND)
        p = sppasPanel(child_panel)
        p.SetMinSize(wx.Size(-1, 24))  # for the auto horiz scrollbar
        s.Add(p, 0, wx.EXPAND)
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
        current_state = obj.get_meta("private_checked")
        new_state = "False"
        if current_state == "False":
            new_state = "True"
        obj.set_meta("private_checked", new_state)
        self._dirty = True

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

        elif event_name == "tags":
            MetaDataEdit(self, [self._object])

        else:
            sppasBaseViewPanel._process_event(self, event)

    # ------------------------------------------------------------------------

    def __set_selected(self, value=None):
        """Force to set the given selected value or reverse the existing one."""
        # Old value can be unknown (not already set)
        old_value = self._object.get_meta("private_selected", None)
        if old_value is None:
            self._object.set_meta("private_selected", "False")

        # Given new value is None. We switch the old one.
        if value is None:
            if self._object.get_meta("private_selected") == "False":
                value = "True"
            else:
                value = "False"

        if value != self._object.get_meta("private_selected", "x"):
            self._object.set_meta("private_selected", value)
            self._dirty = True

            if self._object.get_meta("private_selected", "False") == "True":
                self.GetToolsPane().SetBackgroundColour(self._hicolor)
            else:
                self.GetToolsPane().SetBackgroundColour(self.GetBackgroundColour())

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
            self._object.set_meta("private_tiers_expanded", str(panel.IsExpanded()))
        elif panel.GetName() == "media-panel":
            self._object.set_meta("private_media_expanded", str(panel.IsExpanded()))
        elif panel.GetName() == "vocabs-panel":
            self._object.set_meta("private_vocab_expanded", str(panel.IsExpanded()))
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
        # set this bg color to all objects
        wx.Panel.SetBackgroundColour(self, colour)
        for c in self.GetChildren():
            c.SetBackgroundColour(colour)

        # but the tools can have a different one
        if self._object.get_meta("private_selected", "False") == "True":
            self.GetToolsPane().SetBackgroundColour(self._hicolor)

# ---------------------------------------------------------------------------
# Content of a Trs
# ---------------------------------------------------------------------------


class BaseObjectCollapsiblePanel(sppasCollapsiblePanel):
    """A panel to display a list of objects.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      contact@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2019  Brigitte Bigi

    """

    def __init__(self, parent, objects, label="", name="objects-panel"):
        super(BaseObjectCollapsiblePanel, self).__init__(
            parent, label=label, name=name)

        self._create_content()
        self._create_columns()
        # self._setup_events()

        # For convenience, objects identifiers are stored into a list.
        self._objects = list()

        # Look&feel
        # self.SetBackgroundColour(self.GetParent().GetBackgroundColour())
        # self.SetForegroundColour(wx.GetApp().settings.fg_color)
        # self.SetFont(wx.GetApp().settings.text_font)

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

    def SetForegroundColour(self, color):
        """Override."""
        wx.Window.SetForegroundColour(self, color)
        for c in self.GetChildren():
            c.SetForegroundColour(color)

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
        idx = self._objects.index(identifier)
        if state == "True":
            self._listctrl.Select(idx, on=1)
        else:
            self._listctrl.Select(idx, on=0)

    # ------------------------------------------------------------------------

    def update(self, lst_obj):
        """Update each object of a given list.

        :param lst_obj: (list of sppasTier)

        """
        for obj in lst_obj:
            if obj.get_id() not in self._objects:
                self.__add_item(obj, index=None)
            else:
                #self.change_state(obj.get_id(), obj.get_state())
                self.update_item(obj)

    # ------------------------------------------------------------------------
    # Construct the GUI
    # ------------------------------------------------------------------------

    def _create_content(self):
        style = wx.BORDER_NONE | wx.LC_REPORT | wx.LC_NO_HEADER  # | wx.LC_SINGLE_SEL
        lst = CheckListCtrl(self, style=style, name="listctrl")
        lst.Bind(wx.EVT_LIST_ITEM_SELECTED, self.__item_selected)
        self.SetPane(lst)

    # ------------------------------------------------------------------------

    @property
    def _listctrl(self):
        return self.FindWindow("listctrl")

    # ------------------------------------------------------------------------

    def _create_columns(self):
        """Create the columns to display the objects."""
        raise NotImplementedError

    # ------------------------------------------------------------------------

    def __set_pane_size(self):
        """Fix the size of the child panel."""
        pxh = self.get_font_height()
        n = self._listctrl.GetItemCount()
        h = int(pxh * 2.)
        self._listctrl.SetMinSize(wx.Size(-1, n * h))
        self._listctrl.SetMaxSize(wx.Size(-1, (n * h) + pxh))

    # ------------------------------------------------------------------------
    # Management the list of tiers
    # ------------------------------------------------------------------------

    def __add_item(self, obj, index=None):
        """Append an object."""
        if index is None or index < 0 or index > self._listctrl.GetItemCount():
            # Append
            index = self._listctrl.InsertItem(self._listctrl.GetItemCount(), "")
        else:
            # Insert
            index = self._listctrl.InsertItem(index, "")

        self._objects.insert(index, obj.get_id())
        self.update_item(obj)

        self.__set_pane_size()
        self.Layout()

    # ------------------------------------------------------------------------

    def __remove_item(self, identifier):
        """Remove an object of the listctrl."""
        idx = self._objects.index(identifier)
        self._listctrl.DeleteItem(idx)

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
        index = event.GetIndex()  # self._listctrl.GetFirstSelected()
        self._listctrl.Select(index, on=False)

        # notify parent to decide what has to be done
        self.notify(self._objects[index])

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
            parent,
            objects,
            label="Controlled vocabularies",
            name="vocabs-panel")

    # ------------------------------------------------------------------------

    def _create_content(self):
        style = wx.BORDER_NONE | wx.LC_REPORT | wx.LC_NO_HEADER  # | wx.LC_SINGLE_SEL
        lst = sppasListCtrl(self, style=style, name="listctrl")
        lst.Bind(wx.EVT_LIST_ITEM_SELECTED, self.__item_selected)
        self.SetPane(lst)

    # ------------------------------------------------------------------------

    def _create_columns(self):
        """Create a listctrl to display the objects."""
        self._listctrl.AppendColumn("name",
                                    format=wx.LIST_FORMAT_LEFT,
                                    width=sppasPanel.fix_size(200))
        self._listctrl.AppendColumn("description",
                                    format=wx.LIST_FORMAT_LEFT,
                                    width=sppasPanel.fix_size(80))
        self._listctrl.AppendColumn("id",
                                    format=wx.LIST_FORMAT_LEFT,
                                    width=sppasPanel.fix_size(220))

    # ------------------------------------------------------------------------

    def update_item(self, obj):
        """Update information of an object, except its state."""
        if obj.get_id() in self._objects:
            index = self._objects.index(obj.get_id())
            self._listctrl.SetItem(index, 0, obj.get_name())
            self._listctrl.SetItem(index, 1, obj.get_description())
            self._listctrl.SetItem(index, 2, obj.get_id())
            self._listctrl.RefreshItem(index)

    # ------------------------------------------------------------------------

    def __item_selected(self, event):
        index = event.GetIndex()
        self._listctrl.Select(index, on=False)

# ---------------------------------------------------------------------------


class MediaCollapsiblePanel(BaseObjectCollapsiblePanel):
    """A panel to display a list of media.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      contact@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2019  Brigitte Bigi

    """

    def __init__(self, parent, objects):
        super(MediaCollapsiblePanel, self).__init__(
            parent,
            objects,
            label="Media",
            name="media-panel")

    # ------------------------------------------------------------------------

    def _create_content(self):
        style = wx.BORDER_NONE | wx.LC_REPORT | wx.LC_NO_HEADER  # | wx.LC_SINGLE_SEL
        lst = sppasListCtrl(self, style=style, name="listctrl")
        lst.Bind(wx.EVT_LIST_ITEM_SELECTED, self.__item_selected)
        self.SetPane(lst)

    # ------------------------------------------------------------------------

    def _create_columns(self):
        """Create a listctrl to display the objects."""
        self._listctrl.AppendColumn("filename",
                                    format=wx.LIST_FORMAT_LEFT,
                                    width=sppasPanel.fix_size(300))
        self._listctrl.AppendColumn("mimeheader",
                                    format=wx.LIST_FORMAT_LEFT,
                                    width=sppasPanel.fix_size(80))
        self._listctrl.AppendColumn("id",
                                    format=wx.LIST_FORMAT_LEFT,
                                    width=sppasPanel.fix_size(220))

    # ------------------------------------------------------------------------

    def update_item(self, obj):
        """Update information of an object, except its state."""
        if obj.get_id() in self._objects:
            index = self._objects.index(obj.get_id())
            self._listctrl.SetItem(index, 0, obj.get_filename())
            self._listctrl.SetItem(index, 1, obj.get_mime_type())
            self._listctrl.SetItem(index, 2, obj.get_id())
            self._listctrl.RefreshItem(index)

    # ------------------------------------------------------------------------

    def __item_selected(self, event):
        index = event.GetIndex()
        self._listctrl.Select(index, on=False)

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
            parent,
            objects,
            label="Tiers",
            name="tiers-panel")

    # ------------------------------------------------------------------------

    def _create_columns(self):
        """Create a listctrl to display the objects."""
        self._listctrl.AppendColumn("name",
                                    format=wx.LIST_FORMAT_LEFT,
                                    width=sppasPanel.fix_size(160))
        self._listctrl.AppendColumn("len",
                                    format=wx.LIST_FORMAT_LEFT,
                                    width=sppasPanel.fix_size(30))
        self._listctrl.AppendColumn("loctype",
                                    format=wx.LIST_FORMAT_LEFT,
                                    width=sppasPanel.fix_size(50))
        self._listctrl.AppendColumn("begin",
                                    format=wx.LIST_FORMAT_LEFT,
                                    width=sppasPanel.fix_size(40))
        self._listctrl.AppendColumn("end",
                                    format=wx.LIST_FORMAT_LEFT,
                                    width=sppasPanel.fix_size(40))
        self._listctrl.AppendColumn("tagtype",
                                    format=wx.LIST_FORMAT_LEFT,
                                    width=sppasPanel.fix_size(40))
        self._listctrl.AppendColumn("tagged",
                                    format=wx.LIST_FORMAT_LEFT,
                                    width=sppasPanel.fix_size(30))
        self._listctrl.AppendColumn("id",
                                    format=wx.LIST_FORMAT_LEFT,
                                    width=sppasPanel.fix_size(240))

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

        if obj.get_id() in self._objects:
            index = self._objects.index(obj.get_id())
            self._listctrl.SetItem(index, 0, obj.get_name())
            self._listctrl.SetItem(index, 1, str(len(obj)))
            self._listctrl.SetItem(index, 2, tier_type)
            self._listctrl.SetItem(index, 3, begin)
            self._listctrl.SetItem(index, 4, end)
            self._listctrl.SetItem(index, 5, tier_tag_type)
            self._listctrl.SetItem(index, 6, str(obj.get_nb_filled_labels()))
            self._listctrl.SetItem(index, 7, obj.get_id())
            self._listctrl.RefreshItem(index)

            state = obj.get_meta("private_checked", "False")
            if state == "True":
                self._listctrl.Select(index, on=1)

# ----------------------------------------------------------------------------
# Panel tested by test_glob.py
# ----------------------------------------------------------------------------


class TestPanel(sppasPanel):

    def __init__(self, parent):
        super(TestPanel, self).__init__(parent, name="TestPanel-listview")

        f0 = os.path.join(paths.samples, "samples-fra", "F_F_B003-P8.wav")
        f1 = os.path.join(paths.samples, "annotation-results", "samples-fra", "F_F_B003-P8-palign.xra")
        f2 = os.path.join(paths.samples, "annotation-results", "samples-fra", "F_F_B003-P8-salign.xra")
        f3 = os.path.join(paths.samples, "annotation-results", "samples-fra", "F_F_B003-P8-stats.csv")
        p0 = AudioListViewPanel(self, f0)
        p1 = TrsListViewPanel(self, f1)
        p2 = TrsListViewPanel(self, f2)
        p3 = TrsListViewPanel(self, None)
        p3.set_filename(f3)
        self.Bind(wx.EVT_COLLAPSIBLEPANE_CHANGED, self.OnCollapseChanged, p0)
        self.Bind(wx.EVT_COLLAPSIBLEPANE_CHANGED, self.OnCollapseChanged, p1)
        self.Bind(wx.EVT_COLLAPSIBLEPANE_CHANGED, self.OnCollapseChanged, p2)
        self.Bind(wx.EVT_COLLAPSIBLEPANE_CHANGED, self.OnCollapseChanged, p3)

        parser = sppasRW(f1)
        trs = parser.read()

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(p1, 0, wx.EXPAND)
        sizer.Add(p2, 0, wx.EXPAND)
        sizer.Add(p3, 0, wx.EXPAND)
        sizer.Add(p0, 0, wx.EXPAND)

        self.SetBackgroundColour(wx.Colour(28, 28, 28))
        self.SetForegroundColour(wx.Colour(228, 228, 228))

        self.SetSizer(sizer)
        self.SetAutoLayout(True)
        self.Layout()

    def OnCollapseChanged(self, evt=None):
        panel = evt.GetEventObject()
        panel.SetFocus()
        self.Layout()
