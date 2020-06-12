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
import os
import shutil
import glob

# ---------------------------------------------------------------------------


class ImageOutputs(object):
    """Class to write outputs files.

    :author:       Florian Hocquet
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      contact@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2020  Brigitte Bigi

    """

    def __init__(self, path, options):
        """Create a new ImageOutputs instance.

        :param path: (str) The path of the video.
        :param options: (str) The pattern to use for the outputs files.

        """
        # A list of video writers
        self.__base_output = list()
        # A list of folders
        self.__folder_output = list()

        # The path and the name of the video
        self.__path, self.__video_name = self.__path(path)

        # The pattern to use for the outputs files
        self.__mOptions = options

        # Reset outputs files
        self.__reset()

    # -----------------------------------------------------------------------

    def __reset(self):
        """Reset outputs files before using the writers."""
        # Delete video files if already exists
        # Delete folder if already exists
        folder_path = glob.glob(self.__base_path())
        for f in folder_path:
            if os.path.exists(f) is True:
                shutil.rmtree(f)

        # Delete folder if already exists
        folder_path = glob.glob(self.__ffile_path())
        for f in folder_path:
            if os.path.exists(f) is True:
                shutil.rmtree(f)

    # -----------------------------------------------------------------------

    def __path(self, path):
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

    def __base_path(self, index=None):
        """Return the complete path of the output image.

        :param index: (int) Int to add is the name of the usable image.

        """
        if index is not None:
            index = int(index)
            if isinstance(index, int) is False:
                raise TypeError

        if index is None:
            path = self.__path + "*" + self.__mOptions.get_pattern() + "_usable" + os.path.sep
        else:
            path = self.__path + str(index) + self.__mOptions.get_pattern() + "_usable" + os.path.sep
        return path

    # -----------------------------------------------------------------------

    def __ffile_path(self, index=None):
        """Return the complete path of the folder.

        :param index: (int) Int to add is the name of the folder.

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

    def create_out(self, lenght):
        """Create csv outputs files, videos, folders.

        :param lenght: (list) The lenght of the list.

        """
        # if the option is True create the folder
        if self.__mOptions.get_folder() is True:
            self.__out_folder(lenght)

    # -----------------------------------------------------------------------

    def out_base(self, value):
        """Create video writer for each person.

        :param value: (int) The number of person to extract.

        """
        value = int(value)
        if isinstance(value, int) is False:
            raise TypeError

        # Loop over the number of persons on the video
        for i in range(1, value + 1):
            # Create the path of a folder
            path = self.__base_path(i)

            # If the folder does not exist create it
            if os.path.exists(path) is False:
                os.mkdir(path)
                self.__base_output.append(path)

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
            if self.__mOptions.get_mode() == "full" or self.__mOptions.get_mode() == "None":
                break

    # -----------------------------------------------------------------------

    def write(self, image, index, number):
        """Write the image in csv files, videos, and folders.

        :param image: (numpy.ndarray) The image to be processed.
        :param index: (int) The index of the coordinate.
        :param number: (int) The number for output name.

        """
        # Write the image in a folder
        self.__write_folder(image, index, number)

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
            if self.__mOptions.get_mode() == "full" or self.__mOptions.get_mode() == "None":
                index = 0
                cv2.imwrite(self.__folder_output[index] + "image" + str(number) + ".jpg", image)
            else:
                cv2.imwrite(self.__folder_output[index] + "image" + str(number) + ".jpg", image)

    # -----------------------------------------------------------------------

    def write_base(self, image, index, number):
        """Write the image in csv files, videos, and folders.

        :param image: (numpy.ndarray) The image to be processed.
        :param index: (int) The index of the coordinate.
        :param number: (int) The number for output name.

        """
        cv2.imwrite(self.__base_output[index] + "image" + str(number) + ".jpg", image)

    # -----------------------------------------------------------------------
