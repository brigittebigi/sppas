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

    ui.phoenix.page_plugins.plug_list.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""

import logging
import wx
import os
import time

from sppas import msg
from sppas import u
from sppas import sppasTypeError
from sppas.src.plugins import sppasPluginsManager
from sppas.src.files import FileData, States

from ..dialogs import Error, Information, AboutPlugin
from ..windows import sppasDialog
from ..windows import sppasScrolledPanel
from ..windows import sppasProgressDialog
from ..windows import sppasPanel
from ..windows import sppasTextCtrl, sppasTitleText
from ..windows import sppasStaticLine
from ..windows import BitmapTextButton, sppasTextButton

from ..panels import sppasOptionsPanel
from ..main_events import DataChangedEvent

# ---------------------------------------------------------------------------
# List of displayed messages:


def _(message):
    return u(msg(message, "ui"))


MSG_CONFIG = _("Configure")
MSG_ABOUT = _("About")

# -----------------------------------------------------------------------


class sppasPluginsList(sppasScrolledPanel):
    """Create the list of panels with plugins.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2019  Brigitte Bigi

    No data is given at the initialization.
    Use set_data() method instead.

    """

    def __init__(self, parent, name="page_plugins_list"):
        super(sppasPluginsList, self).__init__(
            parent=parent,
            style=wx.BORDER_NONE,
            name=name
        )

        # The workspace to work with
        self.__data = FileData()

        # The manager for the plugins
        try:
            self._manager = sppasPluginsManager()
        except Exception as e:
            self._manager = None
            Error("Plugin manager initialization: {:s}".format(str(e)))

        self._create_content()
        self._setup_events()
        self.Layout()

    # ------------------------------------------------------------------------
    # Public methods to access the data
    # ------------------------------------------------------------------------

    def get_data(self):
        """Return the data currently displayed in the list of files.

        :returns: (FileData) data of the files-viewer model.

        """
        return self.__data

    # ------------------------------------------------------------------------

    def set_data(self, data):
        """Assign new data to this page.

        :param data: (FileData)

        """
        if isinstance(data, FileData) is False:
            raise sppasTypeError("FileData", type(data))
        logging.debug('New data to set in the plugins page. '
                      'Id={:s}'.format(data.id))
        self.__data = data

    # -----------------------------------------------------------------------
    # Actions to perform with plugins
    # -----------------------------------------------------------------------

    def get_plugins(self):
        """Return the list of plugin identifiers."""
        return list(self._manager.get_plugin_ids())

    # ------------------------------------------------------------------------

    def delete(self, plugin_id):
        """Ask for the plugin to be removed, remove of the list.

        :returns: plugin identifier of the plugin to be deleted.

        """
        # Destroy the panel and remove of the sizer
        panel_name = plugin_id + "_panel"
        panel = None
        for i, child in enumerate(self.GetChildren()):
            if child.GetName() == panel_name:
                panel = child
                self.GetSizer().Remove(i)
                break
        if panel is None:
            return
        panel.Destroy()

        # Delete of the manager
        self._manager.delete(plugin_id)

        # Re-organize the UI
        self.Layout()
        self.Refresh()

    # ------------------------------------------------------------------------

    def install(self, filename):
        """Import and install a plugin.

        :param filename: (str) ZIP file of the plugin content
        :return: (str) folder in which the plugin is installed

        """
        # fix a name for the plugin directory
        plugin_folder = os.path.splitext(os.path.basename(filename))[0]
        plugin_folder = plugin_folder.replace(' ', "_")

        # install the plugin and display it in the list
        plugin_id = self._manager.install(filename, plugin_folder)
        self._append(self._manager.get_plugin(plugin_id))

        # Update the UI
        self.Layout()
        self.Refresh()
        return plugin_folder

    # ------------------------------------------------------------------------

    def apply(self, plugin_id):
        """Apply the plugin on the data.

        :param plugin_id: (str)

        """
        # Get the list of checked FileName() instances
        checked = self.__data.get_filename_from_state(States().CHECKED)
        logging.info("Apply plugin {:s} on {:d} files."
                     "".format(plugin_id, len(checked)))
        if len(checked) == 0:
            Information("No file(s) selected to apply the plugin on!")
            return

        # Convert the list of FileName() instances into a list of filenames
        checked_fns = [f.get_id() for f in checked]
        start_time = time.time()

        # Apply the plugin
        dlg = sppasPluginConfigureDialog(self, self._manager.get_plugin(plugin_id))
        if dlg.ShowModal() == wx.ID_OK:
            progress = sppasProgressDialog()
            try:
                progress.Show(True)
                progress.set_new()
                self._manager.set_progress(progress)
                log_text = self._manager.run_plugin(plugin_id, checked_fns)
                progress.close()
                progress = None

                # Show the output message
                if len(log_text) > 0:
                    Information(log_text)

                # Add new data into the list
                added = 0
                for f in checked_fns:
                    a = self.__data.add_file(f, brothers=True, ctime=start_time)
                    if a is not None:
                        added += len(a)

                # Notify the data changed (if any)
                if added > 0:
                    logging.info("{:d} files added into the workspace"
                                 "".format(added))
                    evt = DataChangedEvent(data=self.__data)
                    evt.SetEventObject(self)
                    wx.PostEvent(self.GetParent(), evt)

            except Exception as e:
                if progress is not None:
                    progress.close()
                Error(str(e))

        dlg.Destroy()

    # ------------------------------------------------------------------------
    # Create and manage the GUI
    # ------------------------------------------------------------------------

    def _create_content(self):
        """"""
        sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(sizer)

        if self._manager is not None:
            for plugin_id in self._manager.get_plugin_ids():
                plugin = self._manager.get_plugin(plugin_id)
                self._append(plugin)

        self.SetupScrolling(scroll_x=True, scroll_y=True)

    # -----------------------------------------------------------------------

    def _append(self, plugin):
        """Append a plugin into the panel.

        :param plugin (sppasPluginParam) The plugin to append

        """
        border = sppasPanel.fix_size(64) // 8

        pp = sppasPluginDescription(self, plugin)
        self.GetSizer().Add(self.HorizLine(self), 0, wx.EXPAND | wx.TOP | wx.RIGHT | wx.LEFT, border)
        self.GetSizer().Add(pp, 1, wx.EXPAND | wx.RIGHT | wx.LEFT, border)
        self.GetSizer().Add(self.HorizLine(self), 0, wx.EXPAND | wx.BOTTOM | wx.RIGHT | wx.LEFT, border)

    # -----------------------------------------------------------------------

    def HorizLine(self, parent, depth=1):
        """Return an horizontal static line."""
        line = sppasStaticLine(parent, orient=wx.LI_HORIZONTAL)
        line.SetMinSize(wx.Size(-1, depth))
        line.SetSize(wx.Size(-1, depth))
        line.SetPenStyle(wx.PENSTYLE_SOLID)
        line.SetDepth(depth)
        line.SetForegroundColour(self.GetForegroundColour())
        return line

    # -----------------------------------------------------------------------
    # Events management
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

        for plugin_id in self._manager.get_plugin_ids():
            if event_name == plugin_id:
                logging.debug("User clicked plugin {:s}".format(plugin_id))
                self.apply(plugin_id)
                event.Skip()
                break

