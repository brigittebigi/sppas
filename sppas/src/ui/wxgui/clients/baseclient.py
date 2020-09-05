#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# ---------------------------------------------------------------------------
#            ___   __    __    __    ___
#           /     |  \  |  \  |  \  /              Automatic
#           \__   |__/  |__/  |___| \__             Annotation
#              \  |     |     |   |    \             of
#           ___/  |     |     |   | ___/              Speech
#
#
#                           http://www.sppas.org/
#
# ---------------------------------------------------------------------------
#            Laboratoire Parole et Langage, Aix-en-Provence, France
#                   Copyright (C) 2011-2016  Brigitte Bigi
#
#                   This banner notice must not be removed
# ---------------------------------------------------------------------------
# Use of this software is governed by the GNU Public License, version 3.
#
# SPPAS is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# SPPAS is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with SPPAS. If not, see <http://www.gnu.org/licenses/>.
#
# ---------------------------------------------------------------------------
# File: baseclient.py
# ----------------------------------------------------------------------------

import os.path
import wx
import logging

from sppas.src.ui.wxgui.sp_icons import EMPTY_ICON, NON_EMPTY_ICON
from sppas.src.ui.wxgui.structs.files import xFiles

from sppas.src.ui.wxgui.ui.CustomEvents import FileWanderEvent, spEVT_FILE_WANDER
from sppas.src.ui.wxgui.ui.CustomEvents import spEVT_SETTINGS
from sppas.src.ui.wxgui.ui.CustomEvents import spEVT_NOTEBOOK_NEW_PAGE
from sppas.src.ui.wxgui.ui.CustomEvents import spEVT_NOTEBOOK_CLOSE_PAGE

from sppas.src.ui.wxgui.cutils.imageutils import spBitmap

# ----------------------------------------------------------------------------


