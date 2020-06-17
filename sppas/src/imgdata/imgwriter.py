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

    src.imgdata.imgwriter.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Bunch of classes to write an image with various options:

        - ImageWriterOptions
        - ImageOutputs
        - ImageWriter

"""

import cv2
import os
import shutil
import glob

# ---------------------------------------------------------------------------


class ImageWriterOptions(object):
    """Class to manage options of a writer.

    :author:       Florian Hocquet, Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      contact@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2020  Brigitte Bigi

    """

    # The framing options. The first one is the default one.
    FRAMING = ["face", "portrait"]

    # The mode options. The first one is the default one.
    MODE = ["full", "crop"]

    # The draw options. The first one is the default one.
    DRAW = ["circle", "ellipse", "square"]

    def __init__(self, pattern, folder=False, usable=False):
        """Create a new ImageWriterOptions instance."""

        # The dictionary of options to define the outputs
        self._output = {"usable": False, "folder": False}

        # The framing to use, face or portrait
        self._framing = None
        # The mode to use, full or crop
        self._mode = None

        # The width you want for the outputs files
        self._width = -1
        # The height you want for the outputs files
        self._height = -1

        # Initialize outputs files
        self.__init_outputs(usable, folder)

        # The pattern to use for the outputs files
        self.__pattern = str()
        self.set_pattern(pattern)

    # -----------------------------------------------------------------------

    def __init_outputs(self, usable, folder):
        """Init the values of the output options.

        :param usable: (boolean) If True create the usable videos.
        :param folder: (boolean) If True extract images in a folder.

        """
        # If csv is True set the csv outputs files to True
        if usable is True:
            self.set_usable(True)

        # If folder is True set the folders outputs to True
        if folder is True:
            self.set_folder(True)

    # -----------------------------------------------------------------------

    def set_options(self, framing, mode, width, height):
        """Set the values of the options."""
        self.set_framing(framing)
        self.set_mode(mode)
        self.set_width(width)
        self.set_height(height)

        self.__verify_options()

    # -----------------------------------------------------------------------

    def __verify_options(self):
        """Verify and adjust the option values."""
        if self._mode is None:
            # If only framing has been set and equal to face
            if self._framing == "face":
                self._mode = "full"
            # If only framing has been set and equal to portrait
            if self._framing == "portrait":
                self._mode = "crop"

        elif self._mode == "full":
            # If only mode has been set and equal to full
            if self._framing is None:
                self._framing = "face"

        elif self._mode == "crop":
            # If only mode has been set and equal to crop
            if self._framing is None:
                self._framing = "portrait"
            # If only framing has been set and equal to portrait
            elif self._framing == "face":
                self.set_folder(False)

    # -----------------------------------------------------------------------

    def get_usable(self):
        """Return True if the option usable is enabled."""
        return self._output["usable"]

    # -----------------------------------------------------------------------

    def set_usable(self, value):
        """Enable or not the usable output.

        :param value: (bool) True to enabled and False to disabled.

        """
        value = bool(value)
        if isinstance(value, bool) is False:
            raise TypeError
        self._output["usable"] = value

    # -----------------------------------------------------------------------

    def get_folder(self):
        """Return True if the option folder is enabled."""
        return self._output["folder"]

    # -----------------------------------------------------------------------

    def set_folder(self, value):
        """Enable or not the folder output.

        :param value: (bool) True to enabled and False to disabled.

        """
        value = bool(value)
        if isinstance(value, bool) is False:
            raise TypeError
        self._output["folder"] = value

    # -----------------------------------------------------------------------

    def get_framing(self):
        """Return the framing."""
        return self._framing.get_value()

    # -----------------------------------------------------------------------

    def set_framing(self, value):
        """Set the framing.

        :param value: (str) The framing to use on each image of the buffer,
        face or portrait.

        """
        if isinstance(value, str) is False and value is not None:
            raise TypeError
        if value not in ImageWriterOptions.FRAMING and value is not None:
            raise ValueError
        self._framing.set_value(value)

    # -----------------------------------------------------------------------

    def get_mode(self):
        """Return the mode."""
        return self._mode

    # -----------------------------------------------------------------------

    def set_mode(self, value):
        """Set the mode.

        :param value: (str) The mode to use on each image of the buffer,
        full or crop.

        """
        if isinstance(value, str) is False and value is not None:
            raise TypeError
        if value not in ImageWriterOptions.MODE and value is not None:
            raise ValueError
        self._mode = value

    # -----------------------------------------------------------------------

    def get_width(self):
        """Return the width of the outputs files."""
        return self._width

    # -----------------------------------------------------------------------

    def set_width(self, value):
        """Set the width of outputs.

        :param value: (int) The width of outputs images and videos.

        """
        if isinstance(value, int) is False:
            raise TypeError
        if value < -1 or value > 15360:
            raise ValueError
        self._width = value

    # -----------------------------------------------------------------------

    def get_height(self):
        """Return the height of the outputs files."""
        return self._height

    # -----------------------------------------------------------------------

    def set_height(self, value):
        """Set the height of outputs.

        :param value: (int) The height of outputs images and videos.

        """
        if isinstance(value, int) is False:
            raise TypeError
        if value < -1 or value > 8640:
            raise ValueError
        self._height = value

    # -----------------------------------------------------------------------

    def get_size(self):
        """Return the size of the outputs files."""
        return self._width, self._height

    # -----------------------------------------------------------------------

    def set_size(self, width, height):
        """Set the size of outputs.

        :param width: (int) The width of outputs images and videos.
        :param height: (int) The height of outputs images and videos.

        """
        self.set_width(width)
        self.set_height(height)

    # -----------------------------------------------------------------------

    def get_pattern(self):
        """Return the pattern of the outputs files."""
        return self.__pattern

    # -----------------------------------------------------------------------

    def set_pattern(self, value):
        """Set the pattern of the outputs files.

        :param value: (str) The pattern in all the outputs files.

        """
        if isinstance(value, str) is False:
            raise TypeError
        self.__pattern = value

# ---------------------------------------------------------------------------


class ImagesWriter(object):
    """Write a bunch of images into files.

    :author:       Florian Hocquet, Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      contact@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2020  Brigitte Bigi

    """

    def __init__(self, path, pattern, folder=False, usable=False):
        """Create a new ImgWriter instance.

        :param path: (str) The path of the image.
        :param pattern: (str) The pattern to use for the creation of the files.
        :param folder: (boolean) If is True extract images in a folder.

        """
        # Initialize the options manager
        self._options = ImageWriterOptions(pattern, usable=usable, folder=folder)

        # The outputs manager
        self.__iOutputs = ImageOutputs(path, self._options)

        # The index of the current image
        self.__number = 0

    # -----------------------------------------------------------------------

    def set_options(self, framing=None, mode=None, width=640, height=480):
        """Set the values of the options."""
        self._options.set_options(framing, mode, width, height)

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
        if self._options.get_mode() != "full" and self._options.get_mode() != "None":
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
        if self._options.get_framing() == "portrait":
            # Transform sppasCoords into portrait
            portrait(faces[index])

        # If mode is not full
        if self._options.get_mode() != "full" and self._options.get_mode() != "None":
            # Adjust the sppasCoords
            self.__adjust(image, faces[index])

        # If a mode has been selected
        if self._options.get_mode() != "None":
            # Use one of the extraction options
            image = self.__process_image(image, faces[index], index)

        # If mode is not full
        # or if a mode has been selected
        if self._options.get_mode() != "full" and self._options.get_mode() != "None":
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
        if self._options.get_mode() == "full":
            # Get a different color for each person
            number = (index * 80) % 120

            # Draw a square around the face
            return surrond_square(img, coords, number)

        # If mode is crop
        elif self._options.get_mode() == "crop":
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
        if self._options.get_width() == -1 and self._options.get_height() == -1:
            pass

        # If only the width has been setted use adjust width
        if self._options.get_width() != -1 and self._options.get_height() == -1:
            self.__adjust_height()

        # If only the height has been setted use adjust height
        elif self._options.get_width() == -1 and self._options.get_height() != -1:
            self.__adjust_width()

        # If both of width and height has been setted
        if self._options.get_width() != -1 and self._options.get_height() != -1:
            self.__adjust_both(coords, img)

    # -----------------------------------------------------------------------

    def __adjust_both(self, coords, img=None):
        """Adjust the coordinates with width and height from constructor.

        :param coords: (sppasCoords) The coordinates of the face.
        :param img: (numpy.ndarray) The image to be processed.

        """
        coeff = self._options.get_width() / self._options.get_height()
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
        if self._options.get_framing() == "face":
            coeff = 0.75
        else:
            coeff = 4 / 3
        self._options.set_width(int(self._options.get_height() * coeff))

    # -----------------------------------------------------------------------

    def __adjust_height(self):
        """Adjust the height based on the height from constructor."""
        if self._options.get_framing() == "face":
            coeff = 4 / 3
        else:
            coeff = 0.75
        self._options.set_height(int(self._options.get_width() * coeff))

    # -----------------------------------------------------------------------

    def __resize(self, img):
        """Resize the image with width and height from constructor.

        :param img: (numpy.ndarray) The image to be processed.

        """
        if self._options.get_width() == -1 and self._options.get_height() == -1:
            return img
        else:
            new_image = resize(img, self._options.get_width(), self._options.get_height())
            return new_image

