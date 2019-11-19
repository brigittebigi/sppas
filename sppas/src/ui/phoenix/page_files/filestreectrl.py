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

    src.ui.phoenix.page_files.filestreectrl.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""

import os
import wx
import wx.lib.newevent

from sppas import paths
from sppas import sppasTypeError
from sppas.src.anndata import sppasRW
from sppas.src.files import States, FileName, FileRoot, FilePath, FileData
from sppas.src.ui import sppasTrash

from ..windows import sppasPanel
from ..windows import sppasScrolledPanel
from ..windows import sppasCollapsiblePanel
from ..windows.image import ColorizeImage
from ..tools import sppasSwissKnife


# ---------------------------------------------------------------------------
# Internal use of an event, when an item is clicked.

ItemClickedEvent, EVT_ITEM_CLICKED = wx.lib.newevent.NewEvent()
ItemClickedCommandEvent, EVT_ITEM_CLICKED_COMMAND = wx.lib.newevent.NewCommandEvent()

# ---------------------------------------------------------------------------


STATES_ICON_NAMES = {
    States().UNUSED: "choice_checkbox",
    States().CHECKED: "choice_checked",
    States().LOCKED: "locked",
    States().AT_LEAST_ONE_CHECKED: "choice_pos",
    States().AT_LEAST_ONE_LOCKED: "choice_neg"
}

# ---------------------------------------------------------------------------


class FileAnnotIcon(object):
    """Represents the link between a file extension and an icon name.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      contact@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2019  Brigitte Bigi

    All supported file formats of 'anndata' are linked to an icon file.
    All 'wav' files are linked to an icon file.

    """

    def __init__(self):
        """Constructor of a FileAnnotIcon.

        Set the name of the icon for all known extensions of annotations.

        Create a dictionary linking a file extension to the name of the
        software it comes from. It is supposed this name is matching an
        an icon in PNG format.

        """
        self.__exticon = dict()
        self.__exticon['.WAV'] = "Audio"
        self.__exticon['.WAVE'] = "Audio"

        for ext in sppasRW.TRANSCRIPTION_TYPES:
            software = sppasRW.TRANSCRIPTION_TYPES[ext]().software
            if ext.startswith(".") is False:
                ext = "." + ext
            self.__exticon[ext.upper()] = software

    # -----------------------------------------------------------------------

    def get_icon_name(self, ext):
        """Return the name of the icon matching the given extension.

        :param ext: (str) An extension of an annotated or an audio file.
        :returns: (str) Name of an icon

        """
        if ext.startswith(".") is False:
            ext = "." + ext
        soft = self.__exticon.get(ext.upper(), "files-file")
        return soft

    # -----------------------------------------------------------------------

    def get_names(self):
        """Return the list of known icon names."""
        names = list()
        for ext in self.__exticon:
            n = self.get_icon_name(ext)
            if n not in names:
                names.append(n)

        return names

# ---------------------------------------------------------------------------


