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

    ui.phoenix.page_analyze.anz_listviews.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""

import os
import wx

from sppas import paths

from ..windows import sppasToolbar
from ..dialogs import sppasTextEntryDialog
from ..dialogs import Confirm

from .anz_baseviews import BaseViewFilesPanel
from .listview import TrsListViewPanel

# ----------------------------------------------------------------------------

MSG_CONFIRM = "Confirm?"
TIER_MSG_ASK_NAME = "New name of the checked tiers: "
TIER_MSG_ASK_RADIUS = "Radius value of the checked tiers: "
TIER_ACT_RENAME = "Rename"
TIER_ACT_RADIUS = "Radius"
TIER_MSG_CONFIRM_DEL = "Are you sure to delete {:d} tiers of {:d} files? " \
                       "The process is irreversible."

# ----------------------------------------------------------------------------


class ListViewFilesPanel(BaseViewFilesPanel):
    """Panel to display the list of opened files and their content.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      contact@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2019  Brigitte Bigi

    """

    def __init__(self, parent, name="listviewfiles", files=tuple()):
        super(ListViewFilesPanel, self).__init__(
            parent,
            name=name,
            files=files)
        self.__clipboard = list()

    # -----------------------------------------------------------------------

    def SetHighLightColor(self, color):
        """Set a color to highlight buttons, and for the focus."""
        self._hicolor = color
        # set to the panels
        for filename in self._files:
            panel = self._files[filename]
            panel.SetHighLightColor(color)

    # -----------------------------------------------------------------------

    def can_edit(self):
        """Return True if this view can edit/save the file content.

        Override base class.

        The methods 'is_modified' and 'save' should be implemented in the
        view panel of each file.

        """
        return False   # True

    # -----------------------------------------------------------------------
    # Manage the files
    # -----------------------------------------------------------------------

    def _show_file(self, name):
        """Create a ViewPanel to display a file.

        :param name: (str) Name of the file to view
        :return: wx.Window

        """
        wx.LogMessage("Displaying file {:s} in ListView mode.".format(name))
        panel = TrsListViewPanel(self.GetScrolledPanel(), filename=name)
        panel.SetHighLightColor(self.GetHighLightColor())
        self.GetScrolledSizer().Add(panel, 0, wx.EXPAND | wx.TOP | wx.BOTTOM, 12)
        self.Bind(wx.EVT_COLLAPSIBLEPANE_CHANGED, self.OnCollapseChanged, panel)

        return panel

    # -----------------------------------------------------------------------

    def _create_toolbar(self):
        """Create the main toolbar.

        :return: (sppasPanel, wx.Panel, sppasToolbar, ...)

        """
        toolbar = sppasToolbar(self, name="toolbar_views")
        # focus color of buttons performing an action on tiers
        toolbar.set_focus_color(wx.Colour(180, 230, 255))

        toolbar.AddButton("tier_rename")
        toolbar.AddButton("tier_delete")
        toolbar.AddButton("tier_cut")
        toolbar.AddButton("tier_copy")

        tp = toolbar.AddButton("tier_paste")
        tp.FocusColour = self._hicolor

        toolbar.AddButton("tier_duplicate")
        toolbar.AddButton("tier_moveup")
        toolbar.AddButton("tier_movedown")
        toolbar.AddButton("tier_radius")
        toolbar.AddButton("tier_view")

        toolbar.Bind(wx.EVT_BUTTON, self._process_toolbar_event)
        return toolbar

    # -----------------------------------------------------------------------

    def _process_toolbar_event(self, event):
        """Process a button of the toolbar event.

        :param event: (wx.Event)

        """
        wx.LogDebug("Toolbar Event received by {:s}".format(self.GetName()))
        btn = event.GetEventObject()
        btn_name = btn.GetName()

        if btn_name == "tier_rename":
            self.rename_tiers()
        elif btn_name == "tier_delete":
            self.delete_tiers()
        elif btn_name == "tier_cut":
            self.cut_tiers()
        elif btn_name == "tier_copy":
            self.copy_tiers()
        elif btn_name == "tier_paste":
            self.paste_tiers()
        elif btn_name == "tier_duplicate":
            self.duplicate_tiers()
        elif btn_name == "tier_moveup":
            self.move_tiers(up=True)
        elif btn_name == "tier_movedown":
            self.move_tiers(up=False)
        elif btn_name == "tier_radius":
            self.radius_tiers()

        else:
            event.Skip()

    # -----------------------------------------------------------------------

    def __get_checked_nb(self):
        """Return the number of checked files and checked tiers."""
        nbf = 0
        nbt = 0
        # How many checked tiers into how many files
        for filename in self._files:
            panel = self._files[filename]
            if isinstance(panel, TrsListViewPanel):
                nb_checks = panel.get_nb_checked_tier()
                if nb_checks > 0:
                    nbf += 1
                    nbt += nb_checks

        return nbf, nbt

    # -----------------------------------------------------------------------

    def rename_tiers(self):
        """Ask for a new name and set it to the checked tiers."""
        nbf, nbt = self.__get_checked_nb()
        if nbt == 0:
            wx.LogWarning("Rename: no tier checked.")
            return

        dlg = sppasTextEntryDialog(
            self, TIER_MSG_ASK_NAME, caption=TIER_ACT_RENAME, value="")
        if dlg.ShowModal() == wx.ID_CANCEL:
            wx.LogMessage("Rename: cancelled.")
            return
        tier_name = dlg.GetValue()
        dlg.Destroy()

        for filename in self._files:
            panel = self._files[filename]
            if isinstance(panel, TrsListViewPanel):
                panel.rename_tier(tier_name)
                # if the panel is not a ListView (an ErrorView for example)
                # the method 'rename_tier' is not defined.

    # -----------------------------------------------------------------------

    def delete_tiers(self):
        """Ask confirmation then delete the checked tiers."""
        nbf, nbt = self.__get_checked_nb()
        if nbt == 0:
            wx.LogWarning("Delete: no tier checked.")
            return

        if nbt > 0:
            # User must confirm to really delete
            response = Confirm(TIER_MSG_CONFIRM_DEL.format(nbt, nbf), MSG_CONFIRM)
            if response == wx.ID_CANCEL:
                return

        for filename in self._files:
            panel = self._files[filename]
            if isinstance(panel, TrsListViewPanel):
                panel.delete_tier()

    # -----------------------------------------------------------------------

    def cut_tiers(self):
        """Move checked tiers to the clipboard."""
        self.__clipboard = list()
        nbf, nbt = self.__get_checked_nb()
        if nbt == 0:
            wx.LogWarning("Cut: no tier checked.")
            return

        cut = 0
        for filename in self._files:
            panel = self._files[filename]
            if isinstance(panel, TrsListViewPanel):
                tiers = panel.cut_tier()
                if len(tiers) > 0:
                    self.__clipboard.extend(tiers)
                    cut += len(tiers)

        if cut > 0:
            wx.LogMessage("{:d} tiers cut.".format(cut))
            self.Layout()

    # -----------------------------------------------------------------------

    def copy_tiers(self):
        """Copy checked tiers to the clipboard."""
        self.__clipboard = list()
        nbf, nbt = self.__get_checked_nb()
        if nbt == 0:
            wx.LogWarning("Copy: no tier checked.")
            return

        for filename in self._files:
            panel = self._files[filename]
            if isinstance(panel, TrsListViewPanel):
                tiers = panel.copy_tier()
                if len(tiers) > 0:
                    self.__clipboard.extend(tiers)

    # -----------------------------------------------------------------------

    def paste_tiers(self):
        """Paste tiers of the clipboard to the panels."""
        paste = 0
        for filename in self._files:
            panel = self._files[filename]
            if isinstance(panel, TrsListViewPanel):
                if panel.is_selected() is True:
                    paste += panel.paste_tier(self.__clipboard)

        if paste > 0:
            wx.LogMessage("{:d} tiers paste.".format(paste))
            self.Layout()

    # -----------------------------------------------------------------------

    def duplicate_tiers(self):
        """Duplicate checked tiers of the panels."""
        nbf, nbt = self.__get_checked_nb()
        if nbt == 0:
            wx.LogWarning("Duplicate: no tier checked.")
            return

        copied = 0
        for filename in self._files:
            panel = self._files[filename]
            if isinstance(panel, TrsListViewPanel):
                copied += panel.duplicate_tier()

        if copied > 0:
            wx.LogMessage("{:d} tiers duplicated.".format(copied))
            self.Layout()

    # -----------------------------------------------------------------------

    def move_tiers(self, up=True):
        """Move up or down checked tiers of the panels."""
        nbf, nbt = self.__get_checked_nb()
        if nbt == 0:
            wx.LogWarning("Move: no tier checked.")
            return

        for filename in self._files:
            panel = self._files[filename]
            if isinstance(panel, TrsListViewPanel):
                if up is True:
                    panel.move_up_tier()
                else:
                    panel.move_down_tier()

    # -----------------------------------------------------------------------

    def radius_tiers(self):
        """Ask for a radius value and set it to checked tiers."""
        nbf, nbt = self.__get_checked_nb()
        if nbt == 0:
            wx.LogWarning("Radius: no tier checked.")
            return

        dlg = sppasTextEntryDialog(
            self, TIER_MSG_ASK_RADIUS, caption=TIER_ACT_RADIUS, value="")
        if dlg.ShowModal() == wx.ID_CANCEL:
            wx.LogMessage("Radius: cancelled.")
            return
        radius_str = dlg.GetValue()
        dlg.Destroy()

        try:
            r = float(radius_str)
            if (r-round(r, 0)) == 0.:
                r = int(r)
            for filename in self._files:
                panel = self._files[filename]
                if isinstance(panel, TrsListViewPanel):
                    panel.radius(r)
        except ValueError:
            wx.LogError("Radius: expected an appropriate number.")


# ----------------------------------------------------------------------------
# Panel tested by test_glob.py
# ----------------------------------------------------------------------------


class TestPanel(ListViewFilesPanel):
    TEST_FILES = (
        os.path.join(paths.samples, "COPYRIGHT.txt"),
        os.path.join(paths.samples, "annotation-results", "samples-fra", "F_F_B003-P8-palign.wav"),
        os.path.join(paths.samples, "annotation-results", "samples-fra",
                     "F_F_B003-P8-palign.xra")
    )

    def __init__(self, parent):
        super(TestPanel, self).__init__(
            parent,
            name="TestPanel-anz_baseviews",
            files=TestPanel.TEST_FILES)
        self.SetBackgroundColour(wx.Colour(128, 128, 128))

