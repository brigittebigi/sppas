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

    src.audiodata.aio.aiffio.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Audio Interchange File Format (AIFF) is an audio file format developed by
    Apple Inc. in 1988.

"""

import struct
import aifc

from sppas.src.utils import u

from ..audio import sppasAudioPCM
from ..audiodataexc import AudioDataError

# ---------------------------------------------------------------------------


class AiffIO(sppasAudioPCM):
    """
    :author:      Nicolas Chazeau, Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2017  Brigitte Bigi
    :summary:      An AIFF/AIFC file open/save utility class.

    """
    def __init__(self):
        """Constructor."""
        super(AiffIO, self).__init__()

    # ------------------------------------------------------------------------

    def open(self, filename):
        """Get an audio from an Audio Interchange File Format file.

        :param filename: (str) input file name.

        """
        # Passing a unicode filename to aifc.open() results in the argument
        # being treated like a filepointer instead of opening the file.
        fp = open(u(filename), "r")

        # Use the standard aifc library to load the audio file
        # open method return an Aifc_read object
        self._audio_fp = aifc.open(fp)

    # ----------------------------------------------------------------------
    # Read content, for audiofp
    # ----------------------------------------------------------------------

    def read_frames(self, nframes):
        """Specific frame reader for aiff files.

        AIFF data is in big endian and we need little endian.

        :param nframes: (int) the the number of frames wanted
        :returns: (str) frames

        """
        if not self._audio_fp:
            raise AudioDataError

        data = self._audio_fp.readframes(nframes)

        if self.get_sampwidth() == 4:
            data = struct.unpack(">%ul" % (len(data) / 4), data)
            return struct.pack("<%ul" % (len(data)), *data)

        elif self.get_sampwidth() == 2:
            data = struct.unpack(">%uh" % (len(data)/2), data)
            return struct.pack("<%uh" % (len(data)), *data)

        return data

    # ----------------------------------------------------------------------

    @staticmethod
    def _write_frames(fp, data):
        """Specific writer for aiff files.

        Data is in little endian and aiff files need big endian.

        :param fp: (sppasAudioPCM) the audio file pointer to write in
        :param data: (str) frames to write

        """
        if fp.getsampwidth() == 4:
            data = struct.unpack("<%ul" % (len(data)/4), data)
            fp.writeframes(struct.pack(">%ul" % (len(data)), *data))

        elif fp.getsampwidth() == 2:
            data = struct.unpack("<%uh" % (len(data)/2), data)
            fp.writeframes(struct.pack(">%uh" % (len(data)), *data))

        else:
            fp.writeframes(data)

    # ----------------------------------------------------------------------

    def save(self, filename):
        """Write an audio content as a Audio Interchange File Format file.

        :param filename: (str) output filename.

        """
        if self._audio_fp is not None:
            self.rewind()
            frames = self._audio_fp.readframes(self._audio_fp.getnframes())
            self.save_fragment(filename, frames)

        elif len(self) == 1:
            channel = self._channels[0]
            fp = open(filename, 'w')
            f = aifc.open(fp)
            f.setnchannels(1)
            f.setsampwidth(channel.get_sampwidth())
            f.setframerate(channel.get_framerate())
            f.setnframes(channel.get_nframes())
            try:
                AiffIO._write_frames(f, channel.get_frames())
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

            f = aifc.open(filename, 'w')
            f.setnchannels(len(self._channels))
            f.setsampwidth(sp)
            f.setframerate(self._channels[0].get_framerate())
            f.setnframes(self._channels[0].get_nframes())
            try:
                AiffIO._write_frames(f, frames)
            finally:
                f.close()

    # -----------------------------------------------------------------------

    def save_fragment(self, filename, frames):
        """Write an audio content as a Audio Interchange File Format file.

        :param filename (str) output filename.
        :param frames (str) the frames to write

        """
        fp = open(u(filename), "w")
        f = aifc.Aifc_write(fp)
        f.setnchannels(self.get_nchannels())
        f.setsampwidth(self.get_sampwidth())
        f.setframerate(self.get_framerate())
        f.setnframes(len(frames)/self.get_nchannels()/self.get_sampwidth())
        try:
            AiffIO._write_frames(f, frames)
        except Exception:
            raise
        finally:
            f.close()
