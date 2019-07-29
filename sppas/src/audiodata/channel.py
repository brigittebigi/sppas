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

    src.audiodata.channel.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~

"""

from .audioframes import sppasAudioFrames
from .audiodataexc import IntervalError, SampleWidthError, FrameRateError

# ----------------------------------------------------------------------------


class sppasChannel(object):
    """Manage data and information of a channel.

    :author:       Nicolas Chazeau, Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2017  Brigitte Bigi

    """
    def __init__(self, framerate=16000, sampwidth=2, frames=b""):
        """Create a sppasChannel instance.

        :param framerate: (int) The frame rate of this channel, in Hertz.
        :param sampwidth: (int) 1 for 8 bits, 2 for 16 bits, 4 for 32 bits.
        :param frames: (str) The frames represented by a string.

        """
        self._framerate = 16000
        self._sampwidth = 2
        self._frames = b""
        self._position = 0

        self.set_framerate(framerate)
        self.set_sampwidth(sampwidth)
        self.set_frames(frames)

    # ----------------------------------------------------------------------
    # Setters
    # ----------------------------------------------------------------------

    def set_frames(self, frames):
        """Set new frames to the channel.

        It is supposed the sampwidth and framerate are the same as the 
        current ones.

        :param frames: (str) the new frames

        """
        # we should check if frames are bytes
        self._frames = frames

    # ----------------------------------------------------------------------

    def set_sampwidth(self, sampwidth):
        """Set a new samples width to the channel.

        :param sampwidth: (int) 1 for 8 bits, 2 for 16 bits, 4 for 32 bits.

        """
        sampwidth = int(sampwidth)
        if sampwidth not in [1, 2, 4]:
            raise SampleWidthError(sampwidth)

        self._sampwidth = sampwidth

    # ----------------------------------------------------------------------

    def set_framerate(self, framerate):
        """Set a new framerate to the channel.

        :param framerate: (int) The frame rate of this channel, in Hertz.
        A value between 8000 and 192000

        """
        framerate = int(framerate)
        if 8000 <= framerate <= 192000:
            self._framerate = framerate
        else:
            raise FrameRateError(framerate)

    # ----------------------------------------------------------------------
    # Getters
    # ----------------------------------------------------------------------

    def get_frames(self, chunck_size=None):
        """Return some frames from the current position.

        :param chunck_size: (int) the size of the chunk to return.
        None for all frames of the channel.
        :returns: (str) the frames

        """
        if chunck_size is None:
            return self._frames

        chunck_size = int(chunck_size)
        p = int(self._position)
        m = len(self._frames)
        s = p * self._sampwidth
        e = min(m, s + chunck_size * self._sampwidth)
        #f = b''.join(self._frames[i] for i in range(s, e))
        f = self._frames[s:e]
        self._position = p + chunck_size

        return f

    # -----------------------------------------------------------------------

    def get_nframes(self):
        """Return the number of frames.

        A frame has a length of (sampwidth) bytes.

        :returns: (int) the total number of frames

        """
        return len(self._frames)/self._sampwidth

    # -----------------------------------------------------------------------

    def get_framerate(self):
        """Return the frame rate, in Hz.

        :returns: (int) the frame rate of the channel

        """
        return self._framerate

    # -----------------------------------------------------------------------

    def get_sampwidth(self):
        """Return the sample width.

        :returns: (int) the sample width of the channel

        """
        return self._sampwidth

    # -----------------------------------------------------------------------

    def get_cross(self):
        """Return the number of zero crossings.

        :returns: (int) number of zero crossing

        """
        a = sppasAudioFrames(self._frames, self._sampwidth, 1)
        return a.cross()

    # -----------------------------------------------------------------------

    def rms(self):
        """Return the root mean square of the channel.

        :returns: (int) the root mean square of the channel

        """
        a = sppasAudioFrames(self._frames, self._sampwidth, 1)
        return a.rms()

    # -----------------------------------------------------------------------

    def clipping_rate(self, factor):
        """Return the clipping rate of the frames.

        :param factor: (float) An interval to be more precise on clipping rate.
        It will consider that all frames outside the interval are clipped.
        Factor has to be between 0 and 1.
        :returns: (float) the clipping rate

        """
        a = sppasAudioFrames(self._frames, self._sampwidth, 1)
        return a.clipping_rate(factor)

    # -----------------------------------------------------------------------

    def get_duration(self):
        """Return the duration of the channel, in seconds.

        :returns: (float) the duration of the channel

        """
        return float(self.get_nframes())/float(self.get_framerate())

    # -----------------------------------------------------------------------

    def extract_fragment(self, begin=None, end=None):
        """Extract a fragment between the beginning and the end.

        :param begin: (int: number of frames) the beginning of the fragment to extract
        :param end: (int: number of frames) the end of the fragment to extract

        :returns: (sppasChannel) the fragment extracted.

        """
        nframes = self.get_nframes()
        if begin is None:
            begin = 0
        if end is None:
            end = nframes

        begin = int(begin)
        end = int(end)
        if end < 0 or end > nframes:
            end = nframes

        if begin > nframes:
            return sppasChannel(self._framerate, self._sampwidth, b"")
        if begin < 0:
            begin = 0

        if begin == 0 and end == nframes:
            return sppasChannel(self._framerate, self._sampwidth, self._frames)

        if begin > end:
            raise IntervalError(begin, end)

        pos_begin = int(begin*self._sampwidth)
        if end == self.get_nframes():
            frames = self._frames[pos_begin:]
        else:
            pos_end = int(end*self._sampwidth)
            frames = self._frames[pos_begin:pos_end]

        return sppasChannel(self._framerate, self._sampwidth, frames)

    # -----------------------------------------------------------------------
    # Manage position
    # -----------------------------------------------------------------------

    def tell(self):
        """Return the current position."""
        return self._position

    # ------------------------------------------------------------------------

    def rewind(self):
        """Set the position to 0."""
        self._position = 0

    # ------------------------------------------------------------------------

    def seek(self, position):
        """Fix the current position.

        :param position: (int)

        """
        self._position = max(0, min(position, len(self._frames)/self._sampwidth))

    # ------------------------------------------------------------------------

    def __str__(self):
        return "Channel: framerate %d, sampleswidth %d, position %d, nframes %d" % \
               (self._framerate, self._sampwidth, self._position, len(self._frames))
