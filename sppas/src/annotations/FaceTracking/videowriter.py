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

    src.annotations.FaceTracking.videowriter.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Requires the "video" feature of SPPAS.
    Write a video with the result of face detection and face landmark.

"""

from sppas.src.imgdata import sppasImageWriter

# ---------------------------------------------------------------------------


class sppasVideoWriter(object):

    def __init__(self):
        self._img_writer = sppasImageWriter()

        # Added options
        self._video = False
        self._folder = False

    # -----------------------------------------------------------------------

    def set_options(self, csv=None, tag=None, crop=None,
                    width=None, height=None,
                    video=False, folder=False):
        self._img_writer.set_options(csv, tag, crop, width, height)
        self._video = bool(video)
        self._folder = bool(folder)

    # -----------------------------------------------------------------------

    def write(self, video_buffer, out_name, pattern=""):
        """Save the image into file(s) depending on the options.

        :param video_buffer: (sppasFacesVideoBuffer) The images and results to write
        :param out_name: (str) The output name for the folder and/or the video
        :param pattern: (str) Pattern to add to a cropped image filename

        """
        if self._img_writer.options.csv is True:
            out_csv_name = out_name + ".csv"
            self.write_csv_coords(video_buffer, out_csv_name)

    # -----------------------------------------------------------------------

    def write_csv_coords(self, video_buffer, out_csv_name):
        """Write or append a list of coordinates in a CSV file.

        :param video_buffer: (sppasFacesVideoBuffer) The images and results to write
        :param out_csv_name: (str) The filename of the CSV file to write

        """
        pass

    # -----------------------------------------------------------------------