class FileTreeView(sppasScrolledPanel):
    """A control to display data files in a tree-spreadsheet style.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      contact@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2019  Brigitte Bigi

    This class manages a FileData() instance to add/remove/delete files and
    the wx objects to display it.

    """

    def __init__(self, parent, name=wx.PanelNameStr):
        """Constructor of the FileTreeCtrl.

        :param parent: (wx.Window)
        :param name: (str)

        """
        super(FileTreeView, self).__init__(parent, name=name)

        # The workspace to display
        self.__data = FileData()

        # Each FilePath has its own CollapsiblePanel in the sizer
        self.__fps = dict()  # key=fp.id, value=FilePathCollapsiblePanel
        self._create_content()
        self._setup_events()

        # Look&feel
        self.SetBackgroundColour(wx.GetApp().settings.bg_color)
        self.SetForegroundColour(wx.GetApp().settings.fg_color)
        self.SetFont(wx.GetApp().settings.text_font)

    # ------------------------------------------------------------------------
    # Public methods
    # ------------------------------------------------------------------------

    def get_data(self):
        """Return the data."""
        return self.__data

    # ------------------------------------------------------------------------

    def set_data(self, data):
        """Set the data and update the corresponding wx objects."""
        self.__data = data
        self.__update()

    # ------------------------------------------------------------------------

    def AddFiles(self, entries):
        """Add a list of files or folders.

        The given entries must include their absolute path.

        :param entries: (list of str) Filename or folder with absolute path.
        :return: (int) Number of items added in the tree (folders, roots and files)

        """
        modified = 0

        for entry in entries:
            if os.path.isdir(entry):
                m = self.add_folder(entry, add_files=True)
                modified += len(m)

            elif os.path.isfile(entry):
                m = self.add_file(entry)
                modified += len(m)

        if modified > 0:
            self.Layout()
            self.Refresh()

        return modified

    # ------------------------------------------------------------------------

    def RemoveCheckedFiles(self):
        """Remove all checked files."""
        checked = self.__data.get_filename_from_state(States().CHECKED)
        if len(checked) == 0:
            return

        removed = list()
        for fn in checked:
            removed.append(fn.id)

        wx.LogMessage('{:d} files removed.'.format(len(removed)))
        return removed

    # ------------------------------------------------------------------------

    def DeleteCheckedFiles(self):
        """Delete all checked files."""
        removed_filenames = self.RemoveCheckedFiles()

        # move the files into the trash of SPPAS
        for filename in removed_filenames:
            try:
                sppasTrash().put_file_into(filename)
            except Exception as e:
                # Re-Add it into the data and the panels or not?????
                wx.LogError("File {!s:s} can't be deleted due to the "
                            "following error: {:s}.".format(filename, str(e)))

    # ------------------------------------------------------------------------

    def GetCheckedFiles(self):
        """Return the list of checked files.

        :returns: List of FileName

        """
        return self.__data.get_filename_from_state(States().CHECKED)

    # ------------------------------------------------------------------------

    def LockFiles(self, entries):
        """Lock a list of files.

        Entries are a list of filenames with absolute path or FileName
        instances or both.

        :param entries: (list of str/FileName)

        """
        for entry in entries:
            if isinstance(entry, FileName) is False:
                fs = self.__data.get_object(entry)
            else:
                fs = entry
            self.__data.set_object_state(States().LOCKED, fs)
            # Update object in the panel
            panel = self.__get_path_panel(fs)
            if panel is not None:
                panel.change_state(fs.get_id(), fs.get_state())

    # ------------------------------------------------------------------------
    # Manage the data and their panels
    # ------------------------------------------------------------------------

    def add_folder(self, foldername, add_files=True):
        """Add a folder and its files into to the data and display it.

        Do not layout/refresh the panel.

        :param foldername: (str) Absolute path
        :param add_files: (bool) Add also the files of this folder
        :return: list of added items

        """
        wx.LogDebug('Add folder: {:s}'.format(str(foldername)))
        added = list()

        # Get or create the FilePath of the foldername
        try:
            fp = FilePath(foldername)
        except Exception as e:
            wx.LogError("{:s}".format(str(e)))
            return added

        fpx = self.__data.get_object(fp.id)
        if fpx is None:
            self.__data.add(fp)
            self.__add_folder_panel(fp)
            added.append(foldername)

        if add_files is True:
            # add all files of this folder into the FilePath and the panel
            for f in sorted(os.listdir(foldername)):
                fullname = os.path.join(foldername, f)
                if os.path.isfile(fullname):
                    m = self.add_file(fullname)
                    if len(m) > 0:
                        added.extend(m)

        return added

    # ------------------------------------------------------------------------

    def add_file(self, filename):
        """Add a file to the data and into a path-root panel.

        Do not layout/refresh the panel.

        :param filename: (str) Absolute name of a file
        :return: (bool)

        """
        wx.LogDebug('Add file: {:s}'.format(str(filename)))
        added = list()

        # get the FilePath of this filename
        fpx = FilePath(os.path.dirname(filename))
        fp = self.__data.get_object(fpx.get_id())
        if fp is None:
            added = self.add_folder(fpx.get_id(), add_files=False)
            if len(added) == 0:
                wx.LogError("Folder not added: {:s}".format(fpx.get_id()))
                return added
        fp = self.__data.get_object(fpx.get_id())

        # get the panel of this fp
        p = self.__fps[fp.get_id()]

        # add the entry into the data
        added_fs = self.__data.add_file(filename, brothers=False, ctime=0.)
        if len(added_fs) == 0:
            wx.LogWarning("File not added: {:s}".format(filename))
            return added

        # add the entries into the panels
        for fs in added_fs:
            if isinstance(fs, FileName):
                wx.LogDebug("Added file to the data {:s}".format(fs.get_id()))
                fr = self.__data.get_object(FileRoot.root(fs.get_id()))
                p.add_file(fr, fs)
                added.append(fs)

        return added

    # ------------------------------------------------------------------------

    def __add_folder_panel(self, fp):
        """Create a child panel to display the content of a FilePath.

        :param fp: (FilePath)
        :return: FilePathCollapsiblePanel

        """
        p = FilePathCollapsiblePanel(self, fp)
        p.SetFocus()
        self.ScrollChildIntoView(p)
        self.Bind(wx.EVT_COLLAPSIBLEPANE_CHANGED, self.OnCollapseChanged, p)
        p.GetPane().Bind(EVT_ITEM_CLICKED, self._process_item_clicked)

        self.GetSizer().Add(p, 0, wx.EXPAND | wx.ALL, border=8)
        self.__fps[fp.get_id()] = p
        return p

    # ------------------------------------------------------------------------

    def __update(self):
        """Update the currently displayed wx objects to match the data."""
        pass

    # ------------------------------------------------------------------------

    def _create_content(self):
        sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(sizer)
        self.Layout()
        self.SetupScrolling(scroll_x=True, scroll_y=True)
        self.SetAutoLayout(True)

    # -----------------------------------------------------------------------
    # Events management
    # -----------------------------------------------------------------------

    def _setup_events(self):
        """Associate a handler function with the events.

        It means that when an event occurs then the process handler function
        will be called.

        """
        self.Bind(wx.EVT_SIZE, self.OnSize)

        # The user pressed a key of its keyboard
        # self.Bind(wx.EVT_KEY_DOWN, self._process_key_event)

        # The user clicked an item
        self.Bind(EVT_ITEM_CLICKED, self._process_item_clicked)

    # ------------------------------------------------------------------------

    def _process_item_clicked(self, event):
        """Process an action event: an item was clicked.

        The sender of the event is either a Path or a Root Collapsible Panel.

        :param event: (wx.Event)

        """
        # the object is a FileBase (path, root or file)
        object_id = event.id
        filebase = self.__data.get_object(object_id)
        wx.LogDebug("Process ItemClicked {:s}".format(object_id))

        # change state of the item
        current_state = filebase.get_state()
        new_state = States().UNUSED
        if current_state == States().UNUSED:
            new_state = States().CHECKED
        modified = self.__data.set_object_state(new_state, filebase)

        # update the corresponding panel(s)
        for fs in modified:
            wx.LogDebug("Modified: {:s}".format(fs.id))
            panel = self.__get_path_panel(fs)
            if panel is not None:
                panel.change_state(fs.get_id(), fs.get_state())

    # ------------------------------------------------------------------------

    def __get_path_panel(self, fs):
        """Return the collapsible panel of the given FileXXXX."""
        if isinstance(fs, FilePath):
            fp = fs
        elif isinstance(fs, FileRoot):
            fp = self.__data.get_parent(fs)
        elif isinstance(fs, FileName):
            fr = self.__data.get_parent(fs)
            fp = self.__data.get_parent(fr)
        else:
            return None
        return self.__fps[fp.get_id()]

    # ------------------------------------------------------------------------

    def OnCollapseChanged(self, evt=None):
        panel = evt.GetEventObject()
        panel.SetFocus()
        self.ScrollChildIntoView(panel)

    # ------------------------------------------------------------------------

    def OnSize(self, event):
        """Handle the wx.EVT_SIZE event.

        :param event: a SizeEvent event to be processed.

        """
        # each time our size is changed, the child panel needs a resize.
        self.Layout()

