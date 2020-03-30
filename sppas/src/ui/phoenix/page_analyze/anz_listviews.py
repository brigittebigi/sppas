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
import mimetypes

from sppas import paths
import sppas.src.audiodata.aio
import sppas.src.anndata.aio
from sppas.src.config import msg
from sppas.src.utils import u

from ..windows import sppasToolbar
from ..windows import sppasPanel
from ..windows.dialogs import sppasProgressDialog
from ..windows.dialogs import sppasChoiceDialog
from ..windows.dialogs import sppasTextEntryDialog
from ..windows.dialogs import Confirm
from ..dialogs import TiersView
from ..dialogs import StatsView
from ..dialogs import sppasTiersSingleFilterDialog
from ..dialogs import sppasTiersRelationFilterDialog

from .anz_baseviews import BaseViewFilesPanel
from .listview import AudioListViewPanel
from .listview import TrsListViewPanel
TIER_BG_COLOUR = wx.Colour(180, 230, 250, 128)

# ----------------------------------------------------------------------------


def _(message):
    return u(msg(message, "ui"))


MSG_CONFIRM = u(msg("Confirm?"))
MSG_TIERS = u(msg("Tiers: "))
MSG_ANNS = u(msg("Annotations: "))
TIER_MSG_ASK_NAME = u(msg("New name of the checked tiers: "))
TIER_MSG_ASK_REGEXP = u(msg("Check tiers with name matching: "))
TIER_MSG_ASK_RADIUS = u(msg("Radius value of the checked tiers: "))
TIER_ACT_CHECK = u(msg("Check"))
TIER_ACT_UNCHECK = u(msg("Uncheck"))
TIER_ACT_RENAME = u(msg("Rename"))
TIER_ACT_DELETE = u(msg("Delete"))
TIER_ACT_CUT = u(msg("Cut"))
TIER_ACT_COPY = u(msg("Copy"))
TIER_ACT_PASTE = u(msg("Paste"))
TIER_ACT_DUPLICATE = u(msg("Duplicate"))
TIER_ACT_MOVE_UP = u(msg("Move Up"))
TIER_ACT_MOVE_DOWN = u(msg("Move Down"))
TIER_ACT_RADIUS = u(msg("Radius"))
TIER_ACT_ANN_VIEW = u(msg("View"))
TIER_ACT_STAT_VIEW = u(msg("Statistics"))
TIER_ACT_SINGLE_FILTER = u(msg("Single Filter"))
TIER_ACT_RELATION_FILTER = u(msg("Relation Filter"))
TIER_MSG_CONFIRM_DEL = \
    u(msg("Are you sure to delete {:d} tiers of {:d} files? "
          "The process is irreversible."))
TIER_REL_WITH = u(msg("Name of the tier to be in relation with: "))

# ----------------------------------------------------------------------------


class ListViewType(object):
    """Enum of all types of supported data by the ListView.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2020 Brigitte Bigi

    :Example:

        >>>with ListViewType() as tt:
        >>>    print(tt.transcription)

    This class is a solution to mimic an 'Enum' but is compatible with both
    Python 2.7 and Python 3+.

    """

    def __init__(self):
        """Create the dictionary."""
        self.__dict__ = dict(
            unknown=-1,
            unsupported=0,
            audio=1,
            transcription=3
        )

    # -----------------------------------------------------------------------

    def __enter__(self):
        return self

    # -----------------------------------------------------------------------

    def __exit__(self, exc_type, exc_value, traceback):
        pass

    # -----------------------------------------------------------------------

    def GuessType(self, filename):
        """Return the expected type of the given filename.

        :return: (MediaType) Integer value of the type

        """
        mime_type = "unknown"
        if filename is not None:
            m = mimetypes.guess_type(filename)
            if m[0] is not None:
                mime_type = m[0]

        if "video" in mime_type:
            return self.unsupported

        fn, fe = os.path.splitext(filename)
        if "audio" in mime_type:
            if fe.lower() in sppas.src.audiodata.aio.extensions:
                return self.audio
            return self.unsupported

        if fe.lower() in sppas.src.anndata.aio.extensions:
            return self.transcription

        return self.unknown

# ----------------------------------------------------------------------------


