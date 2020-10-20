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

    ui.phoenix.page_annotate.annotate.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    One of the main pages of the wx4-based GUI of SPPAS: the one to annotate.
    It's content is organized with a wxSimpleBook() with:
        - a page to fix parameters then run, then save the report,
        - 3 pages with the lists of annotations to select and configure,
        - a page with the progress bar and the procedure outcome report.

"""

import wx

from sppas.src.config import msg
from sppas.src.utils import u

from ..windows.panels import sppasPanel
from ..windows import sppasToolbar
from ..windows import sppasStaticLine
from ..main_events import DataChangedEvent, EVT_DATA_CHANGED

from .annotbook import sppasAnnotateBook
from .installresource import InstallResourcesDialog

# ---------------------------------------------------------------------------
# List of displayed messages:


def _(message):
    return u(msg(message, "ui"))


MSG_RESOURCES = _("Resources: ")
MSG_LANG = _("Add languages")
MSG_ANNOT = _("Add annotations")

# ---------------------------------------------------------------------------


class sppasAnnotatePanel(sppasPanel):
    """Create a panel to annotate automatically the checked files.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2020  Brigitte Bigi

    Allows to install new resources.

    """

    TOOLBAR_COLOUR = wx.Colour(250, 120, 50, 196)

    # ------------------------------------------------------------------------

    def __init__(self, parent):
        super(sppasAnnotatePanel, self).__init__(
            parent=parent,
            name="page_annotate",
            style=wx.BORDER_NONE
        )

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
        return self._annbook.get_data()

    # ------------------------------------------------------------------------

    def set_data(self, data):
        """Assign new data to this page.

        :param data: (sppasWorkspace)

        """
        self._annbook.set_data(data)

    # -----------------------------------------------------------------------

    def SetForegroundColour(self, colour):
        """Override. """
        wx.Panel.SetForegroundColour(self, colour)
        for c in self.GetChildren():
            if c.GetName() != "hline":
                c.SetForegroundColour(colour)

    # ------------------------------------------------------------------------
    # Private methods to construct the panel.
    # ------------------------------------------------------------------------

    def _create_content(self):
        """Create the main content."""
        # The view of the Editor page
        main_panel = sppasAnnotateBook(self)

        # The toolbar & the main sizer
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        main_sizer.Add(self._create_toolbar(), 0, wx.EXPAND | wx.BOTTOM, 6)
        main_sizer.Add(self._create_hline(), 0, wx.EXPAND, 0)
        main_sizer.Add(main_panel, 1, wx.EXPAND, 0)
        self.SetSizer(main_sizer)

    @property
    def _annbook(self):
        return self.FindWindow("annotate_book")

    # -----------------------------------------------------------------------

    def _create_toolbar(self):
        """Create the main toolbar.

        :return: (sppasToolbar)

        """
        tb = sppasToolbar(self, name="files_media_toolbar")
        tb.set_focus_color(sppasAnnotatePanel.TOOLBAR_COLOUR)
        tb.AddTitleText(MSG_RESOURCES, self.TOOLBAR_COLOUR, name="files")

        tb.AddButton("add_lang", MSG_LANG)
        tb.AddButton("add_annot", MSG_ANNOT)

        return tb

    # -----------------------------------------------------------------------

    def _create_hline(self):
        """Create an horizontal line, used to separate the anz_panels."""
        line = sppasStaticLine(self, orient=wx.LI_HORIZONTAL, name="hline")
        line.SetMinSize(wx.Size(-1, sppasPanel.fix_size(8)))
        line.SetPenStyle(wx.PENSTYLE_SHORT_DASH)
        line.SetDepth(1)
        line.SetForegroundColour(sppasAnnotatePanel.TOOLBAR_COLOUR)
        return line

    # -----------------------------------------------------------------------
    # Events management
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

        # Bind all events from our buttons (including 'cancel')
        self.Bind(wx.EVT_BUTTON, self._process_event)
        self.Bind(wx.EVT_TOGGLEBUTTON, self._process_event)

    # -----------------------------------------------------------------------

    def _process_event(self, event):
        """Process a button of the toolbar event.

        :param event: (wx.Event)

        """
        wx.LogDebug("Toolbar Event received by {:s}".format(self.GetName()))
        btn = event.GetEventObject()
        btn_name = btn.GetName()

        if btn_name == "add_lang":
            self._add_lang()

        elif btn_name == "add_annot":
            self._add_annot()

        else:
            event.Skip()

    # -----------------------------------------------------------------------

    def _process_key_event(self, event):
        """Process a key event.

        :param event: (wx.Event)

        """
        key_code = event.GetKeyCode()

        if event.AltDown() is True:
            if key_code == 82:  # alt+r Run
                pass

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
        if emitted is self._annbook:
            evt = DataChangedEvent(data=data)
            evt.SetEventObject(self)
            wx.PostEvent(self.GetParent(), evt)
        else:
            self.set_data(data)

    # -----------------------------------------------------------------------

    def _add_lang(self):
        """Open a dialog to add new language resources."""
        dlg = InstallResourcesDialog(self, resource_type="lang")
        dlg.ShowModal()
        dlg.DestroyFadeOut()

    # -----------------------------------------------------------------------

    def _add_annot(self):
        """Open a dialog to add new annotation resources."""
        dlg = InstallResourcesDialog(self, resource_type="annot")
        dlg.ShowModal()
        dlg.DestroyFadeOut()

