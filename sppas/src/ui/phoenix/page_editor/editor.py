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

    ui.phoenix.page_editor.editor.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""

import os
import wx

from sppas.src.config import msg
from sppas.src.config import paths
from sppas.src.utils import u
from sppas.src.exceptions import sppasTypeError
from sppas.src.wkps import sppasWorkspace, States

from ..windows import sppasPanel
from ..windows import sppasToolbar
from ..windows import sppasStaticLine
from ..windows.dialogs import Confirm, Error, Information
from ..windows.dialogs import sppasProgressDialog

from ..main_events import DataChangedEvent, EVT_DATA_CHANGED

from .editorpanel import EditorPanel
from .timeline import EVT_TIMELINE_VIEW  # to close or save a file


# ---------------------------------------------------------------------------
# List of displayed messages:


def _(message):
    return u(msg(message, "ui"))


MSG_FILES = _("Files: ")
MSG_OPEN = _("Open files")
MSG_SAVE = _("Save all")
MSG_CLOSE = _("Close all")

CLOSE_CONFIRM = _("At least a file contains not saved work that will be "
                  "lost. Are you sure you want to close?")
CLOSE_FILE_CONFIRM = _("The file contains not saved work that will be lost."
                       "Close anyway?")
MSG_ANNS = _("Annotations: ")
MSG_MEDIA = _("Media: ")

METADATA = _("Edit metadata of the annotation")
RESTORE = _("Restore the label of the annotation")
DELETE = _("Delete the annotation")
MERGE_PREVIOUS = _("Merge with the previous annotation")
MERGE_NEXT = _("Merge with the next annotation")
SPLIT_ONE = _("Split annotation into 2 and put content to the first")
SPLIT_TWO = _("Split annotation into 2 and put content to the second")
ADD_BEFORE = _("Add an annotation in the hole before")
ADD_AFTER = _("Add an annotation in the hole after")
LABEL_TEXT = _("Edit label in TEXT mode")
LABEL_XML = _("Edit label in XML mode")
LABEL_JSON = _("Edit label in JSON mode")

# ---------------------------------------------------------------------------


