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

    src.videodata.manager.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~

"""

from sppas.src.videodata.personsbuffer import PersonsBuffer
from sppas.src.videodata.videolandmark import VideoLandmark
from sppas.src.videodata.coordswriter import sppasVideoCoordsWriter
from sppas.src.videodata.videotaglfpc import VideoTagLFPC

# ---------------------------------------------------------------------------


class ManagerLFPC(object):
    """Class to manage a process.

    :author:       Florian Hocquet
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      contact@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2020  Brigitte Bigi

    """

    def __init__(self, video, buffer_size, overlap=0, draw=None, pattern="-person", tier=None,
                 v_value=False, f_value=False):
        """Create a new ManagerLFPC instance.

        :param video: (name of video file, image sequence, url or video stream,
        GStreamer pipeline, IP camera) The video to be processed.
        :param buffer_size: (int) The size of the buffer.
        from the previous buffer.
        :param draw: (str) The name of the draw you want to draw.
        :param pattern: (str) The pattern to use for the creation of the files.
        :param v_value: (boolean) If is True extract images in videos.
        :param f_value: (boolean) If is True extract images in folders.

        """
        # Initialize the buffer
        self.__pBuffer = PersonsBuffer(video, buffer_size, overlap)

        # Initialize the writer for the outputs files
        self.__coords_writer = sppasVideoCoordsWriter(video, self.__pBuffer.get_fps(), pattern,
                                                      video=v_value, folder=f_value)

        # Initialize options of the writer
        self.__coords_writer.set_draw(draw)

        # Initialize the LFPC tagger
        self.__lfpc_Tagger = VideoTagLFPC()

        # Initialize the landmark
        self.__landmarks = VideoLandmark()

        # The list of transcription
        self.__transcription = list()
        self.__store_syllable(tier)

    # -----------------------------------------------------------------------

    def launch_process(self):
        """Manage the process."""
        # Loop over the video
        while self.__pBuffer.eov:

            # Store the result of VideoBuffer.next()
            self.__pBuffer.next()

            # Initialize the list of points for the faces with FaceLandmark
            self.__landmarks.process(self.__pBuffer)

            # Launch the Tag process
            self.__lfpc_tagging()

            # Launch the process of creation of the outputs
            self.__coords_writer.process(self.__pBuffer)

            # Reset the output lists
            self.__pBuffer.clear()

        # Close the buffer
        self.__pBuffer.close()

    # -----------------------------------------------------------------------

    def __store_syllable(self, tier):
        """Store the syllable from the tier object.

        :param tier: (sppasTier)

        """
        # The previous code
        prev_end_time = 0
        prev_end_frame = 0
        prev_lpc_code = str()

        # For each LPC-syllable of the tier
        for ann in tier:
            # Get start time and end time in seconds
            start_time, end_time = self.__get_interval_time(ann)

            # Get the string of the C-V key codes
            key_codes = ann.get_best_tag().get_content()

            # There were a gap between the previous syllable and the current one
            if start_time > prev_end_time:
                pass

            # If the code is valid
            if len(key_codes) == 2:
                # Store the duration of the syllable
                duration = end_time - start_time
                # Deduce the number of frames for the syllable
                nb_frame = int(duration * self.__pBuffer.get_fps())
                # Deduce the ID of the first frame of the syllable
                first_frame = int(start_time / self.__pBuffer.get_fps())

                # If there is a blank between the previous syllable and the current one
                if prev_end_frame + 1 != first_frame:
                    # Get the number of blank
                    nb_none = (first_frame - prev_end_frame) - 1
                    # Fill the blank with None
                    for frame in range(nb_none):
                        self.__transcription.append([prev_lpc_code, key_codes, frame, nb_none])

                # Store the syllable in the transcription list
                for frame in range(nb_frame):
                    self.__transcription.append(key_codes)

            # Set the new previous code
            prev_end_time = end_time
            prev_end_frame = len(self.__transcription) - 1
            prev_lpc_code = self.__transcription[prev_end_frame]

    # -----------------------------------------------------------------------

    def __fill_blanks(self):
        """Fill the blanks."""

    # -----------------------------------------------------------------------

    def __lfpc_tagging(self):
        """Call the tagging process for each syllable."""
        iterator = self.__pBuffer.__iter__()
        for frameID in range(len(self.__pBuffer)):
            # If image in the overlap continue
            if frameID < self.__pBuffer.get_overlap():
                continue

            # Get the image
            frame = next(iterator)

            # Get the LPC code
            lpc_code = self.__transcription[frameID + self.__pBuffer.get_frame() - self.__pBuffer.get_size()]

            # Get the landmark points
            landmarks = self.__pBuffer.get_landmark(0, frameID)

            if isinstance(lpc_code, str) and landmarks is not None:
                # Tag the image with the LPC code
                self.__lfpc_Tagger.tag(frame, lpc_code, landmarks)

            if isinstance(lpc_code, list) and landmarks is not None:
                # Tag the image with the LPC code
                self.__lfpc_Tagger.tag_blank(frame, lpc_code, landmarks)

    # -----------------------------------------------------------------------

    @staticmethod
    def __get_interval_time(ann):
        """Return the interval in time of the given annotation.

        :param ann: (sppasAnnotation)
        :returns: (float, float) The interval includes the vagueness.

        """
        # location of the interval (sppasLocation instance)
        location = ann.get_location()

        # Localization of the interval (sppasPoint instances)
        start_loc = location.get_lowest_localization()
        end_loc = location.get_highest_localization()

        # Time values with their vagueness added
        start_time = start_loc.get_midpoint()
        if start_loc.get_radius() is not None:
            start_time -= start_loc.get_radius()
        end_time = end_loc.get_midpoint()
        if end_loc.get_radius() is not None:
            end_time += end_loc.get_radius()

        return float(start_time), float(end_time)

    # -----------------------------------------------------------------------

