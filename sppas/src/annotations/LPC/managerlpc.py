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

from math import ceil

from sppas.src.videodata import PersonsBuffer
from sppas.src.videodata import VideoLandmark
from sppas.src.videodata import sppasVideoCoordsWriter
from sppas.src.annotations.LPC.videotaglpc import VideoTagLFPC

# ---------------------------------------------------------------------------


class ManagerLFPC(object):
    """Class to manage a process.

    :author:       Florian Hocquet
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      contact@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2020  Brigitte Bigi

    """

    def __init__(self, video, tier=None, buffer_size=200, overlap=0, draw=None, pattern="-person",
                 usable=False, v_value=False, f_value=False):
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
        # Initialize the PersonBuffer
        # Because the process have to store the landmark
        self.__pBuffer = PersonsBuffer(video, buffer_size, overlap)

        # Initialize the writer for the outputs files
        self.__coords_writer = sppasVideoCoordsWriter(video, self.__pBuffer.get_fps(), pattern,
                                                      usable=usable, video=v_value, folder=f_value)

        # Initialize options of the writer
        self.__coords_writer.set_options(draw=draw)

        # Initialize the LFPC tagger
        self.__lfpc_Tagger = VideoTagLFPC()

        # Initialize the landmark
        self.__landmarks = VideoLandmark()

        self.__tier = False
        if tier is not None:
            # The list of lpc_codes
            self.__tier = True
            self.__img_codes = list()
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

            if self.__tier is True:
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
        prev_lpc_code = "0-0"

        # For each LPC-syllable of the tier
        for ann in tier:
            # Get start time and end time in seconds
            start_time, end_time = self.__get_interval_time(ann)
            # Get the string of the C-V key codes
            key_codes = ann.get_best_tag().get_content()

            # If the code is valid
            if len(key_codes) == 3:
                # Store the duration of the syllable
                duration = end_time - start_time
                # Deduce the number of frames for the syllable
                nb_frame = ceil(duration * self.__pBuffer.get_fps())
                # Deduce the ID of the first frame of the syllable
                first_frame = ceil(start_time * self.__pBuffer.get_fps())

                # If there were a gap between the previous syllable and the current one
                if prev_end_frame + 1 != first_frame:
                    # Get the number of blank
                    nb_none = (first_frame - prev_end_frame) - 1
                    time = start_time - prev_end_time < 0.5
                    if time is True:
                        # Fill the blank with the prev and the current lpc codes
                        for frame in range(nb_none):
                            self.__img_codes.append((prev_lpc_code, key_codes, frame, nb_none + 1))
                    else:
                        # Fill the blank with None
                        for frame in range(nb_none):
                            self.__img_codes.append(None)

                # Store the syllable in the transcription list
                for frame in range(nb_frame):
                    self.__img_codes.append(key_codes)

            # Set the new previous code
            prev_end_time = end_time
            prev_end_frame = len(self.__img_codes) - 1
            prev_lpc_code = self.__img_codes[prev_end_frame]

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

            # Recover the part of the lpc_code that is interesting
            # from 0 to 100, then from 100 to 200...
            part = int(frameID + self.__pBuffer.get_frame() - self.__pBuffer.get_size())
            # Get the LPC code
            try:
                lpc_code = self.__img_codes[part]
                # Get the landmark points
                landmarks = self.__pBuffer.get_landmark(0, frameID)

                if landmarks is not None and lpc_code is not None:
                    if isinstance(lpc_code, str):
                        # Tag the image with the LPC code
                        self.__lfpc_Tagger.tag(frame, lpc_code, landmarks)

                    else:
                        # Tag the transition with two LPC code
                        self.__lfpc_Tagger.tag_blank(frame, lpc_code, landmarks)
            except IndexError:
                # The len of the lpc codes list is smaller than
                # the number of frame of the input video
                pass

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