# ---------------------------------------------------------------------------


class FilePathCollapsiblePanel(sppasCollapsiblePanel):
    """A panel to display the fp as a list of fr.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      contact@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2019  Brigitte Bigi

    """

    def __init__(self, parent, fp, name="fp-panel"):
        super(FilePathCollapsiblePanel, self).__init__(parent, label=fp.get_id(), name=name)

        self._create_content(fp)
        self._setup_events()

        # Each FileRoot has its own CollapsiblePanel in the sizer
        self.__fpid = fp.get_id()
        self.__frs = dict()  # key=root.id, value=FileRootCollapsiblePanel

        # Look&feel
        self.SetBackgroundColour(self.GetParent().GetBackgroundColour())
        self.SetForegroundColour(wx.GetApp().settings.fg_color)
        self.SetFont(wx.GetApp().settings.text_font)

    # -----------------------------------------------------------------------

    def SetFont(self, font):
        """Override."""
        f = wx.Font(font.GetPointSize(),
                    font.GetFamily(),
                    font.GetStyle(),
                    wx.FONTWEIGHT_BOLD,
                    font.GetUnderlined(),
                    font.GetFaceName())
        sppasCollapsiblePanel.SetFont(self, f)
        self.GetPane().SetFont(font)
        self.Layout()

    # ----------------------------------------------------------------------

    def add_file(self, fr, fn):
        """Add a file in the appropriate root of the child panel.

        """
        if fr.get_id() not in self.__frs:
            p = self.__add_root_panel(fr)
        else:
            p = self.__frs[fr.get_id()]

        wx.LogDebug("Will add file in the root panel: ")
        added = p.add(fn)
        if added is True:
            self.Layout()
            self.Refresh()

    # ------------------------------------------------------------------------

    def __add_root_panel(self, fr):
        """Create a child panel to display the content of a FileRoot.

        :param fr: (FileRoot)
        :return: FileRootCollapsiblePanel

        """
        p = FileRootCollapsiblePanel(self.GetPane(), fr)
        p.SetFocus()
        self.Bind(wx.EVT_COLLAPSIBLEPANE_CHANGED, self.OnCollapseChanged, p)
        self.GetPane().GetSizer().Add(p, 0, wx.EXPAND | wx.ALL, border=4)
        self.__frs[fr.get_id()] = p
        return p

    # ------------------------------------------------------------------------
    # Manage the content
    # ------------------------------------------------------------------------

    def _create_content(self, fp):
        collapse = True
        if fp.subjoined is not None:
            if "expand" in fp.subjoined:
                collapse = not fp.subjoined["expand"]

        self.Collapse(collapse)
        self.AddButton("folder")
        self.AddButton("choice_checkbox")

    # ------------------------------------------------------------------------

    def change_state(self, identifier, state):
        icon_name = STATES_ICON_NAMES[state]

        if self.__fpid == identifier:
            btn = self.FindButton("choice_checkbox")
            btn.SetImage(icon_name)
            btn.Refresh()
        elif identifier in self.__frs:
            self.__frs[identifier].change_state(identifier, state)
        else:
            frid = FileRoot.root(identifier)
            if frid in self.__frs:
                self.__frs[frid].change_state(identifier, state)

    # -----------------------------------------------------------------------
    # Events management
    # -----------------------------------------------------------------------

    def notify(self, identifier):
        """The parent has to be informed of a change of content."""
        wx.LogDebug("PATH: Notification ItemClicked {:s}".format(identifier))
        evt = ItemClickedEvent(id=identifier)
        evt.SetEventObject(self)
        wx.PostEvent(self.GetParent(), evt)

    # ------------------------------------------------------------------------

    def _setup_events(self):
        """Associate a handler function with the events.

        It means that when an event occurs then the process handler function
        will be called.

        """
        self.FindButton("choice_checkbox").Bind(wx.EVT_BUTTON, self.OnCkeckedPath)

    # ------------------------------------------------------------------------

    def OnCollapseChanged(self, evt=None):
        panel = evt.GetEventObject()
        panel.SetFocus()
        self.GetParent().SendSizeEvent()

    # ------------------------------------------------------------------------

    def OnCkeckedPath(self, evt):
        self.notify(self.__fpid)