class ListViewFilesPanel(BaseViewFilesPanel):
    """Panel to display the list of opened files and their content.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      contact@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2020  Brigitte Bigi

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
        # set to toolbar
        btn = self.FindWindow("subtoolbar1").get_button("tier_paste")
        btn.SetFocusColour(color)
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
        return True

    # -----------------------------------------------------------------------
    # Manage the files
    # -----------------------------------------------------------------------

    def _show_file(self, name):
        """Create a ViewPanel to display a file.

        :param name: (str) Name of the file to view
        :return: wx.Window

        """
        if name is None:
            # In case we created a new file, it'll be a transcription!
            panel = TrsListViewPanel(self.GetScrolledPanel(), filename=None)
            panel.SetHighLightColor(self._hicolor)
        else:
            with ListViewType() as tt:
                if tt.GuessType(name) == tt.audio:
                    panel = AudioListViewPanel(self.GetScrolledPanel(), filename=name)
                elif tt.GuessType(name) == tt.transcription:
                    panel = TrsListViewPanel(self.GetScrolledPanel(), filename=name)
                    panel.SetHighLightColor(self._hicolor)
                elif tt.GuessType(name) == tt.unsupported:
                    raise IOError("File format not supported.")
                elif tt.GuessType(name) == tt.unknown:
                    raise TypeError("Unknown file format.")

        border = sppasPanel.fix_size(10)
        self.GetScrolledSizer().Add(panel, 0, wx.EXPAND | wx.LEFT | wx.TOP | wx.BOTTOM, border)
        self.Bind(wx.EVT_COLLAPSIBLEPANE_CHANGED, self.OnCollapseChanged, panel)

        return panel

    # -----------------------------------------------------------------------

    def _create_toolbar(self):
        """Create the main toolbar.

        :return: (sppasPanel, wx.Panel, sppasToolbar, ...)

        """
        panel = sppasPanel(self, name="toolbar_views")
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self._create_toolbar_tiers(panel), 0, wx.ALIGN_LEFT | wx.EXPAND, 0)
        sizer.Add(self._create_toolbar_anns(panel), 0, wx.ALIGN_LEFT | wx.EXPAND, 0)
        panel.SetSizerAndFit(sizer)
        return panel

    # -----------------------------------------------------------------------

    def _create_toolbar_tiers(self, parent):
        """Create a toolbar for actions on tiers. """
        toolbar = sppasToolbar(parent, name="subtoolbar1")
        toolbar.SetMinSize(wx.Size(toolbar.get_height()*5, -1))

        # focus color of buttons performing an action on tiers
        toolbar.set_focus_color(TIER_BG_COLOUR)
        toolbar.AddTitleText(MSG_TIERS, TIER_BG_COLOUR)

        b = toolbar.AddButton("tier_check", TIER_ACT_CHECK)
        b.LabelPosition = wx.BOTTOM
        b.Spacing = 1

        b = toolbar.AddButton("tier_uncheck", TIER_ACT_UNCHECK)
        b.LabelPosition = wx.BOTTOM
        b.Spacing = 1

        b = toolbar.AddButton("tier_rename", TIER_ACT_RENAME)
        b.LabelPosition = wx.BOTTOM
        b.Spacing = 1

        b = toolbar.AddButton("tier_delete", TIER_ACT_DELETE)
        b.LabelPosition = wx.BOTTOM
        b.Spacing = 1

        b = toolbar.AddButton("tier_cut", TIER_ACT_CUT)
        b.LabelPosition = wx.BOTTOM
        b.Spacing = 1

        b = toolbar.AddButton("tier_copy", TIER_ACT_COPY)
        b.LabelPosition = wx.BOTTOM
        b.Spacing = 1

        b = toolbar.AddButton("tier_paste", TIER_ACT_PASTE)
        b.FocusColour = self._hicolor
        b.LabelPosition = wx.BOTTOM
        b.Spacing = 1

        b = toolbar.AddButton("tier_duplicate", TIER_ACT_DUPLICATE)
        b.LabelPosition = wx.BOTTOM
        b.Spacing = 1

        b = toolbar.AddButton("tier_moveup", TIER_ACT_MOVE_UP)
        b.LabelPosition = wx.BOTTOM
        b.Spacing = 1

        b = toolbar.AddButton("tier_movedown", TIER_ACT_MOVE_DOWN)
        b.LabelPosition = wx.BOTTOM
        b.Spacing = 1

        toolbar.Bind(wx.EVT_BUTTON, self._process_toolbar_event)
        return toolbar

    # -----------------------------------------------------------------------

    def _create_toolbar_anns(self, parent):
        """Create a toolbar for actions on annotations of tiers. """
        toolbar = sppasToolbar(parent, name="subtoolbar2")
        toolbar.SetMinSize(wx.Size(toolbar.get_height() * 5, -1))

        # focus color of buttons performing an action on tiers
        toolbar.set_focus_color(wx.Colour(255, 230, 180, 128))
        toolbar.AddTitleText(MSG_ANNS, wx.Colour(255, 230, 180, 128))

        b = toolbar.AddButton("tier_radius", TIER_ACT_RADIUS)
        b.LabelPosition = wx.BOTTOM
        b.Spacing = 1

        b = toolbar.AddButton("tier_ann_view", TIER_ACT_ANN_VIEW)
        b.LabelPosition = wx.BOTTOM
        b.Spacing = 1

        b = toolbar.AddButton("tier_stat_view", TIER_ACT_STAT_VIEW)
        b.LabelPosition = wx.BOTTOM
        b.Spacing = 1

        b = toolbar.AddButton("tier_filter_single", TIER_ACT_SINGLE_FILTER)
        b.LabelPosition = wx.BOTTOM
        b.Spacing = 1

        b = toolbar.AddButton("tier_filter_relation", TIER_ACT_RELATION_FILTER)
        b.LabelPosition = wx.BOTTOM
        b.Spacing = 1

        toolbar.AddSpacer(5)

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

        if btn_name == "tier_check":
            self.check_tiers()
        elif btn_name == "tier_uncheck":
            self.uncheck_tiers()
        elif btn_name == "tier_rename":
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
        elif btn_name == "tier_stat_view":
            self.view_stats_tiers()
        elif btn_name == "tier_ann_view":
            self.view_anns_tiers()
        elif btn_name == "tier_filter_single":
            self.single_filter_tiers()
        elif btn_name == "tier_filter_relation":
            self.relation_filter_tiers()

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

    def check_tiers(self):
        """Ask for a name and check tiers."""
        dlg = sppasTextEntryDialog(
            self, TIER_MSG_ASK_REGEXP, caption=TIER_ACT_CHECK, value="")
        if dlg.ShowModal() == wx.ID_CANCEL:
            wx.LogMessage("Check: cancelled.")
            return
        tier_name = dlg.GetValue()
        dlg.Destroy()

        for filename in self._files:
            panel = self._files[filename]
            if isinstance(panel, TrsListViewPanel):
                try:
                    panel.check_tier(tier_name)
                except Exception as e:
                    wx.LogError("Match pattern error: {:s}".format(str(e)))
                    return

    # -----------------------------------------------------------------------

    def uncheck_tiers(self):
        """Uncheck tiers."""
        for filename in self._files:
            panel = self._files[filename]
            if isinstance(panel, TrsListViewPanel):
                panel.uncheck_tier()

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

    # -----------------------------------------------------------------------

    def view_anns_tiers(self):
        """Open a dialog to view the content of the checked tiers."""
        nbf, nbt = self.__get_checked_nb()
        if nbt == 0:
            wx.LogWarning("View anns: no tier checked.")
            return

        tiers = list()
        for filename in self._files:
            panel = self._files[filename]
            if isinstance(panel, TrsListViewPanel):
                tiers.extend(panel.get_checked_tier())

        TiersView(self, tiers)

    # -----------------------------------------------------------------------

    def view_stats_tiers(self):
        """Open a dialog to view stats of annotations of the checked tiers."""
        nbf, nbt = self.__get_checked_nb()
        if nbt == 0:
            wx.LogWarning("View stats: no tier checked.")
            return

        tiers = dict()
        for filename in self._files:
            panel = self._files[filename]
            if isinstance(panel, TrsListViewPanel):
                checked = panel.get_checked_tier()
                if len(checked) > 0:
                    tiers[filename] = checked

        StatsView(self, tiers)

    # -----------------------------------------------------------------------

    def single_filter_tiers(self):
        """Open a dialog to define filters and apply on the checked tiers."""
        nbf, nbt = self.__get_checked_nb()
        if nbt == 0:
            wx.LogWarning("Single filter: no tier checked.")
            return

        filters = list()
        dlg = sppasTiersSingleFilterDialog(self)
        if dlg.ShowModal() in (wx.ID_OK, wx.ID_APPLY):
            filters = dlg.get_filters()
            tiername = dlg.get_tiername()
            annot_format = dlg.get_annot_format()
            match_all = dlg.match_all
        dlg.Destroy()

        filtered = 0
        if len(filters) > 0:
            total = len(self._files)
            progress = sppasProgressDialog()
            progress.set_new()
            progress.set_header("Single filter processing...")
            progress.set_fraction(0)
            wx.BeginBusyCursor()
            for i, filename in enumerate(self._files):
                panel = self._files[filename]
                progress.set_text(filename)
                if isinstance(panel, TrsListViewPanel):
                    filtered += panel.single_filter(filters, match_all, annot_format, tiername)
                progress.set_fraction(int(100. * float((i+1)) / float(total)))

            wx.EndBusyCursor()
            progress.set_fraction(100)
            progress.close()

        if filtered > 0:
            wx.LogMessage("{:d} tiers created.".format(filtered))
            self.Layout()

    # -----------------------------------------------------------------------

    def relation_filter_tiers(self):
        """Open a dialog to define filters and apply on the checked tiers."""
        # Get the list of checked tiers and the list of tier names
        tiers = list()
        all_tiernames = list()
        for filename in self._files:
            panel = self._files[filename]
            if isinstance(panel, TrsListViewPanel):
                panel_tiers = panel.get_checked_tier()
                if len(panel_tiers) > 0:
                    tiers.extend(panel_tiers)
                    all_tiernames.extend(panel.get_tiernames())

        if len(tiers) == 0:
            wx.LogWarning("Relation filter: no tier checked.")
            return

        # Create the list of names of tiers
        y_tiername = None
        tiernames = sorted(list(set(all_tiernames)))
        dialog = sppasChoiceDialog(TIER_REL_WITH, title="Tier Name Choice", choices=tiernames)
        if dialog.ShowModal() == wx.ID_OK:
            y_tiername = dialog.GetStringSelection()
        dialog.Destroy()
        if y_tiername is None:
            return

        # Get the list of relations and their options
        filters = list()
        dlg = sppasTiersRelationFilterDialog(self)
        if dlg.ShowModal() in (wx.ID_OK, wx.ID_APPLY):
            filters = dlg.get_filters()
            out_tiername = dlg.get_tiername()
            annot_format = dlg.get_annot_format()
        dlg.Destroy()

        # Apply the filters on the checked tiers
        filtered = 0
        if len(filters) > 0:
            total = len(self._files)
            progress = sppasProgressDialog()
            progress.set_new()
            progress.set_header("Relation filter processing...")
            progress.set_fraction(0)
            wx.BeginBusyCursor()
            for i, filename in enumerate(self._files):
                panel = self._files[filename]
                progress.set_text(filename)
                if isinstance(panel, TrsListViewPanel):
                    filtered += panel.relation_filter(
                        filters, y_tiername, annot_format, out_tiername)
                progress.set_fraction(int(100. * float((i+1)) / float(total)))

            wx.EndBusyCursor()
            progress.set_fraction(100)
            progress.close()

        if filtered > 0:
            wx.LogMessage("{:d} tiers created.".format(filtered))
            self.Layout()

# ----------------------------------------------------------------------------
# Panel tested by test_glob.py
# ----------------------------------------------------------------------------


class TestPanel(ListViewFilesPanel):
    TEST_FILES = (
        os.path.join(paths.samples, "COPYRIGHT.txt"),
        os.path.join(paths.samples, "annotation-results", "samples-fra", "F_F_B003-P8-palign.wav"),
        os.path.join(paths.samples, "annotation-results", "samples-fra", "F_F_B003-P8-palign.xra"),
        os.path.join(paths.samples, "samples-fra", "F_F_B003-P8.wav")
    )

    def __init__(self, parent):
        super(TestPanel, self).__init__(
            parent,
            name="TestPanel-anz_baseviews",
            files=TestPanel.TEST_FILES)
        self.create_file(os.path.join(paths.samples, "F_F_B003-P8.xxx"))

