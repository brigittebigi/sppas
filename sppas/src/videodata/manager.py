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

    src.videodata.manager.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~

"""

import time

from sppas.src.videodata.videobuffer import VideoBuffer
from sppas.src.videodata.facetracking import FaceTracking
from sppas.src.videodata.coordswriter import sppasVideoCoordsWriter

# ---------------------------------------------------------------------------


class Manager(object):
    """Class to manage a process.

    :author:       Florian Hocquet
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      contact@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2020  Brigitte Bigi

    """

    def __init__(self, video, buffer_size, buffer_overlap,
                 framing, mode, nb_person=0, patron="person", width=-1, height=-1, csv_value=False, v_value=False, f_value=False):
        """Create a new Manager instance.

        :param video: (name of video file, image sequence, url or video stream,
        GStreamer pipeline, IP camera) The video to browse.
        :param buffer_size: (int) The size of the buffer.
        :param buffer_overlap: (overlap) The number of values to keep
        from the previous buffer.
        :param framing: (str) The name of the framing option to use.
        :param mode: (str) The name of the mode option to use.
        :param nb_person: (int) The number of person to detect.
        :param patron: (str) The patron to use for the creation of the files.
        :param width: (int) The width of the outputs images and videos.
        :param height: (int) The height of the outputs images and videos.
        :param csv_value: (boolean) If is True extract images in csv_files.
        :param v_value: (boolean) If is True extract images in videos.
        :param f_value: (boolean) If is True extract images in folders.

        """
        self.__vBuffer = VideoBuffer(video, buffer_size, buffer_overlap)
        self.__coords_writer = sppasVideoCoordsWriter(video, self.__vBuffer.get_fps(), patron,
                                                      csv=csv_value, video=v_value, folder=f_value)
        self.__coords_writer.set_framing(framing)
        self.__coords_writer.set_mode(mode)
        self.__coords_writer.set_width(width)
        self.__coords_writer.set_height(height)

        nb_person = int(nb_person)
        if isinstance(nb_person, int) is False or nb_person < 0:
            raise ValueError
        self.__nb_person = nb_person

        self.__fTracker = FaceTracking(self.__nb_person)

        self.__eov = False

    # -----------------------------------------------------------------------

    def launch_process(self):
        """Manage the process."""
        # Loop over the video
        while self.__eov is False:
            # Clear the FaceTracker
            self.__fTracker.clear()

            # Store the result of VideoBuffer.next()
            result = self.__vBuffer.next()

            # If it's the end of the video break the loop
            if result is False:
                self.__eov = True

            # Initialize the list of coordinates from FaceDetection in the FaceTracker
            self.use_tracker()

            # Launch the process of creation of the video
            self.__coords_writer.write(self.__vBuffer.get_overlap(), self.__vBuffer, self.__fTracker)

        # Close the buffer
        self.__vBuffer.close()

    # -----------------------------------------------------------------------

    def use_tracker(self):
        """Use the FaceTracker object."""
        self.__fTracker.detect(self.__vBuffer)
        self.__fTracker.person()

    # -----------------------------------------------------------------------

