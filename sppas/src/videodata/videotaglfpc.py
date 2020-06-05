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

    def __init__(self, tier, buffer_size, nb_frames, fps):
        """Create a new VideoTagLFPC instance.

        :param tier: (Idk) The ID of the keys(picote).
        :param buffer_size: (int) The size of the buffer.
        :param nb_frames: (int) The number of frame in the video.
        :param fps: (int) The fps of the video.

        """
        # The size of the buffer
        self.__size = buffer_size

        # The duration of the video(milliseconds)
        self.__duration = int(nb_frames * fps)

        # The fps of the video
        self.__fps = fps

        # The list of hands
        self.__hands = list()
        self.__init_hands()

        # The list of transcription
        self.__transcription = list()
        self.__init_transcription(tier)

    # -----------------------------------------------------------------------

    def __init_hands(self):
        """Store the paths of the hands."""
        for i in range(9):
            try:
                filename = "hand-lfpc-" + str(i) + ".png"
                path = os.path.join(sppasPathSettings().etc, "image", filename)
                self.__hands.append(path)
            except OSError:
                return "File does not exist"

    # -----------------------------------------------------------------------

    def __init_transcription(self, transcription):
        """Init the transcription list.

        :param transcription: (Idk) The object which contain audio transcription.

        """
        # Browse the transcription and add each "syllabe" in the private list
        for i in range(400):
            # Bla bla bla

            # Add it in the transcription list
            self.__transcription.append((0, 1, "consonant_ID", "vowel_ID"))

        self.__transform_transcription()

    # -----------------------------------------------------------------------

    def __transform_transcription(self):
        """Convert the transcription list into something useful."""
        list_syllabe = list()

        # Loop over the transcription
        for syllable in self.__transcription:

            # Duration equal "end_time" - "start_time"
            duration = syllable[1] - syllable[0]

            # nb_frames = duration(ms) / fps(images/second)
            nb_frame = int(duration / self.__fps)

            # Determine the hand and the position for the syllable
            for i in range(nb_frame):
                # Add it in the list
                list_syllabe.append((syllable[2], syllable[3]))

        # Replace the transcription list
        self.__transcription.clear()
        self.__transcription = list_syllabe

    # -----------------------------------------------------------------------

    def calcul_position(self, pointID, landmark):
        """Calcul the coordinates of the LFPC points.

        :param pointID: (int) The ID of the LFPC point.
        :param landmark: (list) The landmark positions.

        """
        x = int()
        y = int()

        #   - Position 0: at right, out of the face
        if pointID == 0:
            # x = x.15 + ((x.15 - x.36) / 5.)
            # y = x.15
            x = int(landmark[2][0] - landmark[17][0])
            y = int(landmark[2][1])

        #   - Position 1: at left, close to the eye
        elif pointID == 1:
            # x = x.1 + ((x.30 - x.1) / 3.)
            # y = y.1
            x = landmark[0][0] + ((landmark[29][0] - landmark[1][0]) / 3.)
            y = landmark[0][1]

        #   - Position 2: at the middle of the chin
        elif pointID == 2:
            # x = x.9
            # y = y.9 - ((y.9 - y.58) / 3.)
            x = landmark[8][0]
            y = landmark[8][1] - ((landmark[8][1] - landmark[57][1]) / 3.)

        #   - Position 3: at left
        elif pointID == 3:
            # x = x.3
            # y = y.3
            x = landmark[2][0]
            y = landmark[2][1]

        #   - Position 4: at left of the mouth
        elif pointID == 4:
            # x = x.4 + ((x.49 - x.4) / 5.)
            # y = y.4
            x = landmark[3][0] + ((landmark[48][0] - landmark[3][0]) / 5.)
            y = landmark[3][1]

        #   - Position 5: under the chin, out of the face
        elif pointID == 5:
            # x = x.9
            # y = y.9 + ((y.9 - y.58) / 2.)
            x = landmark[8][0]
            y = landmark[8][1] + ((landmark[8][1] - landmark[57][1]) / 2.)

        return x, y

    # -----------------------------------------------------------------------

    def process(self, buffer):
        """Launch the tag process."""
        for i in range(len(buffer)):
            # Store the lfpc code in a var
            lfpc_code = self.__transcription[i + buffer.get_frame() - buffer.get_size()]

            # Store the path of the hand to use
            path = lfpc_code[0]

            # Determine the position of the hand on the face
            x, y = self.calcul_position(lfpc_code[1], buffer.get_landmark(0, i))

            # Add in a new buffer
            buffer.add_lfpc((path, x, y))

    # -----------------------------------------------------------------------
