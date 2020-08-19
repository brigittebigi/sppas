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

    wxgui.anz_panels.trslist.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""
import wx
import os.path
import logging

from sppas.src.anndata import sppasRW
from sppas.src.anndata.transcription import sppasTranscription

from sppas.src.ui.wxgui.ui.CustomEvents import PanelSelectedEvent
from sppas.src.ui.wxgui.structs.prefs import Preferences
from sppas.src.ui.wxgui.views.preview import PreviewTierDialog
from sppas.src.ui.wxgui.dialogs.choosers import RadiusChooser
from sppas.src.ui.wxgui.dialogs.msgdialogs import ShowInformation
from sppas.src.ui.wxgui.dialogs.msgdialogs import ShowYesNoQuestion

from sppas.src.ui.wxgui.ui.CustomListCtrl import CheckListCtrl


# -------------------------------------------------------------------------
# Constants
# -------------------------------------------------------------------------

FG_FILE_COLOUR = wx.Colour(45, 60, 10)
FG_FILE_DIRTY_COLOUR = wx.Colour(45, 60, 170)

# -------------------------------------------------------------------------


class TrsList(wx.Panel):
    """Show data about transcriptions, in a panel including a list of tiers.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2018  Brigitte Bigi

    """
    def __init__(self, parent, filename, trs=None, multiple=False):
        wx.Panel.__init__(self, parent, -1, size=wx.DefaultSize)

        # initialize the GUI
        self._prefs = Preferences()
        self._filename = filename
        self._dirty = False       # the transcription was changed
        self._selected = False    # the transcription is selected
        self._protected = list()  # list of the tiers that are protected (i.e. they can't be modified)

        if len(filename) == 0:
            self._filename = "Empty"

        box_title = self._create_title()
        self.tier_list = self._create_list(multiple)

        # load the Transcription
        if trs is None and len(filename) != 0:
            self.LoadFile(filename)
        else:
            self._transcription = trs
        # add Transcription information in the list
        for tier in self._transcription:
            self.AddTierProperties(tier)
        self._checksize()

        # events
        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.OnListItemSelected, self.tier_list)
        self.Bind(wx.EVT_LIST_COL_CLICK, self.OnListItemSelected, self.tier_list)

        # layout
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(box_title, 0, wx.EXPAND | wx.ALL, border=4)
        sizer.Add(self.tier_list, 1, wx.EXPAND | wx.ALL, border=4)

        self.SetFont(self._prefs.GetValue('M_FONT'))
        self.SetForegroundColour(self._prefs.GetValue('M_FG_COLOUR'))
        self.SetBackgroundColour(self._prefs.GetValue('M_BG_COLOUR'))
        self._box_title.SetForegroundColour(FG_FILE_COLOUR)

        self.SetSizerAndFit(sizer)
        self.SetAutoLayout(True)
        self.Layout()

    # ----------------------------------------------------------------------

    def _create_title(self):
        """Create the title of the panel."""

        _sizer = wx.BoxSizer(wx.HORIZONTAL)

        self._static_tx = wx.TextCtrl(self, -1, "File: ", style=wx.TE_READONLY | wx.NO_BORDER)
        self._box_title = wx.TextCtrl(self, -1, self._filename, style=wx.TE_READONLY | wx.NO_BORDER)

        _sizer.Add(self._static_tx, 0, wx.RIGHT, border=2)
        _sizer.Add(self._box_title,  1, wx.EXPAND)

        return _sizer

    # ----------------------------------------------------------------------

    def _create_list(self, multiple=False):
        """Create the list to show information of a each tier of a transcription."""

        if multiple:
            tier_list = CheckListCtrl(self, -1, style=wx.LC_REPORT | wx.BORDER_NONE)
        else:
            tier_list = CheckListCtrl(self, -1, style=wx.LC_REPORT | wx.BORDER_NONE | wx.LC_SINGLE_SEL)

        # Add all columns
        col_names = [" Number ", " Name ", " Begin   ", " End     ", " Type    ", " Size    "]
        for i, n in enumerate(col_names):
            tier_list.InsertColumn(i, n)

        # Fix column width
        for i in range(len(col_names)):
            tier_list.SetColumnWidth(i, wx.LIST_AUTOSIZE_USEHEADER)
        # Enlarge column with tier name
        tier_list.SetColumnWidth(1, 140)

        return tier_list

    # -------------------------------------------------------------------------

    def AddTierProperties(self, tier):
        """Display tier properties."""

        if tier is None:
            ShowInformation(self,
                            self._prefs,
                            "Attempt to add a tier but tier is None!!!",
                            style=wx.ICON_ERROR)
            return

        try:
            if tier.is_point() is True:
                tier_type = "Point"
            elif tier.is_interval():
                tier_type = "Interval"
            elif tier.is_disjoint():
                tier_type = "Disjoint"
            else:  # probably an empty tier
                tier_type = "Unknown"

            if tier.is_empty() is True:
                begin = " ... "
                end = " ... "
            else:
                begin = tier.get_first_point().get_midpoint()
                end = tier.get_last_point().get_midpoint()

            tier_idx = self._transcription.get_tier_index(tier.get_name())
            self.tier_list.InsertStringItem(tier_idx, " -- {:d} -- ".format(tier_idx+1))
            self.tier_list.SetStringItem(tier_idx, 1, tier.get_name())
            self.tier_list.SetStringItem(tier_idx, 2, str(begin))
            self.tier_list.SetStringItem(tier_idx, 3, str(end))
            self.tier_list.SetStringItem(tier_idx, 4, tier_type)
            self.tier_list.SetStringItem(tier_idx, 5, str(len(tier)))

        except Exception as e:
            self.tier_list.InsertStringItem(1, "Error: {:s}".format(str(e)))

    # ----------------------------------------------------------------------
    # Callbacks...
    # ----------------------------------------------------------------------

    def OnListItemSelected(self, event):
        """An item of this panel was clicked. Inform the parent."""

        evt = PanelSelectedEvent(panel=self)
        evt.SetEventObject(self)
        wx.PostEvent(self.GetParent(), evt)

    # ----------------------------------------------------------------------
    # GUI
    # ----------------------------------------------------------------------

    def SetPreferences(self, prefs):
        """Set new preferences."""

        self._prefs = prefs
        self.SetBackgroundColour(self._prefs.GetValue("M_BG_COLOUR"))
        self.SetForegroundColour(self._prefs.GetValue("M_FG_COLOUR"))
        self.SetFont(self._prefs.GetValue("M_FONT"))

    # -------------------------------------------------------------------------

    def SetFont(self, font):
        """Set a new font."""

        wx.Window.SetFont(self, font)

        self.tier_list.SetFont(font)
        for i in range(len(self._transcription)):
            self.tier_list.SetItemFont(i, font)
        self._static_tx.SetFont(font)
        self._box_title.SetFont(font)
        self.Layout()  # bigger/smaller font can impact on the layout

    # -------------------------------------------------------------------------

    def SetBackgroundColour(self, color):
        """Set background."""

        wx.Window.SetBackgroundColour(self, color)

        self.tier_list.SetBackgroundColour(color)
        for i in range(len(self._transcription)):
            self.tier_list.SetItemBackgroundColour(i, color)
        self._static_tx.SetBackgroundColour(color)
        self._box_title.SetBackgroundColour(color)
        self.Refresh()

    # -------------------------------------------------------------------------

    def SetForegroundColour(self, color):
        """Set foreground and items text color."""

        wx.Window.SetForegroundColour(self, color)

        self.tier_list.SetForegroundColour(color)
        for i in range(len(self._transcription)):
            self.tier_list.SetItemTextColour(i, color)
        self._static_tx.SetForegroundColour(color)
        self.Refresh()

    # ----------------------------------------------------------------------
    # Functions...
    # ----------------------------------------------------------------------

    def Protect(self):
        """Fix the current list of tiers as protected: they won't be changed."""

        self._protected = list()
        for i, t in enumerate(self._transcription):
            self._protected.append(t)
            self.tier_list.SetItemTextColour(i, wx.Colour(140, 10, 10))

    # -------------------------------------------------------------------------

    def Unprotect(self):
        """Erase the list of protected tiers."""

        self._protected = list()

    # ----------------------------------------------------------------------

    def IsSelected(self, tier_name, case_sensitive=False):
        """Return True if the tier is selected."""

        i = self._transcription.get_tier_index(tier_name, case_sensitive)
        if i != -1:
            return self.tier_list.IsSelected(i)
        return False

    # ----------------------------------------------------------------------

    def Select(self, tier_name, case_sensitive=False):
        """Select tiers which name is exactly matching."""

        i = self._transcription.get_tier_index(tier_name, case_sensitive)
        if i != -1:
            self.tier_list.Select(i, on=True)
            return True
        return False

    # ----------------------------------------------------------------------

    def Deselect(self):
        #for i in range(self.tier_list.GetItemCount()):
        #    self.tier_list.Select(i, on=0)
        self.tier_list.DeSelectAll()

    # ----------------------------------------------------------------------

    def Rename(self):
        """Rename the selected tier. Dialog with the user to get the new name."""

        sel_list = self._check_selected_tier()
        if sel_list == -1:
            return

        tier = self._transcription[sel_list]
        if tier in self._protected:
            ShowInformation(self,
                            self._prefs,
                            "Attempt to rename a protected tier: forbidden!",
                            style=wx.ICON_INFORMATION)
            return

        # Ask the user to enter a new name (set current as default)
        dlg = wx.TextEntryDialog(self,
                                 'Indicate the new tier name',
                                 'Data Roamer',
                                 'Rename a tier.')
        dlg.SetValue(tier.get_name())
        if dlg.ShowModal() == wx.ID_OK:
            new_name = dlg.GetValue()
        else:
            new_name = tier.get_name()
        dlg.Destroy()

        if new_name != tier.get_name():
            # Update tier name of the transcription
            tier.set_name(new_name)
            # Update tier name of the list
            self.tier_list.SetStringItem(sel_list, 1, dlg.GetValue())
            self._dirty = True
            self._box_title.SetForegroundColour(FG_FILE_DIRTY_COLOUR)
            self.Refresh()

    # ----------------------------------------------------------------------

    def Cut(self):
        """Cut the selected tier. Return the clipboard."""

        sel_list = self._check_selected_tier()
        if sel_list == -1:
            return

        tier = self._transcription[sel_list]
        if tier in self._protected:
            ShowInformation(self,
                            self._prefs,
                            "Attempt to cut a protected tier: forbidden!",
                            style=wx.ICON_INFORMATION)
            return

        # Copy the tier to the clipboard
        clipboard = tier.copy()
        clipboard.set_meta("tier_was_cut_from_id", tier.get_meta('id'))
        clipboard.set_meta("tier_was_cut_from_name", tier.get_name())

        # Delete tier of the transcription
        self._transcription.pop(sel_list)
        # Delete tier of the list
        self.tier_list.DeleteItem(sel_list)

        # Update tier numbers of next items in the list.
        for i in range(sel_list, self.tier_list.GetItemCount()):
            self.tier_list.SetStringItem(i, 0, " -- {:d} -- ".format(i+1))

        self.Deselect()
        self._checksize()
        self._dirty = True
        self._box_title.SetForegroundColour(FG_FILE_DIRTY_COLOUR)
        self.Refresh()

        return clipboard

    # ----------------------------------------------------------------------

    def Copy(self):
        """Return the selected tier."""

        sel_list = self._check_selected_tier()
        if sel_list == -1:
            return

        # Copy the tier to the clipboard
        tier = self._transcription[sel_list]
        new_tier = tier.copy()
        new_tier.set_meta("tier_was_copied_from_id", tier.get_meta('id'))
        new_tier.set_meta("tier_was_copied_from_name", tier.get_name())
        new_tier.gen_id()

        return new_tier

    # ----------------------------------------------------------------------

    def Paste(self, clipboard):
        """Paste the clipboard tier to the current page."""

        # Get the clipboard tier
        if clipboard is None:
            return

        # Append clipboard to the transcription
        tier = clipboard.copy()
        tier.gen_id()
        self.AddTier(tier)

        # The tier comes from another Transcription... must update infos.
        if not (tier.get_parent() is self._transcription):
            # parent transcription (it also adds the related media and ctrl vocab)
            tier.set_parent(self._transcription)

        self._checksize()

    # ----------------------------------------------------------------------

    def Delete(self):
        """Delete the selected tier.

            Dialog with the user to confirm.

        """
        sel_list = self._check_selected_tier(multiple=True)

        # Get Indexes of tiers to remove
        indexes = list()
        while sel_list != -1:
            indexes.append(sel_list)
            sel_list = self.tier_list.GetNextSelected(sel_list)

        # how many tiers to delete???
        d = 0
        for sel_list in indexes:
            tier = self._transcription[sel_list]
            if tier not in self._protected:
                d += 1
        if d == 0:
            message = 'None of the selected tiers can be deleted.' \
                      ''.format(d, self._filename)
            ShowInformation(self, self._prefs, message, style=wx.ICON_INFORMATION)
            return

        # Ask the user to confirm before deleting
        delete = 0
        message = 'Are you sure you want to definitively delete:\n' \
                  '{:d} tiers in {:s}?'.format(d, self._filename)
        dlg = ShowYesNoQuestion(self, self._prefs, message)
        if dlg == wx.ID_YES:
            for sel_list in reversed(sorted(indexes)):

                tier = self._transcription[sel_list]
                if tier in self._protected:
                    logging.info('Attempted to delete the protected tier {:s}'
                                 ''.format(tier.get_name()))
                else:

                    # Delete tier of the transcription
                    self._transcription.pop(sel_list)
                    # Delete tier of the list
                    self.tier_list.DeleteItem(sel_list)
                    delete = delete + 1
                    # Update tier numbers of next items in the list.
                    for i in range(sel_list, self.tier_list.GetItemCount()):
                        self.tier_list.SetStringItem(i, 0, " -- {:d} --".format(i+1))

        self._dirty = True
        self._box_title.SetForegroundColour(FG_FILE_DIRTY_COLOUR)
        self.Refresh()

        self._checksize()
        return delete

    # ----------------------------------------------------------------------

    def Duplicate(self):
        """Duplicate the selected tier."""

        sel_list = self._check_selected_tier()
        if sel_list == -1:
            return

        tier = self._transcription[sel_list]
        
        new_tier = tier.copy()
        new_tier.gen_id()
        new_tier.set_meta("tier_was_duplicated_from_id", tier.get_meta('id'))
        new_tier.set_meta("tier_was_duplicated_from_name", tier.get_name())

        self.AddTier(new_tier)

    # ----------------------------------------------------------------------

    def MoveUp(self):
        """Move up the selected tier (except for the first one)."""

        sel_list = self._check_selected_tier()

        # Impossible to move up the first tier.
        if sel_list <= 0:
            return

        #
        tier = self._transcription[sel_list]
        if tier in self._protected:
            ShowInformation(self,
                            self._prefs,
                            "Attempt to move a protected tier: forbidden!",
                            style=wx.ICON_INFORMATION)
            return

        # move up into the transcription
        self._transcription.set_tier_index_id(tier.get_id(), sel_list-1)

        # Delete old tier of the list
        self.tier_list.DeleteItem(sel_list)
        # Add moved tier to the list
        self.AddTierProperties(tier)
        # Update tier number
        self.tier_list.SetStringItem(sel_list, 0, " -- {:d} --".format(sel_list+1))

        # Let the item selected
        self.tier_list.Select(sel_list-1, on=True)
        self._dirty = True
        self._box_title.SetForegroundColour(FG_FILE_DIRTY_COLOUR)
        self.Refresh()

    # ----------------------------------------------------------------------

    def MoveDown(self):
        """Move down the selected tier (except for the last one)."""

        sel_list = self._check_selected_tier()
        if sel_list == -1:
            return

        #
        tier = self._transcription[sel_list]
        if tier in self._protected:
            ShowInformation(self,
                            self._prefs,
                            "Attempting to move a protected tier: forbidden!",
                            style=wx.ICON_INFORMATION)
            return

        # Impossible to move down the last tier.
        if (sel_list+1) == self.tier_list.GetItemCount():
            return

        # move down into the transcription
        self._transcription.set_tier_index_id(tier.get_id(), sel_list+1)

        # Delete old tier of the list
        self.tier_list.DeleteItem(sel_list)
        # Add moved tier to the list
        self.AddTierProperties(tier)
        # Update tier number
        self.tier_list.SetStringItem(sel_list, 0, " -- {:d} --".format(sel_list+1))

        # Let the item selected
        self.tier_list.Select(sel_list+1, on=True)
        self._dirty = True
        self._box_title.SetForegroundColour(FG_FILE_DIRTY_COLOUR)
        self.Refresh()

    # ----------------------------------------------------------------------

    def Radius(self):
        """Fix a new radius value to all TimePoint instances of the selected tier."""

        if len(self._transcription) == 0:
            return

        # Get the selected tier in the list
        sel_list = self.tier_list.GetFirstSelected()
        if sel_list == -1:
            return

        #
        tier = self._transcription[sel_list]
        if tier in self._protected:
            ShowInformation(self,
                            self._prefs,
                            "Attempt to modify a protected tier: forbidden!",
                            style=wx.ICON_INFORMATION)
            return

        # Open a dialog to ask the new radius value
        radius = 0.005
        dlg = RadiusChooser(self, self._prefs, radius)
        if dlg.ShowModal() == wx.ID_OK:
            # Get the value
            r = dlg.GetValue()
            try:
                r = float(r)
                if r > 1.0 or r < 0.:
                    raise ValueError('Radius must range 0-1.')
            except Exception as e:
                ShowInformation(self,
                                self._prefs,
                                "Error: {:s}".format(str(e)),
                                style=wx.ICON_ERROR)
                return

            # Set the value
            while sel_list != -1:
                tier.set_radius(r)
                sel_list = self.tier_list.GetNextSelected(sel_list)

        dlg.Destroy()

    # ----------------------------------------------------------------------

    def Preview(self):
        """Open a grid frame with the selected tier content."""

        sel_list = self._check_selected_tier()
        if sel_list == -1: return

        tier = self._transcription[sel_list]
        dlg = PreviewTierDialog(self, self._prefs, tiers=[tier])
        dlg.Show()

    # ----------------------------------------------------------------------

    def AddTier(self, new_tier):
        """Append a tier into the transcription and add in the list."""
        
        # Append tier to the transcription
        self._transcription.append(new_tier)

        # Append tier into the list
        self.AddTierProperties(new_tier)

        # Display information
        self._dirty = True
        self._box_title.SetForegroundColour(FG_FILE_DIRTY_COLOUR)
        self.Refresh()

    # ----------------------------------------------------------------------

    def LoadFile(self, filename):
        """Load a file in memory and show it.

        :param filename: an annotated file.

        """
        self._filename = filename
        if os.path.exists(filename) is False:
            self._transcription = sppasTranscription("Empty")
            return
        try:
            parser = sppasRW(filename)
            self._transcription = parser.read()
            self._dirty = False
            self._box_title.SetForegroundColour(FG_FILE_COLOUR)
            self.Refresh()
        except Exception as e:
            logging.info('Error loading file {:s}: {:s}'.format(filename, str(e)))
            self._transcription = sppasTranscription("IO-Error")
            #raise

    # ----------------------------------------------------------------------

    def Save(self):
        """Save the current page content."""

        if self._dirty is False:
            return

        try:
            parser = sppasRW(self._filename)
            parser.write(self._transcription)
            self._dirty = False
            self._box_title.SetForegroundColour(FG_FILE_COLOUR)
            self.Refresh()
        except Exception as e:
            # give information
            ShowInformation(self,
                            self._prefs,
                            'File not saved due to the following error: {:s}'.format(e),
                            style=wx.ICON_ERROR)

    # ----------------------------------------------------------------------

    def SaveAs(self, filename):
        """Save the current page content with another file name.
        
        Keep everything un-changed in self.
        
        """
        try:
            parser = sppasRW(filename)
            parser.write(self._transcription)
        except Exception as e:
            # give information
            ShowInformation(self,
                            self._prefs,
                            'File not saved due to the following error: {:s}'.format(e),
                            style=wx.ICON_ERROR)

    # ----------------------------------------------------------------------

    def GetTranscription(self):
        """Return the Transcription."""

        return self._transcription

    # ----------------------------------------------------------------------

    def GetTranscriptionName(self):
        """Return the name of the transcription."""

        return self._transcription.get_name()

    # ----------------------------------------------------------------------
    # Private
    # ----------------------------------------------------------------------

    def _check_selected_tier(self, multiple=False):
        if len(self._transcription) == 0:
            return -1

        # Too many selected items
        if multiple is False and self.tier_list.GetSelectedItemCount() > 1:
            ShowInformation(self,
                            self._prefs,
                            "Only one tier must be checked",
                            style=wx.ICON_INFORMATION)
            return -1

        # Get the selected tier in the list
        return self.tier_list.GetFirstSelected()

    # ----------------------------------------------------------------------

    def _checksize(self):
        """Check the transcription size.
        
        Append an "empty line" if
        transcription is empty. Remove this empty line if transcription
        is not empty. Return True if something has changed.

        """
        # Append an "empty" line in the ListCtrl
        if len(self._transcription) == 0 and self.tier_list.GetItemCount() == 0:
            self.tier_list.InsertStringItem(0, " ... ")
            
            if self._transcription.get_name() == "IO-Error":
                self.tier_list.SetStringItem(0, 1, " Error while reading this file ")
            else:
                self.tier_list.SetStringItem(0, 1, " Empty file: no tiers ")
            for i in range(2, 5):
                self.tier_list.SetStringItem(0, i, " ")
            return True

        # Remove the "empty" line of the ListCtrl
        if len(self._transcription) < self.tier_list.GetItemCount():
            self.tier_list.DeleteItem(self.tier_list.GetItemCount()-1)
            return True

        return False
