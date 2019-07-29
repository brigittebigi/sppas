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

    src.audiodata.channelformatter.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""

from .channelframes import sppasChannelFrames
from .channel import sppasChannel
from .audioframes import sppasAudioFrames

# ---------------------------------------------------------------------------


class sppasChannelFormatter(object):
    """
    :author:       Nicolas Chazeau, Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2017  Brigitte Bigi
    :summary:      A channel formatter class.

    """
    def __init__(self, channel):
        """Create a sppasChannelFormatter instance.

        :param channel: (sppasChannel) The channel to work on.

        """
        self._channel = channel
        self._framerate = channel.get_framerate()
        self._sampwidth = channel.get_sampwidth()

    # -----------------------------------------------------------------------
    # Getters
    # -----------------------------------------------------------------------

    def get_channel(self):
        """Return the sppasChannel."""
        return self._channel

    # -----------------------------------------------------------------------

    def get_framerate(self):
        """Return the expected frame rate for the channel.

        Notice that while convert is not applied, it can be different of the
        current one of the channel.

        :returns: the frame rate that will be used by the converter

        """
        return self._framerate

    # -----------------------------------------------------------------------

    def get_sampwidth(self):
        """Return the expected sample width for the channel.

        Notice that while convert is not applied, it can be different of the
        current one  of the channel.

        :returns: the sample width that will be used by the converter

        """
        return self._sampwidth

    # -----------------------------------------------------------------------
    # Setters
    # -----------------------------------------------------------------------

    def set_framerate(self, framerate):
        """Fix the expected frame rate for the channel.

        Notice that while convert is not applied, it can be different of the
        current one  of the channel.

        :param framerate:

        """
        self._framerate = int(framerate)

    # -----------------------------------------------------------------------

    def set_sampwidth(self, sampwidth):
        """Fix the expected sample width for the channel.

        Notice that while convert is not applied, it can be different of the
        current one  of the channel.

        :param sampwidth:

        """
        self._sampwidth = int(sampwidth)

    # -----------------------------------------------------------------------

    def convert(self):
        """Convert the channel.

        Convert to the expected (already) given sample width and frame rate.

        """
        new_channel = sppasChannel()
        new_channel.set_frames(self.__convert_frames(self._channel.get_frames()))
        new_channel.set_sampwidth(self._sampwidth)
        new_channel.set_framerate(self._framerate)

        self._channel = new_channel

    # -----------------------------------------------------------------------
    # Workers
    # -----------------------------------------------------------------------

    def bias(self, bias_value):
        """Convert the channel with a bias added to each frame.

        Samples wrap around in case of overflow.

        :param bias_value: (int) the value to bias the frames

        """
        if bias_value == 0:
            return
        new_channel = sppasChannel()
        new_channel.set_sampwidth(self._sampwidth)
        new_channel.set_framerate(self._framerate)
        a = sppasAudioFrames(self._channel.get_frames(self._channel.get_nframes()), self._channel.get_sampwidth(), 1)
        new_channel.set_frames(a.bias(bias_value))

        self._channel = new_channel

    # -----------------------------------------------------------------------

    def mul(self, factor):
        """Convert the channel.

        All frames in the original channel are multiplied by the floating-
        point value factor.
        Samples are truncated in case of overflow.

        :param factor: (float) the factor to multiply the frames

        """
        if factor == 1.:
            return
        new_channel = sppasChannel()
        new_channel.set_sampwidth(self._sampwidth)
        new_channel.set_framerate(self._framerate)
        a = sppasAudioFrames(self._channel.get_frames(self._channel.get_nframes()), self._channel.get_sampwidth(), 1)
        new_channel.set_frames(a.mul(factor))

        self._channel = new_channel

    # ----------------------------------------------------------------------

    def remove_offset(self):
        """Convert the channel by removing the offset in the channel."""
        new_channel = sppasChannel()
        new_channel.set_sampwidth(self._sampwidth)
        new_channel.set_framerate(self._framerate)
        a = sppasAudioFrames(self._channel.get_frames(self._channel.get_nframes()), self._channel.get_sampwidth(), 1)
        avg = a.avg()
        new_channel.set_frames(a.bias(- avg))

        self._channel = new_channel

    # ----------------------------------------------------------------------

    def sync(self, channel):
        """Convert the channel with the parameters from the channel put in input.

        :param channel: (sppasChannel) the channel used as a model

        """
        if isinstance(channel, sppasChannel) is not True:
            raise TypeError("Expected a channel, got %s" % type(channel))

        self._sampwidth = channel.get_sampwidth()
        self._framerate = channel.get_framerate()
        self.convert()

    # ----------------------------------------------------------------------

    def remove_frames(self, begin, end):
        """Convert the channel by removing frames.

        :param begin: (int) the position of the beginning of the frames to remove
        :param end: (int) the position of the end of the frames to remove

        """
        if begin == end:
            return
        if end < begin:
            raise ValueError
        new_channel = sppasChannel()
        f = self._channel.get_frames()
        new_channel.set_frames(f[:begin*self._sampwidth] + f[end*self._sampwidth:])
        new_channel.set_sampwidth(self._sampwidth)
        new_channel.set_framerate(self._framerate)
        self._channel = new_channel

    # ----------------------------------------------------------------------

    def add_frames(self, frames, position):
        """Convert the channel by adding frames.

        :param frames: (str)
        :param position: (int) the position where the frames will be inserted

        """
        if len(frames) == 0:
            return
        new_channel = sppasChannel()
        f = self._channel.get_frames()
        new_channel.set_frames(f[:position*self._sampwidth] + frames + f[position*self._sampwidth:])
        new_channel.set_sampwidth(self._sampwidth)
        new_channel.set_framerate(self._framerate)
        self._channel = new_channel

    # ----------------------------------------------------------------------

    def append_frames(self, frames):
        """Convert the channel by appending frames.

        :param frames: (str) the frames to append

        """
        if len(frames) == 0:
            return
        new_channel = sppasChannel()
        new_channel.set_frames(self._channel.get_frames() + frames)
        new_channel.set_sampwidth(self._sampwidth)
        new_channel.set_framerate(self._framerate)
        self._channel = new_channel

    # ----------------------------------------------------------------------
    # Private
    # ----------------------------------------------------------------------

    def __convert_frames(self, frames):
        """Convert frames to the expected sample width and frame rate.

        :param frames: (str) the frames to convert

        """
        f = frames
        fragment = sppasChannelFrames(f)

        # Convert the sample width if it needs to
        if self._channel.get_sampwidth() != self._sampwidth:
            fragment.change_sampwidth(self._channel.get_sampwidth(), self._sampwidth)

        # Convert the self._framerate if it needs to
        if self._channel.get_framerate() != self._framerate:
            fragment.resample(self._sampwidth, self._channel.get_framerate(), self._framerate)

        return fragment.get_frames()
