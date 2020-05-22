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


class sppasVideoCoordsWriter(object):
    """Class to write images.

    :author:       Florian Hocquet
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      contact@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2020  Brigitte Bigi

    """

    FRAMING = ["face", "portrait"]
    MODE = ["full", "crop"]

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
        self.output = {"csv": False, "video": False, "folder": False}

        self.framing = None
        self.mode = None

        self.width = None
        self.height = None

        # If csv is True create csv files
        if csv is True:
            self.output["csv"] = True

        # If video is True create video writers
        if video is True:
            self.output["video"] = True

        # If folder is True create folders
        if folder is True:
            self.output["folder"] = True

        self.__number = 0

    # -----------------------------------------------------------------------

    def get_csv(self):
        """Return True if the option csv is activate."""
        return self.output["csv"]

    # -----------------------------------------------------------------------

    def set_csv(self, value):
        """Set the value of csv."""
        value = bool(value)
        if isinstance(value, bool) is False:
            raise TypeError
        self.output["csv"] = value

    # -----------------------------------------------------------------------

    def get_video(self):
        """Return True if the option video is activate."""
        return self.output["video"]

    # -----------------------------------------------------------------------

    def set_video(self, value):
        """Set the value of video."""
        value = bool(value)
        if isinstance(value, bool) is False:
            raise TypeError
        self.output["video"] = value

    # -----------------------------------------------------------------------

    def get_folder(self):
        """Return True if the option folder is activate."""
        return self.output["folder"]

    # -----------------------------------------------------------------------

    def set_folder(self, value):
        """Set the value of folder."""
        value = bool(value)
        if isinstance(value, bool) is False:
            raise TypeError
        self.output["folder"] = value

    # -----------------------------------------------------------------------

    def get_framing(self):
        """Return the framing."""
        return self.framing

    # -----------------------------------------------------------------------

    def set_framing(self, value):
        """Set the framing."""
        if isinstance(value, str) is False:
            raise TypeError
        if value not in self.FRAMING:
            raise IndexError
        self.framing = value

    # -----------------------------------------------------------------------

    def get_mode(self):
        """Return the mode."""
        return self.mode

    # -----------------------------------------------------------------------

    def set_mode(self, value):
        """Set the mode."""
        if isinstance(value, str) is False:
            raise TypeError
        if value not in self.MODE:
            raise IndexError
        self.mode = value

    # -----------------------------------------------------------------------

    def get_width(self):
        """Return the width."""
        return self.width

    # -----------------------------------------------------------------------

    def set_width(self, value):
        """Set the width."""
        if isinstance(value, int) is False:
            raise TypeError
        if value < -1 or value > 15360:
            raise ValueError
        self.width = value

    # -----------------------------------------------------------------------

    def get_height(self):
        """Return the width."""
        return self.height

    # -----------------------------------------------------------------------

    def set_height(self, value):
        """Set the width."""
        if isinstance(value, int) is False:
            raise TypeError
        if value < -1 or value > 8640:
            raise ValueError
        self.height = value

    # -----------------------------------------------------------------------

    def browse_faces(self, overlap, buffer, tracker):
        """Browse the detected faces.

        :param overlap: (overlap) The number of values to delete.
        :param buffer: (VideoBuffer) The buffer which contains images.
        :param tracker: (FaceTracking) The FaceTracker object.

        """
        iterator = buffer.__iter__()

        # Loop over the buffer
        for i in range(0, buffer.__len__()):

            # Go to the next frame
            img = next(iterator)

            # If overlap continue
            if i < overlap:
                continue

            # Show the image
            # cv2.imshow("Image", img)
            # cv2.waitKey(1) & 0xFF

            # Loop over the persons
            for person in tracker.get_persons():
                index = tracker.get_persons().index(person)
                image = img
                if i > len(person) - 1:
                    continue
                self.__portrait(person[i])
                # Use one of the option of extraction
                image = self.__mode(image, person[i], index)
                image = self.__resize(image, person[i], index)
                # Store the width and the height of the image
                (h, w) = image.shape[:2]
                # Create the output files
                self.__create_out(tracker.get_persons(), w, h)
                # Write the image in csv file, video, folder
                self.__write(image, index, person[i])

            # Increment the number of image by 1
            self.__number += 1

    # -----------------------------------------------------------------------

    def __portrait(self, coords):
        """Transform face coordinates to a portrait coordinates.

        :param coords: (Coordinates) The coordinates of the face.

        """
        if isinstance(coords, Coordinates) is False:
            raise TypeError

        if self.framing == "portrait":
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

        # If full_square option is True, draw a square around the face.
        if self.mode == "full":
            number = (index * 80) % 120
            return surrond_square(img_buffer, coords, number)

        # If crop option is True, crop the face.
        elif self.mode == "crop":
            self.set_video(False)
            return crop(img_buffer, coords)

        # If crop_resize option is True, crop the face and resize the image.
        # elif self.get_crop_resize() is True:
        #     new_image = crop(img_buffer, coords)
        #     new_image = resize(new_image, 640, 480)
        #     return new_image

    # -----------------------------------------------------------------------

    def __resize(self, img_buffer, coords, index):
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

        if self.width == -1 and self.height == -1:
            return img_buffer

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
        if self.output["csv"] is True:
            self.__csv_output[index].writerow(
                [self.__number, image, coordinate.x, coordinate.y, coordinate.w, coordinate.h])

        # If self.__video is True write the image in the good video writer.
        if self.output["video"] is True:
            self.__video_output[index].write(image)

        # If self.__folder is True write the image in the good folder.
        if self.output["folder"] is True:
            cv2.imwrite("../../../../../faces_extract/person_" +
                        str(index + 1) + "/image" + str(self.__number) + ".jpg", image)

    # -----------------------------------------------------------------------

