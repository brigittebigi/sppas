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

from sppas.src.videodata.personsbuffer import PersonsBuffer
from sppas.src.videodata.facetracking import FaceTracking
from sppas.src.videodata.videolandmark import VideoLandmark
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

    def __init__(self, video, buffer_size, buffer_overlap, framing=None, mode=None, draw=None, nb_person=0,
                 pattern="-person", width=-1, height=-1, csv_value=False, v_value=False, f_value=False):
        """Create a new Manager instance.

        :param video: (name of video file, image sequence, url or video stream,
        GStreamer pipeline, IP camera) The video to browse.
        :param buffer_size: (int) The size of the buffer.
        :param buffer_overlap: (overlap) The number of values to keep
        from the previous buffer.
        :param framing: (str) The name of the framing option to use.
        :param mode: (str) The name of the mode option to use.
        :param draw: (str) The name of the draw you want to draw.
        :param nb_person: (int) The number of person to detect.
        :param pattern: (str) The pattern to use for the creation of the files.
        :param width: (int) The width of the outputs images and videos.
        :param height: (int) The height of the outputs images and videos.
        :param csv_value: (boolean) If is True extract images in csv_files.
        :param v_value: (boolean) If is True extract images in videos.
        :param f_value: (boolean) If is True extract images in folders.

        """
        self.__pBuffer = PersonsBuffer(video, buffer_size, buffer_overlap)
        self.__coords_writer = sppasVideoCoordsWriter(video, self.__pBuffer.get_fps(), pattern,
                                                      csv=csv_value, video=v_value, folder=f_value)
        self.__coords_writer.set_framing(framing)
        self.__coords_writer.set_mode(mode)
        self.__coords_writer.set_draw(draw)
        self.__coords_writer.set_width(width)
        self.__coords_writer.set_height(height)

        nb_person = int(nb_person)
        if isinstance(nb_person, int) is False or nb_person < 0:
            raise ValueError
        self.__nb_person = nb_person

        self.__mode = mode

        self.__fTracker = FaceTracking()

        self.__landmarks = VideoLandmark()

    # -----------------------------------------------------------------------

    def launch_process(self):
        """Manage the process."""
        # Loop over the video
        while self.__pBuffer.eov:
            # Clear the FaceTracker
            self.__fTracker.clear()

            # Store the result of VideoBuffer.next()
            self.__pBuffer.next()

            # Initialize the list of coordinates from FaceDetection in the FaceTracker
            self.use_tracker()

            # Initialize the list of points for the faces with FaceLandmark
            self.__landmarks.process(self.__pBuffer)

            # Launch the process of creation of the video
            self.__coords_writer.write(self.__pBuffer)

            # Reset the output lists
            self.__pBuffer.clear()

        # Close the buffer
        self.__pBuffer.close()

    # -----------------------------------------------------------------------

    def use_tracker(self):
        """Use the FaceTracker object."""
        self.__fTracker.detect(self.__pBuffer)
        self.__fTracker.create_persons(self.__pBuffer, self.__nb_person)

    # -----------------------------------------------------------------------

