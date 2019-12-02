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

    src.annotations.irms.py
    ~~~~~~~~~~~~~~~~~~~~~~~

"""

from sppas.src.audiodata.channel import sppasChannel
from sppas.src.audiodata.channelvolume import sppasChannelVolume

# ---------------------------------------------------------------------------


class IntervalsRMS(object):
    """Estimate RMS on intervals of a channel.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2019  Brigitte Bigi

    """

    def __init__(self, channel=None):
        """Create a sppasIntervalsRMS instance.

        :param channel: (sppasChannel) the input channel

        """
        self.__win_len = 0.010

        self._channel = None
        self.__volumes = None
        if channel is not None:
            self.set_channel(channel)

    # -----------------------------------------------------------------------
    # Getters and setters
    # -----------------------------------------------------------------------

    def set_channel(self, channel):
        """Set a channel, then reset all previous results.

        :param channel: (sppasChannel)

        """
        if isinstance(channel, sppasChannel) is False:
            raise TypeError('Expected a sppasChannel, got {:s} instead'
                            ''.format(str(type(channel))))

        self._channel = channel
        self.__volumes = None

    # -----------------------------------------------------------------------

    def estimate(self, begin, end):
        """Estimate RMS values of the given interval.

        rms = sqrt(sum(S_i^2)/n)

        :param begin: (float) Start value, in seconds
        :param end: (float) End value, in seconds

        """
        begin = float(begin)
        end = float(end)
        if (end - begin) < self.__win_len:
            raise Exception('Invalid interval [{:f};{:f}]'.format(begin, end))

        # Create a channel with only the frames of the interval [begin, end]
        from_pos = int(begin * float(self._channel.get_framerate()))
        to_pos = int(end * float(self._channel.get_framerate()))
        fragment = self._channel.extract_fragment(from_pos, to_pos)

        # Estimates the RMS values
        self.__volumes = sppasChannelVolume(fragment, self.__win_len)

    # -----------------------------------------------------------------------

    def get_values(self):
        """Return the list of estimated rms values."""
        if self.__volumes is None:
            return list()
        return self.__volumes.volumes()

    # -----------------------------------------------------------------------

    def get_rms(self):
        """Return the global rms value or 0."""
        if self.__volumes is None:
            return 0
        return self.__volumes.volume()

    # -----------------------------------------------------------------------

    def get_fmean(self):
        """Return the fmean rms value or 0."""
        if self.__volumes is None:
            return 0.
        return self.__volumes.mean()