class BaseClient(wx.Window):
    """
    @author:       Brigitte Bigi
    @organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    @contact:      develop@sppas.org
    @license:      GPL, v3
    @copyright:    Copyright (C) 2011-2016  Brigitte Bigi
    @summary:      This class is used to manage the opened files.

    This class manages the pages of a notebook with all opened files.

    Each page (except if empty...) contains an instance of a component.

    """
    def __init__(self, parent, prefsIO):

        wx.Window.__init__(self, parent, -1, style=wx.NO_BORDER)
        self.SetBackgroundColour( prefsIO.GetValue('M_BG_COLOUR') )

        box = wx.BoxSizer(wx.VERTICAL)

        # members
        self._prefsIO = prefsIO
        self._xfiles  = xFiles()

        # The component can deal with multiple files, or not.
        self._multiplefiles = False

        # a notebook
        self._set_notebook()

        # Do not show an empty notebook: create an empty page
        self.AddEmptyPage()

        # Events
        self.Bind(wx.EVT_SIZE,  self.OnSize)
        self.Bind(wx.EVT_CLOSE, self.OnClose)

        self.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED, self.OnPageChanged)
        self.Bind(spEVT_NOTEBOOK_NEW_PAGE,      self.OnNewPage)
        self.Bind(spEVT_NOTEBOOK_CLOSE_PAGE,    self.OnClosePage)
        self.Bind(spEVT_SETTINGS,               self.OnSettings)
        self.Bind(spEVT_FILE_WANDER,            self.OnFileWander)

        box.Add(self._notebook, 1, wx.EXPAND)
        self.SetSizer(box)

        self._LayoutFrame()

    # ------------------------------------------------------------------------

    def _set_notebook(self):
        """Create the notebook and set images."""

        self._notebook = wx.Notebook( self, style=wx.NB_TOP|wx.CLIP_CHILDREN|wx.NB_MULTILINE|wx.NB_NOPAGETHEME|wx.NO_BORDER )
        self._notebook.SetBackgroundColour( self._prefsIO.GetValue( 'M_BG_COLOUR' ) )
        self._notebook.SetForegroundColour( self._prefsIO.GetValue( 'M_FG_COLOUR' ) )
        self._notebook.SetFont( self._prefsIO.GetValue( 'M_FONT' ) )

        # assign images to the notebook
        il = wx.ImageList(16, 16)
        idx1 = il.Add(spBitmap(EMPTY_ICON, 16, theme=self._prefsIO.GetValue('M_ICON_THEME')))
        idx2 = il.Add(spBitmap(NON_EMPTY_ICON, 16, theme=self._prefsIO.GetValue('M_ICON_THEME')))
        self._notebook.AssignImageList(il)
        self._notebookimages = { EMPTY_ICON:idx1, NON_EMPTY_ICON:idx2 }

    # ------------------------------------------------------------------------

    def _LayoutFrame(self):
        """Layout and Refresh the frame and refresh all GDI objects.  """

        page = self._notebook.GetCurrentPage()
        for i in range(self._xfiles.GetSize()):
            if self._xfiles.GetOther(i) == page:
                o = self._xfiles.GetObject(i)
                if o is not None:
                    o.SendSizeEvent()

        self.Layout()
        self.Refresh()

    # ------------------------------------------------------------------------
    # The panel including the component
    # ------------------------------------------------------------------------

    def CreateComponent(self, parent, prefsIO):
        """
        Create the real client: the component itself.
        Must be overridden.

        """
        raise NotImplementedError


    # ------------------------------------------------------------------------
    # Notebook
    # ------------------------------------------------------------------------

    def SetImage(self, pageidx, imgname):
        """Set an image to a page of the notebook."""

        if imgname in self._notebookimages.keys():
            # now put an image on the page:
            self._notebook.SetPageImage(pageidx, self._notebookimages[imgname])

    # ------------------------------------------------------------------------

    def AddEmptyPage(self, title=None):
        """
        Add a new empty page in the notebook.

        @param title (String) is this new page title
        @param select (Boolean) is used to select this page (or not)

        A sizer is added to the panel.
        The default title is the page number.

        """
        _panel = wx.Panel( self._notebook )
        _panel.SetBackgroundColour( self._prefsIO.GetValue( 'M_BG_COLOUR' ) )
        _sizer = wx.BoxSizer( wx.VERTICAL )
        _panel.SetSizer(_sizer)

        if title is None:
            title = " New tab "
        self._notebook.AddPage( _panel, title)
        self._notebook.GetCurrentPage()

        self.SetImage(self._notebook.GetPageCount()-1, EMPTY_ICON)

    # ------------------------------------------------------------------------

    def ChangePage(self, direction=0):
        """
        Go at the next page if direction > 0 or at the previous page if direction < 0.

        """
        curp = self._notebook.GetSelection()
        maxp = self._notebook.GetPageCount()

        if direction < 0:
            if curp == 0:
                # go at last
                self._notebook.SetSelection(maxp-1)
            else:
                # go at previous
                self._notebook.SetSelection(curp-1)

        elif direction > 0:
            if curp == (maxp-1):
                # go at first
                self._notebook.SetSelection(0)
            else:
                # go at next
                self._notebook.SetSelection(curp+1)

    # ------------------------------------------------------------------------
    # Callbacks for the notebook
    # ------------------------------------------------------------------------

    def OnNewPage(self, event):
        """We received an event to add an empty new page."""

        self.AddEmptyPage()

    # ------------------------------------------------------------------------

    def OnClosePage(self, event):
        """
        We received an event to close the selected page.

        All files of this page are unset.

        """
        # get current selected page
        page = self._notebook.GetCurrentPage()

        # get files of this page
        files = []
        for i in range(self._xfiles.GetSize()):
            pagei = self._xfiles.GetOther(i)
            obj   = self._xfiles.GetObject(i)
            if page == pagei:
                f = self._xfiles.GetFilename(i)
                files.append( f )

        if len( files ) == 0:
            # close the page
            n = self.__getIndexPageNotebook( page )
            if n > -1:
                self._notebook.DeletePage( n )
            # Oups... this was the last page! Create a new EmptyPage.
            if self._notebook.GetCurrentPage() is None:
                self.AddEmptyPage()
        else:
            for f in files:
                self.UnsetData( f )

    # ------------------------------------------------------------------------

    def OnPageChanged(self, event):
        """
        Update information if page changed.
        """
        # get new selected page
        page = self._notebook.GetCurrentPage()
        # TODO: call ChangePage

    # ------------------------------------------------------------------------
    # Callbacks for the files
    # ------------------------------------------------------------------------

    def OnFileWander(self, event):
        """ A file was checked/unchecked somewhere else, then, set/unset the data."""
        owner = event.GetEventObject()
        f = event.filename
        s = event.status

        if s is True:
            self.SetData( f )

        else:
            if owner == self.GetTopLevelParent():
                #A file was checked/unchecked in the file manager.
                self.UnsetData( f )

            else:
                # Get the page and check before deleting it!
                for i in range(self._xfiles.GetSize()):
                    filename = self._xfiles.GetFilename(i)
                    if f == filename:
                        page = self._xfiles.GetOther(i)
                        self._xfiles.Remove(i)
                        self.DeletePage( page )

        self.Refresh()

    # ------------------------------------------------------------------------

    def OnSize(self, event):
        """Called by the parent when the frame is resized and lays out the client window."""

        self._LayoutFrame()

    # ------------------------------------------------------------------------

    def OnClose(self, event):
        """Destroy all objects then self."""

        for i in range(self._xfiles.GetSize()):
            #obj = self._xfiles.GetObject(i)
            self.UnsetData(self._xfiles.GetFilename(i))


    # ------------------------------------------------------------------------
    # Decoration management...
    # ------------------------------------------------------------------------

    def OnSettings(self, event):
        """Set new preferences, then apply them.  """

        self._prefsIO = event.prefsIO

        # Apply the changes on self
        self.SetBackgroundColour( self._prefsIO.GetValue( 'M_BG_COLOUR' ) )
        self._notebook.SetBackgroundColour( self._prefsIO.GetValue( 'M_BG_COLOUR' ) )
        self._notebook.SetForegroundColour( self._prefsIO.GetValue( 'M_FG_COLOUR' ) )
        self._notebook.SetFont( self._prefsIO.GetValue( 'M_FONT' ) )

        for i in range(self._notebook.GetPageCount()):
            page = self._notebook.GetPage(i)
            page.SetBackgroundColour( self._prefsIO.GetValue( 'M_BG_COLOUR' ) )

        # Apply on all anz_panels
        for i in range(self._xfiles.GetSize()):
            p = self._xfiles.GetObject(i)
            p.SetBackgroundColour( self._prefsIO.GetValue( 'M_BG_COLOUR' ) )
            p.SetForegroundColour( self._prefsIO.GetValue( 'M_FG_COLOUR' ) )
            p.SetFont( self._prefsIO.GetValue( 'M_FONT' ) )
            wx.PostEvent( p,event )

        self.Layout()
        self.Refresh()

    # ------------------------------------------------------------------------
    # Data management...
    # ------------------------------------------------------------------------

    def SetData(self, filename):
        """
        Add new data to draw.

        @param filename (String / List of String) is file name(s) to draw.

        """
        loaded = []
        if not type(filename) is list:
            filenames = [filename]
        else:
            filenames = filename

        #self.GetTopLevelParent().SetCursor(wx.StockCursor(wx.CURSOR_WAIT))
        wx.BeginBusyCursor()

        for f in filenames:

            # Do not add an existing file
            if self._xfiles.Exists( f ):
                loaded.append(False)
                continue

            # get all required data
            page = self._notebook.GetCurrentPage()
            if page is None:
                self.AddEmptyPage()
                self._LayoutFrame()
            i = self.__getIndexPageXFiles( page )

            if i > -1 and self._multiplefiles is False:
                # the current page has already a component and it can't support multiple files
                # -- > add a page.
                self.AddEmptyPage()
                self._notebook.SetSelection(self._notebook.GetPageCount()-1)
                page = self._notebook.GetCurrentPage()
                i = self.__getIndexPageXFiles( page )

            if i == -1:
                # none of the loaded files is using this page: create a component
                client = self.CreateComponent( parent=page, prefsIO=self._prefsIO )
                sizer = page.GetSizer()
                sizer.Add(client, proportion=1, flag=wx.EXPAND, border=0 )
                n = self.__getIndexPageNotebook( page )
                if n > -1:
                    self._notebook.SetPageText( n, os.path.splitext( os.path.basename(f) )[0] )
                    self.SetImage(n, NON_EMPTY_ICON)
                page.Layout()
            else:
                client = self._xfiles.GetObject(i)

            try:
                self._xfiles.Append(f, client, page)
                evt = FileWanderEvent(filename=f,status=True)
                evt.SetEventObject(self)
                wx.PostEvent(client, evt)
            except Exception as e:
                logging.info('Error uploading: '+f+' '+str(e))
                loaded.append( False )
                evt = FileWanderEvent(filename=f,status=False)
                evt.SetEventObject(self)
                wx.PostEvent(self.GetTopLevelParent(), evt)
            loaded.append( True )

        # redraw objects of this page
        wx.EndBusyCursor()
        #self.GetTopLevelParent().SetCursor(wx.StockCursor(wx.CURSOR_ARROW))
        self.Refresh()

        if len(loaded)==1:
            return loaded[0]

        return loaded

    # ------------------------------------------------------------------------

    def UnsetData(self, f):
        """Remove the given file."""

        if not self._xfiles.Exists(f):
            logging.debug('WARNING. Try to unset an un-existing data:%s '%f)
            return

        # Get information about this file (index, Display object, page)
        idx    = self._xfiles.GetIndex(f)
        client = self._xfiles.GetObject(idx)
        #page   = self._xfiles.GetOther(idx)

        evt = FileWanderEvent(filename=f, status=False)
        evt.SetEventObject(self)
        wx.PostEvent( client, evt )
        wx.PostEvent( self.GetTopLevelParent(), evt )

    # ------------------------------------------------------------------------

    def DeletePage(self, page):
        """Delete a page of the notebook."""

        # Close the page ???
        unused = True
        for i in range(self._xfiles.GetSize()):
            #f = self._xfiles.GetFilename(i)
            pagei = self._xfiles.GetOther(i)
            if page == pagei:
                unused = False # an other file is using the same page

        if unused is True:
            # close the page
            n = self.__getIndexPageNotebook( page )
            if n > -1:
                self._notebook.DeletePage( n )

        # Oups... this was the last page! Create a new EmptyPage.
        if self._notebook.GetCurrentPage() is None:
            self.AddEmptyPage()

    # ------------------------------------------------------------------------

    def GetSelection(self):
        """Return the list of displayed files (files of this page)."""

        if self._notebook.GetCurrentPage() is None:
            return []

        selection = []
        idxselection = self.__getIndexPageXFiles( self._notebook.GetCurrentPage() )
        for i in range(self._xfiles.GetSize()):
            if i in idxselection:
                selection.append(self._xfiles.GetObject(i))

        return selection


    # ------------------------------------------------------------------------
    # Private methods
    # ------------------------------------------------------------------------

    def __getIndexPageNotebook(self, page):
        """Get the index of this page in the notebook."""

        idx_page = filter(lambda i: page==self._notebook.GetPage(i),range(self._notebook.GetPageCount()))
        if len( idx_page )>0:
            return idx_page[0]
        return -1

    def __getIndexPageXFiles(self, page):
        """Get the index of this page in xfiles."""

        idx_page = filter(lambda i: page==self._xfiles.GetOther(i),range(self._xfiles.GetSize()))
        if len( idx_page )>0:
            return idx_page[0]
        return -1

# ----------------------------------------------------------------------------
# A few doc:
# An application can either use wxWindow::Close event just as the framework
# does, or it can call wxWindow::Destroy directly.
# If using Close(), you can pass a true argument to this function to tell
# the event handler that we definitely want to delete the frame and it cannot
# be vetoed.

# The advantage of using Close instead of Destroy is that it will call any
# clean-up code defined by the EVT_CLOSE handler; for example it may close
# a document contained in a window after first asking the user whether the
# work should be saved. Close can be vetoed by this process (return false),
# whereas Destroy definitely destroys the window.
# ----------------------------------------------------------------------------