# ---------------------------------------------------------------------------


class FileRootCollapsiblePanel(sppasCollapsiblePanel):
    """A panel to display the fr as a list of fn.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      contact@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2019  Brigitte Bigi

    """

    COLUMNS = ['state', 'icon', 'file', 'type', 'date', 'size']

    def __init__(self, parent, fr, name="fr-panel"):
        super(FileRootCollapsiblePanel, self).__init__(parent, label=fr.get_id(), name=name)

        self._create_content(fr)
        self._setup_events()

        # Files are displayed in a listctrl. For convenience, their ids are
        # stored into a list.
        self.__frid = fr.get_id()
        self.__fns = list()

        # Look&feel
        self.SetBackgroundColour(self.GetParent().GetBackgroundColour())
        self.SetForegroundColour(wx.GetApp().settings.fg_color)
        self.SetFont(wx.GetApp().settings.text_font)

    # -----------------------------------------------------------------------
    # Public methods
    # -----------------------------------------------------------------------

    def SetBackgroundColour(self, color):
        """Calculate a lightness background color."""
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
        self.FindWindow("listctrl_files").SetImageList(self.__il, wx.IMAGE_LIST_SMALL)
        self.__set_pane_size()
        self.Layout()

    # ----------------------------------------------------------------------

    def add(self, fn):
        """Add a file in the dataview of the child panel.

        :param fn: (FileName)

        """
        if fn.get_id() in self.__fns:
            return False

        wx.LogDebug("In add. Item {:s} not found so we'll add it.".format(fn.id))
        self.__add_file(fn)
        return True

    # ------------------------------------------------------------------------

    def change_state(self, identifier, state):
        icon_name = STATES_ICON_NAMES[state]
        wx.LogDebug("change state. index of image: {:d}".format(self.__ils.index(icon_name)))

        if self.__frid == identifier:
            self.FindButton("choice_checkbox").SetImage(icon_name)
            self.FindButton("choice_checkbox").Refresh()

        else:
            listctrl = self.FindWindow("listctrl_files")
            idx = self.__fns.index(identifier)
            listctrl.SetItem(idx, 0, "", imageId=self.__ils.index(icon_name))

    # ------------------------------------------------------------------------
    # Construct the GUI
    # ------------------------------------------------------------------------

    def _create_content(self, fr):
        list_ctrl = self.__create_listctrl()
        self.SetPane(list_ctrl)

        collapse = True
        if fr.subjoined is not None:
            if "expand" in fr.subjoined:
                collapse = not fr.subjoined["expand"]

        self.Collapse(collapse)
        self.AddButton("root")
        self.AddButton("choice_checkbox")

    # ------------------------------------------------------------------------

    def __create_listctrl(self):
        """Create a listctrl to display files."""
        style = wx.LC_REPORT | wx.LC_NO_HEADER | wx.LC_SINGLE_SEL | wx.LC_HRULES
        lst = wx.ListCtrl(self, style=style, name="listctrl_files")

        lst.Bind(wx.EVT_LIST_ITEM_SELECTED, self.__item_selected)
        info = wx.ListItem()
        info.Mask = wx.LIST_MASK_TEXT | wx.LIST_MASK_IMAGE | wx.LIST_MASK_FORMAT
        info.Image = -1
        info.Align = 0
        lst.InsertColumn(0, info)
        lst.SetColumnWidth(0, sppasScrolledPanel.fix_size(24))
        lst.AppendColumn("icon",
                         format=wx.LIST_FORMAT_CENTRE,
                         width=sppasScrolledPanel.fix_size(36))
        lst.AppendColumn("file",
                         format=wx.LIST_FORMAT_LEFT,
                         width=sppasScrolledPanel.fix_size(160))
        lst.AppendColumn("type",
                         format=wx.LIST_FORMAT_LEFT,
                         width=sppasScrolledPanel.fix_size(80))
        lst.AppendColumn("date",
                         format=wx.LIST_FORMAT_CENTRE,
                         width=sppasScrolledPanel.fix_size(100))
        lst.AppendColumn("size",
                         format=wx.LIST_FORMAT_RIGHT,
                         width=sppasScrolledPanel.fix_size(60))

        return lst

    # ------------------------------------------------------------------------

    def __create_image_list(self):
        """Create a list of images to be displayed in the listctrl."""
        h = self.GetFont().GetPixelSize()[1]
        icon_size = sppasCollapsiblePanel.fix_size(int(h))

        il = wx.ImageList(icon_size, icon_size)
        self.__ils = list()

        # All icons to represent the state of the root or a filename
        for state in STATES_ICON_NAMES:
            icon_name = STATES_ICON_NAMES[state]
            bitmap = sppasSwissKnife.get_bmp_icon(icon_name, icon_size)
            il.Add(bitmap)
            self.__ils.append(icon_name)

        # The default icon to represent a missing file
        bitmap = sppasSwissKnife.get_bmp_icon("files-file", icon_size)
        il.Add(bitmap)
        self.__ils.append("files-file")

        # The icons of the known file extensions
        for icon_name in FileAnnotIcon().get_names():
            bitmap = sppasSwissKnife.get_bmp_icon(icon_name, icon_size)
            il.Add(bitmap)
            self.__ils.append(icon_name)

        return il

    # ------------------------------------------------------------------------

    def __set_pane_size(self):
        """Fix the size of the child panel."""
        listctrl = self.FindWindow("listctrl_files")
        n = listctrl.GetItemCount() + 1
        if n == 0:
            n = 1
        h = n * self.GetFont().GetPixelSize()[1] * 2
        listctrl.SetMinSize(wx.Size(-1, h+2))

    # ------------------------------------------------------------------------
    # Management the list of files
    # ------------------------------------------------------------------------

    def __add_file(self, fn):
        listctrl = self.FindWindow("listctrl_files")
        icon_name = FileAnnotIcon().get_icon_name(fn.get_extension())
        img_index = self.__ils.index(icon_name)

        index = listctrl.InsertItem(listctrl.GetItemCount(), 0)
        listctrl.SetItemColumnImage(index, FileRootCollapsiblePanel.COLUMNS.index("icon"), img_index)
        listctrl.SetItem(index, FileRootCollapsiblePanel.COLUMNS.index("file"), fn.get_name())
        listctrl.SetItem(index, FileRootCollapsiblePanel.COLUMNS.index("type"), fn.get_extension())  # type=extension
        listctrl.SetItem(index, FileRootCollapsiblePanel.COLUMNS.index("date"), fn.get_date())  # last modif
        listctrl.SetItem(index, FileRootCollapsiblePanel.COLUMNS.index("size"), fn.get_size())  # file size

        self.__fns.append(fn.get_id())
        self.__set_pane_size()
        self.GetPane().Layout()

    # ------------------------------------------------------------------------

    def __remove_file(self, fn):
        listctrl = self.FindWindow("listctrl_files")

        #item = listctrl.FindItem(label) or item = listctrl.GetItem(idx)
        #listctrl.DeleteItem(item)

    # ------------------------------------------------------------------------

    def __update_file(self, fn):
        listctrl = self.FindWindow("listctrl_files")

        #item = listctrl.FindItem(label) or item = listctrl.GetItem(idx)
        #listctrl.RefreshItem(item)

    # ------------------------------------------------------------------------
    # Management of the events
    # ------------------------------------------------------------------------

    def _setup_events(self):
        """Associate a handler function with the events.

        It means that when an event occurs then the process handler function
        will be called.

        """
        self.FindButton("choice_checkbox").Bind(wx.EVT_BUTTON, self.OnCkeckedRoot)

    # ------------------------------------------------------------------------

    def notify(self, identifier):
        """The parent has to be informed of a change of content."""
        evt = ItemClickedEvent(id=identifier)
        evt.SetEventObject(self)
        wx.PostEvent(self.GetParent(), evt)

    # ------------------------------------------------------------------------

    def __item_selected(self, event):
        """"""
        listctrl = self.FindWindow("listctrl_files")
        index = listctrl.GetFirstSelected()
        listctrl.Select(index, on=False)

        # get the corresponding fn
        item = listctrl.GetItem(index, col=FileRootCollapsiblePanel.COLUMNS.index("file"))
        wx.LogDebug("THE item I SEARCH ={:s}".format(str(item)))
        wx.LogDebug("THE item I SEARCH ={:s}".format(str(listctrl.GetItemText(index, col=FileRootCollapsiblePanel.COLUMNS.index("file")))))

        fn_clicked = self.__fns[index]
        wx.LogDebug("fn clicked is {:s}".format(fn_clicked))

        # notify parent to decide what has to be done
        self.notify(fn_clicked)

    # ------------------------------------------------------------------------

    def OnCkeckedRoot(self, evt):
        # button = evt.GetEventObject()
        self.notify(self.__frid)

# ----------------------------------------------------------------------------
# Panel tested by test_glob.py
# ----------------------------------------------------------------------------


class TestPanel(FileTreeView):

    def __init__(self, parent):
        super(TestPanel, self).__init__(parent)
        self.AddFiles([os.path.abspath(__file__)])
        self.AddFiles([os.path.join(paths.samples, "samples-fra")])
