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

    src.videodata.facetracking.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~

"""


from sppas.src.imagedata.facedetection import FaceDetection, np


# ---------------------------------------------------------------------------


class FaceTraking(object):
    """Class to track a face.

    :author:       Florian Hocquet
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      contact@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2020  Brigitte Bigi

    """

    def __init__(self):
        """Create a new FaceTraking instance."""
        self.__faces = list()

    # -----------------------------------------------------------------------

    def append(self, image):
        """Add a FaceDetection object in the list."""
        if isinstance(image, np.ndarray) is False:
            raise BufferError
        self.__faces.append(FaceDetection(image))

    # -----------------------------------------------------------------------

    def get_faces(self):
        """Return a list of FaceDetection objects."""
        return self.__faces

    # -----------------------------------------------------------------------

