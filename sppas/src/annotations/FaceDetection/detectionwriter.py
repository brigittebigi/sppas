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
    src.videodata.coordswriter.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~
"""

import numpy as np

from sppas.src.imgdata import sppasImage
from sppas.src.imgdata.imageutils import surrond_square, resize, portrait
from sppas.src.imgdata.coordinates import sppasCoords
from sppas.src.annotations.FaceDetection.detectionoptions import ImageOptions
from sppas.src.annotations.FaceDetection.detectionoutputs import ImageOutputs

# ---------------------------------------------------------------------------


class DetectionWriter(object):
    """Class to manage outputs files.

    :author:       Florian Hocquet
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      contact@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2020  Brigitte Bigi

    """

    def __init__(self, path, pattern, usable=False, folder=False):
        """Create a new sppasImgCoordsWriter instance.

        :param path: (str) The path of the image.
        :param pattern: (str) The pattern to use for the creation of the files.
        :param folder: (boolean) If is True extract images in a folder.

        """
        # Initialize the options manager
        self.__iOptions = ImageOptions(pattern, usable=usable, folder=folder)

        # The outputs manager
        self.__iOutputs = ImageOutputs(path, self.__iOptions)

        # The index of the current image
        self.__number = 0

    # -----------------------------------------------------------------------

    def set_options(self, framing=None, mode=None, width=640, height=480):
        """Set the values of the options."""
        self.__iOptions.set_options(framing, mode, width, height)

    # -----------------------------------------------------------------------

    def manage_modifications(self, faces, image1, image2):
        """Verify the option values.

        :param faces: (list) The list of face coordinates;
        :param image1: (numpy.ndarray) The first image to be processed.
        :param image2: (numpy.ndarray) The second to be processed.

        """
        # Loop over the persons
        for i in range(len(faces)):

            # Write the usable output videos
            self.__manage_usable(faces, image1, i)

            # Write the outputs
            self.__manage_verification(faces, image2, i)

    # -----------------------------------------------------------------------

    def __manage_usable(self, faces, image, index):
        """Manage the creation of one of the usable output video.

        :param faces: (list) The list of face coordinates.
        :param image: (numpy.ndarray) The image to be processed.
        :param index: (int) The ID of the person.

        """
        image = self.__apply_usable(faces, image, index)

        # Create the usable output videos
        self.__iOutputs.out_base(len(faces))

        # Write the image in usable output video
        self.__iOutputs.write_base(image, index, self.__number)

    # -----------------------------------------------------------------------

    def __apply_usable(self, faces, image, index):
        """Modify the image for the usable output video.

        :param faces: (list) The list of face coordinates.
        :param image: (numpy.ndarray) The image to be processed.
        :param index: (int) The ID of the person.

        """
        # Copy the sppasCoords object in the faces
        coord = faces[index].copy()

        # Adjust the coordinate
        self.__adjust(image, coord)

        # Crop the image
        img = sppasImage(input_array=image)
        base_image = img.icrop(coord)

        # Resize the image
        base_image = self.__resize(base_image)

        return base_image

    # -----------------------------------------------------------------------

    def __manage_verification(self, faces, image, index):
        """Manage the creation of the verification outputs.

        :param faces: (list) The list of face coordinates.

        """
        if self.__iOptions.get_mode() != "full" and self.__iOptions.get_mode() != "None":
            # Copy the image
            image = image.copy()

        # Aplly modification
        image = self.__apply_tracked(faces, image, index)

        # Store the width and the height of the image
        (h, w) = image.shape[:2]

        # Create the output files
        self.__iOutputs.create_out(len(faces))

        # Write the image in csv file, video, folder
        try:
            self.__iOutputs.write(image, index, self.__number)
        except IndexError:
            self.__iOutputs.write(image, index, self.__number)

    # -----------------------------------------------------------------------

    def __apply_tracked(self, faces, image, index):
        """Apply modification based on the tracking.

        :param faces: (list) The list of face coordinates.
        :param image: (numpy.ndarray) The image to be processed.
        :param index: (int) The ID of the person.

        """
        # If portrait option has been selected
        if self.__iOptions.get_framing() == "portrait":
            # Transform sppasCoords into portrait
            portrait(faces[index])

        # If mode is not full
        if self.__iOptions.get_mode() != "full" and self.__iOptions.get_mode() != "None":
            # Adjust the sppasCoords
            self.__adjust(image, faces[index])

        # If a mode has been selected
        if self.__iOptions.get_mode() != "None":
            # Use one of the extraction options
            image = self.__process_image(image, faces[index], index)

        # If mode is not full
        # or if a mode has been selected
        if self.__iOptions.get_mode() != "full" and self.__iOptions.get_mode() != "None":
            # Resize the image
            image = self.__resize(image)

        return image

    # -----------------------------------------------------------------------

    def __process_image(self, img, coords, index):
        """Draw squares around faces or crop the faces.

        :param img: (numpy.ndarray) The image to be processed.
        :param coords: (sppasCoords) The coordinates of the face.
        :param index: (int) The ID of the person in the list of person.

        """
        index = int(index)
        if isinstance(index, int) is False:
            raise TypeError
        if isinstance(img, np.ndarray) is False:
            raise TypeError
        if isinstance(coords, sppasCoords) is False:
            raise TypeError

        # If mode is full
        if self.__iOptions.get_mode() == "full":
            # Get a different color for each person
            number = (index * 80) % 120

            # Draw a square around the face
            return surrond_square(img, coords, number)

        # If mode is crop
        elif self.__iOptions.get_mode() == "crop":
            # Crop the face
            simg = sppasImage(input_array=img)
            return simg.icrop(coords)

    # -----------------------------------------------------------------------

    def __adjust(self, img, coords):
        """Adjust the coordinates to get a good result.

        :param img: (numpy.ndarray) The image to be processed.
        :param coords: (sppasCoords) The coordinates of the face.

        """
        # If anything has been setted pass
        if self.__iOptions.get_width() == -1 and self.__iOptions.get_height() == -1:
            pass

        # If only the width has been setted use adjust width
        if self.__iOptions.get_width() != -1 and self.__iOptions.get_height() == -1:
            self.__adjust_height()

        # If only the height has been setted use adjust height
        elif self.__iOptions.get_width() == -1 and self.__iOptions.get_height() != -1:
            self.__adjust_width()

        # If both of width and height has been setted
        if self.__iOptions.get_width() != -1 and self.__iOptions.get_height() != -1:
            self.__adjust_both(coords, img)

    # -----------------------------------------------------------------------

    def __adjust_both(self, coords, img=None):
        """Adjust the coordinates with width and height from constructor.

        :param coords: (sppasCoords) The coordinates of the face.
        :param img: (numpy.ndarray) The image to be processed.

        """
        coeff = self.__iOptions.get_width() / self.__iOptions.get_height()
        coeff_coords = coords.w / coords.h
        if coeff != coeff_coords:
            new_w = int(coords.h * coeff)
            old_w = coords.w
            coords.w = new_w
            shift_x = int((old_w - new_w) / 2)
            if coords.x + shift_x < 0:
                shift_x = -coords.x
            coords.x = coords.x + shift_x

        if img is not None:
            (h, w) = img.shape[:2]
            if coords.h > h:
                coords.h = h
                coords.y = 0
            if coords.w > w:
                coords.w = w
                coords.x = 0

    # -----------------------------------------------------------------------

    def __adjust_width(self):
        """Adjust the width based on the width from constructor."""
        if self.__iOptions.get_framing() == "face":
            coeff = 0.75
        else:
            coeff = 4 / 3
        self.__iOptions.set_width(int(self.__iOptions.get_height() * coeff))

    # -----------------------------------------------------------------------

    def __adjust_height(self):
        """Adjust the height based on the height from constructor."""
        if self.__iOptions.get_framing() == "face":
            coeff = 4 / 3
        else:
            coeff = 0.75
        self.__iOptions.set_height(int(self.__iOptions.get_width() * coeff))

    # -----------------------------------------------------------------------

    def __resize(self, img):
        """Resize the image with width and height from constructor.

        :param img: (numpy.ndarray) The image to be processed.

        """
        if self.__iOptions.get_width() == -1 and self.__iOptions.get_height() == -1:
            return img
        else:
            new_image = resize(img, self.__iOptions.get_width(), self.__iOptions.get_height())
            return new_image

    # -----------------------------------------------------------------------
