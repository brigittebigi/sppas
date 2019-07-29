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

    src.audiodata.audiovolume.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    The volume is the estimation of RMS values, sampled with a window of 10ms.

"""

from .audioframes import sppasAudioFrames
from .basevolume import sppasBaseVolume

# ----------------------------------------------------------------------------


class sppasAudioVolume(sppasBaseVolume):
    """Estimate the volume of an audio file.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2017  Brigitte Bigi

    """

    def __init__(self, audio, win_len=0.01):
        """Create a sppasAudioVolume instance.

        :param audio: (sppasAudioPCM) The audio to work on.
        :param win_len: (float) Window length to estimate the volume.

        """
        super(sppasAudioVolume, self).__init__(win_len)

        # Remember current position
        pos = audio.tell()

        # Rewind to the beginning
        audio.rewind()

        # Find the rms values (explore all frames)
        nb_frames = int(win_len * audio.get_framerate())

        while audio.tell() < audio.get_nframes():
            frames = audio.read_frames(nb_frames)
            a = sppasAudioFrames(frames, audio.get_sampwidth(), audio.get_nchannels())
            self._volumes.append(a.rms())

        # Returns to the position where we was before
        audio.seek(pos)

        self._rms = audio.rms()
