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

    ui.phoenix.page_editor.timeline.timeline_panel.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""

import os
import wx

from sppas.src.config import paths  # only for the test
from sppas.src.config import msg
from sppas.src.utils import u

from sppas.src.ui.phoenix.windows import sppasPanel
from sppas.src.ui.phoenix.windows import sppasScrolledPanel

from ..media import MediaEvents

from .timedatatype import TimelineType
from .smmpctrl_risepanel import SMMPCPanel
from .errorview_risepanel import ErrorViewPanel
from .trsview_risepanel import TrsViewPanel
from .audioview_risepanel import AudioViewPanel
from .videoview_risepanel import VideoViewPanel
from .timeevents import EVT_TIMELINE_VIEW, TimelineViewEvent

# ---------------------------------------------------------------------------
# List of displayed messages:


def _(message):
    return u(msg(message, "ui"))


MSG_CLOSE = _("Close")
MSG_UNKNOWN = _("Unknown file format.")

CLOSE_CONFIRM = _("The file contains not saved work that will be "
                  "lost. Are you sure you want to close?")

# ----------------------------------------------------------------------------


class sppasTimelinePanel(sppasPanel):
    """Panel to display opened files and their content in a time-line style.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      contact@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2020 Brigitte Bigi

    The event emitted by this view is TimelineViewEvent with:

        - action="close" and filename to ask for closing the panel
        - action="save" and filename to ask for saving the file of the panel
        - action="collapsed" with the filename and value=the object
        - action="expanded" with the filename and value=the object

    """

    def __init__(self, parent, name="timeline_panel"):
        super(sppasTimelinePanel, self).__init__(
            parent,
            id=wx.ID_ANY,
            pos=wx.DefaultPosition,
            size=wx.DefaultSize,
            style=wx.BORDER_SIMPLE | wx.NO_FULL_REPAINT_ON_RESIZE,
            name=name)

        # To get an easy access to the opened files and their panel
        # (key=filename, value=wx.SizerItem)
        self._files = dict()

        # Create a scrolled panel and a multi media player control system
        self._create_content()

        # Setup the events
        self.smmpc.Bind(wx.EVT_BUTTON, self._process_tool_event)
        self.smmpc.Bind(wx.EVT_TOGGLEBUTTON, self._process_tool_event)
        self._scrolled_panel.Bind(EVT_TIMELINE_VIEW, self._process_time_event)
        self.FindWindow("smmpc_risepanel").Bind(MediaEvents.EVT_MEDIA_LOADED, self.__on_media_loaded)
        self.Bind(MediaEvents.EVT_MEDIA_NOT_LOADED, self.__on_media_not_loaded)

        # Colors and font
        try:
            self.SetBackgroundColour(wx.GetApp().settings.bg_color)
            self.SetForegroundColour(wx.GetApp().settings.fg_color)
            self.SetFont(wx.GetApp().settings.text_font)
        except AttributeError:
            self.InheritAttributes()

        # self.Layout()

    # -----------------------------------------------------------------------
    # Manage the set of files
    # -----------------------------------------------------------------------

    def get_files(self):
        """Return the list of filenames this panel is displaying."""
        return list(self._files.keys())

    # -----------------------------------------------------------------------

    def is_trs(self, name):
        """Return True if name is a transcription file."""
        if name not in self._files:
            return False
        return self._files[name].is_trs()

    # -----------------------------------------------------------------------

    def is_audio(self, name):
        """Return True if name is an audio file."""
        if name not in self._files:
            return False
        return self._files[name].is_audio()

    # -----------------------------------------------------------------------

    def is_video(self, name):
        """Return True if name is a video file."""
        if name not in self._files:
            return False
        return self._files[name].is_video()

    # -----------------------------------------------------------------------

    def is_error(self, name):
        """Return True if name is matching a non-opened file."""
        if name not in self._files:
            return False
        return self._files[name].is_unknown()

    # -----------------------------------------------------------------------

    def is_modified(self, name=None):
        """Return True if the content of the file has changed.

        :param name: (str) Name of a file or none for all files.

        """
        if name is not None:
            page = self._files.get(name, None)
            try:
                changed = page.is_modified()
                return changed
            except:
                return False

        # All files
        for name in self._files:
            page = self._files.get(name, None)
            try:
                if page.is_modified() is True:
                    return True
            except:
                pass

        return False

    # -----------------------------------------------------------------------
    # Manage one file at a time
    # -----------------------------------------------------------------------

    def append_file(self, name):
        """Append a file and create a rise panel to display its content.

        Do not refresh/layout the GUI.

        If the file is a media, its panel will emit action "media_loaded" in
        an event that we'll capture and re-send to the parent.
        If the file is a trs, we'll emit the action "tiers_added" in an event.

        :param name: (str)
        :raise: ValueError

        """
        if name in self._files:
            wx.LogError('Name {:s} is already in the list of files.')
            return False

        else:
            # Create the appropriate XxxxViewPanel
            panel = self._create_panel(name)
            self._sizer.Add(panel, 0, wx.EXPAND, 0)  # no border at all
            self.Bind(wx.EVT_COLLAPSIBLEPANE_CHANGED, self._on_collapse_changed, panel)
            self.Layout()

            self._files[name] = panel

            # For transcription, each panel is managing the content of a file
            if panel.is_trs():
                panel.load()
                all_tiers = panel.get_tier_list()
                self.notify(action="tiers_added", filename=name, value=all_tiers)

            # For media, it's the SMMPC that is managing all files.
            # It's easier to manage media files this way particularly
            # because we need to play synchronously...
            elif panel.is_audio():
                self.smmpc.add_audio(name)

            elif panel.is_video():
                self.smmpc.add_video(name)

            return True

    # -----------------------------------------------------------------------

    def remove_file(self, name, force=False):
        """Remove a panel corresponding to the name of a file.

        Do not refresh/layout the GUI.

        :param name: (str)
        :param force: (bool) Force to remove, even if a file is modified
        :return: (bool) The file was removed or not

        """
        if force is True or self.is_modified(name) is False:

            # Remove of the object
            panel = self._files.get(name, None)
            if panel is None:
                wx.LogError("There's no file with name {:s}".format(name))
                return False

            # If the closed page is a media, this media must be
            # removed of the multimedia player control.
            if panel.is_audio() is True or panel.is_video() is True:
                self.smmpc.remove(name)

            # Destroy the panel and remove of the sizer
            for i, child in enumerate(self.GetChildren()):
                if child == panel:
                    self._sizer.Remove(i)
                    break
            panel.Destroy()

            # Delete of the list
            self._files.pop(name)
            return True

        return False

    # -----------------------------------------------------------------------

    def save_file(self, name):
        """Save a file.

        :param name: (str)
        :return: (bool) The file was saved or not

        """
        panel = self._files.get(name, None)
        saved = False
        if panel.is_modified() is True:
            try:
                saved = panel.save()
                if saved is True:
                    wx.LogMessage("File {:s} saved successfully.".format(name))
            except Exception as e:
                saved = False
                wx.LogError("Error while saving file {:s}: {:s}"
                            "".format(name, str(e)))

        return saved

    # -----------------------------------------------------------------------
    # Methods to operate on a TrsViewPanel()
    # -----------------------------------------------------------------------

    def get_tier_list(self, name):
        """Return the list of sppasTier() of the given file.

        :param name: (str) Name of a file
        :return: (list)

        """
        if name not in self._files:
            return list()

        if self._files[name].is_trs() is True:
            return self._files[name].get_tier_list()

        return list()

    # -----------------------------------------------------------------------

    def get_selected_filename(self):
        """Return the filename of the currently selected tier."""
        for fn in self._files:
            panel = self._files[fn]
            if panel.is_trs() is True:
                tn = panel.get_selected_tiername()
                if tn is not None:
                    return fn

        return None

    # -----------------------------------------------------------------------

    def get_selected_tiername(self):
        """Return the name of the currently selected tier."""
        fn = self.get_selected_filename()
        if fn is not None:
            panel = self._files[fn]
            return panel.get_selected_tiername()

        return None

    # -----------------------------------------------------------------------

    def set_selected_tiername(self, filename, tier_name):
        """Change selected tier.

        :param filename: (str) Name of a file
        :param tier_name: (str) Name of a tier
        :return: (bool)

        """
        for fn in self._files:
            panel = self._files[fn]
            if panel.is_trs() is True:
                if fn == filename:
                    panel.set_selected_tiername(tier_name)
                else:
                    panel.set_selected_tiername(None)

    # -----------------------------------------------------------------------

    def get_selected_annotation(self):
        """Return the index of the currently selected annotation.

        :return: (int) Index or -1 if nor found.

        """
        fn = self.get_selected_filename()
        if fn is not None:
            panel = self._files[fn]
            return panel.get_selected_ann()
        return -1

    # -----------------------------------------------------------------------

    def set_selected_annotation(self, idx):
        """Set the index of the selected annotation.

        :param idx: Index or -1 to cancel the selection.

        """
        fn = self.get_selected_filename()
        if fn is not None:
            panel = self._files[fn]
            panel.set_selected_ann(idx)

    # -----------------------------------------------------------------------
    # Methods to operate on an AudioViewPanel()
    # -----------------------------------------------------------------------

    def enable_audio_infos(self, value=True):
        """Enable or disable the view of the audio information."""
        for fn in self._files:
            panel = self._files[fn]
            if panel.is_audio() is True:
                panel.GetPane().show_infos(bool(value))

        self.Layout()

    # -----------------------------------------------------------------------

    def enable_audio_waveform(self, value=True):
        """Enable or disable the view of the audio waveform."""
        for fn in self._files:
            panel = self._files[fn]
            if panel.is_audio() is True:
                panel.GetPane().show_waveform(bool(value))

        self.Layout()

    # -----------------------------------------------------------------------
    # Methods to operate on a VideoViewPanel()
    # -----------------------------------------------------------------------

    def enable_video_infos(self, value=True):
        """Enable or disable the view of the video information."""
        for fn in self._files:
            panel = self._files[fn]
            if panel.is_video() is True:
                panel.GetPane().show_infos(bool(value))

        self.Layout()

    # -----------------------------------------------------------------------

    def enable_video_film(self, value=True):
        """Enable or disable the view of the video film."""
        for fn in self._files:
            panel = self._files[fn]
            if panel.is_video() is True:
                panel.GetPane().show_film(bool(value))

        self.Layout()

    # -----------------------------------------------------------------------
    # GUI creation
    # -----------------------------------------------------------------------

    def _create_content(self):
        """Create the main content. """
        smmpc = SMMPCPanel(self, name="smmpc_risepanel")
        scrolled = sppasScrolledPanel(self, name="scrolled_panel")
        scrolled.SetupScrolling(scroll_x=False, scroll_y=True)
        sizer = wx.BoxSizer(wx.VERTICAL)
        scrolled.SetSizer(sizer)

        # Fix size&layout
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        main_sizer.Add(smmpc, 0, wx.EXPAND | wx.BOTTOM | wx.LEFT | wx.RIGHT, border=sppasPanel.fix_size(4))
        main_sizer.Add(scrolled, 1, wx.EXPAND | wx.LEFT | wx.RIGHT, border=sppasPanel.fix_size(4))
        self.SetSizer(main_sizer)

    # -----------------------------------------------------------------------

    @property
    def _scrolled_panel(self):
        return self.FindWindow("scrolled_panel")

    @property
    def _sizer(self):
        return self._scrolled_panel.GetSizer()

    @property
    def smmpc(self):
        """Return the SPPAS Multi Media Player Ctrl."""
        return self.FindWindow("smmpc_risepanel").GetPane()

    # -----------------------------------------------------------------------
    # Events management
    # -----------------------------------------------------------------------

    def notify(self, action, filename, value=None):
        """Notify the parent of an event."""
        wx.LogDebug("{:s} notifies its parent {:s} of action {:s}."
                    "".format(self.GetName(), self.GetParent().GetName(), action))
        evt = TimelineViewEvent(action=action, filename=filename, value=value)
        evt.SetEventObject(self)
        wx.PostEvent(self.GetParent(), evt)

    # -----------------------------------------------------------------------

    def _process_time_event(self, event):
        """Process a time view event.

        A child emitted this event to inform an action occurred or to ask
        for an action.

        :param event: (wx.Event)

        """
        try:
            panel = event.GetEventObject()
            action = event.action
            value = event.value
            filename = panel.get_filename()
            if filename not in self._files:
                raise Exception("An unknown panel {:s} emitted an EVT_TIMELINE_VIEW."
                                "".format(filename))
        except Exception as e:
            wx.LogError(str(e))
            return

        # Send the event to the parent, including the filename
        self.notify(action, filename, value)

    # -----------------------------------------------------------------------

    def _process_tool_event(self, event):
        """Process a button event from the player.

        Not implemented yet: the smmpc does not include such tool buttons.

        :param event: (wx.Event)

        """
        btn = event.GetEventObject()
        btn_name = btn.GetName()

        if btn_name == "sound_infos":
            self.enable_audio_infos(btn.GetValue())

        elif btn_name == "sound_wave_lines":
            self.enable_audio_waveform(btn.GetValue())

        elif btn_name == "video_infos":
            self.enable_video_infos(btn.GetValue())

        elif btn_name == "video_film":
            self.enable_video_film(btn.GetValue())

        event.Skip()

    # -----------------------------------------------------------------------

    def _on_collapse_changed(self, evt=None):
        panel = evt.GetEventObject()
        self._collapse_changed(panel)

    # ----------------------------------------------------------------------

    def _collapse_changed(self, panel):
        # Update our layout - the sizer needs to get new sizes
        self.Layout()
        self._scrolled_panel.ScrollChildIntoView(panel)

        # Enable or disable the media into the SMMPC
        if panel.is_audio() is True or panel.is_video() is True:
            self.smmpc.enable(panel.get_filename(), value=panel.IsExpanded())

        # Notify parent: at least, it needs to layout
        if panel.IsExpanded() is True:
            action = "expanded"
        else:
            action = "collapsed"
        self.notify(action, filename=panel.get_filename(), value=panel.GetPane())

    # ----------------------------------------------------------------------

    def __on_media_loaded(self, event):
        filename = event.filename
        panel = self._files[filename]

        if self.smmpc.is_audio(filename):
            wx.LogMessage("Audio loaded successfully: {}".format(filename))
            panel.GetPane().set_audio_data(
                nchannels=self.smmpc.get_nchannels(filename),
                sampwidth=self.smmpc.get_sampwidth(filename),
                framerate=self.smmpc.get_framerate(filename),
                duration=self.smmpc.get_duration(filename),
                frames=None
            )

        elif self.smmpc.is_video(filename):
            wx.LogMessage("Video loaded successfully: {}".format(filename))
            panel.GetPane().set_video_data(
                framerate=self.smmpc.get_framerate(filename),
                duration=self.smmpc.get_duration(filename),
                width=self.smmpc.get_video_width(filename),
                height=self.smmpc.get_video_height(filename)
            )
        panel.Expand()
        self._collapse_changed(panel)

    # ----------------------------------------------------------------------

    def __on_media_not_loaded(self, event):
        filename = event.filename
        wx.LogError("Media file {} not loaded".format(filename))
        panel = self._files[filename]
        panel.Collapse()
        self._collapse_changed(panel)

    # -----------------------------------------------------------------------
    # Private
    # -----------------------------------------------------------------------

    def _create_panel(self, name):
        """Create a view rise panel to display a file.

        :param name: (str) Name of the file to view
        :return: wx.Window

        """
        try:
            with TimelineType() as tt:
                if tt.guess_type(name) == tt.video:
                    panel = VideoViewPanel(self._scrolled_panel, filename=name)

                elif tt.guess_type(name) == tt.audio:
                    panel = AudioViewPanel(self._scrolled_panel, filename=name)

                elif tt.guess_type(name) == tt.transcription:
                    panel = TrsViewPanel(self._scrolled_panel, filename=name)

                elif tt.guess_type(name) == tt.unknown:
                    raise IOError(MSG_UNKNOWN)

        except Exception as e:
            # traceback.print_exc()
            panel = ErrorViewPanel(self._scrolled_panel, name)
            panel.set_error_message(str(e))

        return panel

    # -----------------------------------------------------------------------

    def update_ann(self, trs_filename, idx, what="select"):
        """Modify annotation into the scrolled panel only.

        """
        for filename in self._files:
            panel = self._files[filename]
            if panel.is_trs():
                self._scrolled_panel.ScrollChildIntoView(panel)
                if filename == trs_filename:
                    if what == "select":
                        panel.set_selected_ann(idx)
                    elif what == "update":
                        panel.update_ann(idx)
                    elif what == "delete":
                        panel.delete_ann(idx)
                    elif what == "create":
                        panel.create_ann(idx)

                    break