# ---------------------------------------------------------------------------


class sppasPluginDescription(sppasPanel):
    """Panel to describe the given plugin.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2019  Brigitte Bigi

    """

    def __init__(self, parent, plugin):
        super(sppasPluginDescription, self).__init__(
            parent=parent,
            style=wx.BORDER_NONE,
            name=plugin.get_key() + "_panel"
        )

        # The plugin to work with
        self.__plugin = plugin

        self._create_content()
        self._setup_events()
        self.Layout()

    # -----------------------------------------------------------------------

    def _create_content(self):
        """"""
        apply = self.__create_enable_btn()
        about = self.__create_about_text()
        descr = self.__create_description_sizer()

        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(apply, 0, wx.ALIGN_CENTRE | wx.LEFT, 8)
        sizer.Add(about, 0, wx.ALIGN_CENTRE | wx.RIGHT | wx.LEFT, 8)
        sizer.Add(descr, 1, wx.ALIGN_CENTRE_VERTICAL | wx.RIGHT, 8)

        self.SetSizer(sizer)

    # -----------------------------------------------------------------------

    def __create_enable_btn(self):

        w = sppasPanel.fix_size(64)
        h = sppasPanel.fix_size(48)

        btn_enable = BitmapTextButton(
            self, label=self.__plugin.get_key(),
            name=self.__plugin.get_key())

        btn_enable.SetImage(
            os.path.join(self.__plugin.get_directory(),
                         self.__plugin.get_icon()))
        btn_enable.LabelPosition = wx.BOTTOM
        btn_enable.Spacing = 6
        btn_enable.FocusWidth = 0
        btn_enable.BorderWidth = 0
        btn_enable.BitmapColour = self.GetForegroundColour()
        btn_enable.SetMinSize(wx.Size(w, h))

        return btn_enable

    # -----------------------------------------------------------------------

    def __create_about_text(self):
        w = sppasPanel.fix_size(96)
        h = sppasPanel.fix_size(32)

        btn_about = sppasTextButton(
            self, label=MSG_ABOUT + "...", name="about_plugin")
        btn_about.SetForegroundColour(wx.Colour(80, 100, 220))
        btn_about.SetMinSize(wx.Size(w, h))

        return btn_about

    # -----------------------------------------------------------------------

    def __create_description_sizer(self):
        s = wx.BoxSizer(wx.VERTICAL)
        tt = sppasTitleText(self, label=self.__plugin.get_name(), name="text_title")

        text_style = wx.TAB_TRAVERSAL | \
                     wx.TE_MULTILINE | \
                     wx.TE_READONLY | \
                     wx.TE_BESTWRAP | \
                     wx.TE_AUTO_URL | \
                     wx.NO_BORDER | \
                     wx.TE_RICH
        td = sppasTextCtrl(self, value=self.__plugin.get_descr(), style=text_style)

        s.Add(tt, 0, wx.ALIGN_CENTRE_VERTICAL, wx.ALL, 4)
        s.Add(td, 1, wx.EXPAND | wx.ALIGN_CENTRE_VERTICAL | wx.ALL, 4)
        return s

    # -----------------------------------------------------------------------
    # Events management
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

        if event_name == "about_plugin":
            AboutPlugin(self, self.__plugin)

        event.Skip()

    # -----------------------------------------------------------------------

    def SetFont(self, font):
        wx.Window.SetFont(self, font)
        for c in self.GetChildren():
            if c.GetName() != "text_title":
                c.SetFont(font)

    # -----------------------------------------------------------------------

    def SetForegroundColour(self, colour):
        wx.Window.SetForegroundColour(self, colour)
        for c in self.GetChildren():
            if c.GetName() != "about_plugin":
                c.SetForegroundColour(colour)

    # -----------------------------------------------------------------------

    def SetBackgroundColour(self, colour):
        r, g, b = colour.Red(), colour.Green(), colour.Blue()
        delta = 10
        if (r + g + b) > 384:
            colour = wx.Colour(r, g, b, 50).ChangeLightness(100 - delta)
        else:
            colour = wx.Colour(r, g, b, 50).ChangeLightness(100 + delta)

        wx.Window.SetBackgroundColour(self, colour)
        for c in self.GetChildren():
            c.SetBackgroundColour(colour)

