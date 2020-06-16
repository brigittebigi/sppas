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

    src.videodata.videooutputs.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~

"""

import cv2
from cv2 import VideoWriter_fourcc
import os
import csv
import shutil
import glob

# ---------------------------------------------------------------------------


class VideoOutputs(object):
    """Class to write outputs files.

    :author:       Florian Hocquet
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      contact@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2020  Brigitte Bigi

    """

    def __init__(self, path, fps, options):
        """Create a new LandmarkOutputs instance.

        :param path: (str) The path of the video.
        :param fps: (int) The FPS of the video.
        :param options: (str) The pattern to use for the outputs files.

        """
        # A list of csv files
        self._csv_output = list()
        # A list of video writers
        self._video_output = list()
        # A list of video writers
        self._base_output = list()
        # A list of folders
        self._folder_output = list()

        # The path and the name of the video
        self._path, self._video_name = self._path_video(path)

        # The FPS of the video
        fps = int(fps)
        self._fps = fps

        # The pattern to use for the outputs files
        self._mOptions = options

        # Reset outputs files
        self._reset()

    # -----------------------------------------------------------------------

    def _reset(self):
        """Reset outputs files before using the writers."""
        # Delete csv files if already exists
        csv_path = glob.glob(self._cfile_path())
        for f in csv_path:
            if os.path.exists(f) is True:
                os.remove(f)

        # Delete video files if already exists
        video_path = glob.glob(self._vfile_path())
        for f in video_path:
            if os.path.exists(f) is True:
                os.remove(f)

        # Delete video files if already exists
        usable_path = glob.glob(self._base_path())
        for f in usable_path:
            if os.path.exists(f) is True:
                os.remove(f)

        # Delete folder if already exists
        folder_path = glob.glob(self._ffile_path())
        for f in folder_path:
            if os.path.exists(f) is True:
                shutil.rmtree(f)

    # -----------------------------------------------------------------------

    def _path_video(self, path):
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

    def _cfile_path(self, index=None):
        """Return the complete path of the csv file.

        :param index: (int) Int to add is the name of the csv file.

        """
        if index is not None:
            index = int(index)
            if isinstance(index, int) is False:
                raise TypeError

        if index is None:
            path = self._path + self._video_name + "_*" + self._mOptions.get_pattern() + ".csv"
        else:
            path = self._path + self._video_name + "_" + str(index) + self._mOptions.get_pattern() + ".csv"
        return path

    # -----------------------------------------------------------------------

    def _base_path(self, index=None):
        """Return the complete path of the video file.

        :param index: (int) Int to add is the name of the video file.

        """
        if index is not None:
            index = int(index)
            if isinstance(index, int) is False:
                raise TypeError

        if index is None:
            path = self._path + self._video_name + "_*" + self._mOptions.get_pattern() + "_usable" + ".avi"
        else:
            path = self._path + self._video_name + "_" + str(index) + self._mOptions.get_pattern() + "_usable.avi"
        return path

    # -----------------------------------------------------------------------

    def _vfile_path(self, index=None):
        """Return the complete path of the video file.

        :param index: (int) Int to add in the name of the usable video file.

        """
        if index is not None:
            index = int(index)
            if isinstance(index, int) is False:
                raise TypeError

        if index is None:
            path = self._path + self._video_name + "_*" + self._mOptions.get_pattern() + ".avi"
        else:
            path = self._path + self._video_name + "_" + str(index) + self._mOptions.get_pattern() + ".avi"
        return path

    # -----------------------------------------------------------------------

    def _ffile_path(self, index=None):
        """Return the complete path of the folder.

        :param index: (int) Int to add is the name of the folder.

        """
        if index is not None:
            index = int(index)
            if isinstance(index, int) is False:
                raise TypeError

        if index is None:
            path = self._path + "*" + self._mOptions.get_pattern() + os.path.sep
        else:
            path = self._path + str(index) + self._mOptions.get_pattern() + os.path.sep
        return path

    # -----------------------------------------------------------------------

    def create_out(self, lenght, w, h):
        """Create csv outputs files, videos, folders.

        :param lenght: (list) The lenght of the list.
        :param w: (int) The width of the image.
        :param h: (int) The height of the image.

        """
        # if the option is True create the csv files
        if self._mOptions.get_csv() is True:
            self._out_csv(lenght)

        # if the option is True create the videos
        if self._mOptions.get_video() is True:
            self._out_video(lenght, width=w, height=h)

        # if the option is True create the folder
        if self._mOptions.get_folder() is True:
            self._out_folder(lenght)

    # -----------------------------------------------------------------------

    def _out_csv(self, value):
        """Create csv file for each person.

        :param value: (int) The number of person on the video.

        """
        value = int(value)
        if isinstance(value, int) is False:
            raise TypeError

        # Loop over the number of persons on the video
        for i in range(1, value + 1):
            # Create the path
            path = os.path.join(self._cfile_path(i))

            # If the csv file does not exist create it
            if os.path.exists(path) is False:
                file = open(path, 'w', newline='')
                writer = csv.writer(file)
                self._csv_output.append(writer)

    # -----------------------------------------------------------------------

    def _out_video(self, value, width=640, height=480):
        """Create video writer for each person.

        :param value: (int) The number of person to extract.
        :param width: (int) The width of the videos.
        :param height: (int) The height of the videos.

        """
        pass

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
            path = os.path.join(self._base_path(i))

            # If the output video does not exist create it
            if os.path.exists(path) is False:
                self._base_output.append(cv2.VideoWriter(path, VideoWriter_fourcc(*'MJPG'),
                                                          self._fps, (width, height)))

    # -----------------------------------------------------------------------

    def _out_folder(self, value):
        """Create folder for each person.

        :param value: (int) The number of person to extract.

        """
        pass

    # -----------------------------------------------------------------------

    def write(self, image, index, number, coordinate=None, landmark=None):
        """Write the image in csv files, videos, and folders.

        :param image: (numpy.ndarray) The image to be processed.
        :param index: (int) The index of the coordinate.
        :param number: (int) The number for output name.
        :param coordinate: (sppasCoords) The sppasCoords object.
        :param landmark: (list) The list of landmark points.

        """
        # Write the image in a csv file
        self._write_csv(index, number, coordinate, landmark)

        # Write the image in a video
        self._write_video(image, index)

        # Write the image in a folder
        self._write_folder(image, index, number)

    # -----------------------------------------------------------------------

    def _write_csv(self, index, number, coordinate, landmark):
        """Write the information in a csv file.

        :param index: (int) The index of the coordinate.
        :param number: (int) The number for output name.
        :param coordinate: (sppasCoords) The sppasCoords object.
        :param landmark: (list) The list of landmark points.

        """
        pass

    # -----------------------------------------------------------------------

    def _write_video(self, image, index):
        """Write the image in a video.

        :param image: (numpy.ndarray) The image to be processed.
        :param index: (int) The index of the coordinate.

        """
        pass

    # -----------------------------------------------------------------------

    def _write_folder(self, image, index, number):
        """Write the image in a folder.

        :param image: (numpy.ndarray) The image to be processed.
        :param index: (int) The index of the coordinate.
        :param number: (int) The number for output name.

        """
        pass

    # -----------------------------------------------------------------------

    def write_base(self, image, index):
        """Write the image in csv files, videos, and folders.

        :param image: (numpy.ndarray) The image to be processed.
        :param index: (int) The index of the coordinate.

        """
        self._base_output[index].write(image)

    # -----------------------------------------------------------------------
