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

    src.audiodata.audioconvert.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""

import struct
import math

from .audiodataexc import SampleWidthError, ChannelIndexError

# ---------------------------------------------------------------------------


class sppasAudioConverter(object):
    """An utility to convert data formats.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2017  Brigitte Bigi

    """

    def __init__(self):
        """Create a sppasAudioConverter instance."""
        pass

    # -----------------------------------------------------------------------

    @staticmethod
    def unpack_data(frames, samples_width, nchannels=1):
        """Turn frames into samples.

        Unpack the data frames depending on their sample width.

        :param frames: (str) Audio frames
        :param samples_width: (int)
        :param nchannels: (int) number of channels in the frames

        """
        samples_width = int(samples_width)

        # Unpack to get all values, depending on the number of bytes of each value.
        if samples_width == 4:
            data = list(struct.unpack("<%ul" % (len(frames) / 4), frames))

        elif samples_width == 2:
            data = list(struct.unpack("<%uh" % (len(frames) / 2), frames))

        elif samples_width == 1:
            tmp_data = struct.unpack("%uB" % len(frames), frames)
            data = [s - 128 for s in tmp_data]

        else:
            raise SampleWidthError(samples_width)

        samples = list()
        if nchannels > 1:
            # Split channels
            for i in range(nchannels):
                samples.append([data[j] for j in range(i, len(data), nchannels)])
        else:
            samples.append(list(data))

        return samples

    # ----------------------------------------------------------------------------

    @staticmethod
    def samples2frames(samples, samples_width, nchannels=1):
        """Turn samples into frames.

        :param samples: (int[][]) samples list,
        first index is the index of the channel, second is the index of the sample.
        :param samples_width: (int) sample width of the frames.
        :param nchannels: (int) number of channels in the samples
        :returns: frames

        """
        samples_width = int(samples_width)
        nchannels = int(nchannels)
        if nchannels < 1:
            raise ChannelIndexError(nchannels)

        nframes = len(samples[0])
        frames = b""

        if samples_width == 4:
            for i in range(nframes):
                for j in range(nchannels):
                    frames += struct.pack("<l", samples[j][i])
            return frames

        if samples_width == 2:
            for i in range(nframes):
                for j in range(nchannels):
                    frames += struct.pack("<h", samples[j][i])
            return frames

        if samples_width == 1:
            for i in range(nframes):
                for j in range(nchannels):
                    frames += struct.pack("<b", samples[j][i])
            return frames

        raise SampleWidthError(samples_width)

    # -----------------------------------------------------------------------

    @staticmethod
    def hz2mel(value):
        """Return the equivalent value in a mel scale, from a frequency value.

        Mel is a unit of pitch proposed by Stevens, Volkmann and Newmann in
        1937. The mel scale is a scale of pitches judged by listeners to be
        equal in distance one from another.
        The name mel comes from the word melody to indicate that the scale
        is based on pitch comparisons.

        :param value: (int) the value to convert
        :returns: (int) the value in mel

        """
        return 2595*math.log10(1. + (float(value)/700.))

    # -----------------------------------------------------------------------

    @staticmethod
    def mel2hz(value):
        """Return the equivalent value in frequency, from a mel value.

        :param value: (int) the value in mel to convert
        :returns: (int) the value in dB

        """
        return round(700*(10**(float(value)/2595)-1), 2)

    # -----------------------------------------------------------------------

    @staticmethod
    def amp2db(value):
        """Return the equivalent value in a dB scale, from an amplitude value.

        Decibels express a power ratio, not an amount. They tell how many times
        more (positive dB) or less (negative dB) but not how much in absolute terms.
        Decibels are logarithmic, not linear.
        Doubling of the value leads to an increase of 6.02dB.

        :param value: (int) the amplitude value to convert
        :returns: (float) the value in dB

        """
        if value < 3:
            return 0.
        return round(20. * math.log10(value), 2)
