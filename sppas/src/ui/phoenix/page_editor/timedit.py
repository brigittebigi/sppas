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

    ui.phoenix.page_edit.timeedit.py
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

from ..windows import sppasScrolledPanel
from ..windows import sppasSplitterWindow
from ..windows import sppasMultiPlayerPanel
from ..windows import MediaEvents
from ..windows import BitmapTextButton
from ..windows.dialogs import Confirm
from ..anz_panels import sppasTiersEditWindow
from ..main_events import ViewEvent, EVT_VIEW

from .errview import ErrorViewPanel
from .timeview import MediaTimeViewPanel
from .timeview import TrsTimeViewPanel

# ---------------------------------------------------------------------------
# List of displayed messages:


def _(message):
    return u(msg(message, "ui"))


MSG_CLOSE = _("Close")

CLOSE_CONFIRM = _("The file contains not saved work that will be "
                  "lost. Are you sure you want to close?")

# ----------------------------------------------------------------------------


class TimeViewType(object):
    """Enum all types of supported data by the TimeView.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2020 Brigitte Bigi

    :Example:

        >>>with TimeViewType() as tt:
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


class TimeEditPanel(sppasScrolledPanel):
    """Panel to display opened files and their content in a time-line style.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      contact@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2020 Brigitte Bigi

    """

    def __init__(self, parent, name="timeview_panel"):
        super(TimeEditPanel, self).__init__(
            parent,
            id=wx.ID_ANY,
            pos=wx.DefaultPosition,
            size=wx.DefaultSize,
            style=wx.BORDER_NONE | wx.NO_FULL_REPAINT_ON_RESIZE,
            name=name)

        # The files of this panel (key=name, value=wx.SizerItem)
        self._files = dict()
        self._hicolor = wx.Colour(200, 200, 180)

        self._create_content()

        # Look&feel
        try:
            self.SetBackgroundColour(wx.GetApp().settings.bg_color)
            self.SetForegroundColour(wx.GetApp().settings.fg_color)
            self.SetFont(wx.GetApp().settings.text_font)
        except AttributeError:
            self.InheritAttributes()

        self.Layout()

    # -----------------------------------------------------------------------

    def GetHighLightColor(self):
        """Get the color to highlight buttons."""
        return self._hicolor

    # -----------------------------------------------------------------------

    def SetHighLightColor(self, color):
        """Set a color to highlight buttons, and for the focus."""
        self._hicolor = color

    # -----------------------------------------------------------------------
    # Manage the set of files
    # -----------------------------------------------------------------------

    def get_files(self):
        """Return the list of filenames this panel is displaying."""
        return list(self._files.keys())

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
        """Add a file and display its content.

        Do not refresh/layout the GUI.

        :param name: (str)
        :raise: ValueError

        """
        if name in self._files:
            wx.LogError('Name {:s} is already in the list of files.')
            raise ValueError('Name {:s} is already in the list of files.')

        try:
            panel = self._add_file(name)
        except Exception as e:
            panel = ErrorViewPanel(self.GetScrolledPanel(), name)
            panel.set_error_message(str(e))
            self.GetScrolledSizer().Add(panel, 0, wx.EXPAND | wx.LEFT | wx.TOP | wx.BOTTOM, 20)
            self.Bind(wx.EVT_COLLAPSIBLEPANE_CHANGED, self.OnCollapseChanged, panel)

        self._files[name] = panel

        # Is there already a selected period?
        period = False
        for filename in self._files:
            panel = self._files[filename]
            if isinstance(panel, TrsTimeViewPanel):
                start, end = panel.get_selected_period()
                if start != 0 or end != 0:
                    period = True
                    break

        if period is False:
            self.__select_first()

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

            # Destroy the panel and remove of the sizer
            for i, child in enumerate(self.GetChildren()):
                if child == panel:
                    self.GetSizer().Remove(i)
                    break
                for c in child.GetChildren():
                    if c == panel:
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
    # Actions on media
    # -----------------------------------------------------------------------

    def set_offset_period(self, start, end):
        """Fix the time range to play the media (milliseconds).

        The change of offset period will:

         - stop all the media,
         - return the real start/end, i.e. the ones the player can deal with.


        """
        # Set the period to the player. It will set to the media.
        s, e = self._player_controls_panel.set_range(start, end)
        for filename in self._files:
            panel = self._files[filename]
            if isinstance(panel, TrsTimeViewPanel):
                panel.set_draw_period(s, e)

        return s, e

    # -----------------------------------------------------------------------

    def media_playing(self):
        """Return the first panel we found playing, None instead."""
        return self._player_controls_panel.media_playing()

    # -----------------------------------------------------------------------

    def media_paused(self):
        """Return the first panel with a paused media or None."""
        return self._player_controls_panel.media_paused()

    # -----------------------------------------------------------------------
    # GUI creation
    # -----------------------------------------------------------------------

    def _create_content(self):
        """Create the main content. """
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        scrolled = self._create_scrolled_content()
        main_sizer.Add(scrolled, 1, wx.EXPAND, 0)
        self.SetSizer(main_sizer)
        self.Bind(wx.EVT_BUTTON, self._process_event)

    # -----------------------------------------------------------------------

    def _create_scrolled_content(self):
        """Override. Create the main panel to display the content.

        In the base class, it is supposed that it returns a scrolled panel.
        In this case, we'll return a wx.Splitter. Window1 of the splitter is
        a player controls, and Window2 is another splitter, in which Window1
        is a scrolled panel and Window2 is a ListCtrl.

        :return: (sppasPanel, wx.Panel, sppasScrolled, ...)

        """
        splitter = sppasSplitterWindow(self, name="horiz_splitter")

        # Window 1 of the splitter: player controls
        p1 = sppasMultiPlayerPanel(splitter, style=wx.BORDER_NONE, name="player_controls_panel")
        best_size = p1.GetBestSize()
        self.__add_custom_controls(p1)
        splitter.Bind(MediaEvents.EVT_MEDIA_ACTION, self._process_media_action)

        # Window 2 of the splitter: a scrolled panel with all media
        p2 = self.__create_scrolled_panel(splitter)

        # Fix size&layout
        splitter.SetMinimumPaneSize(best_size[1])
        splitter.SplitHorizontally(p1, p2, best_size[1])
        splitter.SetSashGravity(0.)

        return splitter

    # -----------------------------------------------------------------------

    def __create_scrolled_panel(self, parent):
        """The returned scrolled panel is at left in a splitter."""
        splitter = sppasSplitterWindow(parent, name="vert_splitter")

        # Window 1 of the splitter: time view of media and other files
        p1 = sppasScrolledPanel(splitter,
                                style=wx.SHOW_SB_ALWAYS | wx.VSCROLL | wx.BORDER_SIMPLE,
                                name="scrolled_views")
        sizer = wx.BoxSizer(wx.VERTICAL)
        p1.SetupScrolling(scroll_x=False, scroll_y=True)
        p1.AlwaysShowScrollbars(False, True)
        p1.SetSizer(sizer)
        p1.Bind(MediaEvents.EVT_MEDIA_ACTION, self._process_media_action)

        # Window 2 of the splitter: edit view of annotated files
        p2 = sppasTiersEditWindow(splitter, name="tiers_edit_splitter")
        splitter.Bind(EVT_VIEW, self._process_editview_event)

        # Fix size&layout
        splitter.SetMinimumPaneSize(sppasScrolledPanel.fix_size(178))
        splitter.SplitVertically(p1, p2, sppasScrolledPanel.fix_size(512))
        splitter.SetSashGravity(0.)

        return splitter

    # -----------------------------------------------------------------------

    def __add_custom_controls(self, control_panel):
        """Add custom widgets to the player controls panel."""
        # to switch anz_panels of the splitter
        btn1 = BitmapTextButton(control_panel.widgets_panel, name="way_up_down")
        control_panel.SetButtonProperties(btn1)
        control_panel.AddWidget(btn1)

        btn2 = BitmapTextButton(control_panel.widgets_panel, name="way_left_right")
        control_panel.SetButtonProperties(btn2)
        control_panel.AddWidget(btn2)

    # -----------------------------------------------------------------------

    @property
    def _player_controls_panel(self):
        return self.FindWindow("player_controls_panel")

    @property
    def _scrolled_view(self):
        return self.FindWindow("scrolled_views")

    # -----------------------------------------------------------------------

    def GetScrolledPanel(self):
        return self.FindWindow("scrolled_views")

    # -----------------------------------------------------------------------

    def GetScrolledSizer(self):
        return self.FindWindow("scrolled_views").GetSizer()

    # -----------------------------------------------------------------------

    def GetScrolledChildren(self):
        return self.FindWindow("scrolled_views").GetChildren()

    # -----------------------------------------------------------------------

    def _add_file(self, name):
        """Create a ViewPanel to display a file.

        :param name: (str) Name of the file to view
        :return: wx.Window

        """
        with TimeViewType() as tt:
            if tt.guess_type(name) == tt.video:
                panel = MediaTimeViewPanel(self.GetScrolledPanel(), filename=name)
            elif tt.guess_type(name) == tt.audio:
                panel = MediaTimeViewPanel(self.GetScrolledPanel(), filename=name)
            elif tt.guess_type(name) == tt.transcription:
                panel = TrsTimeViewPanel(self.GetScrolledPanel(), filename=name)
                panel.SetHighLightColor(self._hicolor)
                trs = panel.get_object()
                if trs is not None:
                    w = self.FindWindow("tiers_edit_splitter")
                    w.add_tiers(name, trs.get_tier_list())
                    # This is the first trs of the panel.
                    # if len(self._files) == 0:
                    #     tier_name = trs[0].get_name()
                    #    selected = w.set_selected_tiername(name, tier_name)
                    #     if selected is True:
                    #         panel.set_selected_tiername(tier_name)

            elif tt.guess_type(name) == tt.unsupported:
                raise IOError("File format not supported.")
            elif tt.guess_type(name) == tt.unknown:
                raise TypeError("Unknown file format.")

        border = sppasScrolledPanel.fix_size(8)
        self.GetScrolledSizer().Add(panel, 0, wx.EXPAND | wx.LEFT | wx.TOP | wx.BOTTOM, border)
        self.Bind(wx.EVT_COLLAPSIBLEPANE_CHANGED, self.OnCollapseChanged, panel)
        self.FindWindow("vert_splitter").Layout()
        self.FindWindow("vert_splitter").UpdateSize()

        return panel

    # -----------------------------------------------------------------------

    def swap_top_down_panels(self):
        splitter = self.FindWindow("horiz_splitter")
        win_1 = splitter.GetWindow1()
        win_2 = splitter.GetWindow2()
        w, h = win_2.GetSize()
        splitter.Unsplit(toRemove=win_1)
        splitter.Unsplit(toRemove=win_2)
        splitter.SplitHorizontally(win_2, win_1, h)

        if win_1 == self._player_controls_panel:
            splitter.SetSashGravity(1.)
        else:
            splitter.SetSashGravity(0.)

        self.Layout()
        splitter.UpdateSize()

    # -----------------------------------------------------------------------

    def swap_left_right_panels(self):
        splitter = self.FindWindow("vert_splitter")
        win_1 = splitter.GetWindow1()
        win_2 = splitter.GetWindow2()
        w, h = win_2.GetSize()
        splitter.Unsplit(toRemove=win_1)
        splitter.Unsplit(toRemove=win_2)

        splitter.SplitVertically(win_2, win_1, w)
        if win_1 == self._scrolled_view:
            splitter.SetSashGravity(1.)
        else:
            splitter.SetSashGravity(0.)

        self.Layout()
        splitter.UpdateSize()

    # -----------------------------------------------------------------------

    def close_page(self, filename):
        """Close the page matching the given filename.

        :param filename: (str)
        :return: (bool) The page was closed.

        """
        if filename not in self._files:
            return False
        page = self._files[filename]

        if page.is_modified() is True:
            wx.LogWarning("File contains not saved changes.")
            # Ask the user to confirm to close (and changes are lost)
            response = Confirm(CLOSE_CONFIRM, MSG_CLOSE)
            if response == wx.ID_CANCEL:
                return False

        removed = self.remove_file(filename, force=True)
        if removed is True:
            self.GetScrolledPanel().Layout()
            self.Layout()
            self.Refresh()

            # The parent will unlock the file in the workspace
            self.notify(action="close", filename=filename)
            return True

        return False

    # -----------------------------------------------------------------------
    # Events management
    # -----------------------------------------------------------------------

    def notify(self, action, filename):
        """Notify the parent of a ViewEvent.

        :param action: (str) the action to perform
        :param filename: (str) name of the file to perform the action

        """
        evt = ViewEvent(action=action, filename=filename)
        evt.SetEventObject(self)
        wx.PostEvent(self.GetParent(), evt)

    # -----------------------------------------------------------------------

    def _process_event(self, event):
        """Process a button of the toolbar event.

        :param event: (wx.Event)

        """
        wx.LogDebug("Toolbar Event received by {:s}".format(self.GetName()))
        btn = event.GetEventObject()
        btn_name = btn.GetName()

        if btn_name == "way_up_down":
            self.swap_top_down_panels()
            pass

        elif btn_name == "way_left_right":
            self.swap_left_right_panels()
            pass

        else:
            event.Skip()

    # -----------------------------------------------------------------------

    def _process_view_event(self, event):
        """Process a view event: an action has to be performed.

        :param event: (wx.Event)

        """
        try:
            panel = event.GetEventObject()
            panel_name = panel.GetName()

            action = event.action
            fn = None
            for filename in self._files:
                p = self._files[filename]
                if p == panel:
                    fn = filename
                    break
            if fn is None:
                raise Exception("Unknown {:s} panel in ViewEvent."
                                "".format(panel_name))
        except Exception as e:
            wx.LogError(str(e))
            return

        if action == "save":
            self.save_file(fn)

        elif action == "close":
            # If the closed page is a media, this media must be removed of the
            # multimedia player control.
            if isinstance(panel, MediaTimeViewPanel):
                self._player_controls_panel.remove_media(panel.GetPane())
            closed = self.close_page(fn)

        elif action == "tier_selected":
            panel = event.GetEventObject()
            trs_filename = panel.get_filename()
            tier_name = panel.get_selected_tiername()

            # change selected tier into the notebook of tier views
            w = self.FindWindow("tiers_edit_splitter")
            changed = w.set_selected_tiername(trs_filename, tier_name)
            if changed is False:
                # switch back to the previously selected tier
                self.__enable_tier_into_scrolled(w.get_filename(),
                                                 w.get_selected_tiername())
            else:
                self.__enable_tier_into_scrolled(trs_filename, tier_name)

        # not implemented yet: child anz_panels don't allow to select an ann
        elif action == "period_selected":
            period = event.value
            # start = int(period[0] * 1000.)
            # end = int(period[1] * 1000.)
            # self.set_offset_period(start, end)

    # -----------------------------------------------------------------------

    def _process_media_action(self, event):
        """Process an action event from the player.

        An action on media files has to be performed.

        :param event: (wx.Event)

        """
        name = event.action
        value = event.value
        wx.LogDebug("Received a player event. "
                    "Action is {:s}. Value is {:s}"
                    "".format(name, str(event.value)))

        if name == "loaded":
            if value is True:
                panel = event.GetEventObject()
                self._player_controls_panel.add_media(panel.GetPane())
                panel.Expand()

        event.Skip()

    # -----------------------------------------------------------------------

    def _process_editview_event(self, event):
        """Process a view event: an action has to be performed.

        :param event: (wx.Event)

        """
        action = event.action
        if action == "tier_selected":
            w = event.GetEventObject()
            trs_filename = w.get_filename()
            tier_name = w.get_selected_tiername()
            self.__enable_tier_into_scrolled(trs_filename, tier_name)

        elif action == "ann_modified":
            w = event.GetEventObject()
            trs_filename = w.get_filename()
            self.__ann_into_scrolled(trs_filename, event.value, what="update")

        elif action == "ann_selected":
            w = event.GetEventObject()
            trs_filename = w.get_filename()
            self.__ann_into_scrolled(trs_filename, event.value, what="select")

        elif action == "ann_deleted":
            w = event.GetEventObject()
            trs_filename = w.get_filename()
            self.__ann_into_scrolled(trs_filename, event.value, what="delete")

    # -----------------------------------------------------------------------

    def OnCollapseChanged(self, evt=None):
        panel = evt.GetEventObject()
        if isinstance(panel, MediaTimeViewPanel) is True:
            if panel.IsExpanded() is True:
                # The panel was collapsed, and now it is expanded.
                self._player_controls_panel.add_media(panel.GetPane())
            else:
                self._player_controls_panel.remove_media(panel.GetPane())

        self.FindWindow("vert_splitter").Layout()
        self.FindWindow("vert_splitter").UpdateSize()
        self.GetScrolledPanel().ScrollChildIntoView(panel)

    # -----------------------------------------------------------------------
    # Private management of the UI
    # -----------------------------------------------------------------------

    def __select_first(self):
        """Select the first annotation of the first tier of the first file."""
        logging.debug("Select the first ann of the first tier of the first file")
        for filename in self._files:
            logging.debug(filename)
            panel = self._files[filename]
            if isinstance(panel, TrsTimeViewPanel):
                logging.debug(" -> is a trs")
                trs = panel.get_object()
                if len(trs) > 0:
                    # enable the tier into the panel of time tier views
                    tier_name = trs[0].get_name()
                    logging.debug(tier_name)

                    # enable the tier into the notebook of list tier views
                    w = self.FindWindow("tiers_edit_splitter")
                    w.set_selected_tiername(filename, tier_name)
                    self.__enable_tier_into_scrolled(filename, tier_name)
                    wx.LogMessage("Tier {:s} selected, from file {:s}"
                                  "".format(tier_name, filename))
                    break

    # -----------------------------------------------------------------------

    def __enable_tier_into_scrolled(self, trs_filename, tier_name):
        """Disable the currently selected tier and enable the new one.

        into the scrolled panel only.

        """
        for filename in self._files:
            panel = self._files[filename]
            if isinstance(panel, TrsTimeViewPanel):
                if filename != trs_filename:
                    panel.set_selected_tiername(None)
                    panel.set_selected_ann(-1)
                else:
                    panel.set_selected_tiername(tier_name)
                    start, end = panel.get_selected_period()
                    self.set_offset_period(start, end)

    # -----------------------------------------------------------------------

    def __ann_into_scrolled(self, trs_filename, idx, what="select"):
        """Modify annotation into the scrolled panel only.

        """
        for filename in self._files:
            panel = self._files[filename]
            if isinstance(panel, TrsTimeViewPanel):
                self.GetScrolledPanel().ScrollChildIntoView(panel)
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
                    self.set_offset_period(start, end)
                    break

# ----------------------------------------------------------------------------
# Panel for tests
# ----------------------------------------------------------------------------


class TestPanel(TimeEditPanel):
    TEST_FILES = (
        os.path.join(paths.samples, "samples-fra", "F_F_B003-P8.wav"),
        # "C:\\Users\\bigi\\Videos\\agay_2.mp4",
        # os.path.join("/Users/bigi/Movies/Monsters_Inc.For_the_Birds.mpg"),
        # os.path.join("/E/Videos/Monsters_Inc.For_the_Birds.mpg"),
        os.path.join(paths.samples, "COPYRIGHT.txt"),
        os.path.join(paths.samples, "annotation-results", "samples-fra", "F_F_B003-P8-palign.xra"),
        # os.path.join(paths.samples, "samples-fra", "F_F_B003-P8-merge.TextGrid"),
        # os.path.join(paths.samples, "toto.xxx"),
        # os.path.join(paths.samples, "toto.ogg")
    )

    def __init__(self, parent):
        super(TestPanel, self).__init__(
            parent,
            name="Time Edit Panel")
        for filename in TestPanel.TEST_FILES:
            self.append_file(filename)
        self.Layout()
        self.Refresh()
