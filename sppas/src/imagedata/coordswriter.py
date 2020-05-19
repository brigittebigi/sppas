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
import os

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

    def __init__(self, csv=False, video=False, folder=False):
        """Create a new sppasImgCoordsWriter instance.

        :param video: (boolean) If is True extract images in a video.
        :param folder: (boolean) If is True extract images in a folder.

        """
        # The list where receivers are stored.
        self.__video_output = list()
        self.__folder_output = list()
        self.__csv_output = list()

        self.options = {
            "output": {"csv": False, "video": False, "folder": False},
            "framing": {"portrait": False},
            "mode": {"full_square": False, "crop": False, "crop_resize": False}
        }

        # If video is True create video writers
        if csv is True:
            self.options["output"]["csv"] = True
            self.__out_csv(2)

        # If video is True create video writers
        if video is True:
            self.options["output"]["video"] = True

        # If folder is True create folders
        if folder is True:
            self.options["output"]["folder"] = True

        self.__number = 0

    # -----------------------------------------------------------------------

    def del_path(self):
        """Return True if the option csv is activate."""
        for path in self.__video_output:
            os.rmdir(path)
        for path in self.__folder_output:
            os.rmdir(path)

    # -----------------------------------------------------------------------

    def get_csv(self):
        """Return True if the option csv is activate."""
        return self.options["output"]["csv"]

    # -----------------------------------------------------------------------

    def get_video(self):
        """Return True if the option video is activate."""
        return self.options["output"]["video"]

    # -----------------------------------------------------------------------

    def get_folder(self):
        """Return True if the option folder is activate."""
        return self.options["output"]["folder"]

    # -----------------------------------------------------------------------

    def get_portrait(self):
        """Return True if the option portrait is activate."""
        return self.options["framing"]["portrait"]

    # -----------------------------------------------------------------------

    def set_portrait(self, value):
        """Set the value of the option portrait."""
        value = bool(value)
        if isinstance(value, bool) is False:
            raise TypeError
        self.options["framing"]["portrait"] = value
        # if value is True:
        #     self.options["framing"]["face"] = False

    # -----------------------------------------------------------------------

    def get_square(self):
        """Return True if the option full_square is activate."""
        return self.options["mode"]["full_square"]

    # -----------------------------------------------------------------------

    def set_square(self, value):
        """Set the value of the option full_square."""
        value = bool(value)
        if isinstance(value, bool) is False:
            raise TypeError
        self.options["mode"]["full_square"] = value
        if value is True:
            self.options["mode"]["crop"] = False
            self.options["mode"]["crop_resize"] = False

    # -----------------------------------------------------------------------

    def get_crop(self):
        """Return True if the option crop is activate."""
        return self.options["mode"]["crop"]

    # -----------------------------------------------------------------------

    def set_crop(self, value):
        """Set the value of the option crop."""
        value = bool(value)
        if isinstance(value, bool) is False:
            raise TypeError
        self.options["mode"]["crop"] = value
        if value is True:
            self.options["mode"]["full_square"] = False
            self.options["mode"]["crop_resize"] = False

    # -----------------------------------------------------------------------

    def get_crop_resize(self):
        """Return True if the option crop_resize is activate."""
        return self.options["mode"]["crop_resize"]

    # -----------------------------------------------------------------------

    def set_crop_resize(self, value):
        """Set the value of the option crop_resize."""
        value = bool(value)
        if isinstance(value, bool) is False:
            raise TypeError
        self.options["mode"]["crop_resize"] = value
        if value is True:
            self.options["mode"]["crop"] = False
            self.options["mode"]["full_square"] = False

    # -----------------------------------------------------------------------

    def browse_faces(self, liste):
        """Browse the detected faces.

        :param liste: (list) The list of the faces.

        """
        # Detect only one face in the video
        for faceDetection in liste:
            # Detect all the face in the image
            faceDetection.detect_all()

            # Get the Faces with the highest score
            coordinates = faceDetection.get_all()

            if self.get_video() is True:
                self.__out_video(len(coordinates))

            if self.get_folder() is True:
                self.__out_folder(len(coordinates))

            # Loop over the coordinates
            for c in coordinates:
                # The index of the Coordinate in the list of Coordinates objects.
                index = coordinates.index(c)

                # The image to be processed
                image = faceDetection.get_image()

                self.to_portrait(c)
                image = self.mode(image, c)
                self.write(image, index)

                # Show the image
                cv2.imshow("Image", image)
                cv2.waitKey(1) & 0xFF
            self.__number += 1

    # -----------------------------------------------------------------------

    def to_portrait(self, coords):
        """Transform face coordinates to a portrait coordinates.

        :param coords: (Coordinates) The coordinates of the face.

        """
        if isinstance(coords, Coordinates) is False:
            raise TypeError

        if self.get_portrait() is True:
            # Extend the image with a coeff equal to 2.4
            result = coords.scale(2.4)

            # Reframe the image on the face
            coords.shift(result, -30)

    # -----------------------------------------------------------------------

    def mode(self, img_buffer, coords):
        """Use the face or the portrait.

        :param img_buffer: (numpy.ndarray) The image to be processed.
        :param coords: (Coordinates) The coordinates of the face.

        """
        if isinstance(img_buffer, np.ndarray) is False:
            raise TypeError
        if isinstance(coords, Coordinates) is False:
            raise TypeError

        # If any option is True, crop the face and resize the image.
        if self.get_square() is False and self.get_crop() is False and self.get_crop_resize() is False:
            new_image = crop(img_buffer, coords)
            new_image = resize(new_image, 640, 480)
            return new_image

        # If full_square option is True, draw a square around the face.
        if self.get_square() is True:
            return surrond_square(img_buffer, coords)

        # If crop option is True, crop the face.
        elif self.get_crop() is True:
            return crop(img_buffer, coords)

        # If crop_resize option is True, crop the face and resize the image.
        elif self.get_crop_resize() is True:
            new_image = crop(img_buffer, coords)
            new_image = resize(new_image, 640, 480)
            return new_image

    # -----------------------------------------------------------------------

    def __out_csv(self, value):
        """Create csv file for each person.

        :param value: (int) The number of person to extract.

        """
        pass

    # -----------------------------------------------------------------------

    def __out_video(self, value, width=640, height=480):
        """Create video writer for each person.

        :param value: (int) The number of person to extract.

        """
        for i in range(1, value + 1):
            path = os.path.join("../../../../../person_nb_" + str(i) + ".avi")
            if os.path.exists(path) is False:
                self.__video_output.append(cv2.VideoWriter(path, VideoWriter_fourcc('M', 'J', 'P', 'G'),
                                                           24, (width, height)))

    # -----------------------------------------------------------------------

    def __out_folder(self, value):
        """Create folder for each person.

        :param value: (int) The number of person to extract.

        """
        main_path = "../../../../../video_extract/"
        if os.path.exists(main_path) is False:
            os.mkdir(main_path)
        for i in range(1, value + 1):
            path = "../../../../../video_extract/person_" + str(i)
            if os.path.exists(path) is False:
                os.mkdir(path)
                self.__folder_output.append("../../../../../video_extract/person_" + str(i) + "/")

    # -----------------------------------------------------------------------

    def write(self, image, index):
        """Use the face or the portrait.

        :param image: (numpy.ndarray) The image to be processed.
        :param index: (int) The index of the coordinate.

        """
        print(index)
        # If self.__video is True write the image in the good csv file.
        if self.options["output"]["csv"] is True:
            pass

        # If self.__video is True write the image in the good video writer.
        if self.options["output"]["video"] is True:
            print(self.__video_output)
            self.__video_output[index].write(image)

        # If self.__folder is True write the image in the good folder.
        if self.options["output"]["folder"] is True:
            cv2.imwrite("../../../../../video_extract/person_" +
                        str(index + 1) + "/image" + str(self.__number) + ".jpg", image)

        # Increment the number of images by one

    # -----------------------------------------------------------------------
