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

    ui.phoenix.page_annotate.installresource.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""

import wx
import traceback
import sys
import logging

from sppas.src.config import msg, info, error
from sppas.src.utils import u
from sppas.src.preinstall import sppasInstallerDeps

from ..windows.dialogs import sppasDialog
from ..windows.dialogs import sppasProgressDialog
from ..windows.dialogs import Information, Error
from ..windows.panels import sppasPanel
from ..install_window import sppasFeaturesInstallPanel

# ---------------------------------------------------------------------------
# List of displayed messages:


def _(message):
    return u(msg(message, "ui"))


MSG_INSTALL = _("Install a SPPAS resource")
MSG_INSTALL_LANG = _("Install linguistic resources")
MSG_INSTALL_ANNOT = _("Install annotation resources")

INFO_INSTALL_FINISHED = info(560, "install")
INFO_SEE_LOGS = info(512, "install")

MSG_RESTART = _("Restart SPPAS for the changes to take effect.")

# ---------------------------------------------------------------------------


class InstallResourcesDialog(sppasDialog):
    """Create a dialog to install a new feature of type lang or annot.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2020  Brigitte Bigi

    """

    def __init__(self, parent, resource_type=""):
        super(InstallResourcesDialog, self).__init__(
            parent=parent,
            title=MSG_INSTALL,
            style=wx.WANTS_CHARS | wx.TAB_TRAVERSAL | wx.CAPTION |
                  wx.RESIZE_BORDER | wx.CLOSE_BOX | wx.FRAME_TOOL_WINDOW,
            name="install_dialog")

        self._feat_type = resource_type
        delta = self._init_infos()
        try:
            self.__installer = sppasInstallerDeps()
        except Exception as e:
            logging.error("No installation will be performed. The installer "
                          "wasn't created due to the following error: {}"
                          "".format(str(e)))
            exc_type, exc_value, exc_traceback = sys.exc_info()
            logging.error(repr(traceback.format_exception(exc_type, exc_value, exc_traceback)))
            self.__installer = None

        #
        self._create_content(resource_type)
        self.Bind(wx.EVT_BUTTON, self._process_event)

        # Fix this frame properties
        self.Enable()
        self.CenterOnScreen(wx.BOTH)
        self.FadeIn(delta)

    # ------------------------------------------------------------------------

    def _init_infos(self):
        """Overridden. Initialize the main frame.

        Set the title, the icon and the properties of the frame.

        :return: Delta value to fade in the window

        """
        sppasDialog._init_infos(self)

        # Fix some frame properties
        # Fix some frame properties
        self.SetMinSize(wx.Size(sppasDialog.fix_size(320), sppasDialog.fix_size(200)))
        w = int(wx.GetApp().settings.frame_size[0] * 0.8)
        h = int(wx.GetApp().settings.frame_size[1] * 0.8)
        self.SetSize(wx.Size(w, h))

        try:
            delta = wx.GetApp().settings.fade_in_delta
        except AttributeError:
            delta = -5
        return delta

    # -----------------------------------------------------------------------

    def _create_content(self, resource_type):
        """Create the content of the frame.

        Content is made of a menu, an area for anz_panels and action buttons.

        """
        if resource_type == "lang":
            self.CreateHeader(MSG_INSTALL_LANG)
            feats = sppasFeaturesInstallLangPanel(self, installer=self.__installer)

        elif resource_type == "annot":
            self.CreateHeader(MSG_INSTALL_ANNOT)
            feats = sppasFeaturesInstallAnnotPanel(self, installer=self.__installer)

        else:
            self.CreateHeader("Error: unknown resource type to install")
            feats = sppasPanel(self)

        self.SetContent(feats)

        # add some action buttons
        self.CreateActions([wx.ID_APPLY, wx.ID_CLOSE])
        self.SetAffirmativeId(wx.ID_CLOSE)

        # organize the content and lays out.
        self.LayoutComponents()

    # -----------------------------------------------------------------------

    def _process_event(self, event):
        """Process a button of the toolbar event.

        :param event: (wx.Event)

        """
        wx.LogDebug("Toolbar Event received by {:s}".format(self.GetName()))
        btn = event.GetEventObject()

        if btn.GetId() == wx.ID_APPLY:
            self.process_install()
        else:
            event.Skip()

    # -----------------------------------------------------------------------

    def process_install(self):
        """Installation process is here."""
        progress = sppasProgressDialog()
        progress.set_new()
        wx.BeginBusyCursor()
        self.__installer.set_progress(progress)
        errors = self.__installer.install(self._feat_type)
        wx.EndBusyCursor()
        progress.close()

        msg = INFO_INSTALL_FINISHED
        msg += "\n"

        if len(errors) > 0:
            msg += error(500, "install").format("\n".join(errors))
            msg += "\n"
            msg += INFO_SEE_LOGS
            Error(msg)
        else:
            msg += "\n"
            msg += MSG_RESTART
            msg += "\n"
            Information(msg)

# ---------------------------------------------------------------------------


class sppasFeaturesInstallLangPanel(sppasFeaturesInstallPanel):
    """Create a panel to select the features of type lang to enable.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2020  Brigitte Bigi

    """

    def __init__(self, parent, installer=None):
        super(sppasFeaturesInstallLangPanel, self).__init__(
            parent=parent, name="features_lang_panel",
            installer=installer, ft="lang")


# ---------------------------------------------------------------------------


class sppasFeaturesInstallAnnotPanel(sppasFeaturesInstallPanel):
    """Create a panel to select the features of type annot to enable.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2020  Brigitte Bigi

    """

    def __init__(self, parent, installer=None):
        super(sppasFeaturesInstallAnnotPanel, self).__init__(
            parent=parent, name="features_annot_panel",
            installer=installer, ft="annot")
