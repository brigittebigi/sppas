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

    src.audiodata.audioframes.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""

import audioop
import struct

from .audiodataexc import SampleWidthError, ChannelIndexError

# ---------------------------------------------------------------------------


class sppasAudioFrames(object):
    """An utility class for audio frames.

    :author:       Nicolas Chazeau, Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2016  Brigitte Bigi

    TODO: There's no unittests of this class.

    """
    def __init__(self, frames=b"", sampwidth=2, nchannels=1):
        """Create an sppasAudioFrames instance.

        :param frames: (str) input frames.
        :param sampwidth: (int) sample width of the frames.
        :param nchannels: (int) number of channels in the samples

        """
        # Check the type and if values are appropriate
        # frames = str(frames)
        if sampwidth not in [1, 2, 4]:
            raise SampleWidthError
        nchannels = int(nchannels)
        if nchannels < 1:
            raise ChannelIndexError(nchannels)

        # Set data
        self._frames = frames
        self._sampwidth = sampwidth
        self._nchannels = nchannels

    # -----------------------------------------------------------------------

    def resample(self, rate, new_rate=16000):
        """Return re-sampled frames.

        :param rate: (int) current frame rate of the frames
        :param new_rate: (int) new frame rate of the frames
        :returns: (str) converted frames

        """
        return audioop.ratecv(self._frames, self._sampwidth, self._nchannels, rate, new_rate, None)[0]

    # -----------------------------------------------------------------------

    def change_sampwidth(self, new_sampwidth):
        """Return frames with the given number of bytes.

        :param new_sampwidth: (int) new sample width of the frames.
            (1 for 8 bits, 2 for 16 bits, 4 for 32 bits)
        :returns: (str) converted frames

        """
        if new_sampwidth not in [1, 2, 4]:
            raise SampleWidthError
        return audioop.lin2lin(self._frames, self._sampwidth, new_sampwidth)

    # -----------------------------------------------------------------------

    def bias(self, value):
        """Return frames that is the original fragment with a bias added to each sample.
        Samples wrap around in case of overflow.

        :param value: (int) the bias which will be applied to each sample.
        :returns: (str) converted frames

        """
        value = int(value)
        return audioop.bias(self._frames, self._sampwidth, value)

    # -----------------------------------------------------------------------

    def mul(self, factor):
        """Return frames for which all samples are multiplied by factor.
        Samples are truncated in case of overflow.

        :param factor: (int) the factor which will be applied to each sample.
        :returns: (str) converted frames

        """
        return audioop.mul(self._frames, self._sampwidth, factor)

    # -----------------------------------------------------------------------

    def cross(self):
        """Return the number of zero crossings in frames.

        :returns: number of zero crossing

        """
        return audioop.cross(self._frames, self._sampwidth)

    # -----------------------------------------------------------------------

    def minmax(self):
        """Return the (minimum,maximum) of the values of all frames.

        :returns (min,max)

        """
        return audioop.minmax(self._frames, self._sampwidth)

    # -----------------------------------------------------------------------

    def min(self):
        """Return the minimum of the values of all frames."""

        return audioop.minmax(self._frames, self._sampwidth)[0]

    # -----------------------------------------------------------------------

    def max(self):
        """Return the maximum of the values of all frames."""

        return audioop.minmax(self._frames, self._sampwidth)[1]

    # -----------------------------------------------------------------------

    def avg(self):
        """Return the average of all the frames."""

        return audioop.avg(self._frames, self._sampwidth)

    # -----------------------------------------------------------------------

    def rms(self):
        """Return the root mean square of the frames."""
        if self._nchannels == 1:
            return audioop.rms(self._frames, self._sampwidth)

        rms_sum = 0
        for i in range(self._nchannels):
            new_frames = b""
            for j in range(i*self._sampwidth,
                           len(self._frames),
                           self._sampwidth*self._nchannels):

                for k in range(self._sampwidth):
                    new_frames += self._frames[j+k]
            rms_sum += audioop.rms(new_frames, self._sampwidth)

        return int(rms_sum/self._nchannels)

    # -----------------------------------------------------------------------

    def clipping_rate(self, factor):
        """Return the clipping rate of the frames.

        :param factor: (float) An interval to be more precise on clipping rate.
        It will consider that all frames outside the interval are clipped.
        Factor has to be between 0 and 1.
        :returns: (float) the clipping rate

        """
        if self._sampwidth == 4:
            data = struct.unpack("<%ul" % (len(self._frames) / 4), self._frames)
        elif self._sampwidth == 2:
            data = struct.unpack("<%uh" % (len(self._frames) / 2), self._frames)
        else:
            data = struct.unpack("%uB" % len(self._frames), self._frames)
            data = [s - 128 for s in data]

        max_val = int(sppasAudioFrames.get_maxval(self._sampwidth) * float(factor))
        min_val = int(sppasAudioFrames.get_minval(self._sampwidth) * float(factor))

        nb_clipping = 0
        for d in data:
            if d >= max_val or d <= min_val:
                nb_clipping += 1

        return float(nb_clipping)/len(data)

    # -----------------------------------------------------------------------

    @staticmethod
    def get_maxval(size, signed=True):
        """Return the max value for a given sampwidth.

        :param size: (int) the sampwidth
        :param signed: (bool) if the values will be signed or not
        :returns: (int) the max value

        """
        if signed and size == 1:
            return 0x7f
        elif size == 1:
            return 0xff
        elif signed and size == 2:
            return 0x7fff
        elif size == 2:
            return 0xffff
        elif signed and size == 4:
            return 0x7fffffff
        elif size == 4:
            return 0xffffffff

    # -----------------------------------------------------------------------

    @staticmethod
    def get_minval(size, signed=True):
        """Return the min value for a given sampwidth.

        :param size: (int) the sampwidth
        :param signed: (bool) if the values will be signed or not
        :returns: (int) the min value

        """
        if not signed:
            return 0
        elif size == 1:
            return -0x80
        elif size == 2:
            return -0x8000
        elif size == 4:
            return -0x80000000