# ---------------------------------------------------------------------------


class sppasPluginConfigureDialog(sppasDialog):
    """Dialog to configure the given plugin.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2019  Brigitte Bigi

    Returns either wx.ID_CANCEL or wx.ID_OK if ShowModal().

    """
    def __init__(self, parent, plugin):
        """Create a dialog to fix an annotation config.

        :param parent: (wx.Window)

        """
        super(sppasPluginConfigureDialog, self).__init__(
            parent=parent,
            title="plugin_configure",
            style=wx.DEFAULT_FRAME_STYLE | wx.DIALOG_NO_PARENT)

        self.plugin = plugin
        self.items = []
        self._options_key = []

        self.CreateHeader(MSG_CONFIG + " {:s}".format(plugin.get_name()),
                          "wizard-config")
        self._create_content()
        self._create_buttons()

        # Bind events
        self.Bind(wx.EVT_BUTTON, self._process_event)

        self.LayoutComponents()
        self.GetSizer().Fit(self)
        self.CenterOnParent()
        self.FadeIn(deltaN=-8)

    # -----------------------------------------------------------------------

    def _create_content(self):
        """Create the content of the dialog."""
        all_options = self.plugin.get_options()
        selected_options = []
        for option in all_options:
            if option.get_key() != "input" and option.get_value() != "input":
                self._options_key.append(option.get_key())
                selected_options.append(option)

        options_panel = sppasOptionsPanel(self, selected_options)
        options_panel.SetAutoLayout(True)
        self.items = options_panel.GetItems()
        self.SetContent(options_panel)

    # -----------------------------------------------------------------------

    def _create_buttons(self):
        self.CreateActions([wx.ID_CANCEL, wx.ID_OK])
        self.Bind(wx.EVT_BUTTON, self._process_event)
        self.SetAffirmativeId(wx.ID_OK)

    # -----------------------------------------------------------------------

    def _process_event(self, event):
        """Process any kind of events.

        :param event: (wx.Event)

        """
        event_obj = event.GetEventObject()
        event_id = event_obj.GetId()

        if event_id == wx.ID_CANCEL:
            self.SetReturnCode(wx.ID_CANCEL)
            self.Close()

        elif event_id == wx.ID_OK:
            # Set the list of "Option" instances to the plugin
            for i, item in enumerate(self.items):
                new_value = item.GetValue()
                key = self._options_key[i]
                option = self.plugin.get_option_from_key(key)
                option.set_value(str(new_value))
            # OK. Close the dialog and return wxID_OK
            self.EndModal(wx.ID_OK)
