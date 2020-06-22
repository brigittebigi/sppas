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

    src.videodata.videolandmark.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~

"""

from sppas.src.imgdata import sppasImage
from sppas.src.annotations.FaceMark.facelandmark import FaceLandmark
from sppas.src.imgdata.imageutils import portrait

# ---------------------------------------------------------------------------


class VideoLandmark(object):
    """Class to landmark faces.

    :author:       Florian Hocquet
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      contact@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2020  Brigitte Bigi

    """

    def __init__(self):
        """Create a new VideoLandmark instance."""

        self.__face = FaceLandmark()

    # -----------------------------------------------------------------------

    def process(self, buffer):
        """Browse the buffer.

        :param buffer: (VideoBuffer) The buffer which contains images.

        """
        # If Tracker process haven't been used create only one
        # person for the landmark
        if buffer.is_tracked() is False:
            buffer.add_landmarks()

        # Else create a landmark for each person in the video
        else:
            for i in range(buffer.nb_persons()):
                buffer.add_landmarks()

        # Initialise the iterator
        iterator = buffer.__iter__()

        # Loop over the buffer
        for j in range(0, len(buffer)):
            print(j)
            # Go to the next image
            img = next(iterator)

            # If Tracker process haven't been used apply
            # landmark for only one person
            if buffer.is_tracked() is False:
                self.landmark_person(buffer, img)

            # Else apply landmark for each person
            # in the video
            else:
                self.__landmark_persons(buffer, img, j)

    # -----------------------------------------------------------------------

    def landmark_person(self, buffer, image):
        """Apply landmark on an already good video.

        :param buffer: (VideoBuffer) The buffer which contains images.
        :param image: (np.ndarray) The image to be processed.

        """
        # Reset the FaceLandmark
        self.reset()

        # Launch the landmark on the image
        landmark = self.__landmark(image)

        # Add the values in the buffer
        buffer.add_landmark(0, landmark)

    # -----------------------------------------------------------------------

    def __landmark_persons(self, buffer, img, index):
        """Apply landmark for each person on the image.

        :param buffer: (VideoBuffer) The buffer which contains images.
        :param img: (np.ndarray) The image to be processed.
        :param index: (int) The index of the image in the Buffer.

        """
        # Loop over the result of PersonTracking
        for i in range(buffer.nb_persons()):
            # Reset the FaceLandmark
            self.reset()

            # Copy the image
            image = img.copy()

            # Store the index of the person
            index_person = i

            # To avoid IndexError
            if index > len(buffer.get_person(i)) - 1:
                continue

            # If a person has been detected
            if buffer.get_coordinate(i, index) is not None:
                # Duplicate the coordinates
                coords = buffer.get_coordinate(i, index).copy()

                # Adjust the coordinates to get a more accurate result
                portrait(coords, 1.5)

                # Crop the visage according to the values of the coordinates
                img = sppasImage(input_array=image)
                image = img.icrop(coords)

                # Launch the landmark on the image
                landmark = self.__landmark(image)

                if landmark is not None:
                    # Adjust the result according to the base image
                    landmark = self.__adjust_points(landmark, coords.x, coords.y)

                # Add the values in the buffer
                buffer.add_landmark(index_person, landmark)

            else:
                # Add the values in the buffer
                buffer.add_landmark(index_person, None)

    # -----------------------------------------------------------------------

    def __landmark(self, image):
        """Apply face landmark process.

        :param image: (np.ndarray) The image to be processed.

        """
        try:
            # Launch the process of FaceLandmark
            self.__face.landmarks(image)
        except IndexError:
            raise IOError

        # Add the list of x-axis, y-axis coordinates
        return self.__face.get_landmarks()

    # -----------------------------------------------------------------------

    def __adjust_points(self, points, x, y):
        """Adjust values of the points according to the base image.

        :param points: (list) The list of landmark points.
        :param x: (int) The start value on the x-axis of
        the cropped image from the base image.
        :param y: (int) The start value on the y-axis of
        the cropped image from the base image.

        """
        # Loop over the result of landmark and change the values
        # according to the base image
        new_points = list()
        for tu in points:
            new_x, new_y = tu
            new_x += x
            new_y += y
            new_points.append((new_x, new_y))

        # Return the new list of tuple(x-axis, y-axis) values
        return new_points

    # -----------------------------------------------------------------------

    def reset(self):
        """Reset the FaceLandmark object."""
        self.__face.reset()

    # -----------------------------------------------------------------------
