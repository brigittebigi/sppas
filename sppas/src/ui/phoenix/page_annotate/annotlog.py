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

    ui.phoenix.page_annotate.annotlog.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""

import wx
import codecs

from sppas.src.config import sg
from sppas.src.config import msg
from sppas.src.utils import u
from sppas.src.annotations import sppasAnnotationsManager

from sppas.src.config.logs import sppasLogFile

from ..windows import sppasScrolledPanel
from ..windows import BitmapTextButton
from ..windows import sppasTextCtrl
from ..windows import sppasStaticText
from ..windows import sppasProgressDialog
from ..main_events import DataChangedEvent

from .annotevent import PageChangeEvent

# -----------------------------------------------------------------------


def _(message):
    return u(msg(message, "ui"))


ERROR_COLOUR = wx.Colour(220, 30, 10)     # red
INFO_COLOUR = wx.Colour(55, 30, 200)      # blue
IGNORE_COLOUR = wx.Colour(140, 100, 160)  # gray-violet
WARNING_COLOUR = wx.Colour(250, 150, 40)  # orange
OK_COLOUR = wx.Colour(25, 160, 50)        # green

# ---------------------------------------------------------------------------


class sppasLogAnnotatePanel(sppasScrolledPanel):
    """Create a panel to run automatic annotations and show log.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2019  Brigitte Bigi

    Notice that the log_report() filename can be different of the param()
    report filename. It happens if show() is called and param() report
    filename was changed.

    """

    def __init__(self, parent, param):
        super(sppasLogAnnotatePanel, self).__init__(
            parent=parent,
            name="page_annot_log",
            style=wx.BORDER_NONE
        )
        # Manage the report file name of each run
        self.__log_report = sppasLogFile(pattern="report")
        # The annotation parameters (including the displayed report filename)
        self.__param = param
        # internal use: the currently displayed file name
        self.__report = ""
        # The annotations manager
        self.__manager = sppasAnnotationsManager()
        self.__manager.set_do_merge(True)

        self._create_content()
        self._setup_events()
        self.Layout()

    # -----------------------------------------------------------------------
    # Public methods to manage the data
    # -----------------------------------------------------------------------

    def get_param(self):
        return self.__param

    def set_param(self, param):
        self.__param = param

    # ------------------------------------------------------------------------

    def run(self):
        """Perform the automatic annotations of param on data."""
        wx.LogMessage('Perform automatic annotations')

        # The procedure outcome report file.
        self.__report = self.__log_report.get_filename()
        self.__param.set_report_filename(self.__report)
        self.__name_log_text()
        self.Refresh()

        # Prepare the report filename for a next run
        self.__log_report.increment()

        progress = sppasProgressDialog()
        progress.Show(True)
        progress.set_new()

        # Create the progress bar then run the annotations
        self.__manager.annotate(self.__param, progress)

        self.__update_log_text()
        self.Refresh()
        progress.close()

        # Send to parent
        evt = DataChangedEvent(data=self.__param.get_workspace())
        evt.SetEventObject(self)
        wx.PostEvent(self.GetParent(), evt)

    # ------------------------------------------------------------------------

    def show(self):
        """Show the active report."""
        if self.__param.get_report_filename() != self.__report:
            self.__report = self.__param.get_report_filename()
            if self.__report is None:
                self.__clear_log_text()
            else:
                self.__name_log_text()
                self.__update_log_text()

    # ------------------------------------------------------------------------
    # Private methods to construct the panel.
    # ------------------------------------------------------------------------

    def _create_content(self):
        """Create the main content."""
        sizer = wx.BoxSizer(wx.VERTICAL)

        btn_size = sppasScrolledPanel.fix_size(64)

        btn_back_top = BitmapTextButton(self, name="arrow_up")
        btn_back_top.SetFocusWidth(0)
        btn_back_top.SetMinSize(wx.Size(btn_size, btn_size))

        title = sppasStaticText(self, label="Procedure Outcome Report", name="title_text")

        sizer_top = wx.BoxSizer(wx.HORIZONTAL)
        sizer_top.Add(btn_back_top, 0, wx.RIGHT, btn_size // 4)
        sizer_top.Add(title, 1, wx.ALIGN_CENTER)
        sizer.Add(sizer_top, 0, wx.EXPAND)

        log_txt = self.__create_log_text()
        sizer.Add(log_txt, 2, wx.EXPAND | wx.LEFT, btn_size // 4)

        self.SetSizer(sizer)
        self.SetupScrolling(scroll_x=True, scroll_y=True)

    @property
    def _txtctrl(self):
        return self.FindWindow("log_textctrl")

    # -----------------------------------------------------------------------

    def __create_log_text(self):
        style = wx.TE_MULTILINE | wx.TE_READONLY | wx.TE_RICH2 | wx.TE_AUTO_URL | wx.NO_BORDER
        txtctrl = sppasTextCtrl(self, style=style, name="log_textctrl")
        return txtctrl

    # -----------------------------------------------------------------------

    def __clear_log_text(self):
        self._txtctrl.SetValue("")

    # -----------------------------------------------------------------------

    def __name_log_text(self):
        logcontent = "\n" + "Report file is " + self.__report + "\n\n"
        self._txtctrl.SetValue(logcontent)
        self._txtctrl.SetStyle(0, len(logcontent), wx.TextAttr(wx.Colour(245, 25, 25, 128)))

    # -----------------------------------------------------------------------

    def __update_log_text(self):
        """ """
        logcontent = self._txtctrl.GetValue()
        oldi = len(self._txtctrl.GetValue())
        try:
            with codecs.open(self.__report, 'r', sg.__encoding__) as fp:
                logcontent += fp.read()
        except Exception as e:
            logcontent += "The report is not available...\n" \
                          "Error is: %s" % str(e)

        self._txtctrl.SetValue(logcontent)
        self._txtctrl.SetStyle(oldi+1, len(logcontent), self._txtctrl.GetDefaultStyle())

        # Highlight the name of the file.
        # i = logcontent.find("\n", 0)
        # self._txtctrl.SetStyle(0, i, wx.TextAttr(wx.Colour(245, 25, 25, 128)))

        i = oldi
        while i >= 0:
            i = logcontent.find("[ ", oldi)
            if logcontent.find(_("OK"), i, i + 14) > -1:
                self._txtctrl.SetStyle(i, i + 12, wx.TextAttr(OK_COLOUR))

            elif logcontent.find(_("ERROR"), i, i + 14) > -1:
                self._txtctrl.SetStyle(i, i + 12, wx.TextAttr(ERROR_COLOUR))

            elif logcontent.find(_("WARNING"), i, i + 14) > -1:
                self._txtctrl.SetStyle(i, i + 12, wx.TextAttr(WARNING_COLOUR))

            elif logcontent.find(_("INFO"), i, i + 14) > -1:
                self._txtctrl.SetStyle(i, i + 12, wx.TextAttr(INFO_COLOUR))

            elif logcontent.find(_("IGNORED"), i, i + 14) > - 1:
                self._txtctrl.SetStyle(i, i + 12, wx.TextAttr(IGNORE_COLOUR))

            oldi = i + 13

    # -----------------------------------------------------------------------
    # Events management
    # -----------------------------------------------------------------------

    def notify(self):
        """Send the EVT_PAGE_CHANGE to the parent."""
        if self.GetParent() is not None:
            evt = PageChangeEvent(from_page=self.GetName(),
                                  to_page="page_annot_actions",
                                  fct="")
            evt.SetEventObject(self)
            wx.PostEvent(self.GetParent(), evt)

    # -----------------------------------------------------------------------

    def _setup_events(self):
        """Associate a handler function with the events.

        It means that when an event occurs then the process handler function
        will be called.

        """
        # Bind all events from our buttons (including 'exit')
        self.Bind(wx.EVT_BUTTON, self._process_event)

    # -----------------------------------------------------------------------

    def _process_event(self, event):
        """Process any kind of events.

        :param event: (wx.Event)

        """
        event_obj = event.GetEventObject()
        event_name = event_obj.GetName()

        if event_name == "arrow_up":
            self.notify()

    # -----------------------------------------------------------------------

    def SetFont(self, font):
        wx.Window.SetFont(self, font)
        for child in self.GetChildren():
            if child.GetName() == "title_text":
                try:
                    settings = wx.GetApp().settings
                    child.SetFont(settings.header_text_font)
                except:
                    pass
            elif child is self._txtctrl:
                try:
                    settings = wx.GetApp().settings
                    child.SetFont(settings.mono_text_font)
                except:
                    pass
            else:
                child.SetFont(font)

    # -----------------------------------------------------------------------

    def SetForegroundColour(self, colour):
        wx.Window.SetForegroundColour(self, colour)
        for child in self.GetChildren():
            if child.GetName() != "title_text":
                child.SetForegroundColour(colour)
            elif child.GetName() == "title_text":
                try:
                    settings = wx.GetApp().settings
                    child.SetForegroundColour(settings.header_fg_color)
                except:
                    child.SetForegroundColour(colour)
