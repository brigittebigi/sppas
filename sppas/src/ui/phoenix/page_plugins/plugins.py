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

    ui.phoenix.page_plugins.plugins.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    One of the main pages of the wx4-based GUI of SPPAS.

    It manages the set of plugins: install, delete, run.

"""

import logging
import wx

from sppas import msg
from sppas import u
from sppas.src.files import States

from ..windows import sppasPanel
from ..windows import sppasToolbar
from ..dialogs import Error, Information
from ..dialogs import sppasChoiceDialog
from ..dialogs import sppasFileDialog

from ..main_events import DataChangedEvent, EVT_DATA_CHANGED

from .plug_list import sppasPluginsList


# ---------------------------------------------------------------------------
# List of displayed messages:

def _(message):
    return u(msg(message, "ui"))


PGS_TITLE = "Plugins: "
PGS_ACT_ADD = "Install"
PGS_ACT_DEL = "Delete"
PGS_ACT_ADD_ERROR = "Plugin '{:s}' can't be installed due to the following" \
                       " error:\n{!s:s}"
PGS_ACT_DEL_ERROR = "Plugin '{:s}' can't be deleted due to the following" \
                       " error:\n{!s:s}"
FLS_MSG_CONFIRM_DEL = "Are you sure you want to delete the plugin {:s}?"

# ----------------------------------------------------------------------------


class sppasPluginsPanel(sppasPanel):
    """Create a panel to work with plugins on the selected files.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2019  Brigitte Bigi

    """

    HIGHLIGHT_COLOUR = wx.Colour(196, 128, 196, 196)

    def __init__(self, parent):
        super(sppasPluginsPanel, self).__init__(
            parent=parent,
            name="page_plugins",
            style=wx.BORDER_NONE | wx.TAB_TRAVERSAL | wx.WANTS_CHARS | wx.NO_FULL_REPAINT_ON_RESIZE,
        )
        self._create_content()
        self._setup_events()

        self.SetBackgroundColour(wx.GetApp().settings.bg_color)
        self.SetForegroundColour(wx.GetApp().settings.fg_color)
        self.SetFont(wx.GetApp().settings.text_font)

        self.Layout()

    # ------------------------------------------------------------------------
    # Public methods to access the data
    # ------------------------------------------------------------------------

    def get_data(self):
        """Return the data currently displayed in the list of files.

        :returns: (FileData) data of the files-viewer model.

        """
        return self.FindWindow("pluginslist").get_data()

    # ------------------------------------------------------------------------

    def set_data(self, data):
        """Assign new data to this page.

        :param data: (FileData)

        """
        self.FindWindow("pluginslist").set_data(data)

    # ------------------------------------------------------------------------
    # Private methods to construct the panel.
    # ------------------------------------------------------------------------

    def _create_content(self):
        """"""
        tb = self.__create_toolbar()
        fv = sppasPluginsList(self, name="pluginslist")

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(tb, proportion=0, flag=wx.EXPAND, border=0)
        sizer.Add(fv, proportion=1, flag=wx.EXPAND, border=0)
        self.SetSizer(sizer)

        self.SetMinSize(wx.Size(sppasPanel.fix_size(320), sppasPanel.fix_size(200)))
        self.SetAutoLayout(True)

    # -----------------------------------------------------------------------

    def __create_toolbar(self):
        """Create the toolbar."""
        tb = sppasToolbar(self)
        tb.set_focus_color(sppasPluginsPanel.HIGHLIGHT_COLOUR)
        tb.AddTitleText(PGS_TITLE, sppasPluginsPanel.HIGHLIGHT_COLOUR)
        tb.AddButton("plugin-import", PGS_ACT_ADD)
        tb.AddButton("plugin-delete", PGS_ACT_DEL)
        return tb

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

        # The user clicked (LeftDown - LeftUp) an action button of the toolbar
        self.Bind(wx.EVT_BUTTON, self._process_action)

        # The data have changed.
        # This event is sent by any of the children or by the parent
        self.Bind(EVT_DATA_CHANGED, self._process_data_changed)

    # ------------------------------------------------------------------------
    # Callbacks to events
    # ------------------------------------------------------------------------

    def _process_key_event(self, event):
        """Process a key event.

        :param event: (wx.Event)

        """
        key_code = event.GetKeyCode()
        cmd_down = event.CmdDown()
        shift_down = event.ShiftDown()
        logging.debug('Plugins page received a key event. key_code={:d}'.format(key_code))

        event.Skip()

    # ------------------------------------------------------------------------

    def _process_action(self, event):
        """Process an action of a button.

        :param event: (wx.Event)

        """
        name = event.GetButtonObj().GetName()
        logging.debug("Event received of button: {:s}".format(name))

        if name == "plugin-import":
            self._install()

        elif name == "plugin-delete":
            self._delete()

        event.Skip()

    # -----------------------------------------------------------------------

    def _process_data_changed(self, event):
        """Process a change of data.

        Set the data of the event to the other panels.

        :param event: (wx.Event)

        """
        emitted = event.GetEventObject()
        try:
            wkp = event.data
        except AttributeError:
            logging.error('Data were not sent in the event emitted by {:s}'
                          '.'.format(emitted.GetName()))
            return

        plg_panel = self.FindWindow("pluginslist")
        if emitted != plg_panel:
            try:
                plg_panel.set_data(wkp)
            except:
                pass

        # Send the data to the parent
        pm = self.GetParent()
        if pm is not None and emitted != pm:
            wkp.set_state(States().CHECKED)
            evt = DataChangedEvent(data=wkp)
            evt.SetEventObject(self)
            wx.PostEvent(self.GetParent(), evt)

    # ------------------------------------------------------------------------

    def _delete(self):
        """Delete a plugin."""
        logging.debug('User asked to delete a plugin')
        p = self.FindWindow("pluginslist")

        keys = p.get_plugins()
        logging.debug('List of plugins: {:s}'.format(str(keys)))
        if len(keys) == 0:
            Information("No plugin installed.")
            return None

        plugin_id = None
        dlg = sppasChoiceDialog("Select the plugin to delete:", choices=keys)
        if dlg.ShowModal() == wx.ID_OK:
            plugin_id = dlg.GetStringSelection()
            try:
                p.delete(plugin_id)
                Information("Plugin %s was successfully deleted." % plugin_id)
            except Exception as e:
                message = PGS_ACT_DEL_ERROR.format(plugin_id, str(e))
                Error(message, "Delete error")

        dlg.Destroy()

    # ------------------------------------------------------------------------

    def _install(self):
        """Import a plugin from a zip file."""
        logging.debug('User asked to install a plugin')
        p = self.FindWindow("pluginslist")

        # Get the name of the file to be imported
        dlg = sppasFileDialog(self, title=PGS_ACT_ADD,
                              style=wx.FC_OPEN | wx.FC_NOSHOWHIDDEN)
        dlg.SetWildcard("ZIP files|*.zip")  #  |*.[zZ][iI][pP]")
        if dlg.ShowModal() == wx.ID_OK:
            filename = dlg.GetPath()
            try:
                folder = p.install(filename)
                Information("Plugin successfully installed in folder {:s}."
                            "".format(folder))

            except Exception as e:
                message = PGS_ACT_ADD_ERROR.format(filename, str(e))
                Error(message, "Install error")

        dlg.Destroy()
