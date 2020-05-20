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

    src.videodata.coordswriter.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~

"""

import cv2
from cv2 import VideoWriter_fourcc
import numpy as np
import os
import csv

from sppas.src.imagedata.imageutils import crop, surrond_square, resize
from sppas.src.imagedata.coordinates import Coordinates


# ---------------------------------------------------------------------------


class sppasImgCoordsWriter(object):
    """Class to write images.

    :author:       Florian Hocquet
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      contact@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2020  Brigitte Bigi

    """

    def __init__(self, csv=False, video=False, folder=False):
        """Create a new sppasImgCoordsWriter instance.

        :param video: (boolean) If is True extract images in csv file.
        :param video: (boolean) If is True extract images in a video.
        :param folder: (boolean) If is True extract images in a folder.

        """
        # A list of csv files
        self.__csv_output = list()
        # A list of video writers
        self.__video_output = list()
        # A list of folders
        self.__folder_output = list()

        # The dictionary of options
        self.options = {
            "output": {"csv": False, "video": False, "folder": False},
            "framing": {"portrait": False},
            "mode": {"full_square": False, "crop": False, "crop_resize": False}
        }

        # If csv is True create csv files
        if csv is True:
            self.options["output"]["csv"] = True

        # If video is True create video writers
        if video is True:
            self.options["output"]["video"] = True

        # If folder is True create folders
        if folder is True:
            self.options["output"]["folder"] = True

        self.__number = 0

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
            self.set_crop(False)
            self.set_crop_resize(False)

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
            self.set_square(False)
            self.set_crop_resize(False)
            self.options["output"]["video"] = False

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
            self.set_crop(False)
            self.set_square(False)

    # -----------------------------------------------------------------------

    def browse_faces(self, overlap, liste):
        """Browse the detected faces.

        :param overlap: (overlap) The number of values to delete.
        :param liste: (list) The list of the faces.

        """
        # Loop over the detected faces.
        for faceDetection in liste:
            if liste.index(faceDetection) < overlap:
                continue

            # Get the Faces
            coordinates = faceDetection.get_all()

            # Browse the coordinates which or the result of the FaceDetection
            self.__browse_coordinates(coordinates, faceDetection)

            # Increment the number of images by one
            self.__number += 1

    # -----------------------------------------------------------------------

    def __browse_coordinates(self, coordinates, face):
        """Browse the coordinates from the analysis of an image.

        :param coordinates: (list) The list of coordinates.
        :param face: (numpy.ndarray) The image to be processed.

        """
        # Loop over the coordinates
        for c in coordinates:
            # The index of the Coordinate in the list of Coordinates objects.
            index = coordinates.index(c)

            # Try to transform face coordinate into portrait coordinate
            self.__portrait(c)

            # Use one of the option of extraction
            image = self.__mode(face.get_image(), c, index)

            # Store the width and the height of the image
            (h, w) = image.shape[:2]

            # Create the output files
            self.__create_out(coordinates, w, h)

            # Write the image in csv file, video, folder
            self.__write(image, index, c)

            # Show the image
            # cv2.imshow("Image", image)
            # cv2.waitKey(1) & 0xFF

    # -----------------------------------------------------------------------

    def __create_out(self, coords, w, h):
        """Create outputs files and folders for the images.

        :param coords: (list) The list of coordinates.
        :param w: (int) The width of the image.
        :param h: (int) The height of the image.

        """
        # if the option is True create the csv files
        if self.get_csv() is True:
            self.__out_csv(len(coords))

        # if the option is True create the videos
        if self.get_video() is True:
            self.__out_video(len(coords), width=w, height=h)

        # if the option is True create the folder
        if self.get_folder() is True:
            self.__out_folder(len(coords))

    # -----------------------------------------------------------------------

    def __portrait(self, coords):
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

    def __mode(self, img_buffer, coords, index):
        """Draw squares, crop, crop and resize.

        :param img_buffer: (numpy.ndarray) The image to be processed.
        :param coords: (Coordinates) The coordinates of the face.
        :param index: (int) The index of the Coordinates object in the list.


        """
        index = int(index)
        if isinstance(index, int) is False:
            raise TypeError
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
            number = (index * 80) % 120
            return surrond_square(img_buffer, coords, number)

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
        value = int(value)
        if isinstance(value, int) is False:
            raise TypeError
        for i in range(1, value + 1):
            path = '../../../../../person_' + str(i) + '.csv'
            if os.path.exists(path) is False:
                file = open('../../../../../person_' + str(i) + '.csv', 'w', newline='')
                writer = csv.writer(file)
                self.__csv_output.append(writer)

    # -----------------------------------------------------------------------

    def __out_video(self, value, width=640, height=480):
        """Create video writer for each person.

        :param value: (int) The number of person to extract.
        :param width: (int) The width of the videos.
        :param height: (int) The height of the videos.

        """
        value = int(value)
        if isinstance(value, int) is False:
            raise TypeError
        for i in range(1, value + 1):
            path = os.path.join("../../../../../person_" + str(i) + ".avi")
            if os.path.exists(path) is False:
                self.__video_output.append(cv2.VideoWriter(path, VideoWriter_fourcc('M', 'J', 'P', 'G'),
                                                           24, (width, height)))

    # -----------------------------------------------------------------------

    def __out_folder(self, value):
        """Create folder for each person.

        :param value: (int) The number of person to extract.

        """
        value = int(value)
        if isinstance(value, int) is False:
            raise TypeError
        main_path = "../../../../../faces_extract/"
        if os.path.exists(main_path) is False:
            os.mkdir(main_path)
        for i in range(1, value + 1):
            path = "../../../../../faces_extract/person_" + str(i)
            if os.path.exists(path) is False:
                os.mkdir(path)
                self.__folder_output.append("../../../../../faces_extract/person_" + str(i) + "/")

    # -----------------------------------------------------------------------

    def __write(self, image, index, coordinate):
        """Write the image in csv file, video, and folder.

        :param image: (numpy.ndarray) The image to be processed.
        :param index: (int) The index of the coordinate.
        :param coordinate: (Coordinates) The Coordinates object.

        """
        # If self.__video is True write the image in the good csv file.
        if self.options["output"]["csv"] is True:
            self.__csv_output[index].writerow(
                [self.__number, image, coordinate.x, coordinate.y, coordinate.w, coordinate.h])

        # If self.__video is True write the image in the good video writer.
        if self.options["output"]["video"] is True:
            self.__video_output[index].write(image)

        # If self.__folder is True write the image in the good folder.
        if self.options["output"]["folder"] is True:
            cv2.imwrite("../../../../../faces_extract/person_" +
                        str(index + 1) + "/image" + str(self.__number) + ".jpg", image)

    # -----------------------------------------------------------------------

