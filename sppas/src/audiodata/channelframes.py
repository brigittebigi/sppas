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

    src.audiodata.channelframes.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""

from sppas.src.utils import b
from .audioframes import sppasAudioFrames

# ---------------------------------------------------------------------------


class sppasChannelFrames(object):
    """
    :author:       Nicolas Chazeau, Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2017  Brigitte Bigi
    :summary:      An utility for frames of one channel only.

    """
    def __init__(self, frames=b""):
        """Create a sppasChannelFrames instance.

        :param frames: (str) Frames that must be MONO ONLY.

        """
        self._frames = frames

    # -----------------------------------------------------------------------

    def get_frames(self):
        """Return the frames

        :returns: (str) the frames

        """
        return self._frames

    # ----------------------------------------------------------------------------

    def set_frames(self, frames):
        """Set the frames.

        :param frames: (str) the frames to set

        """
        self._frames = frames

    # ----------------------------------------------------------------------------

    def append_silence(self, nframes):
        """Create n frames of silence and append it to the frames.

        :param nframes: (int) the number of frames of silence to append

        """
        nframes = int(nframes)
        if nframes <= 0:
            return False

        self._frames += b(" \x00") * nframes
        return True

    # ----------------------------------------------------------------------------

    def prepend_silence(self, nframes):
        """Create n frames of silence and prepend it to the frames.

        :param nframes: (int) the number of frames of silence to append

        """
        nframes = int(nframes)
        if nframes <= 0:
            return False

        self._frames = b(" \x00") * nframes + self._frames
        return True

    # ----------------------------------------------------------------------------

    def resample(self, sampwidth, rate, newrate):
        """Resample the frames with a new frame rate.

        :param sampwidth: (int) sample width of the frames.
        :param rate: (int) current frame rate of the frames
        :param newrate: (int) new frame rate of the frames

        """
        a = sppasAudioFrames(self._frames, sampwidth, 1)
        self._frames = a.resample(rate, newrate)

    # ----------------------------------------------------------------------------

    def change_sampwidth(self, sampwidth, newsampwidth):
        """Change the number of bytes used to encode the frames.

        :param sampwidth: (int) current sample width of the frames.
        (1 for 8 bits, 2 for 16 bits, 4 for 32 bits)
        :param newsampwidth: (int) new sample width of the frames.
        (1 for 8 bits, 2 for 16 bits, 4 for 32 bits)

        """
        a = sppasAudioFrames(self._frames, sampwidth, 1)
        self._frames = a.change_sampwidth(newsampwidth)

    # ----------------------------------------------------------------------------

    @staticmethod
    def get_minval(size, signed=True):
        return sppasAudioFrames().get_minval(size, signed)

    # ----------------------------------------------------------------------------

    @staticmethod
    def get_maxval(size, signed=True):
        return sppasAudioFrames().get_maxval(size, signed)
