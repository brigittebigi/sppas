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

    src.videodata.trackingoutputs.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~

"""

import cv2
from cv2 import VideoWriter_fourcc
import os

from sppas.src.videodata.videooutputs import VideoOutputs

# ---------------------------------------------------------------------------


class TrackingOutputs(VideoOutputs):
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
        VideoOutputs.__init__(self, path, fps, options)

    # -----------------------------------------------------------------------

    def _out_video(self, value, width=640, height=480):
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
            path = os.path.join(self._vfile_path(i))

            # If the output video does not exist create it
            if os.path.exists(path) is False:
                self._video_output.append(cv2.VideoWriter(path, VideoWriter_fourcc(*'MJPG'),
                                                          self._fps, (width, height)))
            if self._mOptions.get_mode() == "full" or self._mOptions.get_mode() == "None":
                break

    # -----------------------------------------------------------------------

    def _out_folder(self, value):
        """Create folder for each person.

        :param value: (int) The number of person to extract.

        """
        value = int(value)
        if isinstance(value, int) is False:
            raise TypeError

        # Loop over the number of persons on the video
        for i in range(1, value + 1):
            # Create the path of a folder
            path = self._ffile_path(i)

            # If the folder does not exist create it
            if os.path.exists(path) is False:
                os.mkdir(path)
                self._folder_output.append(path)
            # If mode equal full create only one output
            if self._mOptions.get_mode() == "full" or self._mOptions.get_mode() == "None":
                break

    # -----------------------------------------------------------------------

    def _write_csv(self, index, number, coordinate, landmark):
        """Write the information in a csv file.

        :param index: (int) The index of the coordinate.
        :param number: (int) The number for output name.
        :param coordinate: (Coordinates) The Coordinates object.
        :param landmark: (list) The list of landmark points.

        """
        # If csv option is True write the image in the good csv file.
        if self._mOptions.get_csv() is True:
            if coordinate is not None:
                self._csv_output[index].writerow(
                    [number, [coordinate.x, coordinate.y, coordinate.w, coordinate.h]])
            else:
                self._csv_output[index].writerow(
                    [number, None])

    # -----------------------------------------------------------------------

    def _write_video(self, image, index):
        """Write the image in a video.

        :param image: (numpy.ndarray) The image to be processed.
        :param index: (int) The index of the coordinate.

        """
        # If the video option is True write the image in the good video writer.
        if self._mOptions.get_video() is True:
            # If mode equal full create only one output video
            if self._mOptions.get_mode() == "full" or self._mOptions.get_mode() == "None":
                index = 0
                self._video_output[index].write(image)
            else:
                self._video_output[index].write(image)

    # -----------------------------------------------------------------------

    def _write_folder(self, image, index, number):
        """Write the image in a folder.

        :param image: (numpy.ndarray) The image to be processed.
        :param index: (int) The index of the coordinate.
        :param number: (int) The number for output name.

        """
        # If the folder option is True write the image in the good folder.
        if self._mOptions.get_folder() is True:

            # If mode equal full create only one output folder
            if self._mOptions.get_mode() == "full" or self._mOptions.get_mode() == "None":
                index = 0
                cv2.imwrite(self._folder_output[index] + "image" + str(number) + ".jpg", image)
            else:
                cv2.imwrite(self._folder_output[index] + "image" + str(number) + ".jpg", image)

    # -----------------------------------------------------------------------