# ----------------------------------------------------------------------------
# Panel for tests
# ----------------------------------------------------------------------------


class TestPanel(sppasPanel):
    TEST_FILES = (
        os.path.join(paths.samples, "samples-fra", "F_F_B003-P8.wav"),
        os.path.join(paths.samples, "faces", "video_sample.mp4"),
        os.path.join(paths.samples, "annotation-results", "samples-fra", "F_F_B003-P8-palign.xra"),
        os.path.join(paths.samples, "toto.xxx")
    )

    def __init__(self, parent):
        super(TestPanel, self).__init__(
            parent,
            name="Timeline Panel")

        p = sppasTimelinePanel(self)
        s = wx.BoxSizer(wx.VERTICAL)
        s.Add(p, 1, wx.EXPAND)
        self.SetSizer(s)

        for filename in TestPanel.TEST_FILES:
            p.append_file(filename)

        # the size won't be correct when collapsed. we need a layout.
        self.Bind(EVT_TIMELINE_VIEW, self._process_action)

    # -----------------------------------------------------------------------

    def _process_action(self, event):
        """Process an action event from one of the trs panels.

        :param event: (wx.Event)

        """
        panel = event.GetEventObject()
        filename = event.filename
        action = event.action
        value = event.value
        wx.LogDebug("{:s} received an event action {:s} of file {:s} with value {:s}"
                    "".format(self.GetName(), action, filename, str(value)))

        if action == "save":
            panel.save_file(filename)

        elif action == "close":
            closed = panel.remove_file(filename)
            self.Layout()

        elif action == "tiers_added":
            pass

        elif action == "select_tier":
            pass

        elif action in ("collapsed", "expanded"):
            self.Layout()

        else:
            wx.LogDebug("* * *  UNKNOWN ACTION: skip event  * * *")
            event.Skip()
