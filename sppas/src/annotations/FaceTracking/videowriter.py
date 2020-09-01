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

import os
import codecs
import cv2

from sppas.src.imgdata import sppasImageWriter

# ---------------------------------------------------------------------------


class sppasVideoWriter(object):
    """Write a video and optionally coordinates into files.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      contact@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2020  Brigitte Bigi

    """

    def __init__(self):
        """Create a new sppasVideoWriter instance.

        Write the given video in the given filename.
        Parts of each image can be extracted in separate image files and/or
        surrounded on the given image.
        Output video and images can be resized.

        """
        # Manage options and write images if needed
        self._img_writer = sppasImageWriter()
        # A dict with key=person identifier
        # if crop+video options then value is the cv2.VideoWriter()
        self._person_video_writers = dict()
        # A cv2.VideoWriter() for the tagged video
        # used if tag+video options
        self._tag_video_writer = None

        # Added options
        self._video = False
        self._folder = False
        self._fps = 25

    # -----------------------------------------------------------------------

    def set_fps(self, value):
        self._fps = int(value)

    # -----------------------------------------------------------------------

    def set_options(self, csv=None, tag=None, crop=None,
                    width=None, height=None,
                    video=None, folder=None):
        self._img_writer.set_options(csv, tag, crop, width, height)
        if video is not None:
            self._video = bool(video)
        if folder is not None:
            self._folder = bool(folder)

    # -----------------------------------------------------------------------

    def close(self):
        """Close all currently used cv2.VideoWriter()."""
        if self._tag_video_writer is not None:
            self._tag_video_writer.close()
        for person_id in self._person_video_writers:
            self._person_video_writers[person_id].close()

    # -----------------------------------------------------------------------

    def write(self, video_buffer, out_name,  pattern=""):
        """Save the image into file(s) depending on the options.

        Write all detected faces or only the one of a specific person.

        :param video_buffer: (sppasFacesVideoBuffer) The images and results to write
        :param out_name: (str) The output name for the folder and/or the video
        :param pattern: (str) Pattern to add to a cropped image filename

        """
        if out_name.endswith('.csv') is True:
            out_name = out_name[:-4]
        if self._img_writer.options.csv is True:
            self.write_csv_coords(video_buffer, out_name + ".csv")

        if self._img_writer.options.tag is True:
            self.write_tagged_video(video_buffer, out_name)

    # -----------------------------------------------------------------------

    def write_tagged_video(self, video_buffer, out_name):
        """Tag and save the video with colored squares at given coords.

        :param video_buffer: (sppasImage) The image to write
        :param out_name: (str) The filename of the output video file

        """
        iter_images = video_buffer.__iter__()
        for i in range(video_buffer.__len__()):
            image = next(iter_images)
            # Create the cv2.VideoWriter() if it wasn't already done.
            # An image is required to properly fix the video size.
            if self._tag_video_writer is None:
                self._tag_video_writer = self.__create_video_writer(out_name, "", image)

            self.__update_persons(video_buffer, i)
            all_faces = video_buffer.get_detected_faces(i)

            # Create the list of coordinates ranked by person
            coords = list()
            for known_person_id in self._person_video_writers:
                j = self.__get_person_index_from_id(
                    video_buffer.get_detected_faces(i),
                    known_person_id)
                if j == -1:
                    # this person is not in this image
                    coords.append(None)
                else:
                    coords.append(all_faces[j])

            # Tag the images with squares at the coords
            img = self._img_writer.tag_image(image, coords)
            self._tag_video_writer.write(img)

    # -----------------------------------------------------------------------

    def __update_persons(self, video_buffer, idx):
        """Update the list of known persons from the detected ones at idx."""
        all_persons = video_buffer.get_detected_persons(idx)

        # Sort the new person identifiers alphabetically
        persons_ids = sorted([p[0] for p in all_persons if p is not None])

        # add missing ones in our list of known persons
        for p in persons_ids:
            if p not in self._person_video_writers:
                self._person_video_writers[p] = None

    # -----------------------------------------------------------------------

    @staticmethod
    def __get_person_index_from_id(persons, person_id):
        for i, p in enumerate(persons):
            if p[0] == person_id:
                return i
        return -1

    # -----------------------------------------------------------------------

    def __create_video_writer(self, out_name, person_id, image):
        """Create a cv2.VideoWriter() for a person."""
        # Fix width and height of the video
        if self._img_writer.options.get_width() > 0 or self._img_writer.options.get_height() > 0:
            image = image.iresize(
                self._img_writer.options.get_width(),
                self._img_writer.options.get_height())
        width, height = image.size()

        # Fix the video filename
        if len(person_id) > 0:
            filename = out_name + "_" + person_id + ".mpg"
        else:
            filename = out_name + ".mpg"

        # Create a writer and add it to our dict
        w = cv2.VideoWriter(
            filename,
            cv2.VideoWriter_fourcc(*'MJPG'),
            self._fps,
            (width, height))
        return w

    # -----------------------------------------------------------------------

    def write_csv_coords(self, video_buffer, out_csv_name):
        """Write or append a list of coordinates in a CSV file.

        :param video_buffer: (sppasFacesVideoBuffer) The images and results to write
        :param out_csv_name: (str) The filename of the CSV file to write

        """
        mode = "w"
        if os.path.exists(out_csv_name) is True:
            mode = "a+"
        with codecs.open(out_csv_name, mode, encoding="utf-8") as fd:
            iter_images = video_buffer.__iter__()
            for i in range(video_buffer.__len__()):
                image = next(iter_images)
                begin_idx, end_idx = video_buffer.get_range()
                img_name = "img_{:06d}".format(begin_idx + i)

                # Get the results
                faces = video_buffer.get_detected_faces(i)
                persons = video_buffer.get_detected_persons(i)
                landmarks = video_buffer.get_detected_landmarks(i)
                for j in range(len(faces)):
                    self._img_writer.write_coords(fd, img_name, j+1, faces[j], sep=";")
                    if persons[j] is not None:
                        fd.write("{:s}".format(persons[j][0]))
                    else:
                        fd.write("unk")
                    fd.write(";")
                    if isinstance(landmarks[j], (tuple, list)) is True:
                        for coords in landmarks[j]:
                            fd.write("{:d};".format(coords.x))
                            fd.write("{:d};".format(coords.y))

                    fd.write("\n")
                if len(faces) == 0:
                    fd.write("{:s};".format(img_name))
                    fd.write("\n")
