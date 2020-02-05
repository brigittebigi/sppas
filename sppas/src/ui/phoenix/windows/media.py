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

    src.ui.phoenix.windows.media.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""

import os
import mimetypes
import wx
import wx.media
import wx.lib.newevent

from sppas import paths

# ---------------------------------------------------------------------------


class MediaType(object):
    """Enum of all types of supported media.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2020 Brigitte Bigi

    :Example:

        >>>with MediaType() as mt:
        >>>    print(mt.audio)

    This class is a solution to mimic an 'Enum' but is compatible with both
    Python 2.7 and Python 3+.

    """

    def __init__(self):
        """Create the dictionary."""
        self.__dict__ = dict(
            unknown=-1,
            unsupported=0,
            audio=1,
            video=2
        )

    # -----------------------------------------------------------------------

    def __enter__(self):
        return self

    # -----------------------------------------------------------------------

    def __exit__(self, exc_type, exc_value, traceback):
        pass

# ---------------------------------------------------------------------------


class sppasMedia(wx.Window):
    """Create an extended media control.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2020  Brigitte Bigi

    sppasMedia is using the wx.media.MediaCtrl.
    Extended features are:

        - a normal play or an auto play (to replay);
        - fix an offset period (from, to) in milliseconds;
        - a zoom (percentage) to fix the size of this panel and its media;
        - update a slider (if set);
        - display of the waveform if the media is an audio (To do);
        - send a MediaActionEvent if the mouse did something on the media
          we're interested in.

    The media is embedded and not inherited to allow to capture the paint
    event and to draw a custom "picture" if media is not a video.

    """

    # -----------------------------------------------------------------------
    # Event to be used by the parent to perform an action.
    MediaActionEvent, EVT_MEDIA_ACTION = wx.lib.newevent.NewEvent()
    MediaActionCommandEvent, EVT_MEDIA_ACTION_COMMAND = wx.lib.newevent.NewCommandEvent()

    # -----------------------------------------------------------------------
    # This object size.
    # By default, it is a DFHD aspect ratio (super ultra-wide displays) 32:9
    MIN_WIDTH = 178
    MIN_HEIGHT = 50

    # -----------------------------------------------------------------------

    def __init__(self, parent,
                 id=wx.ID_ANY,
                 pos=wx.DefaultPosition,
                 size=wx.DefaultSize,
                 name="media_ctrl"):
        """Default class constructor.

        :param parent: (wx.Window) parent window. Must not be None;
        :param id: (int) window identifier. -1 indicates a default value;
        :param pos: the control position. (-1, -1) indicates a default
         position, chosen by either the windowing system or wxPython,
         depending on platform;
        :param size: the control size. (-1, -1) indicates a default size,
         chosen by either the windowing system or wxPython, depending on
         platform;
        :param name: (str) Name of the media.

        """

        super(sppasMedia, self).__init__(
            parent, id, pos, size,
            style=wx.BORDER_NONE | wx.TRANSPARENT_WINDOW | wx.TAB_TRAVERSAL | wx.WANTS_CHARS | wx.FULL_REPAINT_ON_RESIZE,
            name=name)

        self._filename = None
        self._offsets = (0, 0)      # from/to offsets
        self._autoreplay = False    # a play mode
        self._length = 0            # duration of the media in milliseconds
        self._refreshtimer = 10     # 10 for audios but should be 40 for videos
        self._loaded = False
        self._slider = None
        self._timer = wx.Timer(self)
        self._mc = wx.media.MediaCtrl(self, style=wx.SIMPLE_BORDER, szBackend="")
        self._mt = MediaType().unknown
        self._zoom = 100

        try:
            # Apply look&feel defined by SPPAS Application
            s = wx.GetApp().settings
            self.SetBackgroundColour(s.bg_color)
            self.SetForegroundColour(s.fg_color)
            self.SetFont(s.text_font)
        except AttributeError:
            # Apply look&feel defined by the parent
            self.InheritAttributes()

        # Fix our min size
        self.SetInitialSize(size)

        # Create the content of the window: only the media...
        s = wx.BoxSizer()
        s.Add(self._mc, 1)
        self.SetSizerAndFit(s)

        # Bind the events related to our window
        self.Bind(wx.EVT_SIZE, self.OnSize)
        self.Bind(wx.EVT_TIMER, self.OnTimer)
        self._mc.Bind(wx.media.EVT_MEDIA_LOADED, self.OnMediaLoaded)
        self.Bind(wx.EVT_PAINT, lambda evt: self.Draw())
        self.Bind(wx.EVT_ERASE_BACKGROUND, self.OnEraseBackground)
        self._mc.Bind(wx.EVT_MOUSE_EVENTS, self.OnMouseEvents)

        # Allow sub-classes to bind other events
        self.InitOtherEvents()

    # -----------------------------------------------------------------------
    # New features: Public methods
    # -----------------------------------------------------------------------

    def SetSlider(self, slider):
        """Set a slider to the media.

        The values MUST be in milliseconds, like for the offset period.
        The value of the slider is updated with a timer.

        :param slider: (wx.Slider)

        """
        if slider is None:
            self._slider = None
        elif isinstance(slider, wx.Slider):
            self._slider = slider
            self._slider.SetRange(self._offsets[0], self._offsets[1])
            self._slider.SetValue(self.Tell())
            self._slider.Bind(wx.EVT_SLIDER, self.__on_slider_seek)
        else:
            raise TypeError("Expected a wx.Slider. Got {:s} instead."
                            "".format(type(slider)))

    # -----------------------------------------------------------------------

    def SetOffsetPeriod(self, start, end):
        """Fix a start position and a end position to play the media.

        :param start: (int) Start time in milliseconds
        :param end: (int) End time in milliseconds

        """
        if self._mc.GetState() == wx.media.MEDIASTATE_PLAYING:
            self.Stop()

        # Check the given interval
        if start is None or start < 0:
            start = 0
        if end is None:
            end = self._length

        self._offsets = (start, end)
        # wx.LogMessage("Offset period set to: {:d} - {:d}".format(start, end))
        if self._slider is not None:
            self._slider.SetRange(start, end)

    # -----------------------------------------------------------------------

    def GetZoom(self):
        """Return the current zoom value."""
        return self._zoom

    # -----------------------------------------------------------------------

    def SetZoom(self, value):
        """Fix the zoom coefficient.

        This coefficient is applied when SetInitialSize is called to enlarge
        or reduce our size and the size of the displayed media.

        :param value: (int) Percentage of zooming, in range 5 .. 300

        """
        value = int(value)
        if value < 5:
            value = 5
        if value > 300:
            value = 300
        self._zoom = value

    # -----------------------------------------------------------------------

    def GetVolume(self):
        """Return the volume (float).

        :return: (float) The volume of the media is a 0.0 to 1.0 range.

        """
        return self._mc.GetVolume()

    # -----------------------------------------------------------------------

    def SetVolume(self, value):
        """Sets the volume of the media from a 0.0 to 1.0 range.

        :param value: (float)

        """
        self._mc.SetVolume(value)

    # -----------------------------------------------------------------------

    def IsPaused(self):
        """Return True if state is wx.media.MEDIASTATE_PAUSED."""
        return self._mc.GetState() == wx.media.MEDIASTATE_PAUSED

    # -----------------------------------------------------------------------

    def IsPlaying(self):
        """Return True if state is wx.media.MEDIASTATE_PLAYING."""
        return self._mc.GetState() == wx.media.MEDIASTATE_PLAYING

    # -----------------------------------------------------------------------

    def IsStopped(self):
        """Return True if state is wx.media.MEDIASTATE_STOPPED."""
        return self._mc.GetState() == wx.media.MEDIASTATE_STOPPED

    # -----------------------------------------------------------------------

    def GetStartPeriod(self):
        """Return start offset (milliseconds)."""
        return self._offsets[0]

    # -----------------------------------------------------------------------

    def GetEndPeriod(self):
        """Return end offset (milliseconds)."""
        return self._offsets[1]

    # -----------------------------------------------------------------------

    @staticmethod
    def ExpectedMediaType(filename):
        """Return the expected media type of the given filename.

        :return: (MediaType) Integer value of the media type

        """
        mime_type = "unknown"
        if filename is not None:
            m = mimetypes.guess_type(filename)
            if m[0] is not None:
                mime_type = m[0]

        if "video" in mime_type:
            return MediaType().video

        if "audio" in mime_type:
            return MediaType().audio

        return MediaType().unknown

    # ----------------------------------------------------------------------

    def AutoPlay(self, start=None, end=None):
        """Play the music and re-play from the beginning."""
        self._autoreplay = True
        self.SetOffsetPeriod(start, end)
        self.Play()

    # ----------------------------------------------------------------------

    def NormalPlay(self, start=None, end=None):
        """Play the music once. Disable auto-replay."""
        self._autoreplay = False
        self.SetOffsetPeriod(start, end)
        self.Play()

    # ----------------------------------------------------------------------

    def GetFilename(self):
        """Return the file associated to the media."""
        return self._filename

    # -----------------------------------------------------------------------

    def InitOtherEvents(self):
        """Initialize other events than paint, mouse, timer or focus.

        Override this method in a subclass to initialize any other events that
        need to be bound.  Added so __init__ method doesn't need to be
        overridden, which is complicated with multiple inheritance.

        """
        pass

    # -----------------------------------------------------------------------
    # Public methods of the wx.media.MediaCtrl.
    # -----------------------------------------------------------------------

    def Load(self, filename):
        """Load the file that filename refers to.

        It resets all known information like the length but also the period.

        :param filename: (str)
        :return: (bool) False if not already loaded

        """
        # If a filename was previously set and file was loaded
        if self._loaded is True:
            self.Stop()

        # we already opened the same file
        if filename == self._filename:
            wx.LogWarning('sppasMedia: file {:s} is already loaded.'
                          ''.format(filename))
            return True

        self.__reset()
        self._filename = filename
        self._loaded = self._mc.Load(filename)
        # Under Windows, Load() always returns True.

        # The current media state is -1. It does not match any of the
        # known media states.
        return self._loaded

    # -------------------------------------------------------------------------

    def Length(self):
        """Obtain the total amount of time the media has in milliseconds.

        :return: (int)

        """
        return self._length

    # -------------------------------------------------------------------------

    def Pause(self):
        """Pause the media if the media is currently playing."""
        if self._length == 0:
            return

        state = self._mc.GetState()
        if state == wx.media.MEDIASTATE_PLAYING:
            self._mc.Pause()

    # ----------------------------------------------------------------------

    def Play(self):
        """Play the media.

        :return: (bool)

        """
        if self._filename is None:
            wx.LogError("No media file defined.")
            return False

        if self._loaded is False:
            wx.LogError("Media file {:s} is not loaded."
                        "".format(self._filename))
            return False

        # OK. We have a filename and the media is declared to be loaded.
        state = self._mc.GetState()
        # Media is currently playing
        if state == wx.media.MEDIASTATE_PLAYING:
            wx.LogMessage("Media file {:s} is already playing."
                          "".format(self._filename))
            return True
        elif state != wx.media.MEDIASTATE_PAUSED:
            # it's probably the first attempt of playing
            if self.__set_infos() is False:
                return False

        self.__validate_offsets()
        self._timer.Start(self._refreshtimer)
        played = self._mc.Play()
        return played

    # -------------------------------------------------------------------------

    def Seek(self, offset, mode=wx.FromStart):
        """Seek to a position within the media.

        Offset must be in the range of the offset period. If the offset period
        is not set, we'll Seek to 0.

        :param offset: (wx.FileOffset)
        :param mode: (SeekMode)
        :return: (wx.FileOffset) Value in milliseconds

        """
        if self._loaded is False or self._length == 0:
            return 0

        if offset < self._offsets[0]:
            offset = self._offsets[0]
        if offset > self._offsets[1]:
            offset = self._offsets[1]

        if self._slider is not None:
            self._slider.SetValue(offset)
        return self._mc.Seek(offset, mode)

    # ----------------------------------------------------------------------

    def Tell(self):
        """Obtain the current position in time within the media.

        :return:( wx.FileOffset) Value in milliseconds

        """
        if self:
            return self._mc.Tell()
        return 0

    # ----------------------------------------------------------------------

    def Stop(self):
        """Stops the media and disable auto-replay."""
        if self._loaded is False or self._length == 0:
            return

        try:
            self._mc.Stop()
            self.Seek(self._offsets[0])
            self._timer.Stop()
            self._autoreplay = False
        except Exception as e:
            # provide errors like:
            # Fatal IO error 11 (Resource temporarily unavailable)
            wx.LogError(str(e))
            pass

    # ----------------------------------------------------------------------
    # Public methods of a wx.Window
    # ----------------------------------------------------------------------

    def Close(self, force=False):
        """Close the sppasMedia."""
        self.Stop()
        del self._timer
        wx.Window.Close(self, force)

    # ----------------------------------------------------------------------

    def Destroy(self):
        """Destroy the sppasMedia."""
        self.Stop()
        wx.Window.DeletePendingEvents(self)
        del self._timer
        wx.Window.Destroy(self)

    # ----------------------------------------------------------------------

    def SetInitialSize(self, size=None):
        """Calculate and set a good size.

        Also sets the window’s minsize to the value passed in for use with
        sizers. This means that if a full or partial size is passed to this
        function then the sizers will use that size instead of the results
        of GetBestSize to determine the minimum needs of the window for
        layout.

        Either a size is given and this media size is then forced to it, or
        no size is given and we have two options:

            - the media is a video and the video is already loaded:
              we know its size so we'll set size to it;
            - the media is an audio: its size is (0, 0),
              so we'll force to a min size.

        :param size: an instance of wx.Size.

        """
        # In any case, we fix a min size...
        self.SetMinSize(wx.Size(sppasMedia.MIN_WIDTH,
                                sppasMedia.MIN_HEIGHT))

        # If a size is given, we'll use it, and that's it!
        if size is not None:
            (w, h) = size
        else:
            self._mc.SetInitialSize()
            (w, h) = self._mc.GetSize()

        # If the media still don't have dimensions
        if w <= 0:
            w = sppasMedia.MIN_WIDTH
        if h <= 0:
            h = sppasMedia.MIN_HEIGHT

        # Apply the zoom coefficient
        w = int(float(w) * float(self._zoom) / 100.)
        h = int(float(h) * float(self._zoom) / 100.)

        # Ensure a minimum size keeping the current aspect ratio
        i = 1.
        w = float(w)
        while w < sppasMedia.MIN_WIDTH:
            w *= 1.5
            i += 1.
        w = int(w)
        if i > 1.:
            h = int(float(h) * 1.5 * i)

        # Fix our size
        wx.Window.SetInitialSize(self, wx.Size(w, h))

        # Fix the size of our wx.media.MediaCtrl (0 if not video)
        if self._mt == MediaType().video:
            self._mc.SetMinSize(wx.Size(w, h))
        else:
            self._mc.SetSize(wx.Size(0, 0))

    SetBestSize = SetInitialSize

    # ----------------------------------------------------------------------
    # Event callbacks
    # ----------------------------------------------------------------------

    def notify(self, action, value=None):
        """The parent has to be informed that an action is required.

        :param action: (str) Name of the action to perform
        :param value: (any) Any kind of value linked to the action

        """
        wx.LogDebug("Notify parent of an action {:s}".format(action))
        evt = sppasMedia.MediaActionEvent(action=action, value=value)
        evt.SetEventObject(self)
        wx.PostEvent(self.GetParent(), evt)

    # -----------------------------------------------------------------------

    def OnMediaLoaded(self, event):
        """Sent when a media has enough data that it can start playing.

        Not sent under windows, but required on MacOS and Linux.

        """
        wx.LogDebug("sppasMedia file {:s} loaded.".format(self._filename))
        self._loaded = True

        # Now, loaded is True, but length is 0 until we attempt to play.
        event.Skip()

    # ----------------------------------------------------------------------

    def OnMouseEvents(self, event):
        """Handle the wx.EVT_MOUSE_EVENTS event.

        Do not accept the event: it could interfere with the media control.

        """
        wx.LogDebug("Received a mouse event.")

        if event.Entering():
            pass

        elif event.Leaving():
            pass

        elif event.LeftDown():
            pass

        elif event.LeftUp():
            wx.LogDebug('{:s} LeftUp'.format(self.GetName()))
            self.notify(action="play")

        elif event.Moving():
            # a motion event and no mouse buttons were pressed.
            pass

        elif event.Dragging():
            # motion while a button was pressed
            pass

        elif event.ButtonDClick():
            wx.LogDebug('{:s} DClick'.format(self.GetName()))
            self.notify(action="stop")

        elif event.RightDown():
            pass

        elif event.RightUp():
            pass

        event.StopPropagation()

    # ----------------------------------------------------------------------

    def OnTimer(self, event):
        """Call it if EVT_TIMER is captured."""
        if not self._mc:
            return
        state = self._mc.GetState()
        offset = self._mc.Tell()
        if state == wx.media.MEDIASTATE_PLAYING and self._slider is not None:
            self._slider.SetValue(offset)

        # wx.LogDebug("Offset=%d, omin=%d, omax=%d, state=%d" % (offset, self._offsets[0], self._offsets[1], state))
        if state == wx.media.MEDIASTATE_STOPPED or \
                (state == wx.media.MEDIASTATE_PLAYING and (offset + 3 > self._offsets[1])):
            # Media reached the end of the file and automatically stopped
            # but our Stop() does much more things
            # or
            # Media is playing and the current position is very close to the
            # end of our limit, so we can stop playing.
            if self._autoreplay is True:
                self.Stop()
                self.AutoPlay(self._offsets[0], self._offsets[1])
            else:
                self.Stop()

        self.Refresh()
            # On MacOS, it seems that offset is not precise enough...
            # It can be + or - 3 compared to the expected value!

    # -----------------------------------------------------------------------

    def OnSize(self, event):
        """Handle the wx.EVT_SIZE event.

        :param event: a wx.SizeEvent event to be processed.

        """
        event.Skip()
        self.Refresh()

    # ------------------------------------------------------------------------

    def OnEraseBackground(self, event):
        """Handle the wx.EVT_ERASE_BACKGROUND event.

        Override the base method.

        """
        # This is intentionally empty, because we are using the combination of
        # wx.BufferedDC + an empty OnEraseBackground event to reduce flicker.
        pass

    # -----------------------------------------------------------------------
    # Draw methods (private)
    # -----------------------------------------------------------------------

    def PrepareDraw(self):
        """Prepare the DC to draw the media.

        :returns: (tuple) dc, gc

        """
        # Create the Graphic Context
        dc = wx.AutoBufferedPaintDCFactory(self)
        gc = wx.GCDC(dc)

        # In any case, the brush is transparent
        dc.SetBrush(wx.TRANSPARENT_BRUSH)
        gc.SetBrush(wx.TRANSPARENT_BRUSH)
        gc.SetBackgroundMode(wx.TRANSPARENT)
        if wx.Platform in ['__WXGTK__', '__WXMSW__']:
            # The background needs some help to look transparent on
            # Gtk and Windows
            gc.SetBackground(self.GetBackgroundBrush(gc))
            gc.Clear()

        # Font
        dc.SetTextForeground(self.GetForegroundColour())
        gc.SetTextForeground(self.GetForegroundColour())
        gc.SetFont(self.GetFont())
        dc.SetFont(self.GetFont())

        return dc, gc

    # ----------------------------------------------------------------------

    def Draw(self):
        """Draw after the WX_EVT_PAINT event."""
        # The paint event could be received after the object was destroyed,
        # because the EVT_TIMER and EVT_PAINT are not queued like others.
        if self:
            # Get the actual client size of ourselves
            width, height = self.GetClientSize()
            if width <= 0 or height <= 0:
                # Nothing to do, we still don't have dimensions!
                return

            dc, gc = self.PrepareDraw()
            self._DrawBackground(dc, gc)
            self._DrawContent(dc, gc)

    # -----------------------------------------------------------------------

    def _DrawBackground(self, dc, gc):
        w, h = self.GetClientSize()

        brush = self.GetBackgroundBrush(dc)
        if brush is not None:
            dc.SetBackground(brush)
            dc.Clear()

        dc.SetPen(wx.TRANSPARENT_PEN)
        dc.SetBrush(brush)
        dc.DrawRectangle(0, 0, w, h)

    # ------------------------------------------------------------------------

    def _DrawContent(self, dc, gc):
        """Draw a content if media is audio or unknown.

        """
        if self._mt == MediaType().unknown:
            self.__draw_label(dc, gc, 20, 20, "No view.")

        elif self._mt == MediaType().unsupported:
            self.__draw_label(dc, gc, 20, 20, "File format not supported.")

        elif self._mt == MediaType().audio:
            self.__draw_label(dc, gc, 20, 20, "View of an audio file is not available.")
            pen = wx.Pen(wx.Colour(128, 128, 128, 128), 2, wx.SOLID)
            w, h = self.GetClientSize()
            dc.SetPen(pen)
            dc.DrawRectangle(0, 0, w, h)

    # -----------------------------------------------------------------------

    def __draw_label(self, dc, gc, x, y, label):
        font = self.GetParent().GetFont()
        gc.SetFont(font)
        dc.SetFont(font)
        if wx.Platform == '__WXGTK__':
            dc.DrawText(label, x, y)
        else:
            gc.DrawText(label, x, y)

    # -----------------------------------------------------------------------

    def GetBackgroundBrush(self, dc):
        """Get the brush for drawing the background of the window.

        :returns: (wx.Brush)

        """
        color = self.GetParent().GetBackgroundColour()

        brush = wx.Brush(color, wx.SOLID)
        my_attr = self.GetDefaultAttributes()
        p_attr = self.GetParent().GetDefaultAttributes()
        my_def = color == my_attr.colBg
        p_def = self.GetParent().GetBackgroundColour() == p_attr.colBg
        if my_def and not p_def:
            color = self.GetParent().GetBackgroundColour()
            brush = wx.Brush(color, wx.SOLID)

        return brush

    # -----------------------------------------------------------------------
    # Private
    # -----------------------------------------------------------------------

    def __on_slider_seek(self, event):
        if self._loaded is False or self._length == 0:
            return
        if self._slider is not None:
            offset = self._slider.GetValue()
            self._mc.Seek(offset)
        event.Skip()

    # -----------------------------------------------------------------------

    def __reset(self):
        """Reset the media: cancel all known information."""
        self._filename = None
        self._loaded = False
        self._offsets = (0, 0)
        self._length = 0
        self._timer.Stop()
        self._refreshtimer = 10
        self._mt = MediaType().unknown
        if self._slider is not None:
            self._slider.SetRange(0, 100)
            self._slider.SetValue(0)

    # -----------------------------------------------------------------------

    def __set_infos(self):
        """Set the length of the media and apply it to objects.

        :return: (bool)

        """
        if self._loaded is False:
            self._mt = MediaType().unknown
            return False

        length = self._mc.Length()
        if length == 0:  # **** BUG of the MediaPlayer? ****
            self._mt = MediaType().unsupported
            wx.LogWarning("The file {:s} is loaded but its length is 0."
                          "".format(self._filename))
            return False

        # if the length has changed (was 0 or was already fixed)
        if length != self._length:
            self._length = length
            self._mt = sppasMedia.ExpectedMediaType(self._filename)
            if self._mt == MediaType().video:
                self._refreshtimer = 40
            else:
                self._refreshtimer = 10

            wx.LogDebug("Media type is {:d}".format(self._mt))
            self.SetInitialSize()

            # if the offset was not fixed
            if self._offsets == (0, 0):
                # We din't already fixed a period.
                # We set the period to the whole content
                self._offsets = (0, self._length)

            # Seek to the beginning of the media
            self._mc.Seek(self._offsets[0], mode=wx.FromStart)

            # Apply to the slider
            if self._slider is not None:
                self._slider.SetRange(self._offsets[0], self._offsets[1])
                self._slider.SetValue(self._offsets[0])

        return True

    # ----------------------------------------------------------------------

    def __validate_offsets(self):
        """Adjust if given offsets are not in an appropriate range."""
        # validate current position
        offset = self._mc.Tell()
        if offset < self._offsets[0]:
            self.Seek(self._offsets[0])
        elif offset > self._offsets[1]:
            self.Seek(self._offsets[0])

        # validate end position
        if self._offsets[1] > self._length:
            self._offsets = (self._offsets[0], self._length)

