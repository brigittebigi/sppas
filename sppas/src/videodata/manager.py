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

from sppas.src.videodata.videobuffer import VideoBuffer, cv2
from sppas.src.videodata.facetracking import FaceTraking
from sppas.src.imagedata.coordswriter import sppasImgCoordsWriter

# ---------------------------------------------------------------------------


class Manager(object):
    """Class to manage a process.

    :author:       Florian Hocquet
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      contact@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2020  Brigitte Bigi

    """

    def __init__(self, csv_value=False, v_value=False, f_value=False,
                 portrait=False, full_square=False, crop=False, crop_resize=False):
        """Create a new Manager instance.

        :param csv_value: (boolean) If is True extract images in csv_files.
        :param v_value: (boolean) If is True extract images in videos.
        :param f_value: (boolean) If is True extract images in folders.

        """
        self.__vBuffer = VideoBuffer("../../../../corpus/Test_01_Celia_Brigitte/montage_compressed.mp4", 20, 0)
        self.__coords_writer = sppasImgCoordsWriter(csv=csv_value, video=v_value, folder=f_value)
        self.__coords_writer.set_portrait(portrait)
        self.__coords_writer.set_square(full_square)
        self.__coords_writer.set_crop(crop)
        self.__coords_writer.set_crop_resize(crop_resize)

    # -----------------------------------------------------------------------

    def launch_process(self):
        """Returns all the faces coordinates in a list"""
        # Loop over the video
        while True:
            # Store the result of VideoBuffer.next()
            result = self.__vBuffer.next()

            # If it's the end of the video break the loop
            if result is False:
                return False

            # Create the faceTracker
            self.__fTracker = FaceTraking()

            # Initialize the list of FaceDetection objects in the faceTracker
            self.init_faces()

            # Launch the process of creation of the video
            self.write()

    # -----------------------------------------------------------------------

    def init_faces(self):
        """Initialize the face_tracker object."""
        iterator = self.__vBuffer.__iter__()
        for i in range(0, self.__vBuffer.__len__()):
            self.__fTracker.append(next(iterator))

    # -----------------------------------------------------------------------

    def write(self):
        """Write images in a video writer."""
        self.__coords_writer.browse_faces(self.__fTracker.get_faces())

    # -----------------------------------------------------------------------


m = Manager(v_value=True, f_value=True, portrait=True, crop_resize=False)
m.launch_process()
