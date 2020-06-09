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

    src.ui.phoenix.windows.media.mediactrl.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""

import logging
import os
import mimetypes
import wx
import wx.media
import wx.lib.newevent

from sppas.src.config import paths
from sppas.src.audiodata import sppasAudioPCM
import sppas.src.audiodata.aio

from sppas.src.ui.phoenix.windows.datactrls import sppasWaveformWindow
from sppas.src.ui.phoenix.windows.panel import sppasPanel
from sppas.src.ui.phoenix.windows.media.mediaevents import MediaEvents

# ---------------------------------------------------------------------------


class AudioViewProperties(object):
    """Represent the possible views of an audio.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2020 Brigitte Bigi

    """

    INFOS_HEIGHT = 20
    WAVEFORM_HEIGHT = 100
    SPECTRAL_HEIGHT = 100
    LEVEL_HEIGHT = 30

    # -----------------------------------------------------------------------

    def __init__(self, parent, audio_filename):
        """Create the AudioTimeView.

        :param parent: (wx.Window) Must not be None.
        :param audio_filename: (str)

        """
        self.__parent = parent
        # All possible views and value (enabled=True, disabled=False)
        self.__infos = True
        self.__waveform = None
        self.__spectral = False
        self.__level = False

        # The audio PCM
        try:
            self.__audio = sppas.src.audiodata.aio.open(audio_filename)
        except Exception as e:
            wx.LogError("View of the audio file {:s} is un-available: "
                        "{:s}".format(audio_filename, str(e)))
            self.__audio = sppasAudioPCM()

    # -----------------------------------------------------------------------
    # Getters for audio infos
    # -----------------------------------------------------------------------

    def GetNumberChannels(self):
        return self.__audio.get_nchannels()

    nchannels = property(fget=GetNumberChannels)

    # -----------------------------------------------------------------------

    def GetSampWidth(self):
        return self.__audio.get_sampwidth()

    sampwidth = property(fget=GetSampWidth)

    # -----------------------------------------------------------------------

    def GetFramerate(self):
        return self.__audio.get_framerate()

    framerate = property(fget=GetFramerate)

    # -----------------------------------------------------------------------
    # Enable/Disable views
    # -----------------------------------------------------------------------

    def get_infos(self):
        return self.__infos

    def EnableInfos(self, value):
        """Enable the view of the infos.

        Cant be disabled if the audio failed to be loaded.

        :param value: (bool)
        :return: (bool)

        """
        value = bool(value)
        if value is True and self.__audio.get_nchannels() > 0:
            self.__infos = True

        self.__infos = False
        return False

    # -----------------------------------------------------------------------

    def get_waveform(self):
        return self.__waveform

    def EnableWaveform(self, value):
        """Enable the view of the waveform.

        Can't be enabled if the audio has more than 1 channel.

        :param value: (bool)
        :return: (bool)

        """
        value = bool(value)
        if value is True and self.__audio.get_nchannels() == 1:
            self.__waveform = sppasWaveformWindow(self.__parent)
            return True

        self.__waveform = None
        return False

    # -----------------------------------------------------------------------

    def EnableSpectral(self, value):
        """Enable the view of the spectrogram.

        Can't be enabled if the audio has more than 1 channel.

        :param value: (bool)
        :return: (bool)

        """
        value = bool(value)
        if value is True and self.__audio.get_nchannels() == 1:
            self.__spectral = True
            return True

        self.__spectral = False
        return False

    # -----------------------------------------------------------------------

    def EnableLevel(self, value):
        """Enable the view of the level.

        Can't be enabled if the audio has more than 1 channel.

        :param value: (bool)
        :return: (bool)

        """
        value = bool(value)
        if value is True and self.__audio.get_nchannels() == 1:
            self.__level = True
            return True

        self.__level = False
        return False

    # -----------------------------------------------------------------------
    # Height of views
    # -----------------------------------------------------------------------

    def GetWaveformHeight(self):
        """Return the height required to draw the Waveform."""
        h = AudioViewProperties.WAVEFORM_HEIGHT
        try:
            h = self.__parent.fix_size(h)
        except AttributeError:
            pass
        return h

    # -----------------------------------------------------------------------

    def GetInfosHeight(self):
        """Return the height required to draw the audio information."""
        h = AudioViewProperties.INFOS_HEIGHT
        try:
            h = self.__parent.fix_size(h)
        except AttributeError:
            pass
        return h

    # -----------------------------------------------------------------------

    def GetLevelHeight(self):
        """Return the height required to draw the audio volume level."""
        h = AudioViewProperties.LEVEL_HEIGHT
        try:
            h = self.__parent.fix_size(h)
        except AttributeError:
            pass
        return h

    # -----------------------------------------------------------------------

    def GetSpectralHeight(self):
        """Return the height required to draw the audio spectrum."""
        h = AudioViewProperties.SPECTRAL_HEIGHT
        try:
            h = self.__parent.fix_size(h)
        except AttributeError:
            pass
        return h

    # -----------------------------------------------------------------------

    def GetMinHeight(self):
        """Return the min height required to draw all views."""
        h = 0
        if self.__infos is True:
            h += AudioViewProperties.INFOS_HEIGHT
        if self.__waveform is not None:
            h += AudioViewProperties.WAVEFORM_HEIGHT
        if self.__level is True:
            h += AudioViewProperties.LEVEL_HEIGHT
        if self.__spectral is True:
            h += AudioViewProperties.SPECTRAL_HEIGHT

        try:
            h = self.__parent.fix_size(h)
        except AttributeError:
            pass

        return h

    # -----------------------------------------------------------------------

    def DrawWaveform(self, pos, size, start_time, end_time):
        self.__waveform.SetPosition(pos)
        self.__waveform.SetSize(size)

        nframes = int((end_time - start_time) * self.__audio.get_framerate())
        self.__audio.seek(int(start_time * float(self.__audio.get_framerate())))
        # read samples of all channels. Channel 0 is data[0]
        data = self.__audio.read_samples(nframes)
        self.__waveform.SetData([data[0], self.__audio.get_sampwidth()])

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


