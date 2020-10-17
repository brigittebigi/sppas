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

    ui.phoenix.page_edit.filesedit.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""

import os
import wx
import mimetypes

from sppas.src.config import paths
from sppas.src.config import msg
from sppas.src.utils import u
import sppas.src.audiodata.aio
import sppas.src.anndata

from ..windows import sppasPanel
from ..windows import sppasScrolledPanel
from ..windows.dialogs import Confirm
from ..windows import sppasMultiPlayerPanel
from ..windows.panels import sppasVerticalRisePanel
from ..windows.buttons import ToggleButton

from .errfileedit import ErrorViewPanel
from .mediafileedit import MediaViewPanel
from .trsfileedit import TrsViewPanel
from .editorevent import EVT_TIME_VIEW, TimeViewEvent

# ---------------------------------------------------------------------------
# List of displayed messages:


def _(message):
    return u(msg(message, "ui"))


MSG_CLOSE = _("Close")

CLOSE_CONFIRM = _("The file contains not saved work that will be "
                  "lost. Are you sure you want to close?")

# ----------------------------------------------------------------------------


class TimeFilesType(object):
    """Enum all types of supported data by the TimeEditFilesPanel.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2020 Brigitte Bigi

    :Example:

        >>>with TimeFilesType() as tt:
        >>>    print(tt.audio)

    This class is a solution to mimic an 'Enum' but is compatible with both
    Python 2.7 and Python 3+.

    """

    def __init__(self):
        """Create the dictionary."""
        self.__dict__ = dict(
            unknown=-1,
            unsupported=0,
            audio=1,
            video=2,
            transcription=3
        )

    # -----------------------------------------------------------------------

    def __enter__(self):
        return self

    # -----------------------------------------------------------------------

    def __exit__(self, exc_type, exc_value, traceback):
        pass

    # -----------------------------------------------------------------------

    def guess_type(self, filename):
        """Return the expected media type of the given filename.

        :return: (MediaType) Integer value of the media type

        """
        mime_type = "unknown"
        if filename is not None:
            m = mimetypes.guess_type(filename)
            if m[0] is not None:
                mime_type = m[0]

        if "video" in mime_type:
            return self.video

        if "audio" in mime_type:
            return self.audio

        fn, fe = os.path.splitext(filename)
        if fe.lower() in sppas.src.anndata.aio.extensions:
            return self.transcription

        return self.unknown

# ----------------------------------------------------------------------------


class PlayerRisePanel(sppasVerticalRisePanel):
    """A panel embedding the multi-player.

     :author:       Brigitte Bigi
     :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
     :contact:      contact@sppas.org
     :license:      GPL, v3
     :copyright:    Copyright (C) 2011-2020 Brigitte Bigi

    """

    MEDIA_COLOUR = wx.Colour(60, 60, 160, 128)

    # -----------------------------------------------------------------------

    def __init__(self, parent, name="player_rise_panel"):
        """Create the panel to manage the media: play, volume, etc.

        """
        super(PlayerRisePanel, self).__init__(parent, name=name)

        player = sppasMultiPlayerPanel(self, style=wx.BORDER_NONE, name="player_controls_panel")
        player.SetFocusColour(PlayerRisePanel.MEDIA_COLOUR)
        player.ShowWidgets(True)
        player.ShowSlider(True)
        player.ShowVolume(True)
        player.SetButtonWidth(32)

        h = sppasPanel.fix_size(32)
        si = ToggleButton(player.widgets_panel, name="sound_infos")
        si.SetValue(True)
        si.SetBorderWidth(1)
        si.SetFocusColour(PlayerRisePanel.MEDIA_COLOUR)
        si.SetMinSize(wx.Size(h, h))
        player.AddWidget(si)

        sw = ToggleButton(player.widgets_panel, name="sound_wave_lines")
        sw.SetValue(True)
        sw.SetBorderWidth(1)
        sw.SetFocusColour(PlayerRisePanel.MEDIA_COLOUR)
        sw.SetMinSize(wx.Size(h, h))
        player.AddWidget(sw)

        self.SetPane(player)
        self.Expand()

    @property
    def player(self):
        return self.FindWindow("player_controls_panel")

    # -----------------------------------------------------------------------

    def _create_toolbar(self):
        """Create a panel with tools, including the collapsible button."""
        sizer = wx.BoxSizer(wx.VERTICAL)
        # Create, disable and hide the button to collapse/expand.
        self._btn = self._create_collapsible_button()
        self._btn.Enable(False)
        self._btn.Hide()
        sizer.Add(self._btn, 0, wx.FIXED_MINSIZE, 0)
        self._tools_panel.SetSizer(sizer)
        w = self.GetButtonWidth()
        # Fix the size of the tools,
        # it's exactly the same than any other rise panel... so all panels are
        # vertically aligned on screen.
        self._tools_panel.SetMinSize(wx.Size(w, w*2))

