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
from cv2 import error as cv2error

from pympler.asizeof import asizeof
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
                 framing, mode, width=-1, height=-1, csv_value=False, v_value=False, f_value=False):
        """Create a new Manager instance.

        :param video: (name of video file, image sequence, url or video stream,
        GStreamer pipeline, IP camera) The video to browse.
        :param buffer_size: (int) The size of the buffer.
        :param buffer_overlap: (overlap) The number of values to keep
        from the previous buffer.
        :param csv_value: (boolean) If is True extract images in csv_files.
        :param v_value: (boolean) If is True extract images in videos.
        :param f_value: (boolean) If is True extract images in folders.
        :param framing: (boolean) If is True scale the coordinate
        to get the portraits from faces.
        :param mode: (boolean) If is True draw square around faces.
        the coordinates and resize the image.

        """
        self.__vBuffer = VideoBuffer(video, buffer_size, buffer_overlap)
        self.__coords_writer = sppasVideoCoordsWriter(csv=csv_value, video=v_value, folder=f_value)
        self.__coords_writer.set_framing(framing)
        self.__coords_writer.set_mode(mode)
        self.__coords_writer.set_width(width)
        self.__coords_writer.set_height(height)

    # -----------------------------------------------------------------------

    def launch_process(self):
        """Returns all the faces coordinates in a list"""
        # Loop over the video
        start_time = time.time()
        print("Starting")
        while True:
            # Store the result of VideoBuffer.next()
            result = self.__vBuffer.next()

            # If it's the end of the video break the loop
            if result is False:
                print("--- %s seconds ---" % (time.time() - start_time))
                return False
            # Create the faceTracker
            self.__fTracker = FaceTracking()

            # Initialize the list of FaceDetection objects in the faceTracker
            self.init_faces()

            # Launch the process of creation of the video
            self.write()

    # -----------------------------------------------------------------------

    def init_faces(self):
        """Initialize the face_tracker object."""
        self.__fTracker.persons(self.__vBuffer)

    # -----------------------------------------------------------------------

    def write(self):
        """Write images in a video writer."""
        self.__coords_writer.browse_faces(self.__vBuffer.get_overlap(), self.__vBuffer, self.__fTracker)

    # -----------------------------------------------------------------------


# "../../../../../LFPC_test_1.mp4"
# "../../../../corpus/Test_01_Celia_Brigitte/montage_compressed.mp4"
manager = Manager("../../../../corpus/Test_01_Celia_Brigitte/montage_compressed.mp4", 100, 0,
                  "portrait", "crop", width=-1, height=-1, csv_value=True, v_value=True, f_value=True)
manager.launch_process()

