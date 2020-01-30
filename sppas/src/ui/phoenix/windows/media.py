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

from sppas import paths

# ---------------------------------------------------------------------------


class sppasMedia(wx.media.MediaCtrl):
    """Create an extended media control. Inherited from the existing MediaCtrl.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2020  Brigitte Bigi

    Extended feature is the use of a Timer to display a slider and to fix
    a period int time to play.

    """

    # By default, we use a 23:9 ratio
    MIN_WIDTH = 128
    MIN_HEIGHT = 50

    def __init__(self, parent,
                 id=-1,
                 fileName="",
                 pos=wx.DefaultPosition,
                 size=wx.DefaultSize,
                 style=0,
                 szBackend="",
                 validator=wx.DefaultValidator,
                 name="sppasmediaCtrl"):
        """Constructor that calls Create.

        :param parent: (wx.Window) – parent of this control. Must not be None.
        :param id: (wx.WindowID) – id to use for events
        :param fileName: (string) – If not empty, the path of a file to open.
        :param pos: (wx.Point) – Position to put control at.
        :param size: (wx.Size) – Size to put the control at and to stretch movie to.
        :param style: (long) – Optional styles.
        :param szBackend: (string) – Name of backend you want to use, leave blank to make wx.media.MediaCtrl figure it out.
        :param validator: (wx.Validator) – validator to use.
        :param name: (string) – Window name.
        
        """
        self._filename = None
        self._offsets = (0, 0)      # from/to offsets
        self._autoreplay = False    # a play mode
        self._length = 0            # duration of the media in milliseconds
        self._slider = None
        self._refreshTimer = 10     # 10 for audios but should be 40 for videos
        self._loaded = False

        super(sppasMedia, self).__init__(
            parent, id, fileName, pos, size, style, szBackend,
            validator, name)

        try:
            s = wx.GetApp().settings
            self.SetBackgroundColour(s.bg_color)
            self.SetForegroundColour(s.fg_color)
            self.SetFont(s.text_font)
        except AttributeError:
            pass

        # Border width to draw (0=no border)
        self._borderwidth = 2
        self._bordercolor = self.GetForegroundColour()
        self._borderstyle = wx.PENSTYLE_SOLID

        self._timer = wx.Timer(self)
        self.SetInitialSize(size)

        # Bind the events related to our window
        self.Bind(wx.EVT_SIZE, self.OnSize)
        self.Bind(wx.EVT_TIMER, self.OnTimer)
        self.Bind(wx.media.EVT_MEDIA_LOADED, self.__on_media_loaded)

    # -----------------------------------------------------------------------
    # Override.
    # -----------------------------------------------------------------------

    def Load(self, fileName):
        """Load the file that fileName refers to.

        It resets all known information like the length but also the period.

        :param fileName: (string) –
        :return: (bool) False if not loaded (same file or error)

        """
        if self._loaded is True:
            self.Stop()

        # we already opened the same file
        if fileName == self._filename:
            wx.LogWarning('sppasMedia: file {:s} is already loaded.'
                          ''.format(fileName))
            return True

        self.__reset()
        self._filename = fileName
        wx.LogDebug("sppasMedia: Load of {:s}".format(fileName))
        self._loaded = wx.media.MediaCtrl.Load(self, fileName)
        return self._loaded

    # -----------------------------------------------------------------------

    def __on_media_loaded(self, event):
        """Sent when a media has enough data that it can start playing.

        Not sent under windows, but required on MacOS and Linux.

        """
        wx.LogDebug("sppasMedia file {:s} loaded.".format(self._filename))
        self._loaded = True
        # Now, loaded is True, but length is 0 until we attempt to play.
        event.Skip()

    # -----------------------------------------------------------------------

    def __set_length_infos(self):
        if self._loaded is False:
            return False
        length = wx.media.MediaCtrl.Length(self)
        if length == 0:  # **** BUG of the MediaPlayer? ****
            return False
        if length != self._length:
            self._length = length
            if self._offsets == (0, 0):
                # We din't already fixed a period.
                # We set the period to the whole content
                wx.LogDebug("Offset period set to: 0 - {:d}".format(self._length))
                self._offsets = (0, self._length)
            wx.media.MediaCtrl.Seek(self, self._offsets[0], mode=wx.FromStart)
            wx.LogDebug("Media seek to: {:d}".format(self._offsets[0]))

            if self._slider is not None:
                self._slider.SetRange(self._offsets[0], self._offsets[1])
                self._slider.SetValue(self._offsets[0])
                self._slider.SetTickFreq(int(self._offsets[1]/10))
        return True

    # -----------------------------------------------------------------------

    def __reset(self):
        """Reset the media: cancel all known information."""
        self._filename = None
        self._loaded = False
        self._offsets = (0, 0)
        wx.LogMessage("Offset period set to: 0 - 0")
        self._length = 0
        self._timer.Stop()
        self._refreshTimer = 10
        if self._slider is not None:
            self._slider.SetRange(0, 100)
            self._slider.SetValue(0)

    # -----------------------------------------------------------------------

    def LoadURI(self, uri):
        raise NotImplementedError

    # -----------------------------------------------------------------------

    def LoadURIWithProxy(self, uri, proxy):
        raise NotImplementedError

    # -----------------------------------------------------------------------

    def GetPlaybackRate(self):
        raise NotImplementedError

    # -------------------------------------------------------------------------

    def ShowPlayerControls(self, flags=wx.media.MEDIACTRLPLAYERCONTROLS_NONE):
        wx.media.MediaCtrl.ShowPlayerControls(
            self,
            wx.media.MEDIACTRLPLAYERCONTROLS_NONE)

    # -------------------------------------------------------------------------

    def Length(self):
        """Obtain the total amount of time the media has in milliseconds.

        :return: (int)

        """
        return self._length

    # -------------------------------------------------------------------------

    def Pause(self):
        """Pause/Play the media depending on the current state."""
        if self._length == 0:
            return

        state = self.GetState()
        if state == wx.media.MEDIASTATE_PLAYING:
            wx.media.MediaCtrl.Pause(self)

    # ----------------------------------------------------------------------

    def Play(self):
        """Play the media. """
        if self._filename is None:
            wx.LogError("No media file defined")
            return False
        if self._loaded is True:
            state = self.GetState()
            # File is currently playing
            if state == wx.media.MEDIASTATE_PLAYING:
                wx.LogMessage("File {:s} is already playing.".format(self._filename))
                return True
            elif state != wx.media.MEDIASTATE_PAUSED:
                # it's probably the first attempt of playing
                if self.__set_length_infos() is False:
                    wx.LogError("Media loaded but got length 0.")
                    return False
        else:
            wx.LogError("Media is not loaded (length is 0).")
            return False

        self._timer.Start(self._refreshTimer)
        return wx.media.MediaCtrl.Play(self)

    # -------------------------------------------------------------------------

    def Seek(self, offset, mode=wx.FromStart):
        """Seek to a position within the movie.

        :param where: (wx.FileOffset) –
        :param mode: (SeekMode) –
        :return: wx.FileOffset

        """
        if self._loaded is False or self._length == 0:
            return False
        if self._slider is not None:
            self._slider.SetValue(offset)
        return wx.media.MediaCtrl.Seek(self, offset, mode)

    # ----------------------------------------------------------------------

    def Stop(self):
        """Stops the media and disable auto-replay."""
        if self._loaded is False or self._length == 0:
            return

        try:
            wx.media.MediaCtrl.Stop(self)
            self.Seek(self._offsets[0])
            if self._slider is not None:
                self._slider.SetValue(self._offsets[0])
            self._timer.Stop()
            self._autoreplay = False
        except Exception as e:
            # provide errors like:
            # Fatal IO error 11 (Resource temporarily unavailable)
            wx.LogMessage(str(e))
            pass

    # ----------------------------------------------------------------------

    def Close(self, force=False):
        """Close the MediaCtrl."""
        self.Stop()
        del self._timer
        wx.Window.Close(self, force)

    # ----------------------------------------------------------------------

    def Destroy(self):
        """Destroy the MediaCtrl."""
        self.Stop()
        del self._timer
        wx.Window.Destroy(self)

    # ----------------------------------------------------------------------

    def SetInitialSize(self, size=None):
        """Calculate and set a good size.

        Either a size is given and this media size is then forced to it, or
        no size is given and we have two options:

            - the media is a video and the video is already loaded:
              we know its size so we'll set size to it;
            - the media is an audio: its size is (0, 0),
              so we'll force to a min size.

        :param size: an instance of wx.Size.

        """
        self.SetMinSize(wx.Size(sppasMedia.MIN_WIDTH, sppasMedia.MIN_HEIGHT))
        if size is None:
            (w, h) = wx.media.MediaCtrl.GetBestSize(self)
        else:
            (w, h) = size
        wx.LogDebug("w={:d}, h={:d}".format(w, h))

        if w <= 0:
            w = sppasMedia.MIN_WIDTH
        if h <= 0:
            h = sppasMedia.MIN_HEIGHT

        # Ensure a minimum size with the correct aspect ratio
        i = 1.
        w = float(w)
        while w < sppasMedia.MIN_WIDTH:
            w *= 1.5
            i += 1.
            wx.LogDebug("w={:f}, i={:f}".format(w, i))
        w = int(w)
        if i > 1.:
            h = int(float(h) * 1.5 * i)

        wx.media.MediaCtrl.SetInitialSize(self, wx.Size(w, h))

    SetBestSize = SetInitialSize

    # -----------------------------------------------------------------------
    # New features
    # -----------------------------------------------------------------------

    def SetSlider(self, slider):
        """Set a slider to the media.

        The value of the slider is updated with a timer.

        :param slider: (wx.Slider)

        """
        if self._slider is not None:
            raise Exception("A slider is already assigned.")
        if isinstance(slider, wx.Slider):
            self._slider = slider
            self._slider.Bind(wx.EVT_SLIDER, self.__on_seek)
        else:
            raise TypeError("Expected a wx.Slider. Get {:s} instead."
                            "".format(type(slider)))

    # -----------------------------------------------------------------------

    def __on_seek(self, event):
        if self._loaded is False or self._length == 0:
            return
        offset = self._slider.GetValue()
        wx.media.MediaCtrl.Seek(self, offset)
        event.Skip()

    # -----------------------------------------------------------------------

    def SetOffsetPeriod(self, start, end):
        """Fix a start position and a end position to play the media.

        :param start: (int) Start time in milliseconds
        :param end: (int) End time in milliseconds

        """
        if self.GetState() == wx.media.MEDIASTATE_PLAYING:
            self.Stop()

        # Check the given interval
        if start is None or start < 0:
            start = 0
        if end is None:
            end = self._length

        self._offsets = (start, end)
        wx.LogMessage("Offset period set to: {:d} - {:d}".format(start, end))
        if self._slider is not None:
            self._slider.SetRange(start, end)

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

    # ----------------------------------------------------------------------
    # Event callbacks
    # ----------------------------------------------------------------------

    def OnTimer(self, event):
        """Call it if EVT_TIMER is captured."""
        state = self.GetState()
        offset = self.Tell()
        if state == wx.media.MEDIASTATE_PLAYING and self._slider is not None:
            self._slider.SetValue(offset)

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

        self.Draw()
            # On MacOS, it seems that offset is not precise enough...
            # It can be + or - 3 compared to the expected value!

    # ------------------------------------------------------------------------

    def OnEraseBackground(self, event):
        """Handle the wx.EVT_ERASE_BACKGROUND event.

        Override the base method.

        """
        # This is intentionally empty, because we are using the combination
        # of wx.BufferedDC + an empty OnEraseBackground event to
        # reduce flicker
        pass

    # -----------------------------------------------------------------------

    def OnErase(self, evt):
        """Trap the erase event to keep the background transparent on windows.

        :param evt: wx.EVT_ERASE_BACKGROUND

        """
        pass

    # -----------------------------------------------------------------------

    def OnSize(self, event):
        """Handle the wx.EVT_SIZE event.

        :param event: a wx.SizeEvent event to be processed.

        """
        event.Skip()
        self.Draw()

    # -----------------------------------------------------------------------
    # Draw methods (private)
    # -----------------------------------------------------------------------

    def PrepareDraw(self):
        """Prepare the DC to draw the button.

        :returns: gc

        """
        # Create the Graphic Context
        gc = wx.GCDC()
        gc.SetBackground(wx.Brush(self.GetParent().GetBackgroundColour()))

        # In any case, the brush is transparent
        gc.SetBrush(wx.TRANSPARENT_BRUSH)
        gc.SetBackgroundMode(wx.TRANSPARENT)
        if wx.Platform in ['__WXGTK__', '__WXMSW__']:
            # The background needs some help to look transparent on
            # Gtk and Windows
            gc.SetBackground(self.GetBackgroundBrush())

        # Font
        gc.SetFont(self.GetFont())

        return gc

    # ----------------------------------------------------------------------

    def Draw(self):
        """Draw after the WX_EVT_PAINT event.

        """
        # Get the actual client size of ourselves
        width, height = self.GetClientSize()
        wx.LogDebug("Draw method. {:d} {:d}".format(width, height))
        if not width or not height:
            # Nothing to do, we still don't have dimensions!
            return

        gc = self.PrepareDraw()
        self.DrawBackground(gc)
        self.DrawBorder(gc)
        self.DrawContent(gc)

    # -----------------------------------------------------------------------

    def DrawBackground(self, gc):
        w, h = self.GetClientSize()

        brush = self.GetBackgroundBrush()
        if brush is not None:
            gc.SetBackground(brush)
            gc.Clear()

        gc.SetPen(wx.TRANSPARENT_PEN)
        gc.SetBrush(brush)
        gc.DrawRectangle(self._borderwidth,
                         self._borderwidth,
                         w - (2 * self._borderwidth),
                         h - (2 * self._borderwidth))

    # -----------------------------------------------------------------------

    def DrawBorder(self, gc):
        w, h = self.GetClientSize()

        pen = wx.Pen(self._bordercolor, 1, self._borderstyle)
        gc.SetPen(pen)

        # draw the upper left sides
        for i in range(self._borderwidth):
            # upper
            gc.DrawLine(0, i, w - i, i)
            # left
            gc.DrawLine(i, 0, i, h - i)

        # draw the lower right sides
        for i in range(self._borderwidth):
            gc.DrawLine(i, h - i - 1, w + 1, h - i - 1)
            gc.DrawLine(w - i - 1, i, w - i - 1, h)

    # ------------------------------------------------------------------------

    def DrawContent(self, gc):
        self.__draw_label(gc, 20, 50)

    # -----------------------------------------------------------------------

    def __draw_label(self, gc, x, y):
        font = self.GetParent().GetFont()
        gc.SetFont(font)
        gc.SetTextForeground(self.GetParent().GetForegroundColour())

        if self._filename is not None:
            text = self._filename
        else:
            text = "no file"

        gc.SetTextForeground(self.GetParent().GetForegroundColour())
        gc.DrawText(text, x, y)

    # ------------------------------------------------------------------------

    def GetBackgroundBrush(self):
        """Get the brush for drawing the background of the button.

        :returns: (wx.Brush)

        """
        color = self.GetParent().GetBackgroundColour()
        if wx.Platform == '__WXMAC__':
            return wx.TRANSPARENT_BRUSH

        brush = wx.Brush(color, wx.SOLID)
        my_attr = self.GetDefaultAttributes()
        p_attr = self.GetParent().GetDefaultAttributes()
        my_def = color == my_attr.colBg
        p_def = self.GetParent().GetBackgroundColour() == p_attr.colBg
        if my_def and not p_def:
            color = self.GetParent().GetBackgroundColour()
            return wx.Brush(color, wx.SOLID)

        return brush

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
            parent, -1, style=wx.TAB_TRAVERSAL|wx.CLIP_CHILDREN)

        # Create some controls
        backend = ""  # choose default backend, i.e. the system dependent one
        self.mc = sppasMedia(self, style=wx.SIMPLE_BORDER, szBackend=backend)

        # the following event is not sent with the Windows default backend
        # MEDIABACKEND_DIRECTSHOW
        # choose above e.g. MEDIABACKEND_WMP10 if this is a problem for you
        self.mc.Bind(wx.media.EVT_MEDIA_LOADED, self.OnMediaLoaded)
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
        sizer.Add(self.mc, (1, 1), span=(6, 1))
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
        wx.CallAfter(self.DoLoadFile,
                     os.path.join(paths.samples,
                                  "samples-fra",
                                  "F_F_B003-P8.wav"))

    # ----------------------------------------------------------------------

    def OnLoadFile(self, evt):
        dlg = wx.FileDialog(self, message="Choose a media file",
                            defaultDir=paths.samples, defaultFile="",
                            style=wx.FD_OPEN | wx.FD_CHANGE_DIR )
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
            self.playBtn.Enable()

    # ----------------------------------------------------------------------

    def OnMediaLoaded(self, evt):
        self.playBtn.Enable()

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
        m = mimetypes.guess_type(self.mc.GetFilename())
        if m[0] is None:
            mime_type = "unknown"
        else:
            mime_type = m[0]

        if "video" in mime_type:
            self.mc.SetInitialSize()
        else:
            self.mc.SetInitialSize(wx.Size(250, 250))
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