# ----------------------------------------------------------------------------


class sppasTimeEditFilesPanel(sppasPanel):
    """Panel to display opened files and their content in a time-line style.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      contact@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2020 Brigitte Bigi
    
    The event emitted by this view is TimeViewEvent with:

        - action="close" and filename to ask for closing the panel
        - action="save" and filename to ask for saving the file of the panel

        - action="media_collapsed" with the filename and value=the mediactrl object
        - action="media_expanded" with the filename and value=the mediactrl object
        - action="media_removed" with the filename and value=the mediactrl object

        - action="trs_collapsed" with the filename and value=the list of sppasTier instances
        - action="trs_expanded" with the filename and value=the list of sppasTier instances
        - action="tiers_added" with the filename and value=list of sppasTier instances
        - action="select_tier" with the filename and value=name of the tier

    """

    def __init__(self, parent, name="timeview_panel"):
        super(sppasTimeEditFilesPanel, self).__init__(
            parent,
            id=wx.ID_ANY,
            pos=wx.DefaultPosition,
            size=wx.DefaultSize,
            style=wx.BORDER_SIMPLE | wx.NO_FULL_REPAINT_ON_RESIZE,
            name=name)

        # To get an easy access to the opened files and their panel
        # (key=name, value=wx.SizerItem)
        self._files = dict()

        self._create_content()
        self._player.Bind(wx.EVT_BUTTON, self._process_tool_event)
        self._player.Bind(wx.EVT_TOGGLEBUTTON, self._process_tool_event)
        self._scrolled_panel.Bind(EVT_TIME_VIEW, self._process_time_event)

        # Look&feel
        try:
            self.SetBackgroundColour(wx.GetApp().settings.bg_color)
            self.SetForegroundColour(wx.GetApp().settings.fg_color)
            self.SetFont(wx.GetApp().settings.text_font)
        except AttributeError:
            self.InheritAttributes()

        self.Layout()

    # -----------------------------------------------------------------------
    # Manage the set of files
    # -----------------------------------------------------------------------

    def get_files(self):
        """Return the list of filenames this panel is displaying."""
        return list(self._files.keys())

    # -----------------------------------------------------------------------

    def is_trs(self, name):
        """Return True if name is matching a sppasTranscription."""
        if name not in self._files:
            return False
        if isinstance(self._files[name], TrsViewPanel):
            return True
        return False

    # -----------------------------------------------------------------------

    def is_media(self, name):
        """Return True if name is matching a sppasMediaCtrl."""
        if name not in self._files:
            return False
        if isinstance(self._files[name], MediaViewPanel):
            return True
        return False

    # -----------------------------------------------------------------------

    def is_error(self, name):
        """Return True if name is matching a non-opened file."""
        if name not in self._files:
            return False
        if isinstance(self._files[name], ErrorViewPanel):
            return True
        return False

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

    def set_offset_period(self, start, end):
        """Fix the time range to play the media (milliseconds).

        """
        for filename in self._files:
            panel = self._files[filename]
            if isinstance(panel, TrsViewPanel):
                panel.set_draw_period(start, end)

        return start, end

    # -----------------------------------------------------------------------

    def media_playing(self):
        """Return the first panel we found playing, None instead."""
        return self._player.media_playing()

    # -----------------------------------------------------------------------
    # Manage one file at a time
    # -----------------------------------------------------------------------

    def collapse_file(self, name, value):
        """Collapse or Expand the panel of a given file.

        :param name: (str) Name of the file
        :param value: (bool) True to collapse, False to expand.

        """
        if name not in self._files:
            wx.LogError('Name {:s} is not in the list of files.')
            raise ValueError('Name {:s} is not in the list of files.')
        panel = self._files[name]

        if isinstance(panel, MediaViewPanel) is True:
            media = panel.GetPane()
            if value is True:
                # remove the media of the player
                self._player.remove_media(media)
            else:
                # add the media of the player
                self._player.add_media(media)  #, panel.get_filename())

        panel.Collapse(value)
        self.Layout()

    # -----------------------------------------------------------------------

    def append_file(self, name):
        """Append a file and display its content.

        Do not refresh/layout the GUI.

        :param name: (str)
        :raise: ValueError

        """
        if name in self._files:
            wx.LogError('Name {:s} is already in the list of files.')
            return False

        else:
            # Either create a MediaViewPanel, a TrsViewPanel or an ErrorViewPanel
            panel = self._create_panel(name)

            border = sppasScrolledPanel.fix_size(4)
            self._sizer.Add(panel, 0, wx.EXPAND | wx.RIGHT | wx.LEFT | wx.TOP, border)
            self.Bind(wx.EVT_COLLAPSIBLEPANE_CHANGED, self.OnCollapseChanged, panel)
            self.Layout()

            self._files[name] = panel
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
            if isinstance(panel, MediaViewPanel) is True:
                self._player.remove_media(panel.GetPane())

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

        if isinstance(self._files[name], TrsViewPanel):
            return self._files[name].get_tier_list()

        return list()

    # -----------------------------------------------------------------------

    def get_selected_filename(self):
        """Return the filename of the currently selected tier."""
        for fn in self._files:
            panel = self._files[fn]
            if isinstance(panel, TrsViewPanel) is True:
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
            if isinstance(panel, TrsViewPanel) is True:
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
    # Methods to operate on a MediaViewPanel()
    # -----------------------------------------------------------------------

    def enable_media_infos(self, value=True):
        """Enable or disable the view of the media information."""
        for fn in self._files:
            panel = self._files[fn]
            if isinstance(panel, MediaViewPanel) is True:
                audio_prop = panel.GetAudioProperties()
                if audio_prop is not None:
                    audio_prop.EnableInfos(bool(value))
                    panel.Layout()
                # video_prop = panel.GetVideoProperties()

        self.Layout()

    # -----------------------------------------------------------------------

    def enable_media_waveform(self, value=True):
        """Enable or disable the view of the media waveform."""
        for fn in self._files:
            panel = self._files[fn]
            if isinstance(panel, MediaViewPanel) is True:
                audio_prop = panel.GetAudioProperties()
                if audio_prop is not None:
                    audio_prop.EnableWaveform(bool(value))

        self.Layout()

    # -----------------------------------------------------------------------
    # GUI creation
    # -----------------------------------------------------------------------

    def _create_content(self):
        """Create the main content. """
        w1 = PlayerRisePanel(self)
        w2 = sppasScrolledPanel(self, name="scrolled_panel")
        w2.SetupScrolling(scroll_x=False, scroll_y=True)
        sizer = wx.BoxSizer(wx.VERTICAL)
        w2.SetSizer(sizer)

        # Fix size&layout
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        main_sizer.Add(w2, 1, wx.EXPAND, 0)
        main_sizer.Add(w1, 0, wx.EXPAND | wx.TOP | wx.LEFT | wx.RIGHT, border=sppasPanel.fix_size(4))
        self.SetSizer(main_sizer)

    # -----------------------------------------------------------------------

    @property
    def _scrolled_panel(self):
        return self.FindWindow("scrolled_panel")

    @property
    def _sizer(self):
        return self._scrolled_panel.GetSizer()

    @property
    def _player(self):
        panel = self.FindWindow("player_controls_panel")
        return panel

    # -----------------------------------------------------------------------
    # Events management
    # -----------------------------------------------------------------------

    def notify(self, action, filename, value=None):
        """Notify the parent of an event."""
        wx.LogDebug("{:s} notifies its parent {:s} of action {:s}."
                    "".format(self.GetName(), self.GetParent().GetName(), action))
        evt = TimeViewEvent(action=action, filename=filename, value=value)
        evt.SetEventObject(self)
        wx.PostEvent(self.GetParent(), evt)

    # -----------------------------------------------------------------------

    def _process_tool_event(self, event):
        """Process a button event from the player.

        :param event: (wx.Event)

        """
        btn = event.GetEventObject()
        btn_name = btn.GetName()

        if btn_name == "sound_infos":
            self.enable_media_infos(btn.GetValue())

        elif btn_name == "sound_wave_lines":
            self.enable_media_waveform(btn.GetValue())

        event.Skip()

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
                raise Exception("An unknown panel {:s} emitted an EVT_TIME_VIEW."
                                "".format(filename))
        except Exception as e:
            wx.LogError(str(e))
            return

        if action == "media_loaded":
            wx.LogDebug("{:s} received a media_loaded event".format(self.GetName()))
            self.media_loaded(panel, value)

        # Send the event to the parent (it will layout)
        self.notify(action, filename, value)

    # -----------------------------------------------------------------------

    def OnCollapseChanged(self, evt=None):
        panel = evt.GetEventObject()
        if isinstance(panel, MediaViewPanel) is True:
            if panel.IsExpanded() is True:
                # The panel was collapsed, and now it is expanded.
                self._player.add_media(panel.GetPane())
                self.notify(action="media_collapsed", filename=panel.get_filename(), value=panel.GetPane())
            else:
                self._player.remove_media(panel.GetPane())
                self.notify(action="media_expanded", filename=panel.get_filename(), value=panel.GetPane())

        elif isinstance(panel, TrsViewPanel) is True:
            if panel.IsExpanded() is True:
                # The panel was collapsed, and now it is expanded.
                self.notify(action="trs_collapsed", filename=panel.get_filename(), value=panel.get_tier_list())
            else:
                self.notify(action="trs_expanded", filename=panel.get_filename(), value=panel.get_tier_list())

        elif isinstance(panel, ErrorViewPanel) is True:
            if panel.IsExpanded() is True:
                # The panel was collapsed, and now it is expanded.
                self.notify(action="error_collapsed", filename=panel.get_filename(), value=None)
            else:
                self.notify(action="error_expanded", filename=panel.get_filename(), value=None)

        self.Layout()
        self._scrolled_panel.ScrollChildIntoView(panel)

    # -----------------------------------------------------------------------

    def media_loaded(self, panel, value):
        """Deal with the fact that a media was successfully loaded or not."""
        filename = panel.get_filename()
        media = panel.GetPane()
        if value is True:
            audio_prop = media.GetAudioProperties()
            if audio_prop is not None:
                audio_prop.EnableInfos(self.FindWindow("sound_infos").GetValue())
                audio_prop.EnableWaveform(self.FindWindow("sound_wave_lines").GetValue())
                audio_prop.EnableSpectral(False)  # not implemented
                audio_prop.EnableLevel(False)  # not implemented

        # if value=True: Add the media into the player, expand & layout
        # if value=False: Collapse and layout
        self.collapse_file(filename, not value)

    # -----------------------------------------------------------------------
    # Private
    # -----------------------------------------------------------------------

    def _create_panel(self, name):
        """Create a ViewPanel to display a file.

        If the file is a media, its panel will emit action "media_loaded" in
        an event that we'll capture and re-send to the parent.
        If the file is a trs, we'll emit the action "tiers_added" in an event.

        :param name: (str) Name of the file to view
        :return: wx.Window

        """
        try:
            with TimeFilesType() as tt:
                if tt.guess_type(name) == tt.video:
                    panel = MediaViewPanel(self._scrolled_panel, filename=name)

                elif tt.guess_type(name) == tt.audio:
                    panel = MediaViewPanel(self._scrolled_panel, filename=name)

                elif tt.guess_type(name) == tt.transcription:
                    panel = TrsViewPanel(self._scrolled_panel, filename=name)
                    all_tiers = panel.get_tier_list()
                    self.notify(action="tiers_added", filename=name, value=all_tiers)

                elif tt.guess_type(name) == tt.unsupported:
                    raise IOError("File format not supported.")

                elif tt.guess_type(name) == tt.unknown:
                    raise IOError("Unknown file format.")

        except Exception as e:
            panel = ErrorViewPanel(self._scrolled_panel, name)
            panel.set_error_message(str(e))

        return panel

    # -----------------------------------------------------------------------

    def update_ann(self, trs_filename, idx, what="select"):
        """Modify annotation into the scrolled panel only.

        """
        for filename in self._files:
            panel = self._files[filename]
            if isinstance(panel, TrsViewPanel):
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
        # "C:\\Users\\bigi\\Videos\\agay_2.mp4",
        # os.path.join("/Users/bigi/Movies/Monsters_Inc.For_the_Birds.mpg"),
        # os.path.join("/E/Videos/Monsters_Inc.For_the_Birds.mpg"),
        # os.path.join(paths.samples, "COPYRIGHT.txt"),
        os.path.join(paths.samples, "annotation-results", "samples-fra", "F_F_B003-P8-palign.xra"),
        os.path.join(paths.samples, "samples-fra", "F_F_B003-P8-merge.TextGrid"),
        os.path.join(paths.samples, "toto.xxx"),
        # os.path.join(paths.samples, "toto.ogg")
    )

    def __init__(self, parent):
        super(TestPanel, self).__init__(
            parent,
            name="Time Edit Panel")

        p = sppasTimeEditFilesPanel(self)
        s = wx.BoxSizer(wx.VERTICAL)
        s.Add(p, 1, wx.EXPAND)
        self.SetSizer(s)

        for filename in TestPanel.TEST_FILES:
            p.append_file(filename)

        # the size won't be correct when collapsed. we need a layout.
        self.Bind(EVT_TIME_VIEW, self._process_action)

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
            wx.LogDebug("Closed: {}".format(closed))

        elif action == "tiers_added":
            pass

        elif action == "select_tier":
            pass

        elif action in ("media_collapsed", "media_expanded", "trs_collapsed", "trs_expanded"):
            self.Layout()

        #elif action == "media_loaded":
        #    self.Layout()

        else:
            wx.LogDebug("* * *  UNKNOWN ACTION: skip event  * * *")
            event.Skip()
