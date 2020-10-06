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

import logging
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


class sppasTimeEditFilesPanel(sppasScrolledPanel):
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
            style=wx.BORDER_NONE | wx.NO_FULL_REPAINT_ON_RESIZE,
            name=name)

        # To get an easy access to files and their panel
        # (key=name, value=wx.SizerItem)
        self._files = dict()

        self._create_content()
        self.Bind(EVT_TIME_VIEW, self._process_time_event)

        # Look&feel
        try:
            self.SetBackgroundColour(wx.GetApp().settings.bg_color)
            self.SetForegroundColour(wx.GetApp().settings.fg_color)
            self.SetFont(wx.GetApp().settings.text_font)
        except AttributeError:
            self.InheritAttributes()

        self.SetupScrolling(scroll_x=False, scroll_y=True)
        self.Layout()

    # -----------------------------------------------------------------------
    # Manage the set of files
    # -----------------------------------------------------------------------

    def get_files(self):
        """Return the list of filenames this panel is displaying."""
        return list(self._files.keys())

    # -----------------------------------------------------------------------

    def set_selected_tiername(self, filename, tier_name):
        """Change selected tier.

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

    def is_trs(self, name):
        """Return True if name is matching a sppasTranscription."""
        if name not in self._files:
            return False
        if isinstance(self._files[name], TrsViewPanel):
            return True
        return False

    # -----------------------------------------------------------------------

    def get_tier_list(self, name):
        if name not in self._files:
            return list()
        if isinstance(self._files[name], TrsViewPanel):
            return self._files[name].get_tier_list()
        return list()

    # -----------------------------------------------------------------------
    # Manage one file at a time
    # -----------------------------------------------------------------------

    def collapse_file(self, name, value):
        if name not in self._files:
            wx.LogError('Name {:s} is not in the list of files.')
            raise ValueError('Name {:s} is not in the list of files.')
        panel = self._files[name]
        panel.Collapse(value)
        self.Layout()

    # -----------------------------------------------------------------------

    def append_file(self, name):
        """Add a file and display its content.

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
            self.GetSizer().Add(panel, 0, wx.EXPAND | wx.RIGHT | wx.LEFT | wx.TOP, border)
            self.Bind(wx.EVT_COLLAPSIBLEPANE_CHANGED, self.OnCollapseChanged, panel)
            self.Layout()

            self._files[name] = panel
            return True

        """
        # Is there already a selected period?
        period = False
        for filename in self._files:
            panel = self._files[filename]
            if isinstance(panel, TrsViewPanel):
                start, end = panel.get_selected_period()
                if start != 0 or end != 0:
                    period = True
                    break

        if period is False:
            self.__select_first()
        """

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

            """
            # If the closed page is a media, this media must be
            # removed of the multimedia player control.
            if isinstance(panel, MediaViewPanel) is True:
                self._player_controls_panel.remove_media(panel.GetPane())

            # Remove the tiers of the annotations list view
            elif isinstance(panel, TrsViewPanel) is True:
                all_tiers = panel.get_tier_list()
                w = self.FindWindow("tiers_edit_splitter")
                w.remove_tiers(name, all_tiers)
            """

            # Destroy the panel and remove of the sizer
            for i, child in enumerate(self.GetChildren()):
                if child == panel:
                    self.GetSizer().Remove(i)
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

    def close_file(self, filename):
        """Close the panel matching the given filename.

        :param filename: (str)
        :return: (bool) The page was closed.

        """
        if filename not in self._files:
            return False
        panel = self._files[filename]

        if panel.is_modified() is True:
            wx.LogWarning("File contains not saved changes.")
            # Ask the user to confirm to close (and changes are lost)
            response = Confirm(CLOSE_CONFIRM, MSG_CLOSE)
            if response == wx.ID_CANCEL:
                return False

        removed = self.remove_file(filename, force=True)
        if removed is True:
            self.Layout()
            self.Refresh()
            return True

        # Take care of the new selected file/tier/annotation
        # ?????

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
    # GUI creation
    # -----------------------------------------------------------------------

    def _create_content(self):
        """Create the main content. """
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(main_sizer)

    # -----------------------------------------------------------------------
    # Events management
    # -----------------------------------------------------------------------

    def notify(self, action, filename, value=None):
        """Notify the parent of an event."""
        # wx.LogDebug("{:s} notifies its parent {:s} of action {:s}."
        #             "".format(self.GetName(), self.GetParent().GetName(), action))
        evt = TimeViewEvent(action=action, filename=filename, value=value)
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
                raise Exception("An unknown panel {:s} emitted an EVT_TIME_VIEW."
                                "".format(filename))
        except Exception as e:
            wx.LogError(str(e))
            return

        if action == "media_loaded":
            panel = event.GetEventObject()
            media = panel.GetPane()
            if value is True:
                self.notify("media_loaded", filename, value=media)
            else:
                self.notify("media_loaded", filename, value=None)

        else:
            # Send the event to the parent.
            self.notify(action, filename, value)

        return

        if action == "save":
            self.save_file(filename)

        elif action == "close":
            closed = self.close_page(filename)

        elif action == "select_tier":
            panel = event.GetEventObject()
            trs_filename = panel.get_filename()
            tier_name = panel.get_selected_tiername()
            self.__enable_tier(trs_filename, tier_name)

        # not implemented yet: child trs panels don't allow to select an ann
        elif action == "period_selected":
            period = event.value
            # start = int(period[0] * 1000.)
            # end = int(period[1] * 1000.)
            # self.set_offset_period(start, end)

        elif action == "loaded":
            if value is True:
                panel = event.GetEventObject()
                media = panel.GetPane()
                self.notify_media(action="add_media", value=media)

                audio_prop = media.GetAudioProperties()
                if audio_prop is not None:
                    audio_prop.EnableWaveform(True)
                    media.SetBestSize()

                panel.Expand()

    # -----------------------------------------------------------------------

    def OnCollapseChanged(self, evt=None):
        panel = evt.GetEventObject()
        if isinstance(panel, MediaViewPanel) is True:
            if panel.IsExpanded() is True:
                # The panel was collapsed, and now it is expanded.
                # self._player_controls_panel.add_media(panel.GetPane())
                self.notify(action="media_collapsed", filename=panel.get_filename(), value=panel.GetPane())
            else:
                # self._player_controls_panel.remove_media(panel.GetPane())
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

        self.ScrollChildIntoView(panel)

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
                    panel = MediaViewPanel(self, filename=name)

                elif tt.guess_type(name) == tt.audio:
                    panel = MediaViewPanel(self, filename=name)

                elif tt.guess_type(name) == tt.transcription:
                    panel = TrsViewPanel(self, filename=name)
                    all_tiers = panel.get_tier_list()
                    self.notify(action="tiers_added", filename=name, value=all_tiers)

                elif tt.guess_type(name) == tt.unsupported:
                    raise IOError("File format not supported.")

                elif tt.guess_type(name) == tt.unknown:
                    raise IOError("Unknown file format.")

        except Exception as e:
            panel = ErrorViewPanel(self, name)
            panel.set_error_message(str(e))

        return panel

    # -----------------------------------------------------------------------

    def __select_first(self):
        """Select the first annotation of the first tier of the first file."""
        logging.debug("Select the first ann of the first tier of the first file")
        for filename in self._files:
            logging.debug(filename)
            panel = self._files[filename]
            if isinstance(panel, TrsViewPanel):
                logging.debug(" -> is a trs")
                all_tiers = panel.get_tier_list()
                if len(all_tiers) > 0:
                    # enable the tier into the panel of time tier views
                    tier_name = all_tiers[0].get_name()

                    # enable the tier into the notebook of list tier views
                    self.__enable_tier(filename, tier_name)
                    wx.LogMessage("Tier {:s} selected, from file {:s}"
                                  "".format(tier_name, filename))
                    break

    # -----------------------------------------------------------------------

    def __enable_tier(self, trs_filename, tier_name):
        """Disable the currently selected tier and enable the new one.

        into the scrolled panel only.

        """
        for filename in self._files:
            panel = self._files[filename]
            if isinstance(panel, TrsViewPanel) is True:
                if filename != trs_filename:
                    panel.set_selected_tiername(None)
                    panel.set_selected_ann(-1)
                else:
                    panel.set_selected_tiername(tier_name)
                    start, end = panel.get_selected_period()
                    ### self.set_offset_period(start, end)
                    # #self.notify(action="period", filename=trs_filename, value=(start, end))
                    # #self.notify(action="select", filename=trs_filename, value=tier_name)

    # -----------------------------------------------------------------------

    def __update_ann(self, trs_filename, idx, what="select"):
        """Modify annotation into the scrolled panel only.

        """
        for filename in self._files:
            panel = self._files[filename]
            if isinstance(panel, TrsViewPanel):
                self.ScrollChildIntoView(panel)
                if filename == trs_filename:
                    if what == "select":
                        panel.set_selected_ann(idx)
                    elif what == "update":
                        panel.update_ann(idx)
                    elif what == "delete":
                        panel.delete_ann(idx)
                    elif what == "create":
                        panel.create_ann(idx)

                    start, end = panel.get_selected_period()
                    ### self.set_offset_period(start, end)
                    # # self.notify(action="period", filename=filename, value=(start, end))
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
        for filename in TestPanel.TEST_FILES:
            p.append_file(filename)

        s = wx.BoxSizer(wx.VERTICAL)
        s.Add(p, 1, wx.EXPAND)
        self.SetSizer(s)

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

        if action == "select_tier":
            panel.set_selected_tiername(value)

        elif action == "save":
            panel.save_file(filename)

        elif action == "close":
            closed = panel.close_file(filename)
            wx.LogDebug("Closed: {}".format(closed))

        elif action == "media_loaded":
            if value is None:
                panel.collapse_file(filename, True)
            else:
                audio_prop = value.GetAudioProperties()
                if audio_prop is not None:
                    audio_prop.EnableWaveform(True)
                panel.collapse_file(filename, False)
            self.Layout()

        elif action == "media_removed":
            panel.collapse_file(filename, True)
            self.Layout()

        elif action == "media_collapsed":
            self.Layout()

        elif action == "media_expanded":
            self.Layout()

        elif action == "trs_collapsed":
            self.Layout()

        elif action == "trs_expanded":
            self.Layout()

        elif action == "tiers_added":
            pass

        elif action == "zoomed":
            self.Layout()

        else:
            wx.LogDebug("* * *  UNKNOWN ACTION: skip event  * * *")
            event.Skip()
