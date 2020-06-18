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

from sppas.src.annotations.FaceMark.landmarkwriter import LandmarkWriter

# ---------------------------------------------------------------------------


class LPCWriter(LandmarkWriter):
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
        LandmarkWriter.__init__(self, path, fps, pattern, usable, csv, video, folder)

    # -----------------------------------------------------------------------

    def _manage_usable(self, buffer, image, index, frameid):
        """Manage the creation of one of the usable output video.

        :param buffer: (VideoBuffer) The buffer which contains images.
        :param image: (numpy.ndarray) The image to be processed.
        :param index: (int) The ID of the person.
        :param frameid: (int) The ID of the image in the buffer.

        """
        # Store the width and the height of the image
        (h, w) = image.shape[:2]

        # Create the usable output videos
        self._mOutputs.out_base(buffer.nb_persons(), w, h)

        # Write the image in usable output video
        self._mOutputs.write_base(image, index)

    # -----------------------------------------------------------------------

