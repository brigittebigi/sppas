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

    src.imagedata.coordswriter.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~

"""

import cv2
from cv2 import VideoWriter_fourcc
import numpy as np

from sppas.src.imagedata.imageutils import crop, surrond_square, resize
from sppas.src.imagedata.coordinates import Coordinates

# ---------------------------------------------------------------------------


class sppasImgCoordsWriter(object):
    """Class to manage a process.

    :author:       Florian Hocquet
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      contact@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2020  Brigitte Bigi

    """

    def __init__(self, nb_person, video=False, folder=False):
        """Create a new sppasImgCoordsWriter instance.

        :param nb_person: (int) The number of person to extract.
        :param video: (boolean) If is True extract images in a video.
        :param folder: (boolean) If is True extract images in a folder.

        """
        # The list where receivers are stored.
        self.__out_list = list()

        # Write in a video
        self.__video = False

        # Write in a folder
        self.__folder = False

        # If video is True create video writers
        if video is True:
            self.__video = True
            self.__out_video(nb_person)

        # If folder is True create folders
        elif folder is True:
            self.__folder = True
            self.__out_folder(nb_person)
        self.__number = 0

    # -----------------------------------------------------------------------

    def to_portrait(self, coords, portrait=False):
        """Transform face coordinates to a portrait coordinates.

        :param coords: (Coordinates) The coordinates of the face.
        :param portrait: (boolean) If it's True modified coordinates.

        """
        if isinstance(coords, Coordinates) is False:
            raise TypeError

        if portrait is True:
            # Extend the image with a coeff equal to 2.4
            result = coords.scale(2.4)

            # Reframe the image on the face
            coords.shift(result, -30)

    # -----------------------------------------------------------------------

    def mode(self, img_buffer, coords, full_square=False, crop_=False, crop_resize=False):
        """Use the face or the portrait.

        :param img_buffer: (numpy.ndarray) The image to be processed.
        :param coords: (Coordinates) The coordinates of the face.
        :param full_square: (boolean) If True, draw a square around the face.
        :param crop_: (boolean) If True, crop the face.
        :param crop_resize: (boolean) If True, crop the face and resize the image.


        """
        if isinstance(img_buffer, np.ndarray) is False:
            raise TypeError
        if isinstance(coords, Coordinates) is False:
            raise TypeError

        # If full_square option is True, draw a square around the face.
        if full_square is True:
            return surrond_square(img_buffer, coords)

        # If crop option is True, crop the face.
        elif crop_ is True:
            return crop(img_buffer, coords)

        # If crop_resize option is True, crop the face and resize the image.
        elif crop_resize is True:
            new_image = crop(img_buffer, coords)
            new_image = resize(new_image, 640, 480)
            return new_image

    # -----------------------------------------------------------------------

    def __out_video(self, nb_person):
        """Create video writer for each person.

        :param nb_person: (int) The number of person to extract.

        """
        for i in range(1, nb_person + 1):
            self.__out_list.append(cv2.VideoWriter("../../../../../person_nb_" + str(i) + ".avi",
                                         VideoWriter_fourcc('M', 'J', 'P', 'G'), 24, (640, 480)))

    # -----------------------------------------------------------------------

    def __out_folder(self, nb_person):
        """Create folder for each person.

        :param nb_person: (int) The number of person to extract.

        """
        for i in range(1, nb_person + 1):
            self.__out_list.append("../../../../../video_extract/person_nb_" + str(i))

    # -----------------------------------------------------------------------

    def write(self, image, index):
        """Use the face or the portrait.

        :param image: (numpy.ndarray) The image to be processed.
        :param index: (int) The index of the coordinate.

        """

        # If self.__video is True write the image in the good video writer.
        if self.__video is True:
            self.__out_list[index].write(image)

        # If self.__folder is True write the image in the good folder.
        elif self.__folder is True:
            cv2.imwrite("../../../../../video_extract/person_" + str(index + 1) + "/image" + str(self.__number) + ".jpg"
                        , image)

        # Increment the number of images by one
        self.__number += 1

    # -----------------------------------------------------------------------

