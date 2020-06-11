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
    src.videodata.manageroutputs.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~
"""

import cv2
from cv2 import VideoWriter_fourcc
import os
import csv
import shutil
import glob

# ---------------------------------------------------------------------------


class ManagerOutputs(object):
    """Class to write outputs files.

    :author:       Florian Hocquet
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      contact@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2020  Brigitte Bigi

    """

    def __init__(self, path, fps, options):
        """Create a new ManagerOutputs instance.

        :param path: (str) The path of the video.
        :param fps: (int) The FPS of the video.
        :param options: (str) The pattern to use for the outputs files.

        """
        # A list of csv files
        self.__csv_output = list()
        # A list of video writers
        self.__video_output = list()
        # A list of video writers
        self.__base_output = list()
        # A list of folders
        self.__folder_output = list()

        # The path and the name of the video
        self.__path, self.__video_name = self.__path_video(path)

        # The FPS of the video
        fps = int(fps)
        self.__fps = fps

        # The pattern to use for the outputs files
        self.__mOptions = options

        # Reset outputs files
        self.__reset()

    # -----------------------------------------------------------------------

    def __reset(self):
        """Reset outputs files before using the writers."""
        # Delete csv files if already exists
        csv_path = glob.glob(self.__cfile_path())
        for f in csv_path:
            if os.path.exists(f) is True:
                os.remove(f)

        # Delete video files if already exists
        video_path = glob.glob(self.__vfile_path())
        for f in video_path:
            if os.path.exists(f) is True:
                os.remove(f)

        # Delete video files if already exists
        usable_path = glob.glob(self.__base_path())
        for f in usable_path:
            if os.path.exists(f) is True:
                os.remove(f)

        # Delete folder if already exists
        folder_path = glob.glob(self.__ffile_path())
        for f in folder_path:
            if os.path.exists(f) is True:
                shutil.rmtree(f)

    # -----------------------------------------------------------------------

    def __path_video(self, path):
        """Return the path and the name of the video.

        :param path: (string) The path of the video.

        """
        if isinstance(path, str) is False:
            raise TypeError

        # Store the path of the video
        path = os.path.realpath(path)

        # Add the os separator to the path
        video_path = os.path.dirname(path) + os.sep

        # Store the name and the extension of the video
        video = os.path.basename(path)

        # Store separately the name and the extension of the video
        video_name, extension = os.path.splitext(video)

        # Return the path and the name of the video
        return video_path, video_name

    # -----------------------------------------------------------------------

    def __cfile_path(self, index=None):
        """Return the complete path of the csv file.

        :param index: (int) The int to add is the name of the csv file.

        """
        if index is not None:
            index = int(index)
            if isinstance(index, int) is False:
                raise TypeError

        if index is None:
            path = self.__path + self.__video_name + "_*" + self.__mOptions.get_pattern() + ".csv"
        else:
            path = self.__path + self.__video_name + "_" + str(index) + self.__mOptions.get_pattern() + ".csv"
        return path

    # -----------------------------------------------------------------------

    def __base_path(self, index=None):
        """Return the complete path of the video file.

        :param index: (int) The int to add is the name of the video file.

        """
        if index is not None:
            index = int(index)
            if isinstance(index, int) is False:
                raise TypeError

        if index is None:
            path = self.__path + self.__video_name + "_*" + self.__mOptions.get_pattern() + "_usable" + ".avi"
        else:
            path = self.__path + self.__video_name + "_" + str(index) + self.__mOptions.get_pattern() + "_usable.avi"
        return path

    # -----------------------------------------------------------------------

    def __vfile_path(self, index=None):
        """Return the complete path of the video file.

        :param index: (int) The int to add is the name of the video file.

        """
        if index is not None:
            index = int(index)
            if isinstance(index, int) is False:
                raise TypeError

        if index is None:
            path = self.__path + self.__video_name + "_*" + self.__mOptions.get_pattern() + ".avi"
        else:
            path = self.__path + self.__video_name + "_" + str(index) + self.__mOptions.get_pattern() + ".avi"
        return path

    # -----------------------------------------------------------------------

    def __ffile_path(self, index=None):
        """Return the complete path of the folder.

        :param index: (int) The int to add is the name of the folder.

        """
        if index is not None:
            index = int(index)
            if isinstance(index, int) is False:
                raise TypeError

        if index is None:
            path = self.__path + "*" + self.__mOptions.get_pattern() + os.path.sep
        else:
            path = self.__path + str(index) + self.__mOptions.get_pattern() + os.path.sep
        return path

    # -----------------------------------------------------------------------

    def create_out(self, lenght, w, h):
        """Create csv outputs files, videos, folders.

        :param lenght: (list) The lenght of the list.
        :param w: (int) The width of the image.
        :param h: (int) The height of the image.

        """
        # if the option is True create the csv files
        if self.__mOptions.get_csv() is True:
            self.__out_csv(lenght)

        # if the option is True create the videos
        if self.__mOptions.get_video() is True:
            self.__out_video(lenght, width=w, height=h)

        # if the option is True create the folder
        if self.__mOptions.get_folder() is True:
            self.__out_folder(lenght)

    # -----------------------------------------------------------------------

    def __out_csv(self, value):
        """Create csv file for each person.

        :param value: (int) The number of person on the video.

        """
        value = int(value)
        if isinstance(value, int) is False:
            raise TypeError

        # Loop over the number of persons on the video
        for i in range(1, value + 1):
            # Create the path
            path = os.path.join(self.__cfile_path(i))

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

        # Loop over the number of persons on the video
        for i in range(1, value + 1):
            # Create the path
            path = os.path.join(self.__vfile_path(i))

            # If the output video does not exist create it
            if os.path.exists(path) is False:
                self.__video_output.append(cv2.VideoWriter(path, VideoWriter_fourcc(*'MJPG'),
                                                           self.__fps, (width, height)))
            if self.__mOptions.get_mode() == "full" or \
                    self.__mOptions.get_draw() != "None" and self.__mOptions.get_mode() == "None":
                break

    # -----------------------------------------------------------------------

    def out_base(self, value, width=640, height=480):
        """Create video writer for each person.

        :param value: (int) The number of person to extract.
        :param width: (int) The width of the videos.
        :param height: (int) The height of the videos.

        """
        value = int(value)
        if isinstance(value, int) is False:
            raise TypeError

        # Loop over the number of persons on the video
        for i in range(1, value + 1):
            # Create the path
            path = os.path.join(self.__base_path(i))

            # If the output video does not exist create it
            if os.path.exists(path) is False:
                self.__base_output.append(cv2.VideoWriter(path, VideoWriter_fourcc(*'MJPG'),
                                                          self.__fps, (width, height)))

    # -----------------------------------------------------------------------

    def __out_folder(self, value):
        """Create folder for each person.

        :param value: (int) The number of person to extract.

        """
        value = int(value)
        if isinstance(value, int) is False:
            raise TypeError

        # Loop over the number of persons on the video
        for i in range(1, value + 1):
            # Create the path of a folder
            path = self.__ffile_path(i)

            # If the folder does not exist create it
            if os.path.exists(path) is False:
                os.mkdir(path)
                self.__folder_output.append(path)
            # If mode equal full create only one output
            if self.__mOptions.get_mode() == "full" or \
                    self.__mOptions.get_draw() != "None" and self.__mOptions.get_mode() == "None":
                break

    # -----------------------------------------------------------------------

    def write(self, image, index, number, coordinate=None):
        """Write the image in csv files, videos, and folders.

        :param image: (numpy.ndarray) The image to be processed.
        :param index: (int) The index of the coordinate.
        :param number: (int) The number for output name.
        :param coordinate: (Coordinates) The Coordinates object.

        """
        # Write the image in a csv file
        self.__write_csv(image, index, number, coordinate)

        # Write the image in a video
        self.__write_video(image, index)

        # Write the image in a folder
        self.__write_folder(image, index, number)

    # -----------------------------------------------------------------------

    def __write_csv(self, image, index, number, coordinate=None):
        """Write the image in a csv file.

        :param image: (numpy.ndarray) The image to be processed.
        :param index: (int) The index of the coordinate.
        :param number: (int) The number for output name.
        :param coordinate: (Coordinates) The Coordinates object.

        """
        # If csv option is True write the image in the good csv file.
        if self.__mOptions.get_csv() is True:
            if coordinate is not None:
                self.__csv_output[index].writerow(
                    [number, image, coordinate.x, coordinate.y, coordinate.w, coordinate.h])
            else:
                self.__csv_output[index].writerow(
                    [number, image])

    # -----------------------------------------------------------------------

    def __write_video(self, image, index):
        """Write the image in a video.

        :param image: (numpy.ndarray) The image to be processed.
        :param index: (int) The index of the coordinate.

        """
        # If the video option is True write the image in the good video writer.
        if self.__mOptions.get_video() is True:
            # If mode equal full create only one output video
            if self.__mOptions.get_mode() == "full" or \
                    self.__mOptions.get_draw() != "None" and self.__mOptions.get_mode() == "None":
                index = 0
                self.__video_output[index].write(image)
            else:
                self.__video_output[index].write(image)

    # -----------------------------------------------------------------------

    def __write_folder(self, image, index, number):
        """Write the image in a folder.

        :param image: (numpy.ndarray) The image to be processed.
        :param index: (int) The index of the coordinate.
        :param number: (int) The number for output name.

        """
        # If the folder option is True write the image in the good folder.
        if self.__mOptions.get_folder() is True:

            # If mode equal full create only one output folder
            if self.__mOptions.get_mode() == "full" or \
                    self.__mOptions.get_draw() != "None" and self.__mOptions.get_mode() == "None":
                index = 0
                cv2.imwrite(self.__folder_output[index] + "image" + str(number) + ".jpg", image)
            else:
                cv2.imwrite(self.__folder_output[index] + "image" + str(number) + ".jpg", image)

    # -----------------------------------------------------------------------

    def write_base(self, image, index):
        """Write the image in csv files, videos, and folders.

        :param image: (numpy.ndarray) The image to be processed.
        :param index: (int) The index of the coordinate.

        """
        self.__base_output[index].write(image)

    # -----------------------------------------------------------------------
