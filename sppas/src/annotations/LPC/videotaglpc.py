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
import cv2

from sppas.src.config import sppasPathSettings
from sppas import separators

from sppas.src.imagedata.imageutils import add_image, rotate_bound

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

    def __init__(self):
        """Create a new VideoTagLFPC instance."""

        # The list of hands
        self.__hands = list()
        self.__init_hands()

    # -----------------------------------------------------------------------

    def __init_hands(self):
        """Store the paths of the hands."""
        for i in range(9):
            try:
                filename = "hand-lfpc-" + str(i) + ".png"
                path = os.path.join(sppasPathSettings().resources, "lpc", filename)
                self.__hands.append(path)
            except OSError:
                return "File does not exist"

    # -----------------------------------------------------------------------

    def calcul_position(self, pointID, landmark):
        """Calcul the coordinates of the LFPC points.

        :param pointID: (int) The ID of the LFPC point.
        :param landmark: (list) The landmark positions.

        """
        x = int()
        y = int()

        #   - Position 0: at left, out of the face
        if pointID == 0:
            # x = x.1 + ((x.19 - x.0))
            # y = y.1
            x = landmark[0][0] - (landmark[18][0] - landmark[0][0])
            y = landmark[0][1]

        #   - Position 1: at left, close to the eye
        elif pointID == 1:
            # x = x.1 + ((x.29 - x.1) / 3.)
            # y = y.1 + ((x.18 - x.3) / 1.4)
            x = landmark[0][0] + ((landmark[28][0] - landmark[0][0]) / 3.)
            y = landmark[0][1] + ((landmark[17][1] - landmark[2][1]) / 1.4)

        #   - Position 2: at the middle of the chin
        elif pointID == 2:
            # x = (x.9 - x.10) / 2.
            # y = y.9 + ((y.52 - y.9) * 1.2)
            x = (landmark[8][0] + landmark[9][0]) / 2.
            y = landmark[8][1] + ((landmark[51][1] - landmark[8][1]) * 1.2)

        #   - Position 3: at left
        elif pointID == 3:
            # x = x.5
            # y = y.1
            x = landmark[0][0]
            y = landmark[0][1]

        #   - Position 4: at left of the mouth
        elif pointID == 4:
            # x = x.49 - ((x.49 - x.3) / 3.)
            # y = y.3
            x = landmark[48][0] - ((landmark[48][0] - landmark[2][0]) / 3.)
            y = landmark[0][1]

        #   - Position 5: under the chin, out of the face
        elif pointID == 5:
            # x = (x.9 - x.10) / 2.
            # y = y.9 - ((y.58 - y.9) / 8.)
            x = (landmark[8][0] + landmark[9][0]) / 2.
            y = landmark[8][1] - ((landmark[57][1] - landmark[8][1]) / 8.)

        return x, y

    # -----------------------------------------------------------------------

    def tag(self, image, lpc_code, landmarks):
        """Tag the image according to the lpc_code.

        :param image: (numpy.ndarray) The image to be processed.
        :param lpc_code: (string) The LPC code for the syllable.
        :param landmarks: (list) The list a landmark points.

        """
        # Store the width and the height of the image
        h, w = image.shape[:2]

        # Store the consonant and the vowel code separately
        codes = lpc_code.split(separators.phonemes)
        consonant_code = int(codes[0])
        vowel_code = int(codes[1])

        # Get the coordinates of the vowel
        x, y = self.calcul_position(vowel_code, landmarks)
        x = int(x)
        y = int(y)

        # Tag the image
        hand = cv2.imread(self.__hands[consonant_code])
        hand = rotate_bound(hand, -75)
        add_image(image, hand, x, y, int(w * 0.50), int(h * 0.50))

    # -----------------------------------------------------------------------

    def tag_blank(self, image, lpc_code, landmarks):
        """Tag the image according to the lpc_code.

        :param image: (numpy.ndarray) The image to be processed.
        :param lpc_code: (string) The LPC code for the syllable.
        :param landmarks: (list) The list a landmark points.

        """
        # Store the width and the height of the image
        h, w = image.shape[:2]

        # Store the consonant and the vowel of the previous code
        codes = lpc_code[0].split(separators.phonemes)
        prev_vowel = int(codes[1])
        prev_x, prev_y = self.calcul_position(prev_vowel, landmarks)
        prev_x = int(prev_x)
        prev_y = int(prev_y)

        # Store the consonant and the vowel of the next code
        codes = lpc_code[1].split(separators.phonemes)
        next_vowel = int(codes[1])
        next_x, next_y = self.calcul_position(next_vowel, landmarks)
        next_x = int(next_x)
        next_y = int(next_y)

        # Store the index of the blank
        index = lpc_code[2]

        # Store the number of blanks
        nb_blank = lpc_code[3]

        # Calcul the position for this hand
        x = int(prev_x + (next_x - prev_x) / nb_blank * index)
        y = int(prev_y + (next_y - prev_y) / nb_blank * index)

        # Tag the image
        hand = cv2.imread(self.__hands[0])
        hand = rotate_bound(hand, -75)
        add_image(image, hand, x, y, int(w * 0.50), int(h * 0.50))

