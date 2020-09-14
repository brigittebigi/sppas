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

    src.annotations.FaceDetection.facedetection.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Requires the "video" feature of SPPAS.
    Automatic face detection, based on opencv HaarCascadeClassifier and
    Artificial Neural Networks.

"""

from sppas.src.imgdata import sppasImage
from sppas.src.imgdata import sppasImageObjectDetection

# ---------------------------------------------------------------------------


class FaceDetection(sppasImageObjectDetection):
    """Detect faces in an image.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      contact@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2020  Brigitte Bigi

    This class allows to analyze an image in order to detect faces. It
    stores a list of sppasCoords() for each detected face.

    :Example:

        >>> f = FaceDetection()
        >>> f.load_model(filename1, filename2...)
        >>> # Detect all the faces in an image
        >>> image = sppasImage(filename="image path"))
        >>> f.detect(image)
        >>> # Get number of detected faces
        >>> len(f)
        >>> # Browse through all the detected face coordinates:
        >>> for c in f:
        >>>     print(c)
        >>> # Get the detected faces with the highest score
        >>> f.get_best()
        >>> # Get the 2 faces with the highest scores
        >>> f.get_best(2)
        >>> # Get detected faces with a confidence score greater than 0.8
        >>> f.get_confidence(0.8)
        >>> # Convert coordinates to a portrait size (i.e. scale by 2.1)
        >>> f.to_portrait(image)

    Contrariwise to the base class, this class allows multiple models
    in order to launch multiple detections and to combine results.

    """

    def __init__(self):
        """Create a new FaceDetection instance."""
        super(FaceDetection, self).__init__()
        self._extension = ""

    # -----------------------------------------------------------------------

    def detect(self, image):
        """Determine the coordinates of all the detected objects.

        :param image: (sppasImage or numpy.ndarray)

        """
        # Launch the base method to detect objects, here objects are faces
        sppasImageObjectDetection.detect(self, image)

        # Overlapped faces are much rarer than overlapped objects:
        # re-filter with overlapping portraits.

        # Backup the current coords
        backup_coords = dict()
        for coord in self._coords:
            portrait = self.eval_portrait(coord, image)
            backup_coords[portrait] = coord

        # Replace the original coords by the portrait
        self._coords = list(backup_coords.keys())

        # Filter the overlapping portraits but do not re-normalize the scores
        # by the number of classifiers.
        self.filter_overlapped(overlap=60., norm_score=False)
        self.sort_by_score()

        # re-assign the normal size
        new_coords = list()
        for portrait_coord in self._coords:
            normal_coord = backup_coords[portrait_coord]
            new_coords.append(normal_coord)

        self._coords = new_coords

    # -----------------------------------------------------------------------

    def to_portrait(self, image=None):
        """Scale coordinates of faces to a portrait size.

        The given image allows to ensure we wont scale larger than what the
        image can do.

        :param image: (sppasImage) The original image.

        """
        if len(self._coords) == 0:
            return

        portraits = list()
        for coord in self._coords:
            c = self.eval_portrait(coord, image)
            portraits.append(c)

        # no error occurred, all faces are converted to their portrait
        self._coords = portraits

    # -----------------------------------------------------------------------

    @staticmethod
    def eval_portrait(coordinate, image=None):
        """Return the coordinates converted to the portrait scale.

        :param coordinate: (sppasCoords)
        :param image: (sppasImage) The original image.
        :return: (sppasCoords)

        """
        coord = coordinate.copy()
        # Scale the image. Shift values indicate how to shift x,y to get
        # the face exactly at the center of the new coordinates.
        # The scale is done without matter of the image size.
        shift_x, shift_y = coord.scale(2.1)
        # the face is slightly at top, not exactly at the middle
        shift_y = int(float(shift_y) / 1.25)
        if image is None:
            coord.shift(shift_x, shift_y)
        else:

            try:
                coord.shift(shift_x, 0, image)
                shifted_x = True
            except:
                shifted_x = False

            try:
                coord.shift(0, shift_y, image)
                shifted_y = True
            except:
                shifted_y = False

            w, h = image.size()
            if coord.x + coord.w > w or shifted_x is False:
                coord.x = max(0, w - coord.w)

            if coord.y + coord.h > h or shifted_y is False:
                coord.y = max(0, h - coord.h)

        return coord

