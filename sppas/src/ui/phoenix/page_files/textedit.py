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

    src.ui.phoenix.views.textedit.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Edit a sppasTranscription() of anndata package as a text file.

"""

import codecs
import wx
import os
import logging
import wx.lib.newevent

from sppas.src.config import sg
from sppas.src.config import msg
from sppas.src.config import paths
from sppas.src.utils import u

from sppas.src.ui.phoenix.windows import sppasDialog
from sppas.src.ui.phoenix.windows import sppasPanel
from sppas.src.ui.phoenix.windows import sppasToolbar
from sppas.src.ui.phoenix.windows import sppasTextCtrl
from sppas.src.ui.phoenix.windows.book import sppasNotebook

# ---------------------------------------------------------------------------

MSG_HEADER_TEXT = u(msg("TextView", "ui"))

# ---------------------------------------------------------------------------
# Event to be used when the editor closed one or more files.
# The event must contain 1 member: the 'files'.
CloseEditEvent, EVT_CLOSE_EDIT = wx.lib.newevent.NewEvent()
CloseEditCommandEvent, EVT_CLOSE_EDIT_COMMAND = wx.lib.newevent.NewCommandEvent()

# ----------------------------------------------------------------------------


class sppasTextEditDialog(sppasDialog):
    """Dialog to edit any text file in a text editor.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2020  Brigitte Bigi

    Returns either wx.ID_CANCEL or wx.ID_OK if ShowModal().

    """

    def __init__(self, parent, filenames=()):
        """Create a dialog to fix edit text.

        :param parent: (wx.Window)
        :param filenames: (list of str)

        """
        super(sppasTextEditDialog, self).__init__(
            parent=parent,
            title="TextEditor",
            style=wx.CAPTION | wx.RESIZE_BORDER | wx.CLOSE_BOX | wx.MAXIMIZE_BOX | wx.STAY_ON_TOP)

        self.CreateHeader(MSG_HEADER_TEXT, "data-view-text")
        self._create_content()
        self.CreateActions([wx.ID_CANCEL, wx.ID_OK])

        # Add metadata instances in the book
        if len(filenames) > 0:
            for fn in filenames:
                self.add_file(fn)

        self.Bind(wx.EVT_BUTTON, self._process_button_clicked)

        self.LayoutComponents()
        # self.CenterOnParent()
        self.GetSizer().Fit(self)
        self.FadeIn()

    # -----------------------------------------------------------------------

    def add_file(self, filename):
        """Create a page of the book with the given file content.

        :param filename: (str)

        """
        panel = sppasTextEditPanel(self._book, filename)
        tab_title = os.path.basename(filename)
        self._book.AddPage(panel, tab_title, select=True, imageId=wx.NO_IMAGE)

    # -----------------------------------------------------------------------

    def is_loaded(self, filename):
        """Return True if the given filename was loaded."""
        for i in range(self._book.GetPageCount()):
            panel = self._book.GetPage(i)
            if panel.get_filename() == filename:
                return panel.is_loaded()

        return False

    # -----------------------------------------------------------------------

    def save_all(self):
        """Save all modified files."""
        for i in range(self._book.GetPageCount()):
            panel = self._book.GetPage(i)
            panel.save()

    # -----------------------------------------------------------------------
    # Create the GUI
    # -----------------------------------------------------------------------

    def _create_content(self):
        """Create the content of the dialog."""
        panel = sppasPanel(self, name="content")
        tb = self.__create_toolbar(panel)
        bp = self.__create_book(panel)

        s = wx.BoxSizer(wx.VERTICAL)
        s.Add(tb, 0, wx.EXPAND, 0)
        s.Add(bp, 1, wx.EXPAND, 0)

        panel.SetSizer(s)
        panel.Layout()
        self.SetContent(panel)

    # -----------------------------------------------------------------------

    def __create_toolbar(self, parent):
        tb = sppasToolbar(parent)
        b = tb.AddButton("save_as", "Save file")
        b.SetBorderWidth(1)
        b = tb.AddButton("save_all", "Save all files")
        b.SetBorderWidth(1)
        return tb

    # -----------------------------------------------------------------------

    def __create_book(self, parent):
        """Create the simple book to manage the several pages of the frame."""
        book = sppasNotebook(
            parent=parent,
            style=wx.BORDER_NONE | wx.TAB_TRAVERSAL | wx.WANTS_CHARS,
            name="book_list"
        )

        return book

    # -----------------------------------------------------------------------

    @property
    def _book(self):
        return self.FindWindow("book_list")

    @property
    def _page(self):
        page_index = self._book.GetSelection()
        if page_index == -1:
            return None
        return self._book.GetPage(page_index)

    # -----------------------------------------------------------------------

    def _process_button_clicked(self, event):
        evt_object = event.GetEventObject()
        evt_name = evt_object.GetName()
        event_id = evt_object.GetId()

        if evt_name == "save_as":
            p = self._page
            if p is not None:
                p.save()

        elif evt_name == "save_all":
            self.save_all()

        elif event_id == wx.ID_OK:
            self.exit(save=True)

        elif event_id in (wx.ID_CANCEL, wx.ID_CLOSE):
            self.exit(save=False)

        else:
            event.Skip()

    # -----------------------------------------------------------------------

    def Notify(self, filenames):
        evt = CloseEditEvent(files=filenames)
        evt.SetEventObject(self)
        wx.PostEvent(self.GetParent(), evt)

    # -----------------------------------------------------------------------

    def exit(self, save=True):
        """Save files of the frame and end."""
        filenames = list()
        for i in range(self._book.GetPageCount()):
            panel = self._book.GetPage(i)
            filenames.append(panel.get_filename())
        self.Notify(filenames)

        if save is True:
            wx.BeginBusyCursor()
            self.save_all()
            wx.EndBusyCursor()

        try:
            delta = wx.GetApp().settings.fade_out_delta
        except AttributeError:
            delta = -10
        self.DestroyFadeOut(delta)

# ----------------------------------------------------------------------------


class sppasTextEditPanel(sppasPanel):
    """Panel to display the content of a file.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      contact@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2020  Brigitte Bigi

    """

    def __init__(self, parent, filename, name="editor_panel"):

        super(sppasTextEditPanel, self).__init__(
            parent,
            id=wx.ID_ANY,
            pos=wx.DefaultPosition,
            size=wx.DefaultSize,
            style=wx.NO_FULL_REPAINT_ON_RESIZE | wx.BORDER_NONE,
            name=name)

        # Members related to the file (modified, readable, name)
        self._dirty = False
        self._valid = False
        self._filename = filename

        # Create the GUI
        self._create_content()

        # Look&feel
        try:
            settings = wx.GetApp().settings
            self.SetBackgroundColour(settings.bg_color)
            self.SetForegroundColour(settings.fg_color)
            self.SetFont(settings.text_font)
        except AttributeError:
            self.InheritAttributes()

        self.Bind(wx.EVT_TEXT, self._process_text_changed)
        self.SetAutoLayout(True)
        self.Layout()

        # it seems that the ext_text was called at creation, so
        # dirty moved to true... it's needed to switch it back to false...
        self._dirty = False

    # ------------------------------------------------------------------------

    def is_modified(self):
        """Return True if the content of the file has changed."""
        return self._dirty

    # ------------------------------------------------------------------------

    def is_loaded(self):
        """Return True if the content of the file was properly loaded."""
        return self._valid

    # -----------------------------------------------------------------------

    def save(self):
        """Save the displayed text into a file.

        :return: (bool)

        """
        if self._valid is False:
            wx.LogMessage("File {:s} was not loaded. Can't be saved."
                          "".format(self._filename))
            return False
        if self._dirty is False:
            wx.LogMessage("File {:s} was not modified. Won't be saved."
                          "".format(self._filename))
            return False

        try:
            with codecs.open(self._filename, 'w', sg.__encoding__) as fp:
                fp.write(self._textedit.GetValue())
        except Exception as e:
            wx.LogMessage("File {:s} not saved: {}".format(self._filename, e))
            return False

        self._textedit.SetModified(False)
        self._dirty = False
        wx.LogMessage("File {:s} saved.".format(self._filename))
        return True

    # ------------------------------------------------------------------------

    def get_filename(self):
        """Return the filename this panel is displaying."""
        return self._filename

    # ------------------------------------------------------------------------

    def set_filename(self, name):
        """Set a new name to the file.

        :param name: (str) Name of a file. It is not verified.

        """
        self._filename = name
        self.SetLabel(name)
        self._dirty = True

    # -----------------------------------------------------------------------
    # Create the content of the scrolled panel
    # -----------------------------------------------------------------------

    def _create_content(self):
        """Create a text editor content."""
        sizer = wx.BoxSizer(wx.VERTICAL)

        style = wx.NO_BORDER | wx.TE_MULTILINE | wx.TE_RICH | \
                wx.TE_PROCESS_ENTER | wx.HSCROLL
        txtview = sppasTextCtrl(self, style=style, name="content")
        txtview.SetFont(wx.GetApp().settings.mono_text_font)
        txtview.SetEditable(True)
        txtview.SetModified(False)

        try:
            with codecs.open(self._filename, 'r', sg.__encoding__) as fp:
                full_content = fp.readlines()
                # wx.LogMessage("Text loaded: {:d} lines.".format(len(full_content)))
                content = "".join(full_content)
                self._valid = True
        except Exception as e:
            content = str(e)
            self._valid = False

        txtview.SetValue(content)
        txtview.SetStyle(0, len(content), txtview.GetDefaultStyle())
        txtview.SetModified(False)
        self._dirty = False

        sizer.Add(txtview, 1, wx.EXPAND, 0)
        self.SetSizer(sizer)

    # -----------------------------------------------------------------------

    @property
    def _textedit(self):
        return self.FindWindow("content")

    # -----------------------------------------------------------------------

    def _process_text_changed(self, evt):
        self._dirty = True

# ----------------------------------------------------------------------------
# Panel that can be tested
# ----------------------------------------------------------------------------


class TestPanel(sppasPanel):

    def __init__(self, parent, pos=wx.DefaultPosition, size=wx.DefaultSize):
        super(TestPanel, self).__init__(parent, pos=pos, size=size,
                                        name="TestPanel TextEditor")
        s = wx.BoxSizer()
        b = wx.Button(self, label="Text Editor", name="edit_btn")
        s.Add(b, 1, wx.EXPAND)
        self.SetSizer(s)
        self.Bind(wx.EVT_BUTTON, self._open_edit)

    # -----------------------------------------------------------------------

    def _open_edit(self, evt):
        f1 = os.path.join(paths.samples, "annotation-results", "samples-fra",
                          "F_F_B003-P8-palign.xra")
        f2 = os.path.join(paths.samples, "annotation-results", "samples-fra",
                          "F_F_B003-P9-palign.xra")
        f3 = os.path.join(paths.samples, "samples-fra", "F_F_B003-P9.wav")

        t = sppasTextEditDialog(self, [f1, f2, f3])
        t.Show()
