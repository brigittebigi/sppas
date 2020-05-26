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
from cv2 import CAP_PROP_FPS
import numpy as np
import os
import csv
import shutil
import glob

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

    def __init__(self, path, fps, csv=False, video=False, folder=False):
        """Create a new sppasImgCoordsWriter instance.

        :param path: (str) The path of the video.
        :param fps: (int) The FPS of the video.
        :param csv: (boolean) If is True extract images in csv file.
        :param video: (boolean) If is True extract images in a video.
        :param folder: (boolean) If is True extract images in a folder.

        """
        # A list of csv files
        self.__csv_output = list()
        # A list of video writers
        self.__video_output = list()
        # A list of folders
        self.__folder_output = list()

        # The path and the name of the video
        self.__path, self.video_name = self.__path_video(path)

        # The FPS of the video
        fps = int(fps)
        self.__fps = fps

        # The dictionary of options
        self.output = {"csv": False, "video": False, "folder": False}

        # The framing you want, face or portrait
        self.__framing = None
        # The mode you want, full or crop
        self.__mode = None

        # The width you want for your outputs
        self.__width = None
        # The height you want for your outputs
        self.__height = None

        self.__init_outputs(csv, video, folder)

        # The index of the current image
        self.__number = 0

        # Reset outputs
        self.__reset()

    # -----------------------------------------------------------------------

    def __reset(self):
        """Reset outputs before using the writers."""
        # Delete csv files if already exists
        csv_path = glob.glob(self.__path + self.video_name + '_person_*.csv')
        for f in csv_path:
            if os.path.exists(f) is True:
                os.remove(f)

        # Delete video files if already exists
        video_path = glob.glob(self.__path + self.video_name + '_person_*.avi')
        for f in video_path:
            if os.path.exists(f) is True:
                os.remove(f)

        # Delete folder if already exists
        folder_path = self.__path + "faces/"
        if os.path.exists(folder_path) is True:
            shutil.rmtree(folder_path)

    # -----------------------------------------------------------------------

    def __init_outputs(self, csv, video, folder):
        """Init the values of the outputs options.

        :param csv: (boolean) If is True extract images in csv file.
        :param video: (boolean) If is True extract images in a video.
        :param folder: (boolean) If is True extract images in a folder.

        """
        # If csv is True create csv files
        if csv is True:
            self.set_csv(True)

        # If video is True create video writers
        if video is True:
            self.set_video(True)

        # If folder is True create folders
        if folder is True:
            self.set_folder(True)

    # -----------------------------------------------------------------------

    def __path_video(self, path):
        """Return the path and the name of the video.

        :param path: (string) The path of the video.

        """
        if isinstance(path, str) is False:
            raise TypeError

        # Store the video name
        video_name = path.split("/")
        video_name = video_name[len(video_name) - 1].split(".")[0]

        # Store the video path
        video_path = path.split(video_name)[0]
        if video_path == "":
            video_path = "./"

        return video_path, video_name

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
        return self.__framing

    # -----------------------------------------------------------------------

    def set_framing(self, value):
        """Set the framing.

        :param value: (str) The framing option to use.

        """
        if isinstance(value, str) is False:
            raise TypeError
        if value not in self.FRAMING:
            raise ValueError
        self.__framing = value

    # -----------------------------------------------------------------------

    def get_mode(self):
        """Return the mode."""
        return self.__mode

    # -----------------------------------------------------------------------

    def set_mode(self, value):
        """Set the mode.

        :param value: (str) The framing option to use.

        """
        if isinstance(value, str) is False:
            raise TypeError
        if value not in self.MODE:
            raise ValueError
        self.__mode = value

    # -----------------------------------------------------------------------

    def get_width(self):
        """Return the width."""
        return self.__width

    # -----------------------------------------------------------------------

    def set_width(self, value):
        """Set the width."""
        if isinstance(value, int) is False:
            raise TypeError
        if value < -1 or value > 15360:
            raise ValueError
        self.__width = value

    # -----------------------------------------------------------------------

    def get_height(self):
        """Return the height."""
        return self.__height

    # -----------------------------------------------------------------------

    def set_height(self, value):
        """Set the height."""
        if isinstance(value, int) is False:
            raise TypeError
        if value < -1 or value > 8640:
            raise ValueError
        self.__height = value

    # -----------------------------------------------------------------------

    def browse_faces(self, overlap, buffer, tracker):
        """Browse the buffer and apply modification for each person.

        :param overlap: (int) The number of values to delete.
        :param buffer: (VideoBuffer) The buffer which contains images.
        :param tracker: (FaceTracking) The FaceTracker object.

        """
        # Initialise the iterator
        iterator = buffer.__iter__()

        # Loop over the buffer
        for i in range(0, buffer.__len__()):

            # Go to the next frame
            img = next(iterator)

            # If overlap continue
            if i < overlap:
                continue

            # Loop over the persons
            for person in tracker.get_persons():
                index = tracker.get_persons().index(person)
                image = img
                if i > len(person) - 1:
                    continue
                self.__portrait(person[i])

                # If mode != full adjust images
                if self.__mode != "full":
                    self.__adjust(image, person[i])

                # Use one of the extraction options
                image = self.__process(image, person[i], index)

                # If mode != full resize images
                if self.__mode != "full":
                    image = self.__resize(image)

                # Store the width and the height of the image
                (h, w) = image.shape[:2]

                # Create the output files
                self.__create_out(len(tracker.get_persons()), w, h)

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

        if self.__framing == "portrait":
            # Extend the image with a coeff equal to 2.4
            result = coords.scale(2.4)

            # Reframe the image on the face
            coords.shift(result, -30)

    # -----------------------------------------------------------------------

    def __process(self, img_buffer, coords, index):
        """Draw squares around faces or crop the faces.

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

        # If mode == full, draw a square around the face.
        if self.__mode == "full":
            number = (index * 80) % 120
            return surrond_square(img_buffer, coords, number)

        # If mode == crop, crop the face.
        elif self.__mode == "crop":
            return crop(img_buffer, coords)

    # -----------------------------------------------------------------------

    def __adjust(self, img_buffer, coords):
        """Adjust the coordinates.

        :param img_buffer: (numpy.ndarray) The image to be processed.
        :param coords: (Coordinates) The coordinates of the face.

        """
        if self.__mode == "crop" and self.__width == -1 and self.__height == -1:
            self.set_video(False)

        # If anything has been setted pass
        if self.__width == -1 and self.__height == -1:
            pass

        # If only the width has been setted use adjust width
        if self.__width != -1 and self.__height == -1:
            self.__adjust_height()

        # If only the height has been setted use adjust height
        elif self.__width == -1 and self.__height != -1:
            self.__adjust_width()

        # If both of width and height has been setted
        if self.__width != -1 and self.__height != -1:
            self.__adjust_both(coords, img_buffer)

    # -----------------------------------------------------------------------

    def __adjust_both(self, coords, img_buffer=None):
        """Adjust the coordinates with width and height from constructor.

        :param coords: (Coordinates) The coordinates of the face.
        :param img_buffer: (numpy.ndarray) The image to be processed.

        """
        coeff = self.__width / self.__height
        coeff_coords = coords.w / coords.h
        if coeff != coeff_coords:
            new_w = int(coords.h * coeff)
            old_w = coords.w
            coords.w = new_w
            shift_x = int((old_w - new_w) / 2)
            if coords.x + shift_x < 0:
                shift_x = -coords.x
            coords.x = coords.x + shift_x

        if img_buffer is not None:
            (h, w) = img_buffer.shape[:2]
            if coords.h > h:
                coords.h = h
                coords.y = 0
            if coords.w > w:
                coords.w = w
                coords.x = 0

    # -----------------------------------------------------------------------

    def __adjust_width(self):
        """Adjust the width based on the width from constructor."""
        if self.__framing == "face":
            coeff = 0.75
        else:
            coeff = 4 / 3
        self.__width = int(self.__height * coeff)

    # -----------------------------------------------------------------------

    def __adjust_height(self):
        """Adjust the height based on the width from constructor."""
        if self.__framing == "face":
            coeff = 4 / 3
        else:
            coeff = 0.75
        self.__height = int(self.__width * coeff)

    # -----------------------------------------------------------------------

    def __resize(self, img_buffer):
        """Resize the image with width and height from constructor.

        :param img_buffer: (numpy.ndarray) The image to be processed.

        """
        if self.__width == -1 and self.__height == -1:
            return img_buffer
        else:
            new_image = resize(img_buffer, self.__width, self.__height)
            return new_image

    # -----------------------------------------------------------------------

    def __create_out(self, lenght, w, h):
        """Create outputs files and folders for the images.

        :param lenght: (list) The lenght of the list.
        :param w: (int) The width of the image.
        :param h: (int) The height of the image.

        """
        # if the option is True create the csv files
        if self.get_csv() is True:
            self.__out_csv(lenght)

        # if the option is True create the videos
        if self.get_video() is True:
            self.__out_video(lenght, width=w, height=h)

        # if the option is True create the folder
        if self.get_folder() is True:
            self.__out_folder(lenght)

    # -----------------------------------------------------------------------

    def __out_csv(self, value):
        """Create csv file for each person.

        :param value: (int) The number of person to extract.

        """
        value = int(value)
        if isinstance(value, int) is False:
            raise TypeError
        for i in range(1, value + 1):

            # Create the path
            path = os.path.join(self.__path + self.video_name + '_person_' + str(i) + '.csv')

            # If the csv file does not exist create it
            if os.path.exists(path) is False:
                file = open(path, 'w', newline='')
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

            # Create the path
            path = os.path.join(self.__path + self.video_name + '_person_' + str(i) + ".avi")

            # If the output video does not exist create it
            if os.path.exists(path) is False:
                self.__video_output.append(cv2.VideoWriter(path, VideoWriter_fourcc(*'MJPG'),
                                                           self.__fps, (width, height)))
            if self.__mode == "full":
                break

    # -----------------------------------------------------------------------

    def __out_folder(self, value):
        """Create folder for each person.

        :param value: (int) The number of person to extract.

        """
        value = int(value)
        if isinstance(value, int) is False:
            raise TypeError

        # Create the path of the main folder
        main_path = self.__path + "faces/"

        # If the main folder does not exist create it
        if os.path.exists(main_path) is False:
            os.mkdir(main_path)

        for i in range(1, value + 1):
            # Create the path of a folder
            path = main_path + "_person_" + str(i) + "/"

            # If the folder does not exist create it
            if os.path.exists(path) is False:
                os.mkdir(path)
                self.__folder_output.append(path)
            # If mode equal full create only one output
            if self.__mode == "full":
                break

    # -----------------------------------------------------------------------

    def __write(self, image, index, coordinate):
        """Write the image in csv file, video, and folder.

        :param image: (numpy.ndarray) The image to be processed.
        :param index: (int) The index of the coordinate.
        :param coordinate: (Coordinates) The Coordinates object.

        """
        # If csv option is True write the image in the good csv file.
        if self.output["csv"] is True:
            self.__csv_output[index].writerow(
                [self.__number, image, coordinate.x, coordinate.y, coordinate.w, coordinate.h])

        # If the video option is True write the image in the good video writer.
        if self.output["video"] is True:

            # If mode equal full create only one output video
            if self.__mode == "full":
                index = 0
                self.__video_output[index].write(image)
            else:
                self.__video_output[index].write(image)

        # If the folder option is True write the image in the good folder.
        if self.output["folder"] is True:

            # If mode equal full create only one output folder
            if self.__mode == "full":
                index = 0
                cv2.imwrite(self.__folder_output[index] + "image" + str(self.__number) + ".jpg", image)
            else:
                cv2.imwrite(self.__folder_output[index] + "image" + str(self.__number) + ".jpg", image)

    # -----------------------------------------------------------------------

