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
    DNN.

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

    def to_portrait(self, image=None):
        """Scale coordinates of faces to a portrait size.

        The given image allows to ensure we wont scale larger than what the
        image can do.

        :param image: (sppasImage) The original image.

        """
        if len(self._coords) == 0:
            return

        portraits = [c.copy() for c in self._coords]

        for c in portraits:
            # Scale the image. Shift values indicate how to shift x,y to get
            # the face exactly at the center of the new coordinates.
            # The scale is done without matter of the image size.
            shift_x, shift_y = c.scale(2.1)
            # the face is slightly at top, not exactly at the middle
            shift_y = int(float(shift_y) / 1.5)
            if image is None:
                c.shift(shift_x, shift_y)
            else:

                try:
                    c.shift(shift_x, 0, image)
                    shifted_x = True
                except:
                    shifted_x = False

                try:
                    c.shift(0, shift_y, image)
                    shifted_y = True
                except:
                    shifted_y = False

                w, h = image.size()
                if c.x + c.w > w or shifted_x is False:
                    c.x = max(0, w - c.w)

                if c.y + c.h > h or shifted_y is False:
                    c.y = max(0, h - c.h)

        # no error occurred, all faces can be converted to their portrait
        self._coords = portraits
