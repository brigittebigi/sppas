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

    src.audiodata.channelsmixer.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""

import struct

from .channel import sppasChannel
from .channelframes import sppasChannelFrames
from .audiodataexc import MixChannelError
from .audioconvert import sppasAudioConverter

# ---------------------------------------------------------------------------


class sppasChannelMixer(object):
    """
    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2017  Brigitte Bigi
    :summary:      A channel utility class to mix several channels in one.

    """
    def __init__(self):
        """Create a ChannelMixer instance."""
        
        self._channels = []
        self._factors = []

    # -----------------------------------------------------------------------

    def get_channel(self, idx):
        """Return the channel of a given index.

        :param idx: (int) the index of the channel to return
        :returns: (sppasChannel)

        """
        return self._channels[idx]

    # -----------------------------------------------------------------------

    def append_channel(self, channel, factor=1):
        """Append a channel and the corresponding factor for a mix.

        :param channel: (Channel object) the channel to append
        :param factor: (float) the factor associated to the channel

        """
        self._channels.append(channel)
        self._factors.append(factor)

    # -----------------------------------------------------------------------

    def check_channels(self):
        """Checking the conformity of the channels."""

        if len(self._channels) == 0:
            raise MixChannelError

        sampwidth = self._channels[0].get_sampwidth()
        framerate = self._channels[0].get_framerate()
        nframes = self._channels[0].get_nframes()

        for i in range(1, len(self._channels)):

            if self._channels[i].get_sampwidth() != sampwidth:
                raise MixChannelError(1)

            if self._channels[i].get_framerate() != framerate:
                raise MixChannelError(2)

            if self._channels[i].get_nframes() != nframes:
                raise MixChannelError(3)

    # -----------------------------------------------------------------------

    @staticmethod
    def _sample_calculator(channels, pos, sampwidth, factors, attenuator):
        """Return the sample value, applying a factor and an attenuator.

        :param channels: (Channel[]) the list of channels
        :param pos: (int) the position of the sample to calculate
        :param sampwidth: (int) the sample width
        :param factors: (float[]) the list of factors to apply to each sample of a channel (1 channel = 1 factor)
        :param attenuator: (float) a factor to apply to each sum of samples

        :returns: (float) the value of the sample calculated

        """
        # variables to compare the value of the result sample to avoid clipping
        minval = float(sppasChannelFrames().get_minval(sampwidth))
        maxval = float(sppasChannelFrames().get_maxval(sampwidth))

        # the result sample is the sum of each sample with the application of the factors
        sampsum = 0
        for factor, channel in zip(factors, channels):
            data = channel.get_frames()[pos:pos+sampwidth]
            data = sppasAudioConverter().unpack_data(data, sampwidth, 1)
            data = data[0]
            # without a cast, sum is a float!
            sampsum += (data[0] * factor * attenuator)

        # truncate the values if there is clipping
        if sampsum < 0:
            return max(sampsum, minval)

        elif sampsum > 0:
            return min(sampsum, maxval)

        return 0.

    # -----------------------------------------------------------------------

    def mix(self, attenuator=1):
        """Mix the channels of the list in one.

        :param attenuator: (float) the factor to apply to each sample calculated
        :returns: the result Channel

        """
        self.check_channels()

        sampwidth = self._channels[0].get_sampwidth()
        framerate = self._channels[0].get_framerate()

        frames = b""
        if sampwidth == 4:
            for s in range(0, len(self._channels[0].get_frames()), sampwidth):
                value = sppasChannelMixer._sample_calculator(self._channels, s, sampwidth, self._factors, attenuator)
                try:
                    frames += struct.pack("<l", long(value))  # python 2
                except:
                    frames += struct.pack("<l", int(value))  # python 3

        elif sampwidth == 2:
            for s in range(0, len(self._channels[0].get_frames()), sampwidth):
                value = sppasChannelMixer._sample_calculator(self._channels, s, sampwidth, self._factors, attenuator)
                frames += struct.pack("<h", int(value))

        else:
            for s in range(0, len(self._channels[0].get_frames()), sampwidth):
                value = sppasChannelMixer._sample_calculator(self._channels, s, sampwidth, self._factors, attenuator)
                frames += struct.pack("<b", int(value))

        return sppasChannel(framerate, sampwidth, frames)

    # -----------------------------------------------------------------------

    def get_minmax(self):
        """Return a tuple with the minimum and the maximum samples values.

        :returns: the tuple (minvalue, maxvalue)

        """
        # ensuring conformity
        self.check_channels()

        sampwidth = self._channels[0].get_sampwidth()
        minval = 0
        maxval = 0
        sampsum = 0
        for s in range(0, len(self._channels[0].get_frames()), sampwidth):
            value = sppasChannelMixer._sample_calculator(self._channels, s, sampwidth, self._factors, 1)
            try:
                sampsum = long(value)   # python 2
            except:
                sampsum = int(value)  # python 3
            maxval = max(sampsum, maxval)
            minval = min(sampsum, minval)

        return minval, maxval

    # -----------------------------------------------------------------------

    def norm_length(self):
        """Normalize the number of frames of all the channels,
        by appending silence at the end.

        """
        nframes = 0
        for i in range(len(self._channels)):
            nframes = max(nframes, self._channels[i].get_nframes())

        for i in range(len(self._channels)):
            if self._channels[i].get_nframes() < nframes:
                fragment = sppasChannelFrames(self._channels[i].get_frames())
                fragment.append_silence(nframes - self._channels[i].get_nframes())
                self._channels[i] = sppasChannel(self._channels[i].get_framerate(),
                                                 self._channels[i].get_sampwidth(),
                                                 fragment.get_frames())
