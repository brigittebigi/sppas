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

    ui.phoenix.page_analyze.analyze.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""

import os
import wx

from sppas.src.config import msg
from sppas.src.config import paths
from sppas.src.exceptions import sppasTypeError
from sppas.src.utils import u
from sppas.src.wkps import sppasWorkspace, States
from sppas.src.anndata import sppasRW, FileFormatProperty

from ..windows import sppasPanel
from ..windows import sppasToolbar
from ..windows import sppasStaticLine
from ..windows.dialogs import Confirm, Error
from ..windows.dialogs import sppasFileDialog
from ..windows.dialogs import sppasProgressDialog
from ..windows.dialogs import sppasTextEntryDialog
from ..windows.dialogs import sppasFloatEntryDialog

from ..main_events import DataChangedEvent, EVT_DATA_CHANGED
from ..main_events import EVT_VIEW

from .fileslistview import ListViewFilesPanel

# ---------------------------------------------------------------------------
# List of displayed messages:


def _(message):
    return u(msg(message, "ui"))


MSG_FILES = _("Files: ")
MSG_OPEN = _("Open files")
MSG_CREATE = _("New file")
MSG_SAVE = _("Save all")
MSG_CLOSE = _("Close all")

CLOSE_CONFIRM = _("At least a file contains not saved work that will be "
                  "lost. Are you sure you want to close?")
SAVE_ERROR = _(
    "Files can't be saved due to the following error: {:s}\n")

MSG_CONFIRM = _("Confirm?")
MSG_TIERS = _("Tiers: ")
MSG_ANNS = _("Annotations: ")
TIER_MSG_ASK_NAME = _("New name of the checked tiers: ")
TIER_MSG_ASK_REGEXP = _("Check tiers with name matching: ")
TIER_MSG_ASK_RADIUS = _("Radius value of the checked tiers: ")
TIER_ACT_METADATA = _("Metadata")
TIER_ACT_CHECK = _("Check")
TIER_ACT_UNCHECK = _("Uncheck")
TIER_ACT_RENAME = _("Rename")
TIER_ACT_DELETE = _("Delete")
TIER_ACT_CUT = _("Cut")
TIER_ACT_COPY = _("Copy")
TIER_ACT_PASTE = _("Paste")
TIER_ACT_DUPLICATE = _("Duplicate")
TIER_ACT_MOVE_UP = _("Move Up")
TIER_ACT_MOVE_DOWN = _("Move Down")
TIER_ACT_RADIUS = _("Radius")
TIER_ACT_ANN_VIEW = _("View")
TIER_ACT_STAT_VIEW = _("Statistics")
TIER_ACT_SINGLE_FILTER = _("Single Filter")
TIER_ACT_RELATION_FILTER = _("Relation Filter")
TIER_MSG_CONFIRM_DEL = \
    _("Are you sure to delete {:d} tiers of {:d} files? "
      "The process is irreversible.")

# ---------------------------------------------------------------------------


