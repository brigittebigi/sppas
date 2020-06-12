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

    src.imagedata.managerdetection.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~

"""

import cv2

from sppas.src.imagedata.facedetection import FaceDetection
from sppas.src.annotations.FaceDetection.detectionwriter import DetectionWriter

# ---------------------------------------------------------------------------


class ManagerDetection(object):
    """Class to manage a process.

    :author:       Florian Hocquet
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      contact@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2020  Brigitte Bigi

    >>> manager = ManagerDetection(image,
    >>>                            pattern="-person", width=-1, height=-1,
    >>>                            framing="face",
    >>>                            f_value=True)
    >>> manager.launch_process()

    """

    def __init__(self, image, pattern="-person", width=-1, height=-1,
                 framing=None, mode=None,
                 f_value=False):
        """Create a new ManagerDetection instance.

        :param image: (name of the image, png, jpg...) The image to be processed.
        :param framing: (str) The name of the framing option to use.
        :param mode: (str) The name of the mode option to use.
        :param pattern: (str) The pattern to use for the creation of the files.
        :param width: (int) The width of the outputs images and videos.
        :param height: (int) The height of the outputs images and videos.
        :param f_value: (boolean) If True extract images in folders.

        """
        # The image to be processed
        self.__image = cv2.imread(image)

        # The FaceDetection object
        self.__FaceDetection = FaceDetection(self.__image)

        # The list of coordinates
        self.__faces = list()

        # Initialize the writer for the outputs files
        self.__image_writer = DetectionWriter(image, pattern=pattern, folder=f_value)
        self.__image_writer.set_options(framing, mode, width, height)

    # -----------------------------------------------------------------------

    def launch_process(self):
        """Manage the process."""
        # Loop over the video
        self.__FaceDetection.detect_all()
        self.__faces = self.__FaceDetection.get_all()

        self.__image_writer.manage_modifications(self.__faces, self.__image, self.__image.copy())

    # -----------------------------------------------------------------------