class MediaState(object):
    """Enum of all states of a media.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2020 Brigitte Bigi

    :Example:

        >>>with MediaState() as ms:
        >>>    print(ms.playing)

    This class is a solution to mimic an 'Enum' but is compatible with both
    Python 2.7 and Python 3+.

    """

    def __init__(self):
        """Create the dictionary."""
        self.__dict__ = dict(
            unknown=-1,
            stopped=wx.media.MEDIASTATE_STOPPED,  # 0
            paused=wx.media.MEDIASTATE_PAUSED,    # 1
            playing=wx.media.MEDIASTATE_PLAYING,  # 2
            loading=3
        )

    # -----------------------------------------------------------------------

    def __enter__(self):
        return self

    # -----------------------------------------------------------------------

    def __exit__(self, exc_type, exc_value, traceback):
        pass

# ---------------------------------------------------------------------------


class sppasMediaCtrl(sppasPanel):
    """Create an extended media control embedded in a panel.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2020  Brigitte Bigi

    sppasMediaCtrl is using the wx.media.MediaCtrl.
    Extended features are:

        - TODO: display of waveform/spectrogram/volume if the media is an audio;
        - a zoom (percentage) to fix the height of this panel and its media;
        - works exactly the same on all platforms, except for Seek().

    Other known problems:

     - Under MacOS, if start position is set to a value other than X*1000 ms,
       the backend will display an error message and will seek to the X*1000
       position instead of the required one. Error message is:
       Python[14410:729361] CMTimeMakeWithSeconds(2.870 seconds, timescale 1):
       warning: error of -0.870 introduced due to very low timescale
       (AvPlayer backend)

    Events emitted by this class:

        - MediaEvents.MediaActionEvent
        - MediaEvents.MediaLoadedEvent
        - MediaEvents.MediaNotLoadedEvent

    """

    # -----------------------------------------------------------------------
    # This object size.
    # By default, it is a DFHD aspect ratio (super ultra-wide displays) 32:9
    MIN_WIDTH = 178
    MIN_HEIGHT = 50

    DEFAULT_WIDTH = MIN_WIDTH * 3
    DEFAULT_HEIGHT = MIN_HEIGHT * 3

    # -----------------------------------------------------------------------
    # Delays for loading media files
    LOAD_DELAY = 500
    MAX_LOAD_DELAY = 3000

    # -----------------------------------------------------------------------

    def __init__(self, parent,
                 id=wx.ID_ANY,
                 pos=wx.DefaultPosition,
                 name="media_panel"):
        """Create an instance of sppasMediaCtrl.

        The media is embedded and not inherited to allow to capture the paint
        event and to draw a custom "picture" if media is not a video.

        :param parent: (wx.Window) parent window. Must not be None;
        :param id: (int) window identifier. -1 indicates a default value;
        :param pos: the control position. (-1, -1) indicates a default
         position, chosen by either the windowing system or wxPython,
         depending on platform;
        :param name: (str) Name of the media panel.

        """
        size = wx.Size(sppasMediaCtrl.DEFAULT_WIDTH,
                       sppasMediaCtrl.DEFAULT_HEIGHT)
        super(sppasMediaCtrl, self).__init__(
            parent, id, pos, size,
            style=wx.BORDER_NONE | wx.TRANSPARENT_WINDOW | wx.TAB_TRAVERSAL | wx.WANTS_CHARS | wx.FULL_REPAINT_ON_RESIZE,
            name=name)

        # Members
        self._mt = MediaType().unknown
        self._ms = MediaState().unknown
        self._mc = None
        self._zoom = 100    # zoom level in percentage
        self._filename = None
        self._length = 0    # duration of the media in milliseconds
        self._audio = None
        self._period = None   # a period to draw the audio. Default: whole.

        # Create the media, or destroy ourselves
        self._mc = self._create_media()

        # Create the content of the window: only the media.
        self._create_content()

        # Bind the events related to our window
        self._setup_events()

        # Allow sub-classes to bind other events
        self.InitOtherEvents()

        # Set our min size
        self.SetInitialSize()

    # -----------------------------------------------------------------------
    # Construct the window
    # -----------------------------------------------------------------------

    def _create_media(self):
        """Return the wx.media.MediaCtrl with the appropriate backend.

        Todo: create a media control based on mplayer or gstreamer
              (certainly more reliable than native backends!).

        """
        # The soft to be used to really play the media file
        back_end = ""
        if wx.Platform == "__WXMSW__":
            # default is wx.media.MEDIABACKEND_DIRECTSHOW
            # back_end = wx.media.MEDIABACKEND_WMP10
            back_end = wx.media.MEDIABACKEND_DIRECTSHOW
        # elif wx.Platform == "__WXMAC__":
        #     back_end = wx.media.MEDIABACKEND_QUICKTIME
        #     it raises the NotImplementedError

        # Create the media control based
        try:
            mc = wx.media.MediaCtrl()
            ok = mc.Create(
                self, size=(0, 0),
                style=wx.SIMPLE_BORDER | wx.ALIGN_CENTER_HORIZONTAL,
                szBackend=back_end)
            if not ok:
                raise NotImplementedError("Can't create a media object: "
                                          "requested backend not implemented.")
        except NotImplementedError:
            self.Destroy()
            raise

        return mc

    # -----------------------------------------------------------------------

    def _create_content(self):
        """Construct our panel, made only of the media control."""
        s = wx.BoxSizer()
        s.Add(self._mc, 1, wx.EXPAND, border=0)
        self.SetSizer(s)
        self.SetAutoLayout(True)

    # -----------------------------------------------------------------------
    # New features: Public methods
    # -----------------------------------------------------------------------

    def GetAudioProperties(self):
        """Return a AudioViewProperties() or None.

        It allows to define look&feel of the displayed audio properties:
        information, waveform, etc

        """
        return self._audio

    # -----------------------------------------------------------------------

    def GetZoom(self):
        """Return the current zoom percentage value."""
        return self._zoom

    # -----------------------------------------------------------------------

    def SetZoom(self, value):
        """Fix the zoom percentage value.

        This coefficient is applied when SetBestSize is called to enlarge
        or reduce our size and the size of the displayed media.

        :param value: (int) Percentage of zooming, in range 25 .. 400.

        """
        value = int(value)
        if value < 25:
            value = 25
        if value > 400:
            value = 400
        self._zoom = value
        self.SetBestSize()
        self.Refresh()

    # ----------------------------------------------------------------------

    def SetDrawPeriod(self, start, end):
        self._period = (start, end)

    # ----------------------------------------------------------------------

    def GetFilename(self):
        """Return the file associated to the media."""
        return self._filename

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

    # -----------------------------------------------------------------------

    def GetMediaType(self):
        """Return the media type of the given filename.

        :return: (MediaType) The media type value

        """
        return self._mt

    # -----------------------------------------------------------------------
    # Media states
    # -----------------------------------------------------------------------

    def IsPaused(self):
        """Return True if state is wx.media.MEDIASTATE_PAUSED."""
        return self._ms == MediaState().paused

    # -----------------------------------------------------------------------

    def IsPlaying(self):
        """Return True if state is wx.media.MEDIASTATE_PLAYING."""
        return self._ms == MediaState().playing

    # -----------------------------------------------------------------------

    def IsStopped(self):
        """Return True if state is wx.media.MEDIASTATE_STOPPED."""
        return self._ms == MediaState().stopped

    # -----------------------------------------------------------------------

    def IsLoading(self):
        """Return True if media is currently loading."""
        return self._ms == MediaState().loading

    # -----------------------------------------------------------------------
    # Public methods of the wx.media.MediaCtrl.
    # -----------------------------------------------------------------------

    def GetVolume(self):
        """Return the volume coefficient.

        :return: (float) The volume of the media is a 0.0 to 1.0 range.

        """
        return self._mc.GetVolume()

    # -----------------------------------------------------------------------

    def SetVolume(self, value):
        """Set the volume coefficient of the media.

        :param value: (float) A value in range 0.0 to 1.0

        """
        self._mc.SetVolume(value)

    # -----------------------------------------------------------------------

    def GetState(self):
        """Return the current MediaState() of the media."""
        return self._ms

    # -----------------------------------------------------------------------

    def Load(self, filename):
        """Load the file that filename refers to.

        It resets all known information like the length, etc.

        Contrariwise to the base class, Load() returns False systematically.
        The EVT_MEDIA_LOADED will be send when media is loaded.

        :param filename: (str)
        :return: (bool) Always returns False

        """
        # If a filename was previously set
        if self._filename is not None:
            # ... and file is loading
            if self._ms == MediaState().loading:
                # stop this loading.
                wx.PostEvent(self, MediaEvents.MediaLoadedEvent(time=3000))
            # ... and file was loaded
            elif self._ms != MediaState().unknown:
                # re-draw to come back to an initial image
                self.Stop()
                # # self.SetInitialSize()
                # # self.Layout()
                # # self.Refresh()

        # Reset all known information
        self._filename = filename
        self._length = 0
        self._mt = MediaType().unknown

        # Then start loading the media.
        # The current media state is -1. It does not match any of the
        # known media states. We ignore it and set our custom state.
        self._ms = MediaState().loading

        # The boolean value returned by Load is not reliable (it works
        # differently depending on the backend) and native EVT_LOADED also.
        # We ignore the returned value and implement our custom loaded event.
        self._mc.Load(filename)
        d = sppasMediaCtrl.LOAD_DELAY
        wx.CallLater(d, lambda: wx.PostEvent(self, MediaEvents.MediaLoadedEvent(time=d)))

        #  logging.debug("%s load. call to refresh." % self._filename)
        self.Refresh()
        return False

    # -------------------------------------------------------------------------

    def Length(self):
        """Obtain the total amount of time the media has in milliseconds.

        :return: (int) -1 if the media is not supported or 0 if not loaded

        """
        return self._length

    # -------------------------------------------------------------------------

    def Pause(self):
        """Pause the media if the media is currently playing."""
        if self._length <= 0:
            return

        if self._ms == MediaState().playing:
            self._mc.Pause()
            self._ms = MediaState().paused

    # ----------------------------------------------------------------------

    def Play(self):
        """Play the media.

        :return: (bool)

        """
        if self._filename is None:
            wx.LogError("No media file to play.")
            return False

        with MediaState() as ms:
            if self._ms in (ms.unknown, ms.loading):
                wx.LogError("The media file {:s} can't be played."
                            "".format(self._filename))
                played = False

            elif self._ms == ms.playing:
                wx.LogWarning("Media file {:s} is already playing."
                              "".format(self._filename))
                played = True

            else:  # stopped or paused
                played = self._mc.Play()
                if played is True:
                    self._ms = MediaState().playing
                else:
                    # An error occurred while the mediactrl attempted to play
                    self._ms = MediaState().unknown

        return played

    # -------------------------------------------------------------------------

    def Seek(self, offset, mode=wx.FromStart):
        """Seek to a position within the media.

        BUGS AND LIMITATIONS OF BACK-ENDS:

        - Under MacOS, with AVPLAYER backend, the seek position must be
        X * 1000 ms. If not, it will be forced to it by the backend!

        - Under Windows, with WMP10 backend, it seeks 1000 ms before the
        requested position.

        :param offset: (wx.FileOffset)
        :param mode: (SeekMode)
        :return: (wx.FileOffset) Value in milliseconds

        """
        if self._length <= 0:
            return 0

        return self._mc.Seek(offset, mode)

    # ----------------------------------------------------------------------

    def Tell(self):
        """Obtain the current position in time within the media.

        :return: (wx.FileOffset) Value in milliseconds

        """
        if self:
            return self._mc.Tell()
        return 0

    # ----------------------------------------------------------------------

    def Stop(self):
        """Stop playing/pausing the media."""
        if self._length <= 0:
            return

        try:
            self._ms = MediaState().stopped
            self._mc.Stop()
        except Exception as e:
            # provide errors like:
            # Fatal IO error 11 (Resource temporarily unavailable)
            wx.LogError(str(e))
            pass

    # ----------------------------------------------------------------------
    # Override Public methods of a wx.Window
    # ----------------------------------------------------------------------

    def Close(self, force=False):
        """Close the sppasMediaCtrl."""
        if self._mc:
            self._mc.Stop()
        wx.Window.DeletePendingEvents(self)
        wx.Window.Close(self, force)

    # ----------------------------------------------------------------------

    def Destroy(self):
        """Destroy the sppasMediaCtrl."""
        if self._mc:
            self._mc.Stop()
        wx.Window.DeletePendingEvents(self)
        wx.Window.Destroy(self)

    # -----------------------------------------------------------------------
    # Override Public methods to define the size of the wx.Window
    # -----------------------------------------------------------------------

    def DoGetBestSize(self):
        """Return the size which best suits the window.

        The best size of self is the default size when zoom is applied.
        We don't matter of the original size of the video, if any.

        """
        (w, h) = (sppasMediaCtrl.DEFAULT_WIDTH, sppasMediaCtrl.DEFAULT_HEIGHT)
        # Adjust height, except if video
        with MediaType() as mt:
            if self._mt == mt.audio and self._audio is not None:
                h = self._audio.GetMinHeight()

            elif self._mt in (mt.unknown, mt.unsupported):
                h = sppasMediaCtrl.MIN_HEIGHT

        # Apply the zoom coefficient
        h = int(float(h) * float(self._zoom) / 100.)

        return wx.Size(w, h)

    # ----------------------------------------------------------------------

    def SetSize(self, size):
        best_size = self.DoGetBestSize()

        # the appropriate width is the max between our best and the given one
        w = max(size[0], sppasMediaCtrl.MIN_WIDTH)    # size[0], best_size[0])
        # the appropriate height is the one of the embedded media
        h = best_size[1]

        wx.Panel.SetSize(self, wx.Size(w, h))

        # The size of the mc is set by our sizer, depending on our size.
        # because we enabled auto-layout.
        if self._mt == MediaType().video:
            self._mc.Show()
        else:
            self._mc.SetSize(wx.Size(sppasMediaCtrl.MIN_WIDTH, sppasMediaCtrl.MIN_HEIGHT))
            self._mc.Hide()

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

            - the mediactrl is a video and the video is already loaded:
              we know its size so we'll set size to it;
            - the mediactrl is an audio: its size is (0, 0),
              so we'll force to a min size.

        :param size: (wx.Size)

        """
        (w, h) = (sppasMediaCtrl.MIN_WIDTH, sppasMediaCtrl.MIN_HEIGHT)

        # If a size is given we'll use it, except if -1 or less than our min
        if size is not None:
            (ws, hs) = size
            w = max(ws, w)
            h = max(hs, h)

        # We fix the min size
        self.SetMinSize(wx.Size(w, h))

        # We fix our optimal size
        self.SetBestSize()

    # ----------------------------------------------------------------------

    def GetBestSize(self):
        """Return the best acceptable minimal size for the window."""
        return self.DoGetBestSize()

    # ----------------------------------------------------------------------

    def SetBestSize(self):
        self.SetSize(self.DoGetBestSize())

    # ----------------------------------------------------------------------
    # Events management
    # ----------------------------------------------------------------------

    def InitOtherEvents(self):
        """Initialize other events than paint, mouse, timer or focus.

        Override this method in a subclass to initialize any other events that
        need to be bound. Added so __init__ method doesn't need to be
        overridden, which is complicated with multiple inheritance.

        """
        pass

    # -----------------------------------------------------------------------

    def _setup_events(self):
        """Initialize the events related to our window."""
        # Capture events emitted by the wx.media.MediaCtrl to oversee their
        # operation and provide our own implementation.
        self._mc.Bind(wx.media.EVT_MEDIA_LOADED, self.__on_native_media_loaded)
        self._mc.Bind(wx.EVT_MOUSE_EVENTS, self.OnMouseEvents)
        self.Bind(wx.EVT_MOUSE_EVENTS, self.OnMouseEvents)

        # Custom event to inform the parent the media is loaded
        self.Bind(MediaEvents.EVT_MEDIA_LOADED, self.__on_custom_media_loaded)

        # To draw the audio
        self.Bind(wx.EVT_PAINT, lambda evt: self.Draw())
        self.Bind(wx.EVT_ERASE_BACKGROUND, self.OnEraseBackground)

    # ----------------------------------------------------------------------

    def notify_loaded(self, value=True):
        """The parent is informed that the media is loaded or not.

        :param value: (any) Media is loaded, or media is not loaded.

        """
        if value is True:
            evt = MediaEvents.MediaLoadedEvent()
        else:
            evt = MediaEvents.MediaNotLoadedEvent()
        evt.SetEventObject(self)
        wx.PostEvent(self.GetParent(), evt)

    # ----------------------------------------------------------------------

    def notify_action(self, action, value=None):
        """The parent is informed that an action is required.

        :param action: (str) Name of the action
        :param value: (any) Any kind of value linked to the action

        """
        evt = MediaEvents.MediaActionEvent(action=action, value=value)
        evt.SetEventObject(self)
        wx.PostEvent(self.GetParent(), evt)

    # -----------------------------------------------------------------------

    def __on_native_media_loaded(self, event):
        """Sent by wx.media.MediaCtrl to notify a media has enough data.

        This event is platform dependent: so the event vetoed!

        """
        event.Veto()

    # -----------------------------------------------------------------------

    def __on_custom_media_loaded(self, event):
        """Sent sppasMediaCtrl.LOAD_DELAY ms after Load was called.

        """
        event.Skip()
        delay = event.time

        # If the delay is reached, the backend failed to load the media.
        if delay >= sppasMediaCtrl.MAX_LOAD_DELAY:
            self._mt = MediaType().unsupported
            self._ms = MediaState().unknown
            wx.LogError("The media backend failed to load {:s}: "
                        "Unsupported format?".format(self._filename))
            self.SetInitialSize()
            # Inform the parent the media was not loaded.
            self.notify_loaded(False)

        else:

            media_length = self._mc.Length()
            # We still don't have a length.
            # It means the backend is still loading. We'll try again later.
            if not media_length or type(media_length) not in (int, float) or media_length == -1:
                wx.LogWarning("The media failed to be loaded by the backend "
                              "after a delay of {:d} ms. Will try again later."
                              "".format(delay))
                delay += sppasMediaCtrl.LOAD_DELAY
                wx.CallLater(sppasMediaCtrl.LOAD_DELAY,
                             lambda: wx.PostEvent(self, MediaEvents.MediaLoadedEvent(time=delay)))

            else:
                # We have a length. It means the media is supported and loaded.
                self._length = media_length
                self._mt = sppasMediaCtrl.ExpectedMediaType(self._filename)
                self._ms = MediaState().stopped
                self._mc.Seek(0)
                if self._mt == MediaType().audio:
                    self._audio = AudioViewProperties(self, self._filename)

                self.SetBestSize()
                # Inform the parent we're ready.
                self.notify_loaded(True)

    # ----------------------------------------------------------------------

    def OnMouseEvents(self, event):
        """Handle the wx.EVT_MOUSE_EVENTS event.

        Do not accept the event: it could interfere with the media control.

        """
        if event.Entering():
            pass

        elif event.Leaving():
            pass

        elif event.LeftDown():
            pass

        elif event.LeftUp():
            self.notify_action(action="play")

        elif event.Moving():
            # a motion event and no mouse buttons were pressed.
            pass

        elif event.Dragging():
            # motion while a button was pressed
            pass

        elif event.ButtonDClick():
            pass

        elif event.RightDown():
            pass

        elif event.RightUp():
            self.notify_action(action="stop")

        event.Skip()

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
            if self._mt != MediaType().video:

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
        brush = self.GetBackgroundBrush(dc)
        if brush is not None:
            dc.SetBackground(brush)
            dc.Clear()

        dc.SetPen(wx.TRANSPARENT_PEN)
        dc.SetBrush(brush)
        w, h = self.GetClientSize()
        dc.DrawRectangle(0, 0, w, h)

    # ------------------------------------------------------------------------

    def _DrawContent(self, dc, gc):
        """Draw a content if media is audio, unsupported or unknown.

        """
        w, h = self.GetClientSize()
        x = y = 0
        if self._audio is None:
            self.__draw_audio_infos(dc, gc, x, y, w, h)
        else:
            if self._audio.get_infos() is True:
                h = self._audio.GetInfosHeight()
                h = int(float(h) * float(self._zoom) / 100.)
                self.__draw_audio_infos(dc, gc, x, y, w, h)
                y += h
            if self._audio.get_waveform() is not None:
                h = self._audio.GetWaveformHeight()
                h = int(float(h) * float(self._zoom) / 100.)
                self.__draw_audio_waveform(dc, gc, x, y, w, h)
                y += h

    # -----------------------------------------------------------------------

    def __draw_audio_infos(self, dc, gc, x, y, w, h):
        """Draw the information of the audio file or an error message.

        """
        # Draw the background of the audio infos area
        dc.GradientFillLinear((x, y, w, h),
                              self.GetBackgroundColour(),
                              self.GetHighlightedBackgroundColour(),
                              wx.WEST)

        # Draw the content (information message)
        label = ""
        with MediaType() as mt:
            if self._mt == mt.unknown:
                if self._ms == MediaState().loading:
                    label = "Loading media file"
                else:
                    label = "Unknown file format"

            elif self._mt == mt.unsupported:
                label = "File format not supported"

            elif self._mt == mt.audio:
                if self._audio is None:
                    label = "View of the audio file is not currently available"
                else:
                    label = str(self._audio.framerate) + " Hz, "
                    label += str(self._audio.sampwidth * 8) + " bits, "
                    c = self._audio.nchannels
                    if c == 1:
                        label += "Mono"
                    elif c == 2:
                        label += "Stereo"
                    elif c > 2:
                        label += "%d channels" % c

        lw, lh = self.get_text_extend(dc, gc, label)
        self.__draw_label(dc, gc, 10, y+(h//2) - (lh//2), label)

    # -----------------------------------------------------------------------

    def __draw_audio_volume(self, dc, gc, x, y, w, h):
        """Draw the volume level of the audio file.

        """
        pass

    # -----------------------------------------------------------------------

    def __draw_audio_waveform(self, dc, gc, x, y, w, h):
        """Draw the waveform of the audio file.

        """
        # Draw the background of the waveform area
        dc.GradientFillLinear((x, y, w, h // 2),
                              self.GetBackgroundColour(),
                              self.GetHighlightedBackgroundColour(),
                              wx.NORTH)
        dc.GradientFillLinear((x, y + (h // 2), w, h // 2),
                              self.GetBackgroundColour(),
                              self.GetHighlightedBackgroundColour(),
                              wx.SOUTH)

        pos = wx.Point(x, y)
        size = wx.Size(w, h)
        if self._period is not None:
            start = float(self._period[0]) / 1000.
            end = float(self._period[1]) / 1000.
            self._audio.DrawWaveform(pos, size, start, end)
        else:
            start = 0.
            end = float(self._length) / 1000.
        self._audio.DrawWaveform(pos, size, start, end)

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

    @staticmethod
    def get_text_extend(dc, gc, text):
        if wx.Platform == '__WXGTK__':
            return dc.GetTextExtent(text)
        return gc.GetTextExtent(text)

    # -----------------------------------------------------------------------

    def GetBackgroundBrush(self, dc):
        """Get the brush for drawing the background of the window.

        :returns: (wx.Brush)

        """
        return wx.Brush(self.GetHighlightedBackgroundColour(), wx.SOLID)

    # -----------------------------------------------------------------------

    def GetHighlightedBackgroundColour(self):
        color = self.GetBackgroundColour()
        r, g, b, a = color.Red(), color.Green(), color.Blue(), color.Alpha()

        delta = 15
        if (r + g + b) > 384:
            return wx.Colour(r, g, b, a).ChangeLightness(100 - delta)
        return wx.Colour(r, g, b, a).ChangeLightness(100 + delta)

# ---------------------------------------------------------------------------
# The panel to test
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
        self.mc = sppasMediaCtrl(self)
        self.Bind(MediaEvents.EVT_MEDIA_LOADED, self.OnMediaLoaded)
        self.Bind(MediaEvents.EVT_MEDIA_NOT_LOADED, self.OnMediaNotLoaded)
        self.Bind(MediaEvents.EVT_MEDIA_ACTION, self.OnMediaAction)

        btn1 = wx.Button(self, -1, "Load File")
        self.Bind(wx.EVT_BUTTON, self.OnLoadFile, btn1)

        btn2 = wx.Button(self, -1, "Play")
        self.Bind(wx.EVT_BUTTON, self.OnPlay, btn2)
        self.playBtn = btn2
        self.playBtn.Enable(False)

        btn3 = wx.Button(self, -1, "Pause")
        self.Bind(wx.EVT_BUTTON, self.OnPause, btn3)

        btn4 = wx.Button(self, -1, "Stop")
        self.Bind(wx.EVT_BUTTON, self.OnStop, btn4)

        self.slider = wx.Slider(self, -1, 0, 0, 10, style=wx.SL_HORIZONTAL)
        self.slider.SetMinSize(wx.Size(250, -1))
        self.Bind(wx.EVT_SLIDER, self.OnSeek, self.slider)

        self.st_len = StaticText(self, -1, size=(100, -1))
        self.st_pos = StaticText(self, -1, size=(100, -1))
        self.st_type = StaticText(self, -1, size=(150, -1))
        self.st_file = StaticText(self, -1, size=(300, -1))

        # setup the layout
        sizer = wx.GridBagSizer(6, 5)
        sizer.Add(self.mc, (1, 1), flag=wx.EXPAND, span=(6, 1))
        sizer.Add(btn1, (1, 3))
        sizer.Add(btn2, (2, 3))
        sizer.Add(btn3, (3, 3))
        sizer.Add(btn4, (4, 3))
        sizer.Add(self.slider, (7, 1), flag=wx.EXPAND)
        sizer.Add(self.st_len, (1, 5))
        sizer.Add(self.st_pos, (2, 5))
        sizer.Add(self.st_type, (3, 5))
        sizer.Add(self.st_file, (4, 5))

        # Test another one mediactrl

        mc2 = sppasMediaCtrl(self)

        main_sizer = wx.BoxSizer(wx.VERTICAL)
        main_sizer.Add(sizer, 1, wx.EXPAND)
        main_sizer.Add(mc2, 1, wx.EXPAND)
        self.SetSizer(main_sizer)

        wx.CallAfter(
            self.DoLoad,
            mc2,
            os.path.join(paths.samples, "samples-fra", "F_F_C006-P6.wav")
            #"C:\\Users\\bigi\\Videos\\agay_2.mp4"
            )
        wx.CallAfter(
            self.DoLoad,
            self.mc,
            #"C:\\Users\\bigi\\Videos\\agay_2.mp4")
            os.path.join(paths.samples, "samples-fra", "F_F_B003-P8.wav"))

        mc2.SetZoom(200)

        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.OnTimer)

    # ----------------------------------------------------------------------

    def DoLoad(self, mc, filename):
        self.playBtn.Enable(False)
        mc.Load(filename)
        self.st_len.SetLabel('length: %d seconds' % (mc.Length()/1000))
        self.st_pos.SetLabel('position: %d' % self.mc.Tell())
        self.st_type.SetLabel('type: %s' % self.mediatype(mc.GetMediaType()))
        self.st_file.SetLabel('file: %s' % mc.GetFilename())

    # ----------------------------------------------------------------------

    def OnLoadFile(self, evt):
        dlg = wx.FileDialog(self, message="Choose a media file",
                            defaultDir=paths.samples, defaultFile="",
                            style=wx.FD_OPEN | wx.FD_CHANGE_DIR)
        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            self.DoLoad(path)
        dlg.Destroy()

    # ----------------------------------------------------------------------

    def OnMediaLoaded(self, evt):
        media = evt.GetEventObject()
        if media == self.mc:
            wx.LogDebug(str(media))
            wx.LogDebug(media.GetFilename())
            self.slider.SetRange(0, media.Length())
            self.playBtn.Enable(True)
            self.st_len.SetLabel('length: %d seconds' % (media.Length()/1000))
            self.st_pos.SetLabel('position: %d' % media.Tell())
            self.st_type.SetLabel('type: %s' % self.mediatype(media.GetMediaType()))

        audio_prop = media.GetAudioProperties()
        if audio_prop is not None:
            audio_prop.EnableWaveform(True)
            media.SetBestSize()

        self.Layout()

    # ----------------------------------------------------------------------

    def OnMediaNotLoaded(self, evt):
        media = evt.GetEventObject()
        if media == self.mc:
            self.slider.SetRange(0, 0)
            self.playBtn.Enable(False)
            self.st_len.SetLabel('length: -- seconds')
            self.st_pos.SetLabel('position: %d' % self.mc.Tell())
            self.st_type.SetLabel('type: %s' % self.mediatype(self.mc.GetMediaType()))
        self.Layout()

    # ----------------------------------------------------------------------

    @staticmethod
    def mediatype(value):
        with MediaType() as m:
            if value == m.audio:
                return "audio"
            if value == m.video:
                return "video"
            if value == m.unknown:
                return "unknown"
            if value == m.unsupported:
                return "unsupported"
        return str(m)

    # ----------------------------------------------------------------------

    def OnMediaAction(self, evt):
        logging.debug("Media Action event received. action is %s" % evt.action)
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
        if self.mc.Play() is False:
            self.st_len.SetLabel('length: -- seconds')
            self.st_pos.SetLabel('position: 0')
        else:
            self.GetSizer().Layout()
            self.slider.SetRange(0, self.mc.Length())
            self.timer.Start(20)
        self.st_type.SetLabel('type: %s' % self.mediatype(self.mc.GetMediaType()))

    # ----------------------------------------------------------------------

    def OnPause(self, evt):
        self.mc.Pause()

    # ----------------------------------------------------------------------

    def OnStop(self, evt):
        self.mc.Stop()
        self.timer.Stop()
        self.slider.SetValue(0)

    # ----------------------------------------------------------------------

    def OnSeek(self, evt):
        offset = self.slider.GetValue()
        self.mc.Seek(offset)

    # ----------------------------------------------------------------------

    def OnTimer(self, evt):
        offset = self.mc.Tell()
        self.slider.SetValue(offset)
        self.st_len.SetLabel('length: %d seconds' % (self.mc.Length()/1000))
        self.st_pos.SetLabel('position: %d' % offset)
        self.st_type.SetLabel('type: %s' % self.mediatype(self.mc.GetMediaType()))

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------

    def Destroy(self):
        self.timer.Stop()
        self.DeletePendingEvents()
        del self.timer
        wx.Panel.Destroy(self)