class sppasAnalyzePanel(sppasPanel):
    """Create a panel to analyze the selected files.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2020  Brigitte Bigi

    """

    FILES_COLOUR = wx.Colour(228, 128, 128, 196)
    ANN_COLOUR = wx.Colour(200, 180, 120, 196)
    TIER_COLOUR = wx.Colour(160, 220, 240, 196)

    # ------------------------------------------------------------------------

    def __init__(self, parent):
        super(sppasAnalyzePanel, self).__init__(
            parent=parent,
            name="page_analyze",
            style=wx.BORDER_NONE
        )

        # The data we are working on
        self.__data = sppasWorkspace()

        # Construct the GUI
        self._create_content()
        self._setup_events()

        # Look&feel
        try:
            self.SetBackgroundColour(wx.GetApp().settings.bg_color)
            self.SetForegroundColour(wx.GetApp().settings.fg_color)
            self.SetFont(wx.GetApp().settings.text_font)
        except AttributeError:
            self.InheritAttributes()

        self.Layout()

    # ------------------------------------------------------------------------
    # Public methods to access the data
    # ------------------------------------------------------------------------

    def get_data(self):
        """Return the data currently displayed in the list of files.

        :returns: (sppasWorkspace) data of the files-viewer model.

        """
        return self.__data

    # ------------------------------------------------------------------------

    def set_data(self, data):
        """Assign new data to this page.

        :param data: (sppasWorkspace)

        """
        if isinstance(data, sppasWorkspace) is False:
            raise sppasTypeError("sppasWorkspace", type(data))
        self.__data = data

    # -----------------------------------------------------------------------
    # Colours & Fonts
    # -----------------------------------------------------------------------

    def SetFont(self, font):
        """Override. """
        wx.Panel.SetFont(self, font)
        for c in self.GetChildren():
            if c.GetName().endswith("toolbar") is False:
                c.SetFont(font)
            else:
                # a smaller font for the toolbar(s)
                f = wx.Font(int(font.GetPointSize() * 0.75),
                            wx.FONTFAMILY_SWISS,   # family,
                            wx.FONTSTYLE_NORMAL,   # style,
                            wx.FONTWEIGHT_BOLD,    # weight,
                            underline=False,
                            faceName=font.GetFaceName(),
                            encoding=wx.FONTENCODING_SYSTEM)
                c.SetFont(f)

        self.Layout()

    # -----------------------------------------------------------------------

    def SetForegroundColour(self, colour):
        """Override. """
        wx.Panel.SetForegroundColour(self, colour)
        for c in self.GetChildren():
            if c.GetName() != "hline":
                c.SetForegroundColour(colour)

    # -----------------------------------------------------------------------

    def open_checked_files(self):
        """Add the checked files and display their content.

        Lock the files that are successfully opened and notify parent.

        """
        # Add checked files to the page
        checked = self.__data.get_filename_from_state(States().CHECKED)
        success = 0
        total = len(checked)
        progress = sppasProgressDialog()
        progress.set_new()
        progress.set_header(MSG_OPEN + "...")
        progress.set_fraction(0)
        wx.BeginBusyCursor()
        for i, fn in enumerate(sorted(checked)):
            try:
                fraction = float((i+1)) / float(total)
                message = os.path.basename(fn.get_id())
                progress.update(fraction, message)
                self._viewpanel.append_file(fn.get_id())
                self.__data.set_object_state(States().LOCKED, fn)
                success += 1
            except Exception as e:
                wx.LogError(str(e))
        wx.EndBusyCursor()
        progress.set_fraction(1)
        progress.close()

        # send data to the parent
        if success > 0:
            self._viewpanel.Layout()
            self._viewpanel.Refresh()
            wx.LogMessage("{:d} files opened.".format(success))
            self.notify()
        self.Layout()
        self.Refresh()

    # ------------------------------------------------------------------------

    def create_file(self):
        """Create a new empty transcription file."""
        dlg = sppasFileDialog(self,
                              title="Path and name of a new file",
                              style=wx.FC_SAVE | wx.FC_NOSHOWHIDDEN)
        dlg.SetDirectory(paths.samples)
        wildcard = list()
        extensions = list()
        for e in sppasRW.extensions():
            f = FileFormatProperty(e)
            if f.get_writer() is True:
                wildcard.append(f.get_software() + " files (" + e + ")|*." + e)
                extensions.append(e)
        dlg.SetWildcard("|".join(wildcard))

        if dlg.ShowModal() == wx.ID_OK:
            filename = dlg.GetPath()
            fn, fe = os.path.splitext(filename)
            if len(fn) > 0:
                if len(fe) == 0:
                    filename += "." + extensions[dlg.GetFilterIndex()]

                if os.path.exists(filename) is True:
                    Error("Filename {:s} is already existing.".format(filename))
                else:
                    try:
                        self._viewpanel.create_file(filename)
                        #self._viewpanel.Layout()
                        #self._viewpanel.Refresh()
                    except Exception as e:
                        Error(str(e))
        dlg.Destroy()

    # ------------------------------------------------------------------------

    def save_files(self):
        """Save the files on disk."""
        saved = 0
        for filename in self._viewpanel.get_files():
            s = self._viewpanel.save_file(filename)
            if s is True:
                saved += 1

        if saved > 0:
            wx.LogMessage("{:d} files saved.".format(saved))

    # ------------------------------------------------------------------------

    def close_files(self):
        """Close the opened files.

        Unlock the closed files and notify parent.

        """
        if self._viewpanel.is_modified() is True:
            wx.LogWarning("At least one file contains not saved changes.")
            # Ask the user to confirm to close (and changes are lost)
            response = Confirm(CLOSE_CONFIRM, MSG_CLOSE)
            if response == wx.ID_CANCEL:
                return

        closed = list()
        for filename in self._viewpanel.get_files():
            removed = self._viewpanel.remove_file(filename, force=True)
            if removed is True:
                closed.append(filename)
                fn = self.__data.get_object(filename)
                self.__data.set_object_state(States().CHECKED, fn)

        if len(closed) > 0:
            wx.LogMessage("{:d} files closed.".format(len(closed)))
            self._viewpanel.Layout()
            self.Refresh()
            self.notify()

    # ------------------------------------------------------------------------
    # Private methods to construct the panel.
    # ------------------------------------------------------------------------

    def _create_content(self):
        """Create the main content."""
        # the view must be created before the toolbar
        content_panel = ListViewFilesPanel(self, name="listview_files_panel")

        # The toolbar of the Analyze page and the main sizer
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        main_sizer.Add(self._create_toolbar_one(), 0, wx.EXPAND, 0)
        main_sizer.Add(self._create_toolbar_two(), 0, wx.EXPAND, 0)
        main_sizer.Add(self._create_hline(), 0, wx.EXPAND)
        main_sizer.Add(content_panel, 1, wx.EXPAND | wx.BOTTOM, sppasPanel.fix_size(10))
        self.SetSizer(main_sizer)

    # -----------------------------------------------------------------------

    @property
    def _viewpanel(self):
        return self.FindWindow("listview_files_panel")

    # -----------------------------------------------------------------------

    def _create_hline(self):
        """Create an horizontal line, used to separate the toolbar."""
        line = sppasStaticLine(self, orient=wx.LI_HORIZONTAL, name="hline")
        line.SetMinSize(wx.Size(-1, 20))
        line.SetPenStyle(wx.PENSTYLE_SHORT_DASH)
        line.SetDepth(1)
        line.SetForegroundColour(self.ANN_COLOUR)
        return line

    # -----------------------------------------------------------------------

    def _create_toolbar_one(self):
        """Create the main toolbar.

        :return: (sppasToolbar)

        """
        tb = sppasToolbar(self, name="files_anns_toolbar")
        # tb.set_height(40)
        tb.set_focus_color(sppasAnalyzePanel.FILES_COLOUR)
        tb.AddTitleText(MSG_FILES, self.FILES_COLOUR, name="files")
        
        tb.AddButton("open", MSG_OPEN)
        tb.AddButton("create", MSG_CREATE)
        tb.AddButton("save_all", MSG_SAVE)
        tb.AddButton("close", MSG_CLOSE)
        tb.AddSpacer(1)

        tb.AddTitleText(MSG_ANNS, sppasAnalyzePanel.ANN_COLOUR)

        b = tb.AddButton("tier_radius", TIER_ACT_RADIUS)
        b.SetLabelPosition(wx.BOTTOM)
        b.SetSpacing(1)
        b.SetFocusColour(sppasAnalyzePanel.ANN_COLOUR)

        b = tb.AddButton("tier_ann_view", TIER_ACT_ANN_VIEW)
        b.SetLabelPosition(wx.BOTTOM)
        b.SetSpacing(1)
        b.SetFocusColour(sppasAnalyzePanel.ANN_COLOUR)

        b = tb.AddButton("tier_stat_view", TIER_ACT_STAT_VIEW)
        b.SetLabelPosition(wx.BOTTOM)
        b.SetSpacing(1)
        b.SetFocusColour(sppasAnalyzePanel.ANN_COLOUR)

        b = tb.AddButton("tier_filter_single", TIER_ACT_SINGLE_FILTER)
        b.SetLabelPosition(wx.BOTTOM)
        b.SetSpacing(1)
        b.SetFocusColour(sppasAnalyzePanel.ANN_COLOUR)

        b = tb.AddButton("tier_filter_relation", TIER_ACT_RELATION_FILTER)
        b.SetLabelPosition(wx.BOTTOM)
        b.SetSpacing(1)
        b.SetFocusColour(sppasAnalyzePanel.ANN_COLOUR)

        return tb

    # -----------------------------------------------------------------------

    def _create_toolbar_two(self):
        """Create a toolbar for actions on tiers. """
        tb = sppasToolbar(self, name="tiers_toolbar")
        # tb.set_height(40)
        tb.set_focus_color(sppasAnalyzePanel.TIER_COLOUR)
        tb.AddTitleText(MSG_TIERS, sppasAnalyzePanel.TIER_COLOUR)

        b = tb.AddButton("tags", TIER_ACT_METADATA)
        b.SetLabelPosition(wx.BOTTOM)
        b.SetSpacing(1)

        b = tb.AddButton("tier_check", TIER_ACT_CHECK)
        b.SetLabelPosition(wx.BOTTOM)
        b.SetSpacing(1)

        b = tb.AddButton("tier_uncheck", TIER_ACT_UNCHECK)
        b.SetLabelPosition(wx.BOTTOM)
        b.SetSpacing(1)

        b = tb.AddButton("tier_rename", TIER_ACT_RENAME)
        b.SetLabelPosition(wx.BOTTOM)
        b.SetSpacing(1)

        b = tb.AddButton("tier_delete", TIER_ACT_DELETE)
        b.SetLabelPosition(wx.BOTTOM)
        b.SetSpacing(1)

        b = tb.AddButton("tier_cut", TIER_ACT_CUT)
        b.SetLabelPosition(wx.BOTTOM)
        b.SetSpacing(1)

        b = tb.AddButton("tier_copy", TIER_ACT_COPY)
        b.SetLabelPosition(wx.BOTTOM)
        b.SetSpacing(1)

        b = tb.AddButton("tier_paste", TIER_ACT_PASTE)
        b.SetLabelPosition(wx.BOTTOM)
        b.SetSpacing(1)
        b.SetFocusColour(self._viewpanel.GetHighLightColor())

        b = tb.AddButton("tier_duplicate", TIER_ACT_DUPLICATE)
        b.SetLabelPosition(wx.BOTTOM)
        b.SetSpacing(1)

        b = tb.AddButton("tier_moveup", TIER_ACT_MOVE_UP)
        b.SetLabelPosition(wx.BOTTOM)
        b.SetSpacing(1)

        b = tb.AddButton("tier_movedown", TIER_ACT_MOVE_DOWN)
        b.SetLabelPosition(wx.BOTTOM)
        b.SetSpacing(1)

        return tb

    # -----------------------------------------------------------------------

    def _process_toolbar_event(self, event):
        """Process a button of the toolbar event.

        :param event: (wx.Event)

        """
        wx.LogDebug("Toolbar Event received by {:s}".format(self.GetName()))
        btn = event.GetEventObject()
        btn_name = btn.GetName()

        if btn_name == "open":
            self.open_checked_files()

        elif btn_name == "create":
            self.create_file()

        elif btn_name == "save_all":
            self.save_files()

        elif btn_name == "close":
            self.close_files()

        elif btn_name == "tags":
            self._viewpanel.metadata_tiers()
            
        elif btn_name == "tier_check":
            # Ask for a name and check tiers.
            dlg = sppasTextEntryDialog(
                TIER_MSG_ASK_REGEXP, caption=TIER_ACT_CHECK, value="")
            if dlg.ShowModal() == wx.ID_CANCEL:
                wx.LogMessage("Check: cancelled.")
                return
            tier_name = dlg.GetValue()
            dlg.Destroy()
            self._viewpanel.check_tiers(tier_name)
        
        elif btn_name == "tier_uncheck":
            self._viewpanel.uncheck_tiers()
        
        elif btn_name == "tier_rename":
            # Ask for a new name and set it to the checked tiers.
            nbf, nbt = self._viewpanel.get_checked_nb()
            if nbt == 0:
                wx.LogWarning("Rename: no tier checked.")
                return
            dlg = sppasTextEntryDialog(
                TIER_MSG_ASK_NAME, caption=TIER_ACT_RENAME, value="")
            if dlg.ShowModal() == wx.ID_CANCEL:
                wx.LogMessage("Rename: cancelled.")
                return
            tier_name = dlg.GetValue()
            dlg.Destroy()
            self._viewpanel.rename_tiers(tier_name)
        
        elif btn_name == "tier_delete":
            # Ask confirmation then delete the checked tiers.
            nbf, nbt = self._viewpanel.get_checked_nb()
            if nbt == 0:
                wx.LogWarning("Delete: no tier checked.")
                return
            if nbt > 0:
                # User must confirm to really delete
                response = Confirm(TIER_MSG_CONFIRM_DEL.format(nbt, nbf), MSG_CONFIRM)
                if response == wx.ID_CANCEL:
                    return
            self._viewpanel.delete_tiers()
        
        elif btn_name == "tier_cut":
            nbf, nbt = self._viewpanel.get_checked_nb()
            if nbt == 0:
                wx.LogWarning("Cut: no tier checked.")
                return
            self._viewpanel.cut_tiers()
        
        elif btn_name == "tier_copy":
            nbf, nbt = self._viewpanel.get_checked_nb()
            if nbt == 0:
                wx.LogWarning("Copy: no tier checked.")
                return
            self._viewpanel.copy_tiers()
        
        elif btn_name == "tier_paste":
            self._viewpanel.paste_tiers()
        
        elif btn_name == "tier_duplicate":
            nbf, nbt = self._viewpanel.get_checked_nb()
            if nbt == 0:
                wx.LogWarning("Duplicate: no tier checked.")
                return
            self._viewpanel.duplicate_tiers()
        
        elif btn_name == "tier_moveup":
            nbf, nbt = self._viewpanel.get_checked_nb()
            if nbt == 0:
                wx.LogWarning("Move: no tier checked.")
                return
            self._viewpanel.move_tiers(up=True)
        
        elif btn_name == "tier_movedown":
            nbf, nbt = self._viewpanel.get_checked_nb()
            if nbt == 0:
                wx.LogWarning("Move: no tier checked.")
                return
            self._viewpanel.move_tiers(up=False)
        
        elif btn_name == "tier_radius":
            nbf, nbt = self._viewpanel.get_checked_nb()
            if nbt == 0:
                wx.LogWarning("Radius: no tier checked.")
                return
            dlg = sppasFloatEntryDialog(
                TIER_MSG_ASK_RADIUS, caption=TIER_ACT_RADIUS,
                value=0.01, min_value=0., max_value=0.2)
            if dlg.ShowModal() == wx.ID_CANCEL:
                wx.LogMessage("Radius: cancelled.")
                return
            radius = dlg.GetValue()
            dlg.Destroy()
            self._viewpanel.radius_tiers(radius)
        
        elif btn_name == "tier_stat_view":
            nbf, nbt = self._viewpanel.get_checked_nb()
            if nbt == 0:
                wx.LogWarning("View stats: no tier checked.")
                return
            self._viewpanel.view_stats_tiers()
        
        elif btn_name == "tier_ann_view":
            nbf, nbt = self._viewpanel.get_checked_nb()
            if nbt == 0:
                wx.LogWarning("View anns: no tier checked.")
                return
            self._viewpanel.view_anns_tiers()
        
        elif btn_name == "tier_filter_single":
            nbf, nbt = self._viewpanel.get_checked_nb()
            if nbt == 0:
                wx.LogWarning("Single filter: no tier checked.")
                return
            self._viewpanel.single_filter_tiers()
        
        elif btn_name == "tier_filter_relation":
            self._viewpanel.relation_filter_tiers()
            
        else:
            event.Skip()

    # -----------------------------------------------------------------------
    # Events management
    # -----------------------------------------------------------------------

    def notify(self):
        """The parent has to be informed of a change of content."""
        evt = DataChangedEvent(data=self.__data)
        evt.SetEventObject(self)
        wx.PostEvent(self.GetParent(), evt)

    # -----------------------------------------------------------------------

    def _setup_events(self):
        """Associate a handler function with the events.

        It means that when an event occurs then the process handler function
        will be called.

        """
        # Capture keys
        self.Bind(wx.EVT_CHAR_HOOK, self._process_key_event)

        # The data have changed.
        # This event is sent by the tabs manager or by the parent
        self.Bind(EVT_DATA_CHANGED, self._process_data_changed)

        # The buttons in this page
        self.Bind(wx.EVT_BUTTON, self._process_toolbar_event)
        self.Bind(wx.EVT_TOGGLEBUTTON, self._process_toolbar_event)

        # The view performed an action.
        self.Bind(EVT_VIEW, self._process_view_event)

    # -----------------------------------------------------------------------

    def _process_key_event(self, event):
        """Process a key event.

        :param event: (wx.Event)

        """
        key_code = event.GetKeyCode()

        if event.AltDown() is True:
            if key_code == 77:  # alt+n Create a new files
                self.create_file()
            elif key_code == 78:  # alt+o Open the checked files
                self.open_checked_files()
            elif key_code == 83:  # alt+s Save the files
                self.save_files()
            elif key_code == 87:  # alt+w Close the files
                self.close_files()

        event.Skip()

    # -----------------------------------------------------------------------

    def _process_data_changed(self, event):
        """Process a change of data.

        Set the data of the event to the other anz_panels.

        :param event: (wx.Event)

        """
        emitted = event.GetEventObject()
        try:
            data = event.data
        except AttributeError:
            wx.LogError('Data were not sent in the event emitted by {:s}'
                        '.'.format(emitted.GetName()))
            return
        self.__data = data

    # -----------------------------------------------------------------------

    def _process_view_event(self, event):
        """Process a view event: an action has to be performed.

        :param event: (wx.Event)

        """
        try:
            action = event.action
            filename = event.filename
        except Exception as e:
            wx.LogError(str(e))
            return

        if action == "close":
            # Unlock the closed file
            fns = [self.__data.get_object(filename)]
            try:
                self.__data.unlock(fns)
                self.notify()
            except Exception as e:
                wx.LogError(str(e))
                return False

        elif action == "saved":
            # A file was saved by the panel. Perhaps it was newly created.
            fn = self.__data.get_object(filename)
            if fn is None:
                added = self.__data.add_file(filename)
                if len(added) > 0:
                    self.__data.set_object_state(States().LOCKED, added[0])
                    self.notify()

    # -----------------------------------------------------------------------

    def get_checked_filenames(self):
        """Return the list of checked filenames in data."""
        # Get the list of checked FileName() instances
        checked = self.__data.get_filename_from_state(States().CHECKED)
        if len(checked) == 0:
            return list()

        # Convert the list of FileName() instances into a list of filenames
        return [f.get_id() for f in checked]

# ----------------------------------------------------------------------------
# Panel for tests
# ----------------------------------------------------------------------------


class TestPanel(sppasAnalyzePanel):

    def __init__(self, parent):
        super(TestPanel, self).__init__(parent)
        f1 = os.path.join(paths.samples, "annotation-results", "samples-fra",
                          "F_F_B003-P8-palign.xra")
        f2 = os.path.join(paths.samples, "annotation-results", "samples-fra",
                          "F_F_B003-P9-palign.xra")
        f3 = os.path.join(paths.samples, "samples-fra", "F_F_B003-P8.wav")

        data = sppasWorkspace()
        fn1 = data.add_file(f1)
        data.set_object_state(States().CHECKED, fn1[0])
        fn2 = data.add_file(f2)
        data.set_object_state(States().CHECKED, fn2[0])
        fn3 = data.add_file(f3)
        data.set_object_state(States().CHECKED, fn3[0])
        self.set_data(data)
        self.open_checked_files()