class sppasEditorPanel(sppasPanel):
    """Create a panel to view&edit the selected files.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2020  Brigitte Bigi

    """

    FILES_COLOUR = wx.Colour(228, 128, 128, 196)
    ANN_COLOUR = wx.Colour(200, 180, 120, 128)

    # ------------------------------------------------------------------------

    def __init__(self, parent):
        super(sppasEditorPanel, self).__init__(
            parent=parent,
            name="page_editor",
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

    def get_checked_filenames(self):
        """Return the list of checked filenames in data."""
        # Get the list of checked FileName() instances
        checked = self.__data.get_filename_from_state(States().CHECKED)
        if len(checked) == 0:
            return list()

        # Convert the list of FileName() instances into a list of filenames
        return [f.get_id() for f in checked]

    # -----------------------------------------------------------------------
    # Colours & Fonts
    # -----------------------------------------------------------------------

    def SetFont(self, font):
        """Override. """
        wx.Panel.SetFont(self, font)
        for c in self.GetChildren():
            if "toolbar" not in c.GetName():
                c.SetFont(font)
            else:
                # a smaller font for the toolbar
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
            if "line" not in c.GetName():
                c.SetForegroundColour(colour)

    # -----------------------------------------------------------------------
    # Manage the files
    # -----------------------------------------------------------------------

    def open_checked_files(self):
        """Add the checked files and display their content.

        Lock the files that are successfully opened and notify parent.

        """
        Information("This Editor is still under development. It can be used without any warranty.")
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
                self._editpanel.append_file(fn.get_id())
                self.__data.set_object_state(States().LOCKED, fn)
                success += 1
            except Exception as e:
                wx.LogError(str(e))
        wx.EndBusyCursor()
        progress.set_fraction(1)
        progress.close()

        # send data to the parent
        if success > 0:
            self._editpanel.Layout()
            self._editpanel.Refresh()
            self.notify()

    # ------------------------------------------------------------------------

    def save_files(self):
        """Save the files on disk."""
        saved = list()
        for filename in self._editpanel.get_files():
            s = self._editpanel.save_file(filename)
            if s is True:
                saved.append(filename)

        if len(saved) > 0:
            wx.LogMessage("{:d} files saved.".format(saved))

        return saved

    # ------------------------------------------------------------------------

    def close_files(self):
        """Close the opened files.

        Unlock the closed files and notify parent.

        """
        if self._editpanel.is_modified() is True:
            wx.LogWarning("At least one file contains not saved changes.")
            # Ask the user to confirm to close (and changes are lost)
            response = Confirm(CLOSE_CONFIRM, MSG_CLOSE)
            if response == wx.ID_CANCEL:
                return

        closed = list()
        for filename in self._editpanel.get_files():
            is_closed = self.__remove_file(filename)
            if is_closed is True:
                closed.append(is_closed)

        if len(closed) > 0:
            wx.LogMessage("{:d} files closed.".format(len(closed)))
            self.notify()

        return closed

    # ------------------------------------------------------------------------

    def __remove_file(self, filename):
        """Close and unlock the file in the data BUT do not notify parent.

        """
        removed = self._editpanel.remove_file(filename, force=True)
        if removed is True:
            fns = [self.__data.get_object(filename)]
            # Unlock the closed file
            try:
                self.__data.unlock(fns)
                wx.LogDebug("File {:s} successfully closed and unlocked.".format(filename))
            except Exception as e:
                self._editpanel.append_file(filename)
                wx.LogError(str(e))
                return False

        return removed

    # ------------------------------------------------------------------------

    def close_file(self, filename):
        """Close and unlock the file in the data BUT do not notify parent.

        """
        if self._editpanel.is_modified(filename) is True:
            wx.LogWarning("The file contains not saved changes.")
            # Ask the user to confirm to close (and changes are lost)
            response = Confirm(CLOSE_FILE_CONFIRM, MSG_CLOSE)
            if response == wx.ID_CANCEL:
                return

        removed = self._editpanel.remove_file(filename, force=True)
        if removed is True:
            fns = [self.__data.get_object(filename)]
            # Unlock the closed file
            try:
                self.__data.unlock(fns)
                wx.LogDebug("File {:s} successfully closed and unlocked.".format(filename))
            except Exception as e:
                self._editpanel.append_file(filename)
                wx.LogError(str(e))
                return False

            self.notify()

    # ------------------------------------------------------------------------
    # Private methods to construct the panel.
    # ------------------------------------------------------------------------

    def _create_content(self):
        """Create the main content."""
        # The view of the Editor page
        main_panel = EditorPanel(self, name="editor_panel")

        # The toolbar & the main sizer
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        main_sizer.Add(self._create_toolbar_one(), 0, wx.EXPAND | wx.BOTTOM, 6)
        main_sizer.Add(self._create_toolbar_two(), 0, wx.EXPAND, 0)
        main_sizer.Add(self._create_hline(), 0, wx.EXPAND, 0)
        main_sizer.Add(main_panel, 1, wx.EXPAND, 0)
        self.SetSizer(main_sizer)

    # -----------------------------------------------------------------------

    @property
    def _editpanel(self):
        return self.FindWindow("editor_panel")

    # -----------------------------------------------------------------------

    def _create_toolbar_one(self):
        """Create the main toolbar.

        :return: (sppasToolbar)

        """
        tb = sppasToolbar(self, name="files_toolbar")
        tb.set_height(24)   # default is 32
        tb.set_focus_color(sppasEditorPanel.FILES_COLOUR)
        tb.AddTitleText(MSG_FILES, self.FILES_COLOUR, name="files")

        tb.AddButton("open", MSG_OPEN)
        tb.AddButton("save_all", MSG_SAVE)
        tb.AddButton("close", MSG_CLOSE)

        bd1 = tb.AddButton("way_up_down")
        bd1.SetFocusColour(wx.Colour(self.GetForegroundColour()))
        bd2 = tb.AddButton("way_left_right")
        bd2.SetFocusColour(wx.Colour(self.GetForegroundColour()))

        return tb

    # -----------------------------------------------------------------------

    def _create_toolbar_two(self):
        """Create a toolbar for actions on annotations. """
        tb = sppasToolbar(self, name="anns_toolbar")
        tb.set_height(24)   # default is 32
        tb.set_focus_color(sppasEditorPanel.ANN_COLOUR)

        tb.AddTitleText(MSG_ANNS, sppasEditorPanel.ANN_COLOUR)

        bcs = tb.AddToggleButton("code_review", value=True, group_name="view_mode")
        bcs.SetToolTip(LABEL_TEXT)
        bcx = tb.AddToggleButton("code_xml", group_name="view_mode")
        bcx.SetToolTip(LABEL_XML)
        bcj = tb.AddToggleButton("code_json", group_name="view_mode")
        bcj.SetToolTip(LABEL_JSON)
        br = tb.AddButton("restore")
        br.SetToolTip(RESTORE)

        meta = tb.AddButton("tags")
        meta.SetToolTip(METADATA)

        bd = tb.AddButton("cell_delete")
        bd.SetToolTip(DELETE)
        bmp = tb.AddButton("cell_merge_previous")
        bmp.SetToolTip(MERGE_PREVIOUS)
        bmn = tb.AddButton("cell_merge_next")
        bmn.SetToolTip(MERGE_NEXT)
        bsp = tb.AddButton("cell_split")
        bsp.SetToolTip(SPLIT_ONE)
        bsn = tb.AddButton("cell_split_next")
        bsn.SetToolTip(SPLIT_TWO)
        bab = tb.AddButton("cell_add_before")
        bab.SetToolTip(ADD_BEFORE)
        baa = tb.AddButton("cell_add_after")
        baa.SetToolTip(ADD_AFTER)

        return tb

    # -----------------------------------------------------------------------

    def _create_hline(self):
        """Create an horizontal line, used to separate the panels."""
        line = sppasStaticLine(self, orient=wx.LI_HORIZONTAL, name="hline")
        line.SetMinSize(wx.Size(-1, sppasPanel.fix_size(8)))
        line.SetPenStyle(wx.PENSTYLE_SHORT_DASH)
        line.SetDepth(1)
        line.SetForegroundColour(self.FILES_COLOUR)
        return line

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

        # The buttons of the toolbars
        self.Bind(wx.EVT_BUTTON, self._process_toolbar_event)
        self.Bind(wx.EVT_TOGGLEBUTTON, self._process_toolbar_event)

        # The event emitted by the Timeline view
        self.Bind(EVT_TIMELINE_VIEW, self._process_time_action)
        # The event emitted by the List view
        # self.Bind(EVT_LISTANNS_VIEW, self._process_list_action)

    # -----------------------------------------------------------------------

    def _process_data_changed(self, event):
        """Process a change of data.

        Set the data of the event to the other panels.

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

    def _process_toolbar_event(self, event):
        """Process a button event of one of the toolbars.

        :param event: (wx.Event)

        """
        btn = event.GetEventObject()
        btn_name = btn.GetName()

        if btn_name == "open":
            self.open_checked_files()

        elif btn_name == "save_all":
            self.save_files()

        elif btn_name == "close":
            self.close_files()

        elif btn_name == "way_up_down":
            self._editpanel.swap_panels()

        elif btn_name == "way_left_right":
            self._editpanel.swap_annlist_panels()

        elif btn_name in ("code_review", "code_xml", "code_json"):
            self._editpanel.switch_ann_view(btn_name)

        elif btn_name == "restore":
            self._editpanel.restore_ann()

        elif btn_name.startswith("cell_"):
            # The action to perform is the name of the button, without "cell_"
            self.__anns_action(what=btn_name[5:])

        elif btn_name == "tags":
            self.__anns_action(what="edit_metadata")

        else:
            event.Skip()

    # -----------------------------------------------------------------------

    def _process_time_action(self, event):
        """Process an action event from the time-line view.

        :param event: (wx.Event)

        """
        filename = event.filename
        action = event.action
        value = event.value
        wx.LogDebug("{:s} received an event action {:s} of file {:s} with value {:s}"
                    "".format(self.GetName(), action, filename, str(value)))
        event.Skip()

        if action == "close":
            self.close_file(filename)

        else:
            event.Skip()

    # -----------------------------------------------------------------------

    def _process_key_event(self, event):
        """Process a key event.

        :param event: (wx.Event)

        """
        key_code = event.GetKeyCode()

        if event.AltDown() is True:
            if key_code == 78:  # alt+o Open the checked files
                self.open_checked_files()
            elif key_code == 83:  # alt+s Save the files
                self.save_files()
            elif key_code == 87:  # alt+w Close the files
                self.close_files()

        event.Skip()

    # -----------------------------------------------------------------------

    def __anns_action(self, what=""):
        try:
            self._editpanel.ann_action_requested(what)
        except Exception as e:
            Error(str(e))

# ----------------------------------------------------------------------------
# Panel for tests
# ----------------------------------------------------------------------------


class TestPanel(sppasPanel):

    def __init__(self, parent):
        super(TestPanel, self).__init__(parent, name="Editor Page")
        f1 = os.path.join(paths.samples, "annotation-results", "samples-fra", "F_F_B003-P8-palign.xra")
        f2 = os.path.join(paths.samples, "annotation-results", "samples-fra",  "F_F_B003-P9-palign.xra")
        f3 = os.path.join(paths.samples, "samples-fra", "F_F_B003-P8.wav")

        data = sppasWorkspace()
        fn1 = data.add_file(f1)
        data.set_object_state(States().CHECKED, fn1[0])
        fn2 = data.add_file(f2)
        data.set_object_state(States().CHECKED, fn2[0])
        fn3 = data.add_file(f3)
        data.set_object_state(States().CHECKED, fn3[0])

        panel = sppasEditorPanel(self)
        panel.set_data(data)
        panel.open_checked_files()

        s = wx.BoxSizer()
        s.Add(panel, 1, wx.EXPAND, 0)
        self.SetSizer(s)