# ---------------------------------------------------------------------------


class StaticText(wx.StaticText):
    """A StaticText that only updates the label if it has changed, to
    help reduce potential flicker since these controls would be
    updated very frequently otherwise.

    """
    def SetLabel(self, label):
        if label != self.GetLabel():
            wx.StaticText.SetLabel(self, label)

# ---------------------------------------------------------------------------


class TestPanel(wx.Panel):
    def __init__(self, parent):
        super(TestPanel, self).__init__(
            parent, -1, style=wx.TAB_TRAVERSAL | wx.CLIP_CHILDREN)

        # Create some controls
        self.mc = sppasMedia(self)

        self.mc.Bind(wx.media.EVT_MEDIA_LOADED, self.OnMediaLoaded)
        self.Bind(sppasMedia.EVT_MEDIA_ACTION, self.OnMediaAction)
        self.mc.Bind(wx.EVT_TIMER, self.OnTimer)

        btn1 = wx.Button(self, -1, "Load File")
        self.Bind(wx.EVT_BUTTON, self.OnLoadFile, btn1)

        btn2 = wx.Button(self, -1, "Play")
        self.Bind(wx.EVT_BUTTON, self.OnPlay, btn2)
        self.playBtn = btn2

        btn3 = wx.Button(self, -1, "Pause")
        self.Bind(wx.EVT_BUTTON, self.OnPause, btn3)

        btn4 = wx.Button(self, -1, "Stop")
        self.Bind(wx.EVT_BUTTON, self.OnStop, btn4)

        btn5 = wx.Button(self, -1, "AutoPlay")
        self.Bind(wx.EVT_BUTTON, self.OnAutoPlay, btn5)

        slider = wx.Slider(self, -1, 0, 0, 10, style=wx.SL_HORIZONTAL)
        slider.SetMinSize(wx.Size(250, -1))

        self.st_len = StaticText(self, -1, size=(100, -1))
        self.st_pos = StaticText(self, -1, size=(100, -1))

        # setup the layout
        sizer = wx.GridBagSizer(6, 5)
        sizer.Add(self.mc, (1, 1), flag=wx.EXPAND, span=(6, 1))
        sizer.Add(btn1, (1, 3))
        sizer.Add(btn2, (2, 3))
        sizer.Add(btn3, (3, 3))
        sizer.Add(btn4, (4, 3))
        sizer.Add(btn5, (5, 3))
        sizer.Add(slider, (7, 1), flag=wx.EXPAND)
        sizer.Add(self.st_len, (1, 5))
        sizer.Add(self.st_pos, (2, 5))
        self.SetSizer(sizer)

        self.mc.SetSlider(slider)
        wx.CallAfter(
            self.DoLoadFile,
            os.path.join(paths.samples, "samples-fra", "F_F_B003-P8.wav"))

    # ----------------------------------------------------------------------

    def OnLoadFile(self, evt):
        dlg = wx.FileDialog(self, message="Choose a media file",
                            defaultDir=paths.samples, defaultFile="",
                            style=wx.FD_OPEN | wx.FD_CHANGE_DIR)
        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            self.DoLoadFile(path)
        dlg.Destroy()

    # ----------------------------------------------------------------------

    def DoLoadFile(self, path):
        if self.mc.Load(path) is False:
            wx.MessageBox("Unable to load %s: Unsupported format?" % path,
                          "ERROR",
                          wx.ICON_ERROR | wx.OK)
            self.playBtn.Disable()
        else:
            self.mc.SetInitialSize()
            self.GetSizer().Layout()
            w, h = self.mc.GetSize()
            wx.LogMessage("File loaded. Size is w={:d}, h={:d}".format(w, h))
            self.playBtn.Enable()

    # ----------------------------------------------------------------------

    def OnMediaLoaded(self, evt):
        self.playBtn.Enable()

    # ----------------------------------------------------------------------

    def OnMediaAction(self, evt):
        if evt.action == "play":
            if self.mc.IsPlaying():
                self.OnPause(evt)
            else:
                self.OnPlay(evt)
        elif evt.action == "stop":
            self.OnStop(evt)
        evt.StopPropagation()

    # ----------------------------------------------------------------------

    def OnPlay(self, evt):
        if self.mc.NormalPlay() is False:
            self.st_pos.SetLabel('position: 0')
            self.st_len.SetLabel('length: -- seconds')
            wx.MessageBox("Unable to Play media : Unsupported format?",
                          "ERROR",
                          wx.ICON_ERROR | wx.OK)
        else:
            self.__set_media()

    # ----------------------------------------------------------------------

    def OnAutoPlay(self, evt):
        if self.mc.AutoPlay() is False:
            self.st_pos.SetLabel('position: 0')
            self.st_len.SetLabel('length: -- seconds')
            wx.MessageBox("Unable to Play media : Unsupported format?",
                          "ERROR",
                          wx.ICON_ERROR | wx.OK)
        else:
            self.__set_media()

    # ----------------------------------------------------------------------

    def __set_media(self):
        self.GetSizer().Layout()
        self.st_len.SetLabel(
            'length: {:f} seconds'.format(float(self.mc.Length()) / 1000.))

    # ----------------------------------------------------------------------

    def OnPause(self, evt):
        self.mc.Pause()

    # ----------------------------------------------------------------------

    def OnStop(self, evt):
        self.mc.Stop()

    # ----------------------------------------------------------------------

    def OnTimer(self, evt):
        offset = self.mc.Tell()
        self.st_pos.SetLabel('Position: %d' % offset)
        evt.Skip()
