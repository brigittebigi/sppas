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

    def __init__(self):
        """Create a new Manager instance."""
        self.__coordinates = list()
        self.__persons = list()
        self.__vBuffer = VideoBuffer(20, 0, "../../../../corpus/Test_01_Celia_Brigitte/montage_compressed.mp4")

    # -----------------------------------------------------------------------

    def init_process(self, nb_person, v_value=False, f_value=False):
        """Returns all the faces coordinates in a list

        :param nb_person: (int) The number of person to extract.
        :param v_value: (boolean) If is True extract images in a video.
        :param f_value: (boolean) If is True extract images in a folder.

        """
        nb_person = int(nb_person)
        if isinstance(nb_person, int) is False:
            raise ValueError

        # if v_value is True write images in a video
        if v_value is True:
            self.__coords_writer = sppasImgCoordsWriter(nb_person, video=v_value)

        # if v_value is True write images in a folder
        elif f_value is True:
            self.__coords_writer = sppasImgCoordsWriter(nb_person, folder=f_value)

        self.launch_process(nb_person)

    # -----------------------------------------------------------------------

    def launch_process(self, nb_person):
        """Returns all the faces coordinates in a list

        :param nb_person: (int) The number of person to extract.

        """
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
            self.browse_faces(nb_person)

    # -----------------------------------------------------------------------

    def init_faces(self):
        """Initialize the face_tracker object."""
        for image in self.__vBuffer.get_data():
            self.__fTracker.append(image)

    # -----------------------------------------------------------------------

    def browse_faces(self, nb_person):
        """Browse the detected faces.

        :param nb_person: (int) The number of person to detect.

        """
        # Detect only one face in the video
        for faceDetection in self.__fTracker.get_faces():
            # Detect all the face in the image
            faceDetection.detect_all()

            # Get the Faces with the highest score
            coordinates = faceDetection.get_nbest(nb_person)

            # Loop over the coordinates
            for c in coordinates:
                # The index of the Coordinate in the list of Coordinates objects.
                index = coordinates.index(c)

                # The image to be processed
                image = faceDetection.get_image()

                # For each coordinate write it
                self.write(c, index, image)

    # -----------------------------------------------------------------------

    def write(self, coordinate, index, image):
        """Write images in a video writer.

        :param coordinate: (Coordinates) The coordinate to use.
        :param index: (list) The index of the coordinate.
        :param image: (FaceDetection) The image to be processed.

        """
        self.__coords_writer.to_portrait(coordinate, portrait=True)
        image = self.__coords_writer.mode(image, coordinate, crop_resize=True)
        self.__coords_writer.write(image, index)

        # Show the image
        # cv2.imshow("Image", image)
        # cv2.waitKey(1) & 0xFF

    # -----------------------------------------------------------------------


m = Manager()
m.init_process(2, f_value=True)
