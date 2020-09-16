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

    src.annotations.FaceTracking.videotrackwriter.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Requires the "video" feature of SPPAS.
    Write a video with the results of face detection and face landmark.

"""

import os
import codecs
import cv2
import shutil
import logging

from sppas.src.config import annots
from sppas.src.exceptions import NegativeValueError, IntervalRangeException
from sppas.src.exceptions import sppasExtensionWriteError
from sppas.src.imgdata import sppasImageCoordsWriter
from sppas.src.imgdata import image_extensions
from sppas.src.videodata import video_extensions
from sppas.src.videodata import sppasVideoWriter

# ---------------------------------------------------------------------------


class sppasVideoCoordsWriter(object):
    """Write a video, a set of images and/or coordinates into files.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      contact@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2020  Brigitte Bigi

    There are 3 main solutions to write the result of face tracking:

        1. CSV: coordinates of the faces into a spreadsheet
        2. video
        3. folder with images

    For 2 and 3, there are 2 options - at least one has to be selected:

        1. tag: surround each detected face in the original image
        2. crop: create one image for each detected face

    """

    def __init__(self):
        """Create a new sppasVideoCoordsWriter instance.

        Parts of each image can be extracted in separate image files and/or
        surrounded on the given image.
        Output video and images can be resized.

        """
        # Manage options and write images if needed
        self._img_writer = sppasImageCoordsWriter()
        # A dict with key=person identifier
        # if crop+video options then value is a sppasVideoWriter()
        self._person_video_writers = dict()
        # A sppasVideoWriter() for the tagged video - if tag+video options.
        self._tag_video_writer = None

        # Added options compared to the image writer
        self._video = False     # save results in video file(s)
        self._folder = False    # save results as images in a folder
        self._fps = 25          # default video framerate

        # Output file extensions are initially set to SPPAS default values
        self.__video_ext = annots.video_extension
        self.__image_ext = annots.image_extension

    # -----------------------------------------------------------------------
    # Getters and setters for the options
    # -----------------------------------------------------------------------

    def get_video_extension(self):
        """Return the extension for video files."""
        return self.__video_ext

    # -----------------------------------------------------------------------

    def set_video_extension(self, ext):
        """Set the extension of video files."""
        ext = str(ext)
        if ext.startswith(".") is False:
            ext = "." + ext
        if ext not in video_extensions:
            raise sppasExtensionWriteError(ext)

        self.__video_ext = ext

    # -----------------------------------------------------------------------

    def get_image_extension(self):
        """Return the extension for image files."""
        return self.__image_ext

    # -----------------------------------------------------------------------

    def set_image_extension(self, ext):
        """Set the extension of image files."""
        ext = str(ext)
        if ext.startswith(".") is False:
            ext = "." + ext
        if ext not in image_extensions:
            raise sppasExtensionWriteError(ext)

        self.__image_ext = ext

    # -----------------------------------------------------------------------

    def get_fps(self):
        """Return the defined fps value to write video files."""
        return self._fps

    # -----------------------------------------------------------------------

    def set_fps(self, value):
        """Fix the framerate of the output video.

        :param value: (int) frame per seconds
        :raise: NegativeValueError, IntervalRangeError

        """
        # if the value isn't correct, sppasVideoWriter() will raise an exc.
        w = sppasVideoWriter()
        w.set_fps(value)
        self._fps = value

    # -----------------------------------------------------------------------

    def get_csv_output(self):
        """Return True if coordinates will be saved in a CSV file."""
        return self._img_writer.options.get_csv_output()

    # -----------------------------------------------------------------------

    def get_video_output(self):
        """Return True if results will be saved in a VIDEO file."""
        return self._video

    # -----------------------------------------------------------------------

    def get_folder_output(self):
        """Return True if results will be saved in a folder of image files."""
        return self._folder

    # -----------------------------------------------------------------------

    def get_tag_output(self):
        """Return True if faces of the images will be surrounded."""
        return self._img_writer.options.get_tag_output()

    # -----------------------------------------------------------------------

    def get_crop_output(self):
        """Return True if the option to crop faces is enabled."""
        return self._img_writer.options.get_crop_output()

    # -----------------------------------------------------------------------

    def get_output_width(self):
        """Return the width of the output image files."""
        return self._img_writer.options.get_width()

    # -----------------------------------------------------------------------

    def get_output_height(self):
        """Return the height of the outputs files."""
        return self._img_writer.options.get_height()

    # -----------------------------------------------------------------------

    def set_options(self, csv=None, tag=None, crop=None,
                    width=None, height=None,
                    video=None, folder=None):
        """Set any/some/all of the options."""
        self._img_writer.set_options(csv, tag, crop, width, height)
        if video is not None:
            self._video = bool(video)
        if folder is not None:
            self._folder = bool(folder)

    # -----------------------------------------------------------------------
    # Write into CSV, VIDEO or IMAGES
    # -----------------------------------------------------------------------

    def get_image_size(self, image):
        """Return the size of the image depending on the image and options."""
        return image.get_proportional_size(
            width=self._img_writer.options.get_width(),
            height=self._img_writer.options.get_height()
        )

    # -----------------------------------------------------------------------

    def close(self):
        """Close all currently used sppasVideoWriter().

        It has to be invoked when writing buffers is finished in order to
        release the video writers.

        """
        if self._tag_video_writer is not None:
            self._tag_video_writer.close()
            self._tag_video_writer = None

        for person_id in self._person_video_writers:
            video_writer = self._person_video_writers[person_id]
            if video_writer is not None:
                video_writer.close()
            self._person_video_writers[person_id] = None
        self._person_video_writers = dict()

    # -----------------------------------------------------------------------

    def write(self, video_buffer, out_name, pattern=""):
        """Save the result into file(s) depending on the options.

        The out_name is a base name, its extension is ignored and replaced by
        the one(s) defined in this class.

        :param video_buffer: (sppasFacesVideoBuffer) The images and results to write
        :param out_name: (str) The output name for the folder and/or the video
        :param pattern: (str) Pattern to add to cropped image/video filename(s)
        :return: list of newly created file names

        """
        new_files = list()

        # Remove any existing extension, and ignore it!
        fn, _ = os.path.splitext(out_name)
        out_name = fn

        # Write results in CSV format
        if self._img_writer.options.csv is True:
            out_csv_name = out_name + ".csv"
            self.write_csv_coords(video_buffer, out_csv_name)
            new_files.append(out_csv_name)

        # Write results in VIDEO format
        if self._video is True:
            new_video_files = self.write_video(video_buffer, out_name, pattern)
            if len(new_video_files) > 1:
                logging.info("{:d} video files created".format(len(new_video_files)))
            new_files.extend(new_video_files)

        # Write results in IMAGE format
        if self._folder is True:
            new_image_files = self.write_folder(video_buffer, out_name, pattern)
            if len(new_image_files) > 1:
                logging.info("{:d} image files created".format(len(new_image_files)))
            # Too many files are created, they can't be added to the GUI...
            # TODO: Find a solution in the GUI to deal with a huge nb of files
            # then un-comment the next line
            # new_files.extend(new_image_files)

        return new_files

    # -----------------------------------------------------------------------

    def write_video(self, video_buffer, out_name, pattern):
        """Save the result in video format.

        :param video_buffer: (sppasImage) The image to write
        :param out_name: (str) The filename of the output video file
        :param pattern: (str) Pattern to add to cropped video filename(s)
        :return: list of newly created video file names

        """
        new_files = list()
        if self._img_writer.options.tag is False and self._img_writer.options.crop is False:
            logging.info("Video option is enabled but no tag nor crop. "
                         "Nothing to do.")
            return new_files

        iter_images = video_buffer.__iter__()
        for i in range(video_buffer.__len__()):
            image = next(iter_images)
            b, _ = video_buffer.get_buffer_range()

            # Update the list of known persons from the detected ones
            self.__update_persons(video_buffer, i)

            # Create the list of coordinates ranked by person
            coords = self.__get_coordinates(video_buffer, i)

            if self._img_writer.options.tag is True:

                # Create the sppasVideoWriter() if it wasn't already done.
                # An image is required to properly fix the video size.
                if self._tag_video_writer is None:
                    self._tag_video_writer, fn = self.__create_video_writer(out_name, "", image)
                    new_files.append(fn)

                # Tag&write the image with squares at the coords
                img = self._img_writer.tag_image(image, coords)
                self._tag_video_writer.write(img)

            if self._img_writer.options.crop is True:

                # Browse through the persons and their coords to crop the image
                for j, known_person_id in enumerate(self._person_video_writers):
                    # Create the sppasVideoWriter of this person if necessary
                    if self._person_video_writers[known_person_id] is None:
                        self._person_video_writers[known_person_id], fn = self.__create_video_writer(out_name, known_person_id, image, video_buffer, pattern)
                        new_files.append(fn)
                        img = image.blank_image()
                        for x in range(b + i):
                            self._person_video_writers[known_person_id].write(img)
                    if coords[j] is not None:
                        # Crop the given image to the coordinates
                        img = image.icrop(coords[j])
                    else:
                        # This person is not in the image.
                        # Create an empty image to add it into the video.
                        img = image.blank_image()

                    # Add the image to the video
                    self._person_video_writers[known_person_id].write(img)

        return new_files

    # -----------------------------------------------------------------------

    def write_folder(self, video_buffer, out_name, pattern=""):
        """Save the result in image format into a folder.

        :param video_buffer: (sppasImage) The image to write
        :param out_name: (str) The folder name of the output image files
        :param pattern: (str) Pattern to add to a cropped image filename

        """
        new_files = list()
        # Create the directory with all results
        if os.path.exists(out_name) is False:
            os.mkdir(out_name)

        # Create a folder to save results of this buffer
        begin_idx, end_idx = video_buffer.get_buffer_range()
        folder = os.path.join(out_name, "{:06d}".format(begin_idx))
        if os.path.exists(folder) is True:
            shutil.rmtree(folder)
        os.mkdir(folder)

        iter_images = video_buffer.__iter__()
        for i in range(video_buffer.__len__()):
            image = next(iter_images)
            img_name = self.__image_name(begin_idx + i)

            # Update the list of known persons from the detected ones
            self.__update_persons(video_buffer, i)
            # Create the list of coordinates ranked by person
            # to ensure the colors are respected.
            coords = self.__get_coordinates(video_buffer, i)

            if self._img_writer.options.tag is True:

                # Tag&Save the image
                img = self._img_writer.tag_image(image, coords)
                out_iname = os.path.join(folder, img_name + self.__image_ext)
                img.write(out_iname)
                new_files.append(out_iname)

            if self._img_writer.options.crop is True:

                # Browse through the persons and their coords to crop the image
                for j, known_person_id in enumerate(self._person_video_writers):
                    # Create the image filename
                    iname = img_name + "_" + known_person_id + pattern + self.__image_ext
                    out_iname = os.path.join(folder, iname)

                    if coords[j] is not None:
                        # Crop the given image to the coordinates and
                        # resize only if the option width or height is enabled
                        img = self._img_writer.crop_and_size_image(image, coords[j])
                        # Add the image to the folder
                        img.write(out_iname)
                        new_files.append(out_iname)

        return new_files

    # -----------------------------------------------------------------------
    
    def __get_coordinates(self, video_buffer, i):
        """Return the list of coords of detected faces ranked by person."""
        all_faces = video_buffer.get_detected_faces(i)
        coords = list()
        for known_person_id in self._person_video_writers:
            j = self.__get_person_index_from_id(
                video_buffer.get_detected_persons(i),
                known_person_id)
            if j == -1:
                # this person is not in this image
                coords.append(None)
            else:
                coords.append(all_faces[j])

        return coords
    
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

    def __create_video_writer(self, out_name, person_id, image, video_buffer=None, pattern=""):
        """Create a sppasVideoWriter() for a person."""
        # Fix width and height of the video
        w, h = self.get_image_size(image)

        # Fix the video filename
        filename = self.__out_name_pattern(out_name, person_id, pattern) + self.__video_ext
        logging.debug("Create a video writer {:s}. Size {:d}, {:d}"
                      "".format(filename, w, h))

        # Create a writer and add it to our dict
        try:
            writer = sppasVideoWriter()
            writer.set_size(w, h)
            writer.set_fps(self._fps)
            writer.set_aspect("extend")
            writer.open(filename)
        except Exception as e:
            logging.error("OpenCV failed to open the VideoWriter for file "
                          "{}: {}".format(filename, str(e)))
            return None

        return writer, filename

    # -----------------------------------------------------------------------

    @staticmethod
    def __out_name_pattern(out_name, person_id, pattern):
        """Return the filename. """
        if len(pattern) > 0 and out_name.endswith(pattern):
            # the out_name is already including the pattern
            out_name = out_name[:len(out_name)-len(pattern)]

        if len(person_id) == 0:
            return "{:s}{:s}".format(out_name, pattern)

        return "{:s}_{:s}{:s}".format(out_name, person_id, pattern)

    # -----------------------------------------------------------------------

    def write_csv_coords(self, video_buffer, out_csv_name):
        """Write or append a list of coordinates in a CSV file.

        :param video_buffer: (sppasFacesVideoBuffer) The images and results to write
        :param out_csv_name: (str) The filename of the CSV file to write

        """
        # Get information about the buffer
        begin_idx, end_idx = video_buffer.get_buffer_range()
        buffer_nb = end_idx // video_buffer.get_buffer_size()

        # Open or re-open the CSV file to append the new results
        mode = "w"
        if os.path.exists(out_csv_name) is True:
            mode = "a+"

        with codecs.open(out_csv_name, mode, encoding="utf-8") as fd:
            for i in range(video_buffer.__len__()):
                img_name = self.__image_name(begin_idx + i)

                # Update the list of known persons from the detected ones
                self.__update_persons(video_buffer, i)

                # Get the results
                faces = video_buffer.get_detected_faces(i)
                persons = video_buffer.get_detected_persons(i)
                landmarks = video_buffer.get_detected_landmarks(i)

                # Write the results
                for j in range(len(faces)):
                    fd.write("{:d};".format(buffer_nb))
                    self._img_writer.write_coords(fd, img_name, j+1, faces[j], sep=";")
                    if persons[j] is not None:
                        fd.write("{:s}".format(persons[j][0]))
                    else:
                        fd.write("undeterminated")
                    fd.write(";")
                    if isinstance(landmarks[j], (tuple, list)) is True:
                        for coords in landmarks[j]:
                            fd.write("{:d};".format(coords.x))
                            fd.write("{:d};".format(coords.y))

                    fd.write("\n")
                if len(faces) == 0:
                    fd.write("{:s};".format(img_name))
                    fd.write("\n")

    # -----------------------------------------------------------------------

    @staticmethod
    def __image_name(idx):
        """Return an image name from its index."""
        return "img_{:06d}".format(idx)

