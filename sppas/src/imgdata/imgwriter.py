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
    ~~~~~~~~~~~~~~~~~~~~~~~~

"""

from random import randint
import codecs
import cv2
import os

from .coordinates import sppasCoords
from .image import sppasImage

# ---------------------------------------------------------------------------


class ImageWriterOptions(object):
    """Class to manage options of a writer.

    :author:       Florian Hocquet, Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      contact@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2020  Brigitte Bigi

    Fix options to write an image and a set of coordinates:

    - write coordinates in a CSV file;
    - write the image with coordinates tagged by a square;
    - write a set of cropped images in a folder;
    - can force all saved images to be resized

    """

    def __init__(self):
        """Create a new ImageWriterOptions instance.

        Set options to their default values, i.e. do not write anything!

        """
        # The dictionary of outputs
        self._outputs = {"csv": False, "tag": False, "crop": False}

        # Force the width of output image files (0=No)
        self._width = 0
        # Force the height of output image files (0=No)
        self._height = 0

    # -----------------------------------------------------------------------

    def get_csv_output(self):
        """Return True if coordinates will be saved in a CSV file."""
        return self._outputs["csv"]

    # -----------------------------------------------------------------------

    def set_csv_output(self, value):
        """Set to True to save coordinates to a CSV file.

        :param value: (bool)

        """
        value = bool(value)
        if isinstance(value, bool) is False:
            raise TypeError
        self._outputs["csv"] = value

    # -----------------------------------------------------------------------

    def get_tag_output(self):
        """Return True if faces of the image will be surrounded."""
        return self._outputs["tag"]

    # -----------------------------------------------------------------------

    def set_tag_output(self, value):
        """Set to True to surround the faces of the image.

        :param value: (bool)

        """
        self._outputs["tag"] = bool(value)

    # -----------------------------------------------------------------------

    def get_crop_output(self):
        """Return True if the option to crop faces is enabled."""
        return self._outputs["crop"]

    # -----------------------------------------------------------------------

    def set_crop_output(self, value):
        """Set to true to create cropped images.

        :param value: (bool) True to enabled and False to disabled.

        """
        value = bool(value)
        if isinstance(value, bool) is False:
            raise TypeError
        self._outputs["crop"] = value

    # -----------------------------------------------------------------------

    def get_width(self):
        """Return the width of the output image files."""
        return self._width

    # -----------------------------------------------------------------------

    def set_width(self, value):
        """Set the width of output image files.

        :param value: (int) The width of outputs images and videos.

        """
        if isinstance(value, int) is False:
            raise TypeError
        if value < -1 or value > sppasCoords.MAX_W:
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
        if value < -1 or value > sppasCoords.MAX_H:
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

    csv = property(get_csv_output, set_csv_output)
    tag = property(get_tag_output, set_tag_output)
    crop = property(get_crop_output, set_crop_output)

# ---------------------------------------------------------------------------


class sppasImageWriter(object):
    """Write an image and optionally coordinates into files.

    :author:       Florian Hocquet, Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      contact@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2020  Brigitte Bigi

    """

    # generate 10 visually distinct RGB colours
    N = 10
    COLORS = colors = {k: [] for k in 'rgb'}
    for i in range(N):
        temp = {k: randint(0, 255) for k in 'rgb'}
        for k in temp:
            while 1:
                c = temp[k]
                t = set(j for j in range(c - 15, c + 15) if 0 <= j <= 255)
                if t.intersection(COLORS[k]):
                    temp[k] = randint(0, 255)
                else:
                    break
            COLORS[k].append(temp[k])

    # -----------------------------------------------------------------------

    def __init__(self):
        """Create a new ImgWriter instance.

        Write the given image in the given filename.
        Parts of the image can be extracted in separate image files and/or
        surrounded on the given image.
        Output images can be resized.

        """
        # Initialize the options manager
        self._options = ImageWriterOptions()

    # -----------------------------------------------------------------------

    def set_options(self, csv=None, tag=None, crop=None,
                    width=None, height=None):
        """Set the value of each option."""
        if csv is not None:
            self._options.set_csv_output(csv)
        if tag is not None:
            self._options.set_tag_output(tag)
        if crop is not None:
            self._options.set_crop_output(crop)
        if width is not None:
            self._options.set_width(width)
        if height is not None:
            self._options.set_height(height)

    # -----------------------------------------------------------------------

    def write(self, image, coords, out_img_name, pattern=""):
        """Save the image into file(s) depending on the options.

        :param image: (sppasImage) The image to write
        :param coords: (list or list of list of sppasCoords) The coordinates of objects
        :param out_img_name: (str) The filename of the output image file
        :param pattern: (str) Pattern to add to a cropped image filename

        """
        if self._options.csv is True:
            fn, fe = os.path.splitext(out_img_name)
            out_csv_name = fn + ".csv"
            self.write_csv_coords(coords, out_csv_name, out_img_name)

        if self._options.tag is True:
            self.write_tagged_img(image, coords, out_img_name)

        if self._options.crop is True:
            self.write_cropped_img(image, coords, out_img_name, pattern)

    # -----------------------------------------------------------------------

    def write_csv_coords(self, coords, out_csv_name, img_name=""):
        """Write or append a list of coordinates in a CSV file.

        :param coords: (sppasCoords) The coordinates of objects
        :param out_csv_name: (str) The filename of the CSV file to write
        :param img_name: (str) The filename of the image

        """
        mode = "w"
        if os.path.exists(out_csv_name) is True:
            mode = "a+"
        with codecs.open(out_csv_name, mode, encoding="utf-8") as f:
            for i, c1 in enumerate(coords):
                if isinstance(c1, (list, tuple)) is False:
                    self.__write_coords(img_name, f, c1, i)
                else:
                    for j, c2 in enumerate(c1):
                        self.__write_coords(img_name, f, c2, j)

    # -----------------------------------------------------------------------

    def __write_coords(self, img_name, fd, coords, i):
        fd.write("{:s};".format(img_name))
        fd.write("{:d};".format(i + 1))
        fd.write("{:d};".format(coords.x))
        fd.write("{:d};".format(coords.y))
        fd.write("{:d};".format(coords.w))
        fd.write("{:d};".format(coords.h))
        fd.write("{:f}\n".format(coords.get_confidence()))

    # -----------------------------------------------------------------------

    def write_tagged_img(self, image, coords, out_img_name):
        """Tag and save the images with colored squares at given coords.

        :param image: (sppasImage) The image to write
        :param coords: (list or list of list of sppasCoords) The coordinates of objects
        :param out_img_name: (str) The filename of the output image file

        """
        # Make a copy of the image to tag it without changing the given image
        img = sppasImage(input_array=image.copy())
        w, h = img.size()
        pen_width = int(float(w + h) / 500.)

        # Add squares at given coordinates
        for i, c in enumerate(coords):
            # Get the i-th color
            r = sppasImageWriter.COLORS['r'][i % sppasImageWriter.N]
            g = sppasImageWriter.COLORS['g'][i % sppasImageWriter.N]
            b = sppasImageWriter.COLORS['b'][i % sppasImageWriter.N]
            # Draw the square and
            # the confidence inside the square if the coord is not a point
            if isinstance(c, (list, tuple)) is False:
                c = [c]
            img = img.isurround(c, color=(r, g, b), thickness=pen_width, score=True)
        # Save tagged image
        cv2.imwrite(out_img_name, img)

    # -----------------------------------------------------------------------

    def write_cropped_img(self, image, coords, out_img_name, pattern=""):
        """Crop and save the images with squares at given coords.

        :param image: (sppasImage) The image to write
        :param coords: (sppasCoords) The coordinates of objects
        :param out_img_name: (str) The filename of the output image files
        :param pattern: (str) Pattern to add to each file

        """
        for i, c in enumerate(coords):
            # Fix the image filename
            fn, fe = os.path.splitext(out_img_name)
            if len(pattern) > 0 and fn.endswith(pattern):
                # the out_img_name is already including the pattern
                fn = fn[:len(fn)-len(pattern)]
            out_iname = "{:s}_{:d}{:s}{:s}".format(fn, i+1, pattern, fe)

            # Crop the image at the coordinates
            img = image.icrop(c)

            # Resize the cropped image, if requested
            if self._options.get_width() > 0 or self._options.get_height() > 0:
                img = img.iresize(self._options.get_width(),
                                  self._options.get_height())

            # Save the cropped image
            cv2.imwrite(out_iname, img)



