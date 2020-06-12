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

from sppas.src.imagedata.imageutils import crop, surrond_square, resize, portrait
from sppas.src.imagedata.coordinates import Coordinates
from sppas.src.annotations.FaceTracking.trackingoptions import TrackingOptions
from sppas.src.annotations.FaceTracking.trackingoutputs import TrackingOutputs

# ---------------------------------------------------------------------------


class TrackingWriter(object):
    """Class to manage outputs files.

    :author:       Florian Hocquet
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      contact@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2020  Brigitte Bigi

    """

    def __init__(self, path, fps, pattern, usable=False, csv=False, video=False, folder=False):
        """Create a new sppasImgCoordsWriter instance.

        :param path: (str) The path of the video.
        :param fps: (int) The FPS of the video.
        :param pattern: (str) The pattern to use for the creation of the files.
        :param csv: (boolean) If is True extract images in csv file.
        :param video: (boolean) If is True extract images in a video.
        :param folder: (boolean) If is True extract images in a folder.

        """
        # Initialize the options manager
        self.__tOptions = TrackingOptions(pattern, usable=usable, csv=csv, video=video, folder=folder)

        # The outputs manager
        self.__tOutputs = TrackingOutputs(path, fps, self.__tOptions)

        # The index of the current image
        self.__number = 0

    # -----------------------------------------------------------------------

    def set_options(self, framing=None, mode=None, width=640, height=480):
        """Set the values of the options."""
        self.__tOptions.set_options(framing, mode, width, height)

    # -----------------------------------------------------------------------

    def process(self, buffer):
        """Browse the buffer.

        :param buffer: (VideoBuffer) The buffer which contains images.

        """
        # Verify the options
        self.__verify_options(buffer)

        # Initialise the iterator
        iterator = buffer.__iter__()

        # Loop over the buffer
        for frameID in range(0, buffer.__len__()):

            # If image in the overlap continue
            if frameID < buffer.get_overlap():
                continue

            # Go to the next frame
            img = next(iterator)

            image1 = img.copy()
            image2 = img.copy()

            self.manage_modifications(buffer, image1, image2, frameID)

            # Increment the number of image by 1
            self.__number += 1

    # -----------------------------------------------------------------------

    def manage_modifications(self, buffer, image1, image2, frameid):
        """Verify the option values.

        :param buffer: (VideoBuffer) The buffer which contains images.
        :param image1: (numpy.ndarray) The first image to be processed.
        :param image2: (numpy.ndarray) The second to be processed.
        :param frameid: (int) The ID of the image in the buffer.

        """
        # Loop over the persons
        for i in range(buffer.nb_persons()):

            # If tracking process has been used
            if buffer.is_tracked() is True:
                # If any visage has been detected continue
                if buffer.get_coordinate(i, frameid) is None:
                    continue

            if self.__tOptions.get_width() != -1 and self.__tOptions.get_height() != -1 and \
                    self.__tOptions.get_usable() is True:
                # Write the usable output videos
                self.__manage_usable(buffer, image1, i, frameid)

            # If any option is enabled use only the csv outputs files
            option = self.__tOptions.get_framing() == "None" and self.__tOptions.get_mode() == "None"
            if option is False and \
                    self.__tOptions.get_csv() is True or self.__tOptions.get_video() is True or \
                    self.__tOptions.get_folder() is True:
                # Write the outputs
                self.__manage_verification(buffer, image2, i, frameid)

    # -----------------------------------------------------------------------

    def __verify_options(self, buffer):
        """Verify the option values according to the buffer.

        :param buffer: (VideoBuffer) The buffer which contains images.

        """
        # If option are the same as the one for the usable output videos
        if self.__tOptions.get_framing() == "portrait" and self.__tOptions.get_mode() == "crop":
            # Set output video to False
            self.__tOptions.set_video(False)

    # -----------------------------------------------------------------------

    def __manage_usable(self, buffer, image, index, frameID):
        """Manage the creation of one of the usable output video.

        :param buffer: (VideoBuffer) The buffer which contains images.
        :param image: (numpy.ndarray) The image to be processed.
        :param index: (int) The ID of the person.
        :param frameID: (int) The ID of the image in the buffer.

        """
        # If tracking process has been used
        if buffer.is_tracked() is True:
            # Create the usable image
            image = self.__apply_usable(buffer, image, index, frameID)

        # Store the width and the height of the image
        (h, w) = image.shape[:2]

        # Create the usable output videos
        self.__tOutputs.out_base(buffer.nb_persons(), w, h)

        # Write the image in usable output video
        self.__tOutputs.write_base(image, index)

    # -----------------------------------------------------------------------

    def __apply_usable(self, buffer, image, index, frameID):
        """Modify the image for the usable output video.

        :param buffer: (VideoBuffer) The buffer which contains images.
        :param image: (numpy.ndarray) The image to be processed.
        :param index: (int) The ID of the person.
        :param frameID: (int) The ID of the image in the buffer.

        """
        # Copy the Coordinates object in the buffer
        coord = buffer.get_coordinate(index, frameID).copy()

        # Make portrait with coordinates
        portrait(coord)

        # Adjust the coordinate
        self.__adjust(image, coord)

        # Crop the image
        base_image = crop(image, coord)

        # Resize the image
        base_image = self.__resize(base_image)

        return base_image

    # -----------------------------------------------------------------------

    def __manage_verification(self, buffer, image, index, frameID):
        """Manage the creation of the verification outputs.

        :param buffer: (VideoBuffer) The buffer which contains images.

        """
        if self.__tOptions.get_mode() != "full" and self.__tOptions.get_mode() != "None":
            # Copy the image
            image = image.copy()

        # If the tracking process has been used
        if buffer.is_tracked() is True:
            # Aplly modification
            image = self.__apply_tracked(buffer, image, index, frameID)

        # Store the width and the height of the image
        (h, w) = image.shape[:2]

        # Create the output files
        self.__tOutputs.create_out(buffer.nb_persons(), w, h)

        # Write the image in csv file, video, folder
        self.__tOutputs.write(image, index, self.__number, coordinate=buffer.get_coordinate(index, frameID))

    # -----------------------------------------------------------------------

    def __apply_tracked(self, buffer, image, index, frameID):
        """Apply modification based on the tracking.

        :param buffer: (VideoBuffer) The buffer which contains images.
        :param image: (numpy.ndarray) The image to be processed.
        :param index: (int) The ID of the person.
        :param frameID: (int) The ID of the image in the buffer.

        """
        # If portrait option has been selected
        if self.__tOptions.get_framing() == "portrait":
            # Transform Coordinates into portrait
            portrait(buffer.get_coordinate(index, frameID))

        # If mode is not full
        if self.__tOptions.get_mode() != "full" and self.__tOptions.get_mode() != "None":
            # Adjust the Coordinates
            self.__adjust(image, buffer.get_coordinate(index, frameID))

        # If a mode has been selected
        if self.__tOptions.get_mode() != "None":
            # Use one of the extraction options
            image = self.__process_image(image, buffer.get_coordinate(index, frameID), index)

        # If mode is not full
        # or if a mode has been selected
        if self.__tOptions.get_mode() != "full" and self.__tOptions.get_mode() != "None":
            # Resize the image
            image = self.__resize(image)

        return image

    # -----------------------------------------------------------------------

    def __process_image(self, img_buffer, coords, index):
        """Draw squares around faces or crop the faces.

        :param img_buffer: (numpy.ndarray) The image to be processed.
        :param coords: (Coordinates) The coordinates of the face.
        :param index: (int) The ID of the person in the list of person.

        """
        index = int(index)
        if isinstance(index, int) is False:
            raise TypeError
        if isinstance(img_buffer, np.ndarray) is False:
            raise TypeError
        if isinstance(coords, Coordinates) is False:
            raise TypeError

        # If mode is full
        if self.__tOptions.get_mode() == "full":
            # Get a different color for each person
            number = (index * 80) % 120

            # Draw a square around the face
            return surrond_square(img_buffer, coords, number)

        # If mode is crop
        elif self.__tOptions.get_mode() == "crop":
            # Crop the face
            return crop(img_buffer, coords)

    # -----------------------------------------------------------------------

    def __adjust(self, img_buffer, coords):
        """Adjust the coordinates to get a good result.

        :param img_buffer: (numpy.ndarray) The image to be processed.
        :param coords: (Coordinates) The coordinates of the face.

        """
        if self.__tOptions.get_mode() == "crop" and self.__tOptions.get_width() == -1 and self.__tOptions.get_height() == -1:
            self.__tOptions.set_video(False)

        # If anything has been setted pass
        if self.__tOptions.get_width() == -1 and self.__tOptions.get_height() == -1:
            pass

        # If only the width has been setted use adjust width
        if self.__tOptions.get_width() != -1 and self.__tOptions.get_height() == -1:
            self.__adjust_height()

        # If only the height has been setted use adjust height
        elif self.__tOptions.get_width() == -1 and self.__tOptions.get_height() != -1:
            self.__adjust_width()

        # If both of width and height has been setted
        if self.__tOptions.get_width() != -1 and self.__tOptions.get_height() != -1:
            self.__adjust_both(coords, img_buffer)

    # -----------------------------------------------------------------------

    def __adjust_both(self, coords, img_buffer=None):
        """Adjust the coordinates with width and height from constructor.

        :param coords: (Coordinates) The coordinates of the face.
        :param img_buffer: (numpy.ndarray) The image to be processed.

        """
        coeff = self.__tOptions.get_width() / self.__tOptions.get_height()
        coeff_coords = coords.w / coords.h
        if coeff != coeff_coords:
            new_w = int(coords.h * coeff)
            old_w = coords.w
            coords.w = new_w
            shift_x = int((old_w - new_w) / 2)
            if coords.x + shift_x < 0:
                shift_x = -coords.x
            coords.x = coords.x + shift_x

        if img_buffer is not None:
            (h, w) = img_buffer.shape[:2]
            if coords.h > h:
                coords.h = h
                coords.y = 0
            if coords.w > w:
                coords.w = w
                coords.x = 0

    # -----------------------------------------------------------------------

    def __adjust_width(self):
        """Adjust the width based on the width from constructor."""
        if self.__tOptions.get_framing() == "face":
            coeff = 0.75
        else:
            coeff = 4 / 3
        self.__tOptions.set_width(int(self.__tOptions.get_height() * coeff))

    # -----------------------------------------------------------------------

    def __adjust_height(self):
        """Adjust the height based on the height from constructor."""
        if self.__tOptions.get_framing() == "face":
            coeff = 4 / 3
        else:
            coeff = 0.75
        self.__tOptions.set_height(int(self.__tOptions.get_width() * coeff))

    # -----------------------------------------------------------------------

    def __resize(self, img_buffer):
        """Resize the image with width and height from constructor.

        :param img_buffer: (numpy.ndarray) The image to be processed.

        """
        if self.__tOptions.get_width() == -1 and self.__tOptions.get_height() == -1:
            return img_buffer
        else:
            new_image = resize(img_buffer, self.__tOptions.get_width(), self.__tOptions.get_height())
            return new_image

    # -----------------------------------------------------------------------
