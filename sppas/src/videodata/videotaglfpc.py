# -*- coding : UTF-8 -*-
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

    src.videodata.videotaglfpc.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~

"""

import os

from sppas.src.config import sppasPathSettings
from sppas.src.videodata.personsbuffer import PersonsBuffer
from sppas.src.imagedata.coordinates import Coordinates

# ---------------------------------------------------------------------------


class VideoTagLFPC(object):
    """Class to detect faces.

    :author:       Florian Hocquet
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      contact@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2020  Brigitte Bigi

    This class allows to use a Buffer on a video to manage it
    sequentially and to have a better control on it.

    """

    def __init__(self, transcription, buffer_size, nb_frames, fps):
        """Create a new VideoTagLFPC instance.

        :param transcription: (Idk) The object which contain audio transcription.
        :param buffer_size: (int) The size of the buffer.
        :param nb_frames: (int) The number of frame in the video.
        :param fps: (int) The fps of the video.

        """
        self.__transcription = list()
        self.__init_transcription(transcription)

        # The size of the buffer
        self.__size = buffer_size

        # The duration of the video(milliseconds)
        self.__duration = int(nb_frames * fps)

        # The fps of the video
        self.__fps = fps

        # The list of hands
        self.__hands = list()
        self.__init_hands()

    # -----------------------------------------------------------------------

    def __init_hands(self):
        """Return the predictor file."""
        for i in range(9):
            try:
                filename = "hand-lfpc-" + str(i) + ".png"
                path = os.path.join(sppasPathSettings().resources, "image", filename)
                self.__hands.append(path)
            except OSError:
                return "File does not exist"

    # -----------------------------------------------------------------------

    def __init_transcription(self, transcription):
        """Init the transcription list."""
        # Browse the transcription and add each "syllabe" in the private list
        for i in range(400):
            # Bla bla bla
            self.__transcription.append(("start_ms", "end_ms", "consonant_ID", "vowel_ID"))

    # -----------------------------------------------------------------------

    def __transform_transcription(self):
        """Convert the transcription list into something useful."""
        liste_buffer = list()
        for syllable in self.__transcription:
            duration = syllable[1] - syllable[0]
            nb_frame = duration / self.__fps
            hand, pointID = self.__hand(syllable[2], syllable[3])
            for i in range(nb_frame):
                liste_buffer.append((hand, pointID))

    # -----------------------------------------------------------------------

    def __hand(self, consonant_id, vowel_id):
        """Determine where and which hand to place for a syllable.

        :param consonant_id: (Idk) The object which contain audio transcription.
        :param vowel_id: (int) The number of frame in the video

        """
        # Bla bla bla
        return 1, 2

    # -----------------------------------------------------------------------

    def process(self, transcription):
        """Launch the tag process."""

    # -----------------------------------------------------------------------
