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

    src.audiodata.aio.sunauio.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""

import sunau

from ..audio import sppasAudioPCM

# ---------------------------------------------------------------------------


class SunauIO(sppasAudioPCM):
    """
    :author:      Nicolas Chazeau, Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2017  Brigitte Bigi
    :summary:      A Sun AU file open/save utility class.

    """
    def __init__(self):
        """Constructor."""
        super(SunauIO, self).__init__()

    # ------------------------------------------------------------------------

    def open(self, filename):
        """Get an audio from a Audio Interchange File Format file.

        :param filename: (str) input file name.

        """
        # Use the standard wave library to load the wave file
        # open method returns a Wave_read() object
        self._audio_fp = sunau.open(filename, "r")

    # -----------------------------------------------------------------------

    def save(self, filename):
        """Write an audio content as a Audio Interchange File Format file.

        :param filename: (str) output filename.

        """
        if self._audio_fp:
            self.rewind()
            frames = self._audio_fp.readframes(self._audio_fp.getnframes())
            self.save_fragment(filename, frames)

        elif len(self) == 1:
            channel = self._channels[0]
            f = sunau.Au_write(filename)
            f.setnchannels(1)
            f.setsampwidth(channel.get_sampwidth())
            f.setframerate(channel.get_framerate())
            try:
                f.writeframes(channel.frames)
            finally:
                f.close()

        else:
            self.verify_channels()

            frames = b""
            sp = self._channels[0].get_sampwidth()
            for i in range(0, self._channels[0].get_nframes()*sp, sp):
                for j in range(len(self._channels)):
                    fc = self._channels[j].get_frames()
                    frames += fc[i:i+sp]

            f = sunau.Au_write(filename)
            f.setnchannels(len(self._channels))
            f.setsampwidth(sp)
            f.setframerate(self._channels[0].get_framerate())
            try:
                f.writeframes(frames)
            finally:
                f.close()

    # -----------------------------------------------------------------------

    def save_fragment(self, filename, frames):
        """Write an audio content as a Audio Interchange File Format file.

        :param filename: (str) output filename.
        :param frames: (str) the frames to write

        """
        f = sunau.Au_write(filename)
        f.setnchannels(self.get_nchannels())
        f.setsampwidth(self.get_sampwidth())
        f.setframerate(self.get_framerate())
        try:
            f.writeframes(frames)
        finally:
            f.close()
