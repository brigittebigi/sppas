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

    ui.phoenix.page_analyze.fileslistview.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""

import os
import wx
import mimetypes

from sppas.src.config import paths
import sppas.src.audiodata.aio
import sppas.src.anndata.aio
from sppas.src.config import msg
from sppas.src.utils import u

from ..windows.panels import sppasPanel
from ..windows.panels import sppasScrolledPanel
from ..windows.dialogs import sppasProgressDialog
from ..windows.dialogs import sppasChoiceDialog
from ..windows.dialogs import Confirm
from ..views import MetaDataEdit
from ..views import TiersView
from ..views import StatsView
from ..main_events import ViewEvent, EVT_VIEW

from .filters.single import sppasTiersSingleFilterDialog
from .filters.relation import sppasTiersRelationFilterDialog
from .errfilelist import ErrorFileSummaryPanel
from .medialist import AudioSummaryPanel

from .datalist.trsrisepanel import TrsSummaryPanel

# ----------------------------------------------------------------------------


def _(message):
    return u(msg(message, "ui"))


MSG_CLOSE = _("Close")

CLOSE_CONFIRM = _("The file contains not saved work that will be "
                  "lost. Are you sure you want to close?")
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


class ListViewFilesPanel(sppasScrolledPanel):
    """Panel to display a list of files and a summary of their content.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      contact@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2020  Brigitte Bigi

    """

    def __init__(self, parent, name="summaryfiles_panel"):
        super(ListViewFilesPanel, self).__init__(
            parent,
            style=wx.BORDER_NONE | wx.ALWAYS_SHOW_SB | wx.VSCROLL,
            name=name)

        # The files of this panel (key=name, value=wx.SizerItem)
        self._files = dict()
        self.__clipboard = list()
        self._hicolor = wx.Colour(200, 200, 180)

        self._create_content()

        # Look&feel
        try:
            wx.Window.SetBackgroundColour(self, wx.GetApp().settings.bg_color)
            self.SetForegroundColour(wx.GetApp().settings.fg_color)
            self.SetFont(wx.GetApp().settings.text_font)
        except AttributeError:
            self.InheritAttributes()

        self.SetupScrolling(scroll_x=False, scroll_y=True)
        self.Bind(EVT_VIEW, self._process_view_event)
        self.Bind(wx.EVT_COLLAPSIBLEPANE_CHANGED, self.OnCollapseChanged)

    # -----------------------------------------------------------------------

    def GetHighLightColor(self):
        """Get the color to highlight buttons."""
        return self._hicolor

    # -----------------------------------------------------------------------

    def SetHighLightColor(self, color):
        """Set a color to highlight buttons, and for the focus."""
        self._hicolor = color
        # set to toolbar
        btn = self.FindWindow("subtoolbar1").get_button("tier_paste")
        btn.SetFocusColour(color)
        # set to the anz_panels
        for filename in self._files:
            panel = self._files[filename]
            panel.SetHighLightColor(color)

    # -----------------------------------------------------------------------

    def SetBackgroundColour(self, colour):
        wx.Window.SetBackgroundColour(self, colour)
        # do not propagate the bg to children

    # -----------------------------------------------------------------------
    # Manage the files
    # -----------------------------------------------------------------------

    def get_files(self):
        """Return the list of filenames this panel is displaying."""
        return list(self._files.keys())

    # -----------------------------------------------------------------------

    def is_modified(self, name=None):
        """Return True if the content of the file has been changed.

        :param name: (str) Name of a file. None for all files.

        """
        if name is not None:
            page = self._files.get(name, None)
            try:
                changed = page.is_modified()
                return changed
            except:
                return False

        # All files
        for name in self._files:
            page = self._files.get(name, None)
            try:
                if page.is_modified() is True:
                    return True
            except:
                pass

        return False

    # -----------------------------------------------------------------------
    # Manage one file at a time
    # -----------------------------------------------------------------------

    def _add_file(self, name):
        """Create a SummaryPanel to display a file.

        :param name: (str) Name of the file to view
        :return: wx.Window

        """
        if name is None:
            # In case we created a new file, it'll be a transcription!
            panel = TrsSummaryPanel(self, filename=None)
            panel.SetHighLightColor(self._hicolor)
        else:
            with ListViewType() as tt:
                if tt.GuessType(name) == tt.audio:
                    panel = AudioSummaryPanel(self, filename=name)

                elif tt.GuessType(name) == tt.transcription:
                    panel = TrsSummaryPanel(self, filename=name)
                    panel.SetHighLightColor(self._hicolor)

                elif tt.GuessType(name) == tt.unsupported:
                    raise IOError("File format not supported.")

                elif tt.GuessType(name) == tt.unknown:
                    raise TypeError("Unknown file format.")

        return panel

    # -----------------------------------------------------------------------

    def get_checked_nb(self):
        """Return the number of checked files and checked tiers."""
        nbf = 0
        nbt = 0
        # How many checked tiers into how many files
        for filename in self._files:
            panel = self._files[filename]
            if isinstance(panel, TrsSummaryPanel):
                nb_checks = panel.get_nb_checked_tier()
                if nb_checks > 0:
                    nbf += 1
                    nbt += nb_checks

        return nbf, nbt

    # -----------------------------------------------------------------------

    def metadata_tiers(self):
        """Edit metadata of selected tiers."""
        tiers = list()
        for filename in self._files:
            panel = self._files[filename]
            if isinstance(panel, TrsSummaryPanel):
                tiers.extend(panel.get_checked_tier())

        MetaDataEdit(self, tiers)

    # -----------------------------------------------------------------------

    def check_tiers(self, tier_name):
        """Check tiers of the given name."""
        for filename in self._files:
            panel = self._files[filename]
            if isinstance(panel, TrsSummaryPanel):
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
            if isinstance(panel, TrsSummaryPanel):
                panel.uncheck_tier()

    # -----------------------------------------------------------------------

    def rename_tiers(self, tier_name):
        """Set the given name to the checked tiers."""
        for filename in self._files:
            panel = self._files[filename]
            if isinstance(panel, TrsSummaryPanel):
                # if the panel is not a ListView (an ErrorView for example)
                # the method 'rename_tier' is not defined.
                panel.rename_tier(tier_name)

    # -----------------------------------------------------------------------

    def delete_tiers(self):
        """Ask confirmation then delete the checked tiers."""
        for filename in self._files:
            panel = self._files[filename]
            if isinstance(panel, TrsSummaryPanel):
                panel.delete_tier()

        # self.Layout()

    # -----------------------------------------------------------------------

    def cut_tiers(self):
        """Move checked tiers to the clipboard."""
        self.__clipboard = list()
        cut = 0
        for filename in self._files:
            panel = self._files[filename]
            if isinstance(panel, TrsSummaryPanel):
                tiers = panel.cut_tier()
                if len(tiers) > 0:
                    self.__clipboard.extend(tiers)
                    cut += len(tiers)

        if cut > 0:
            wx.LogMessage("{:d} tiers cut.".format(cut))
            # self.Layout()

    # -----------------------------------------------------------------------

    def copy_tiers(self):
        """Copy checked tiers to the clipboard."""
        self.__clipboard = list()

        for filename in self._files:
            panel = self._files[filename]
            if isinstance(panel, TrsSummaryPanel):
                tiers = panel.copy_tier()
                if len(tiers) > 0:
                    self.__clipboard.extend(tiers)

    # -----------------------------------------------------------------------

    def paste_tiers(self):
        """Paste tiers of the clipboard to the anz_panels."""
        paste = 0
        for filename in self._files:
            panel = self._files[filename]
            if isinstance(panel, TrsSummaryPanel):
                if panel.is_selected() is True:
                    paste += panel.paste_tier(self.__clipboard)

        if paste > 0:
            wx.LogMessage("{:d} tiers paste.".format(paste))
            self.Layout()

    # -----------------------------------------------------------------------

    def duplicate_tiers(self):
        """Duplicate checked tiers of the anz_panels."""
        copied = 0
        for filename in self._files:
            panel = self._files[filename]
            if isinstance(panel, TrsSummaryPanel):
                copied += panel.duplicate_tier()

        if copied > 0:
            wx.LogMessage("{:d} tiers duplicated.".format(copied))
            self.Layout()

    # -----------------------------------------------------------------------

    def move_tiers(self, up=True):
        """Move up or down checked tiers of the anz_panels."""
        for filename in self._files:
            panel = self._files[filename]
            if isinstance(panel, TrsSummaryPanel):
                if up is True:
                    panel.move_up_tier()
                else:
                    panel.move_down_tier()

    # -----------------------------------------------------------------------

    def radius_tiers(self, radius_str):
        """Ask for a radius value and set it to checked tiers."""
        try:
            r = float(radius_str)
            if (r-round(r, 0)) == 0.:
                r = int(r)
            for filename in self._files:
                panel = self._files[filename]
                if isinstance(panel, TrsSummaryPanel):
                    panel.radius(r)
        except ValueError:
            wx.LogError("Radius: expected an appropriate number.")

    # -----------------------------------------------------------------------

    def view_anns_tiers(self):
        """Open a dialog to view the content of the checked tiers."""
        tiers = list()
        for filename in self._files:
            panel = self._files[filename]
            if isinstance(panel, TrsSummaryPanel):
                tiers.extend(panel.get_checked_tier())

        TiersView(self, tiers)

    # -----------------------------------------------------------------------

    def view_stats_tiers(self):
        """Open a dialog to view stats of annotations of the checked tiers."""
        tiers = dict()
        for filename in self._files:
            panel = self._files[filename]
            if isinstance(panel, TrsSummaryPanel):
                checked = panel.get_checked_tier()
                if len(checked) > 0:
                    tiers[filename] = checked

        StatsView(self, tiers)

    # -----------------------------------------------------------------------

    def single_filter_tiers(self):
        """Open a dialog to define filters and apply on the checked tiers."""
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
                if isinstance(panel, TrsSummaryPanel):
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
            if isinstance(panel, TrsSummaryPanel):
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
            fit_option = dlg.get_fit()
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
                if isinstance(panel, TrsSummaryPanel):
                    filtered += panel.relation_filter(
                        filters, y_tiername, annot_format, fit_option, out_tiername)
                progress.set_fraction(int(100. * float((i+1)) / float(total)))

            wx.EndBusyCursor()
            progress.set_fraction(100)
            progress.close()

        if filtered > 0:
            wx.LogMessage("{:d} tiers created.".format(filtered))
            self.Layout()

    # -----------------------------------------------------------------------
    # Action on a file
    # -----------------------------------------------------------------------

    def create_file(self, name):
        """Add a non-existing file with the given name.

        Do not refresh/layout the GUI.

        """
        if name in self._files:
            wx.LogError('Name {:s} is already in the list of files.')
            raise ValueError('Name {:s} is already in the list of files.')
        if os.path.exists(name) is True:
            wx.LogError('Name {:s} is already an existing file. Not created.')
            raise ValueError("Name {:s} is already existing.".format(name))

        panel = TrsSummaryPanel(self, filename=name)
        panel.SetHighLightColor(self._hicolor)

        self._files[name] = panel

        border = sppasPanel.fix_size(10)
        self.GetSizer().Add(panel, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, border)

    # -----------------------------------------------------------------------

    def append_file(self, name):
        """Add a file and display its content.

        Do not refresh/layout the GUI.

        :param name: (str)
        :raise: ValueError

        """
        if name in self._files:
            wx.LogError('Name {:s} is already in the list of files.')
            raise ValueError('Name {:s} is already in the list of files.')

        try:
            panel = self._add_file(name)
        except Exception as e:
            panel = ErrorFileSummaryPanel(self, name)
            panel.set_error_message(str(e))

        self._files[name] = panel

        border = sppasPanel.fix_size(10)
        self.GetSizer().Add(panel, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, border)

    # -----------------------------------------------------------------------

    def remove_file(self, name, force=False):
        """Remove a panel corresponding to the name of a file.

        Do not refresh/layout the GUI.

        :param name: (str)
        :param force: (bool) Force to remove, even if a file is modified
        :return: (bool) The file was removed or not

        """
        if force is True or self.is_modified(name) is False:

            # Remove of the object
            panel = self._files.get(name, None)
            if panel is None:
                wx.LogError("There's no file with name {:s}".format(name))
                return False

            # Destroy the panel and remove of the sizer
            for i, child in enumerate(self.GetChildren()):
                if child == panel:
                    self.GetSizer().Remove(i)
                    break

            panel.Destroy()

            # Delete of the list
            self._files.pop(name)
            return True

        return False

    # -----------------------------------------------------------------------

    def save_file(self, name):
        """Save a file.

        :param name: (str)
        :return: (bool) The file was saved or not

        """
        panel = self._files.get(name, None)
        saved = False
        if panel.is_modified() is True:
            try:
                saved = panel.save()
                if saved is True:
                    self.notify(action="saved", filename=name)
                    wx.LogMessage("File {:s} saved successfully.".format(name))
            except Exception as e:
                saved = False
                wx.LogError("Error while saving file {:s}: {:s}"
                            "".format(name, str(e)))

        return saved

    # -----------------------------------------------------------------------
    # GUI creation
    # -----------------------------------------------------------------------

    def _create_content(self):
        """Create the main content. """
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(main_sizer)

    # -----------------------------------------------------------------------

    def close_page(self, filename):
        """Close the page matching the given filename.

        :param filename: (str)
        :return: (bool) The page was closed.

        """
        if filename not in self._files:
            return False
        page = self._files[filename]

        if page.is_modified() is True:
            wx.LogWarning("File contains not saved changes.")
            # Ask the user to confirm to close (and changes are lost)
            response = Confirm(CLOSE_CONFIRM, MSG_CLOSE)
            if response == wx.ID_CANCEL:
                return False

        removed = self.remove_file(filename, force=True)
        if removed is True:
            # The parent will unlock the file in the workspace & layout
            self.notify(action="close", filename=filename)
            return True

        # Take care of the new selected file/tier/annotation
        # ?????

        return False

    # -----------------------------------------------------------------------
    # Events management
    # -----------------------------------------------------------------------

    def notify(self, action, filename):
        """Notify the parent of a ViewEvent.

        :param action: (str) the action to perform
        :param filename: (str) name of the file to perform the action

        """
        wx.LogDebug("{:s} notifies its parent {:s} of action {:s} for filename {}."
                    "".format(self.GetName(), self.GetParent().GetName(), action, filename))
        evt = ViewEvent(action=action, filename=filename)
        evt.SetEventObject(self)
        wx.PostEvent(self.GetParent(), evt)

    # -----------------------------------------------------------------------

    def _process_view_event(self, event):
        """Process a view event: an action has to be performed.

        :param event: (wx.Event)

        """
        try:
            panel = event.GetEventObject()
            panel_name = panel.GetName()

            action = event.action
            fn = None
            for filename in self._files:
                p = self._files[filename]
                if p == panel:
                    fn = filename
                    break
            if fn is None:
                raise Exception("Unknown {:s} panel in ViewEvent."
                                "".format(panel_name))
        except Exception as e:
            wx.LogError(str(e))
            return

        if action == "save":
            self.save_file(fn)

        elif action == "close":
            closed = self.close_page(fn)

    # ------------------------------------------------------------------------

    def OnCollapseChanged(self, evt=None):
        """One of the child panel was collapsed/expanded."""
        self.Layout()
        self.SendSizeEventToParent()

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
            name="Test Summary Files Panel")
        for filename in TestPanel.TEST_FILES:
            self.append_file(filename)
        self.Layout()
        self.Refresh()

