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

    src.videodata.managerlandmark.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~

"""

from sppas.src.videodata.personsbuffer import PersonsBuffer
from sppas.src.videodata.videolandmark import VideoLandmark
from sppas.src.annotations.FaceMark.landmarkwriter import LandmarkWriter

# ---------------------------------------------------------------------------


class Manager(object):
    """Class to manage a process.

    :author:       Florian Hocquet
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      contact@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2020  Brigitte Bigi


    >>> manager = Manager(video, 90, 0,
    >>>                   pattern="-person",
    >>>                   usable_value=True, csv_value=True, f_value=True)
    >>> manager.launch_process()

    """

    def __init__(self, video, buffer_size, buffer_overlap,
                 draw=True,
                 pattern="-person",
                 usable_value=True, csv_value=False, f_value=False):
        """Create a new Manager instance.

        :param video: (name of video file, image sequence, url or video stream,
        GStreamer pipeline, IP camera) The video to be processed.
        :param buffer_size: (int) The size of the buffer.
        :param buffer_overlap: (overlap) The number of values to keep
        from the previous buffer.
        :param draw: (str) True to draw circle around landmark points.
        :param pattern: (str) The pattern to use for the creation of the files.
        :param csv_value: (boolean) If True extract images in csv_files.
        :param f_value: (boolean) If True extract images in folders.

        """
        # Initialize the buffer
        self.__pBuffer = PersonsBuffer(video, buffer_size, buffer_overlap)

        # Initialize the writer for the outputs files
        self.__lWriter = LandmarkWriter(video, self.__pBuffer.get_fps(), pattern,
                                        usable=usable_value, csv=csv_value, folder=f_value)
        self.__lWriter.set_options(draw)

        # Initialize the landmark
        self.__landmarks = VideoLandmark()

    # -----------------------------------------------------------------------

    def launch_process(self):
        """Manage the process."""
        # Loop over the video
        while self.__pBuffer.eov:
            # Store the result of VideoBuffer.next()
            self.__pBuffer.next()

            # Initialize the list of points for the faces with FaceLandmark
            self.__landmarks.process(self.__pBuffer)

            # Launch the process of creation of the outputs
            self.__lWriter.process(self.__pBuffer)

            # Reset the output lists
            self.__pBuffer.clear()

        # Close the buffer
        self.__pBuffer.close()

    # -----------------------------------------------------------------------

