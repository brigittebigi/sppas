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

    src.ui.players.wxvideoplay.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    A player to play a single video file inside a wx frame.

"""

import logging
import datetime
import time
import threading
import wx
import numpy

from sppas.src.config import sppasAppConfig
from sppas.src.videodata.video import sppasVideoReader
from sppas.src.ui.phoenix.windows.frame import sppasImageFrame
from sppas.src.ui.phoenix.main_settings import WxAppSettings

from .pstate import PlayerState
from .baseplayer import sppasBasePlayer

# ---------------------------------------------------------------------------


class sppasApp(wx.App):

    def __init__(self):
        """Create a customized application."""
        # ensure the parent's __init__ is called with the args we want
        wx.App.__init__(self,
                        redirect=False,
                        filename=None,
                        useBestVisual=True,
                        clearSigInt=True)

        # Fix language and translation
        self.locale = wx.Locale(wx.LANGUAGE_DEFAULT)
        self.__cfg = sppasAppConfig()
        self.settings = WxAppSettings()
        self.setup_debug_logging()

    @staticmethod
    def setup_debug_logging():
        logger = logging.getLogger()
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.DEBUG)
        logging.debug('Logging set to DEBUG level')


EVT_NEW_IMAGE = wx.PyEventBinder(wx.NewEventType(), 0)


class ImageWindow(wx.Window):
    def __init__(self, parent, id=-1, style=wx.FULL_REPAINT_ON_RESIZE):
        wx.Window.__init__(self, parent, id, style=style)

        self.timer = wx.Timer

        self.img = wx.EmptyImage(2, 2)
        self.bmp = self.img.ConvertToBitmap()
        self.clientSize = self.GetClientSize()

        self.Bind(wx.EVT_PAINT, self.OnPaint)

        #For video support
        #------------------------------------------------------------
        self.Bind(EVT_NEW_IMAGE, self.OnNewImage)
        self.eventLock = None
        self.pause = False
        #------------------------------------------------------------

    def OnPaint(self, event):
        size = self.GetClientSize()
        if (size == self.clientSize):
            self.PaintBuffer()
        else:
            self.InitBuffer()

    def PaintBuffer(self):
        dc = wx.PaintDC(self)
        self.Draw(dc)

    def InitBuffer(self):
        self.clientSize = self.GetClientSize()
        self.bmp = self.img.Scale(self.clientSize[0], self.clientSize[1]).ConvertToBitmap()
        dc = wx.ClientDC(self)
        self.Draw(dc)

    def Draw(self,dc):
        dc.DrawBitmap(self.bmp,0,0)

    def UpdateImage(self, img):
        self.img = img
        self.InitBuffer()

    #For video support
    #------------------------------------------------------------
    def OnNewImage(self, event):
        #print sys._getframe().f_code.co_name

        """Update the image from event.img. The eventLock should be
        locked by the method calling the event. If the stream is not
        on pause, the eventLock is released for calling method so that
        new image events may be called.

        The method depends on the use of thread.allocate_lock. The
        event must have the attributes, eventLock and oldImageLock
        which are the lock objects."""

        self.eventLock = event.eventLock

        if not self.pause:
            self.UpdateImage(event.img)
            self.ReleaseEventLock()
        if event.oldImageLock:
            if event.oldImageLock.locked():
                event.oldImageLock.release()

    def ReleaseEventLock(self):
        if self.eventLock:
            if self.eventLock.locked():
                self.eventLock.release()

    def OnPause(self):
        self.pause = not self.pause
        #print "Pause State: " + str(self.pause)
        if not self.pause:
            self.ReleaseEventLock()
    #------------------------------------------------------------


#For video support
#----------------------------------------------------------------------
class ImageEvent(wx.PyCommandEvent):
    def __init__(self, eventType=EVT_NEW_IMAGE.evtType[0], id=0):
        wx.PyCommandEvent.__init__(self, eventType, id)
        self.img = None
        self.oldImageLock = None
        self.eventLock = None
#----------------------------------------------------------------------


class ImageFrame(wx.Frame):
    def __init__(self, parent):
        wx.Frame.__init__(self, parent, -1, "Image Frame",
                pos=(50,50), size=(640,480))
        self.window = ImageWindow(self)
        self.window.SetFocus()


class ImageIn:
    """Interface for sending images to the wx application."""
    def __init__(self, parent):
        self.parent = parent
        self.eventLock = threading.Lock()

    def SetData(self, arr):
        width = arr.shape[1]
        height = arr.shape[0]
        img = wx.Image(width, height)
        img.SetData(arr.tostring())

        # Create the event
        event = ImageEvent()
        event.img = img
        event.eventLock = self.eventLock

        # Trigger the event when app releases the eventLock
        event.eventLock.acquire()  # wait until the event lock is released
        self.parent.AddPendingEvent(event)


class videoThread(threading.Thread):
    """Run the MainLoop as a thread. Access the frame with self.frame."""
    def __init__(self, autoStart=True):
        threading.Thread.__init__(self)
        self.setDaemon(1)
        self.start_orig = self.start
        self.start = self.start_local
        self.frame = None  # to be defined in self.run
        self.lock = threading.Lock()
        self.lock.acquire()  # lock until variables are set
        if autoStart:
            self.start()  # automatically start thread on init

    def run(self):
        app = sppasApp()
        frame = ImageFrame(None)
        frame.SetSize((800, 600))
        frame.Show(True)

        #define frame and release lock
        #The lock is used to make sure that SetData is defined.
        self.frame = frame
        self.lock.release()

        app.MainLoop()

    def start_local(self):
        self.start_orig()
        #After thread has started, wait until the lock is released
        #before returning so that functions get defined.
        self.lock.acquire()


def runVideoThread():
    """MainLoop run as a thread. SetData function is returned."""

    vt = videoThread() #run wx MainLoop as thread
    frame = vt.frame #access to wx Frame
    myImageIn = ImageIn(frame.window) #data interface for image updates
    return myImageIn.SetData


def runVideo(vidSeq):
    """The video sequence function, vidSeq, is run on a separate
    thread to update the GUI. The vidSeq should have one argument for
    SetData."""

    app = wx.PySimpleApp()
    frame = ImageFrame(None)
    frame.SetSize((800, 600))
    frame.Show(True)

    myImageIn = ImageIn(frame.window)
    t = threading.Thread(target=vidSeq, args=(myImageIn.SetData,))
    t.setDaemon(1)
    t.start()

    app.MainLoop()


def vapp():
    app = wx.App()
    frame = ImageFrame(None)
    frame.SetSize((800, 600))
    frame.Show(True)
    app.SetTopWindow(frame)
    return app, frame


def runVideoAsThread():
    """THIS FUNCTION WILL FAIL IF WX CHECKS TO SEE THAT IT IS RUN ON
    MAIN THREAD.  This runs the MainLoop in its own thread and returns
    a function SetData that allows write access to the databuffer."""

    app = wx.PySimpleApp()
    frame = ImageFrame(None)
    frame.SetSize((800, 600))
    frame.Show(True)

    myImageIn = ImageIn(frame.window)

    t = threading.Thread(target=app.MainLoop)
    t.setDaemon(1)
    t.start()

    return myImageIn.SetData

# ---------------------------------------------------------------------------


class sppasSimpleVideoPlayerWX(sppasBasePlayer):
    """A video player based on opencv library and wx.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2020  Brigitte Bigi

    """

    def __init__(self):
        """Create an instance of sppasVideoPlayer."""
        super(sppasSimpleVideoPlayerWX, self).__init__()

    # -----------------------------------------------------------------------

    def __del__(self):
        try:
            self._media.close()
        except:
            pass

    # -----------------------------------------------------------------------

    def reset(self):
        """Re-initialize all known data."""
        if self._media is not None:
            self._media.close()
        sppasBasePlayer.reset(self)

    # -----------------------------------------------------------------------

    def load(self, filename):
        """Open the file that filename refers to and load a buffer of frames.

        :param filename: (str) Name of a video file
        :return: (bool) True if successfully opened and loaded.

        """
        self.reset()
        try:
            self._filename = filename
            self._media = sppasVideoReader()
            self._media.open(filename)
            self._ms = PlayerState().stopped
            return True

        except Exception as e:
            logging.error("Error when opening or loading file {:s}: "
                          "{:s}".format(filename, str(e)))
            self._media = sppasVideoReader()
            self._ms = PlayerState().unknown
            return False

    # -----------------------------------------------------------------------

    def play(self):
        """Start to play the video stream from the current position.

        Start playing only is the video stream is currently stopped or
        paused.

        :return: (bool) True if the action of playing was performed

        """
        if self._ms in (PlayerState().paused, PlayerState().stopped):
            th = threading.Thread(target=self._play_process, args=())
            self._ms = PlayerState().playing
            self._start_datenow = datetime.datetime.now()
            th.start()
            return True

        return False

    # -----------------------------------------------------------------------

    def pause(self):
        """Pause to play the video.

        :return: (bool) True if the action of stopping was performed

        """
        if self._ms == PlayerState().playing:
            self._ms = PlayerState().paused

    # -----------------------------------------------------------------------

    def _play_process(self):
        """Run the process of playing.

        It is expected that reading a frame, converting it to an image and
        displaying it in the video frame is faster than the duration of a
        frame (1. / fps).
        If it's not the case, we should, sometimes, ignore a frame: not tested!

        """
        # the position to start and to stop playing
        start_offset = int(self._from_time * float(self._media.get_framerate()))
        end_offset = int(self._to_time * float(self._media.get_framerate()))
        self._media.seek(start_offset)

        time_delay = round(1. / self._media.get_framerate(), 3)
        min_sleep = time_delay / 4.

        # the time when we started to play and the number of frames we displayed.
        frm = 0
        # SetData = runVideoThread()
        app, frame = vapp()
        myImageIn = ImageIn(frame.window)
        t = threading.Thread(target=app.MainLoop)
        t.setDaemon(1)
        t.start()

        self._start_datenow = datetime.datetime.now()

        while self._media.is_opened():
            if self._ms == PlayerState().playing:
                # read the next frame from the file
                frame = self._media.read_frame(process_image=False)
                frm += 1
                cur_offset = start_offset + frm

                if frame is None or cur_offset > end_offset:
                    # we reached the end of the file or the end of the period
                    self.stop()
                else:
                    myImageIn.SetData(frame.irgb())

                    expected_time = self._start_datenow + datetime.timedelta(seconds=(frm * time_delay))
                    cur_time = datetime.datetime.now()
                    delta = expected_time - cur_time
                    delta_seconds = delta.seconds + delta.microseconds / 1000000.
                    if delta_seconds > min_sleep:
                        # I'm reading too fast, wait a little time.
                        time.sleep(delta_seconds)

                    elif delta_seconds > time_delay:
                        # I'm reading too slow, I'm in late. Go forward...
                        nf = int(delta_seconds / time_delay)
                        self._media.seek(self._media.tell() + nf)
                        frm += nf

            else:
                # stop the loop if any other state than playing
                break
        frame.Close()

    # -----------------------------------------------------------------------

    def stop(self):
        """Stop to play the video.

        :return: (bool) True if the action of stopping was performed

        """
        if self._ms not in (PlayerState().loading, PlayerState().unknown):
            self._ms = PlayerState().stopped
            self._media.seek(0)
            return True
        return False

    # -----------------------------------------------------------------------

    def seek(self, time_pos=0):
        """Seek the video stream at the given position in time.

        :param time_pos: (float) Time in seconds

        """
        if self._ms in (PlayerState().unknown, PlayerState().loading):
            return False

        time_pos = float(time_pos)
        if time_pos < 0.:
            time_pos = 0.
        if time_pos > self.get_duration():
            time_pos = self.get_duration()

        # how many frames this time position is representing since the beginning
        self._from_time = float(time_pos)
        position = self._from_time * self._media.get_framerate()
        if self._from_time >= self._to_time:
            self.stop()

        was_playing = self.is_playing()
        if was_playing is True:
            self.pause()

        # seek at the expected position
        try:
            self._media.seek(int(position))
            # continue playing if the seek was requested when playing
            if was_playing is True:
                self.play()
        except:
            # It can happen if we attempted to seek after the audio length
            self.stop()
            return False

        return True

    # -----------------------------------------------------------------------

    def tell(self):
        """Return the current time position in the video stream (float)."""
        offset = self._media.tell()
        return float(offset) / float(self._media.get_framerate())

    # -----------------------------------------------------------------------
    # About the video
    # -----------------------------------------------------------------------

    def get_duration(self):
        """Return the duration of the loaded video (float)."""
        if self._media is None:
            return 0.
        return self._media.get_duration()

    # -----------------------------------------------------------------------

    def get_framerate(self):
        if self._media is not None:
            return self._media.get_framerate()
        return 0

    # -----------------------------------------------------------------------

    def get_width(self):
        """Return the width of the frames in the video."""
        if self._media is None:
            return 0
        return self._media.get_width()

    # -----------------------------------------------------------------------

    def get_height(self):
        """Return the height of the frames in the video."""
        if self._media is None:
            return 0
        return self._media.get_height()
