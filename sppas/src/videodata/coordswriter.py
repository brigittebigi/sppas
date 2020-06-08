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

import cv2
from cv2 import VideoWriter_fourcc
import numpy as np
import os
import csv
import shutil
import glob

from sppas.src.imagedata.imageutils import crop, surrond_square, resize, portrait, draw_points
from sppas.src.imagedata.coordinates import Coordinates

# ---------------------------------------------------------------------------


class sppasVideoCoordsWriter(object):
    """Class to write outputs files.

    :author:       Florian Hocquet
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      contact@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2020  Brigitte Bigi

    """

    # The framing options
    FRAMING = ["face", "portrait"]

    # The mode options
    MODE = ["full", "crop"]

    # The draw options
    DRAW = ["circle", "ellipse", "square"]

    def __init__(self, path, fps, pattern, csv=False, video=False, folder=False):
        """Create a new sppasImgCoordsWriter instance.

        :param path: (str) The path of the video.
        :param fps: (int) The FPS of the video.
        :param pattern: (str) The pattern to use for the creation of the files.
        :param csv: (boolean) If is True extract images in csv file.
        :param video: (boolean) If is True extract images in a video.
        :param folder: (boolean) If is True extract images in a folder.

        """
        # A list of csv files
        self.__csv_output = list()
        # A list of video writers
        self.__video_output = list()
        # A list of video writers
        self.__base_output = list()
        # A list of folders
        self.__folder_output = list()

        # The path and the name of the video
        self.__path, self.__video_name = self.__path_video(path)

        # The FPS of the video
        fps = int(fps)
        self.__fps = fps

        # The dictionary of options
        self.__output = {"csv": False, "video": False, "folder": False}

        # The framing to use, face or portrait
        self.__framing = None
        # The mode to use, full or crop
        self.__mode = None
        # The shape to draw, circle, ellipse or rectangle
        self.__draw = None

        # The width you want for the outputs files
        self.__width = None
        # The height you want for the outputs files
        self.__height = None

        # Initialize outputs files
        self.__init_outputs(csv, video, folder)

        # The index of the current image
        self.__number = 0

        # The pattern to use for the outputs files
        self.__pattern = str()
        self.set_pattern(pattern)

        # Reset outputs files
        self.__reset()

    # -----------------------------------------------------------------------

    def __reset(self):
        """Reset outputs files before using the writers."""
        # Delete csv files if already exists
        csv_path = glob.glob(self.__cfile_path())
        for f in csv_path:
            if os.path.exists(f) is True:
                os.remove(f)

        # Delete video files if already exists
        video_path = glob.glob(self.__vfile_path())
        for f in video_path:
            if os.path.exists(f) is True:
                os.remove(f)

        # Delete video files if already exists
        usable_path = glob.glob(self.__base_path())
        for f in usable_path:
            if os.path.exists(f) is True:
                os.remove(f)

        # Delete folder if already exists
        folder_path = glob.glob(self.__ffile_path())
        for f in folder_path:
            if os.path.exists(f) is True:
                shutil.rmtree(f)

    # -----------------------------------------------------------------------

    def __init_outputs(self, csv, video, folder):
        """Init the values of the outputs options.

        :param csv: (boolean) If True extract images in csv file.
        :param video: (boolean) If True extract images in a video.
        :param folder: (boolean) If True extract images in a folder.

        """
        # If csv is True set the csv outputs files to True
        if csv is True:
            self.set_csv(True)

        # If video is True set the video outputs files to True
        if video is True:
            self.set_video(True)

        # If folder is True set the folders outputs to True
        if folder is True:
            self.set_folder(True)

    # -----------------------------------------------------------------------

    def __path_video(self, path):
        """Return the path and the name of the video.

        :param path: (string) The path of the video.

        """
        if isinstance(path, str) is False:
            raise TypeError

        # Store the path of the video
        path = os.path.realpath(path)

        # Add the os separator to the path
        video_path = os.path.dirname(path) + os.sep

        # Store the name and the extension of the video
        video = os.path.basename(path)

        # Store separately the name and the extension of the video
        video_name, extension = os.path.splitext(video)

        # Return the path and the name of the video
        return video_path, video_name

    # -----------------------------------------------------------------------

    def __cfile_path(self, index=None):
        """Return the complete path of the csv file.

        :param index: (int) The int to add is the name of the csv file.

        """
        if index is not None:
            index = int(index)
            if isinstance(index, int) is False:
                raise TypeError

        if index is None:
            path = self.__path + self.__video_name + "_*" + self.get_pattern() + ".csv"
        else:
            path = self.__path + self.__video_name + "_" + str(index) + self.get_pattern() + ".csv"
        return path

    # -----------------------------------------------------------------------

    def __base_path(self, index=None):
        """Return the complete path of the video file.

        :param index: (int) The int to add is the name of the video file.

        """
        if index is not None:
            index = int(index)
            if isinstance(index, int) is False:
                raise TypeError

        if index is None:
            path = self.__path + self.__video_name + "_*" + self.get_pattern() + "_usable" + ".avi"
        else:
            path = self.__path + self.__video_name + "_" + str(index) + self.get_pattern() + "_usable" + ".avi"
        return path

    # -----------------------------------------------------------------------

    def __vfile_path(self, index=None):
        """Return the complete path of the video file.

        :param index: (int) The int to add is the name of the video file.

        """
        if index is not None:
            index = int(index)
            if isinstance(index, int) is False:
                raise TypeError

        if index is None:
            path = self.__path + self.__video_name + "_*" + self.get_pattern() + ".avi"
        else:
            path = self.__path + self.__video_name + "_" + str(index) + self.get_pattern() + ".avi"
        return path

    # -----------------------------------------------------------------------

    def __ffile_path(self, index=None):
        """Return the complete path of the folder.

        :param index: (int) The int to add is the name of the folder.

        """
        if index is not None:
            index = int(index)
            if isinstance(index, int) is False:
                raise TypeError

        if index is None:
            path = self.__path + "*" + self.get_pattern() + "/"
        else:
            path = self.__path + str(index) + self.get_pattern() + "/"
        return path

    # -----------------------------------------------------------------------

    def get_csv(self):
        """Return True if the option csv is enabled."""
        return self.__output["csv"]

    # -----------------------------------------------------------------------

    def set_csv(self, value):
        """Enable or not the csv output.

        :param value: (boolean) True to enabled and False to disabled.

        """
        value = bool(value)
        if isinstance(value, bool) is False:
            raise TypeError
        self.__output["csv"] = value

    # -----------------------------------------------------------------------

    def get_video(self):
        """Return True if the option video is enabled."""
        return self.__output["video"]

    # -----------------------------------------------------------------------

    def set_video(self, value):
        """Enable or not the video output.

        :param value: (boolean) True to enabled and False to disabled.

        """
        value = bool(value)
        if isinstance(value, bool) is False:
            raise TypeError
        self.__output["video"] = value

    # -----------------------------------------------------------------------

    def get_folder(self):
        """Return True if the option folder is enabled."""
        return self.__output["folder"]

    # -----------------------------------------------------------------------

    def set_folder(self, value):
        """Enable or not the folder output.

        :param value: (boolean) True to enabled and False to disabled.

        """
        value = bool(value)
        if isinstance(value, bool) is False:
            raise TypeError
        self.__output["folder"] = value

    # -----------------------------------------------------------------------

    def get_framing(self):
        """Return the framing."""
        return self.__framing

    # -----------------------------------------------------------------------

    def set_framing(self, value):
        """Set the framing.

        :param value: (str) The framing to use on each image of the buffer,
        face or portrait.

        """
        if isinstance(value, str) is False and value is not None:
            raise TypeError
        if value not in sppasVideoCoordsWriter.FRAMING and value is not None:
            raise ValueError
        self.__framing = value

    # -----------------------------------------------------------------------

    def get_mode(self):
        """Return the mode."""
        return self.__mode

    # -----------------------------------------------------------------------

    def set_mode(self, value):
        """Set the mode.

        :param value: (str) The mode to use on each image of the buffer,
        full or crop.

        """
        if isinstance(value, str) is False and value is not None:
            raise TypeError
        if value not in sppasVideoCoordsWriter.MODE and value is not None:
            raise ValueError
        self.__mode = value

    # -----------------------------------------------------------------------

    def get_draw(self):
        """Return the draw."""
        return self.__draw

    # -----------------------------------------------------------------------

    def set_draw(self, value):
        """Set the draw.

        :param value: (str) The shape to draw on each image of the buffer,
        circle, ellipse or square.

        """
        if isinstance(value, str) is False and value is not None:
            raise TypeError
        if value not in sppasVideoCoordsWriter.DRAW and value is not None:
            raise ValueError
        self.__draw = value

    # -----------------------------------------------------------------------

    def get_width(self):
        """Return the width of the outputs files."""
        return self.__width

    # -----------------------------------------------------------------------

    def set_width(self, value):
        """Set the width of outputs.

        :param value: (int) The width of outputs images and videos.

        """
        if isinstance(value, int) is False:
            raise TypeError
        if value < -1 or value > 15360:
            raise ValueError
        self.__width = value

    # -----------------------------------------------------------------------

    def get_height(self):
        """Return the height of the outputs files."""
        return self.__height

    # -----------------------------------------------------------------------

    def set_height(self, value):
        """Set the height of outputs.

        :param value: (int) The height of outputs images and videos.

        """
        if isinstance(value, int) is False:
            raise TypeError
        if value < -1 or value > 8640:
            raise ValueError
        self.__height = value

    # -----------------------------------------------------------------------

    def get_size(self):
        """Return the size of the outputs files."""
        return self.__width, self.__height

    # -----------------------------------------------------------------------

    def set_size(self, width, height):
        """Set the size of outputs.

        :param width: (int) The width of outputs images and videos.
        :param height: (int) The height of outputs images and videos.

        """
        self.set_width(width)
        self.set_height(height)

    # -----------------------------------------------------------------------

    def get_pattern(self):
        """Return the pattern of the outputs files."""
        return self.__pattern

    # -----------------------------------------------------------------------

    def set_pattern(self, value):
        """Set the pattern of the outputs files.

        :param value: (str) The pattern in all the outputs files.

        """
        if isinstance(value, str) is False:
            raise TypeError
        self.__pattern = value

    # -----------------------------------------------------------------------

    def process(self, buffer):
        """Browse the buffer.

        :param buffer: (VideoBuffer) The buffer which contains images.

        """
        # Verify the options
        self.__verify_options(buffer)

        # Initialise the iterator
        iterator = buffer.__iter__()

        # Loop over the buffer
        for frameID in range(0, buffer.__len__()):

            # If image in the overlap continue
            if frameID < buffer.get_overlap():
                continue

            # Go to the next frame
            img = next(iterator)

            image1 = img.copy()
            image2 = img.copy()

            # Loop over the persons
            for i in range(buffer.nb_persons()):

                # If tracking process has been used
                if buffer.is_tracked() is True:
                    # If any visage has been detected continue
                    if buffer.get_coordinate(i, frameID) is None:
                        continue

                # If landmark process has been used
                elif buffer.is_landmarked() is True:
                    # If any visage has been detected continue
                    if buffer.get_landmark(i, frameID) is None:
                        continue

                if self.__width != -1 and self.__height != -1:
                    # Write the usable output videos
                    self.__manage_usable(buffer, image1, i, frameID)

                # If any option is enabled use only the csv outputs files
                option = self.__framing is None and self.__mode is None and self.__draw is None
                if option is False and \
                        self.get_csv() is True and self.get_video() is True and self.get_folder() is True:
                    # Write the outputs
                    self.__manage_verification(buffer, image2, i, frameID)

            # Increment the number of image by 1
            self.__number += 1

    # -----------------------------------------------------------------------

    def __verify_options(self, buffer):
        """Verify the option values.

        :param buffer: (VideoBuffer) The buffer which contains images.

        """
        # If only mode has been setted and equal to full
        if self.get_mode() == "full" and self.get_framing() is None:
            # Set framing to face
            self.set_framing("face")

        # If only framing has been setted and equal to face
        if self.get_framing() == "face" and self.get_mode() is None:
            # Set mode to full
            self.set_mode("full")

        # If only mode has been setted and equal to crop
        if self.get_mode() == "crop" and self.get_framing() is None:
            # Set framing to portrait
            self.set_framing("portrait")

        # If only framing has been setted and equal to portrait
        if self.get_framing() == "portrait" and self.get_mode() is None:
            # Set mode to crop
            self.set_mode("crop")

        # If option are the same as the one for the usable output videos
        if self.get_framing() == "portrait" and self.get_mode() == "crop" and \
                self.get_draw() is None or buffer.is_landmarked() is False:
            # Set output video to False
            self.set_video(False)

        # If only landmark process has been used
        if buffer.is_landmarked() is True and buffer.is_tracked() is False:
            # Set the csv output to False
            self.set_csv(False)

    # -----------------------------------------------------------------------

    def __manage_usable(self, buffer, image, index, frameID):
        """Manage the creation of one of the usable output video.

        :param buffer: (VideoBuffer) The buffer which contains images.
        :param image: (numpy.ndarray) The image to be processed.
        :param index: (int) The ID of the person.
        :param frameID: (int) The ID of the image in the buffer.

        """
        # If tracking process has been used
        if buffer.is_tracked() is True:
            # Create the usable image
            image = self.__apply_usable(buffer, image, index, frameID)

        # Store the width and the height of the image
        (h, w) = image.shape[:2]

        # Create the usable output videos
        self.__out_base(buffer.nb_persons(), w, h)

        # Write the image in usable output video
        self.__write_base(image, index)

    # -----------------------------------------------------------------------

    def __apply_usable(self, buffer, image, index, frameID):
        """Modify the image for the usable output video.

        :param buffer: (VideoBuffer) The buffer which contains images.
        :param image: (numpy.ndarray) The image to be processed.
        :param index: (int) The ID of the person.
        :param frameID: (int) The ID of the image in the buffer.

        """
        # Copy the Coordinates object in the buffer
        coord = buffer.get_coordinate(index, frameID).copy()

        # Make portrait with coordinates
        portrait(coord)

        # Adjust the coordinate
        self.__adjust(image, coord)

        # Crop the image
        base_image = crop(image, coord)

        # Resize the image
        base_image = self.__resize(base_image)

        return base_image

    # -----------------------------------------------------------------------

    def __manage_verification(self, buffer, image, index, frameID):
        """Manage the creation of the verification outputs.

        :param buffer: (VideoBuffer) The buffer which contains images.

        """
        if self.get_mode() != "full" and self.get_mode() is not None or \
                self.get_mode() is not None and self.get_framing() is not None and self.get_draw() is None:
            # Copy the image
            image = image.copy()

        # If the landmark process has been used
        if buffer.is_landmarked() is True:
            # Apply modification
            self.__apply_landmarked(buffer, image, index, frameID)

        # If the tracking process has been used
        if buffer.is_tracked() is True:
            # Aplly modification
            image = self.__apply_tracked(buffer, image, index, frameID)

        # Store the width and the height of the image
        (h, w) = image.shape[:2]

        # Create the output files
        self.__create_out(buffer.nb_persons(), w, h)

        # Write the image in csv file, video, folder
        try:
            self.__write(image, index, buffer.get_coordinate(index, frameID))
        except IndexError:
            self.__write(image, index)

    # -----------------------------------------------------------------------

    def __apply_tracked(self, buffer, image, index, frameID):
        """Apply modification based on the tracking.

        :param buffer: (VideoBuffer) The buffer which contains images.
        :param image: (numpy.ndarray) The image to be processed.
        :param index: (int) The ID of the person.
        :param frameID: (int) The ID of the image in the buffer.

        """
        # If portrait option has been selected
        if self.__framing == "portrait":
            # Transform Coordinates into portrait
            portrait(buffer.get_coordinate(index, frameID))

        # If mode is not full
        if self.__mode != "full" and self.__mode is not None:
            # Adjust the Coordinates
            self.__adjust(image, buffer.get_coordinate(index, frameID))

        # If a mode has been selected
        if self.__mode is not None:
            # Use one of the extraction options
            image = self.__process_image(image, buffer.get_coordinate(index, frameID), index)

        # If mode is not full
        # or if a mode has been selected
        if self.__mode != "full" and self.__mode is not None:
            # Resize the image
            image = self.__resize(image)

        return image

    # -----------------------------------------------------------------------

    def __apply_landmarked(self, buffer, image, index, frameID):
        """Apply modification based on the landmark.

        :param buffer: (VideoBuffer) The buffer which contains images.
        :param image: (numpy.ndarray) The image to be processed.
        :param index: (int) The ID of the person.
        :param frameID: (int) The ID of the image in the buffer.

        """
        # If draw is not None
        if self.get_draw() is not None:
            # Draw the shape on landmarks points
            self.__draw_points(image, buffer.get_landmark(index, frameID), index)

    # -----------------------------------------------------------------------

    def __process_image(self, img_buffer, coords, index):
        """Draw squares around faces or crop the faces.

        :param img_buffer: (numpy.ndarray) The image to be processed.
        :param coords: (Coordinates) The coordinates of the face.
        :param index: (int) The ID of the person in the list of person.

        """
        index = int(index)
        if isinstance(index, int) is False:
            raise TypeError
        if isinstance(img_buffer, np.ndarray) is False:
            raise TypeError
        if isinstance(coords, Coordinates) is False:
            raise TypeError

        # If mode is full
        if self.__mode == "full":
            # Get a different color for each person
            number = (index * 80) % 120

            # Draw a square around the face
            return surrond_square(img_buffer, coords, number)

        # If mode is crop
        elif self.__mode == "crop":
            # Crop the face
            return crop(img_buffer, coords)

    # -----------------------------------------------------------------------

    def __draw_points(self, img_buffer, landmark_points, index):
        """Draw circle, ellipse or rectangle on landmark points.

        :param img_buffer: (numpy.ndarray) The image to be processed.
        :param landmark_points: (dict) A list of x-axis, y-axis values,
        landmark points.
        :param index: (int) The index of the person in the list of person.

        """
        if isinstance(landmark_points, list) is False:
            raise TypeError

        if isinstance(img_buffer, np.ndarray) is False:
            raise TypeError

        # Get a different color for each person
        number = (index * 80) % 120

        # Draw shape on each landmark points
        for t in landmark_points:
            x, y = t
            draw_points(img_buffer, x, y, number, self.get_draw())

    # -----------------------------------------------------------------------

    def __adjust(self, img_buffer, coords):
        """Adjust the coordinates to get a good result.

        :param img_buffer: (numpy.ndarray) The image to be processed.
        :param coords: (Coordinates) The coordinates of the face.

        """
        if self.__mode == "crop" and self.__width == -1 and self.__height == -1:
            self.set_video(False)

        # If anything has been setted pass
        if self.__width == -1 and self.__height == -1:
            pass

        # If only the width has been setted use adjust width
        if self.__width != -1 and self.__height == -1:
            self.__adjust_height()

        # If only the height has been setted use adjust height
        elif self.__width == -1 and self.__height != -1:
            self.__adjust_width()

        # If both of width and height has been setted
        if self.__width != -1 and self.__height != -1:
            self.__adjust_both(coords, img_buffer)

    # -----------------------------------------------------------------------

    def __adjust_both(self, coords, img_buffer=None):
        """Adjust the coordinates with width and height from constructor.

        :param coords: (Coordinates) The coordinates of the face.
        :param img_buffer: (numpy.ndarray) The image to be processed.

        """
        coeff = self.__width / self.__height
        coeff_coords = coords.w / coords.h
        if coeff != coeff_coords:
            new_w = int(coords.h * coeff)
            old_w = coords.w
            coords.w = new_w
            shift_x = int((old_w - new_w) / 2)
            if coords.x + shift_x < 0:
                shift_x = -coords.x
            coords.x = coords.x + shift_x

        if img_buffer is not None:
            (h, w) = img_buffer.shape[:2]
            if coords.h > h:
                coords.h = h
                coords.y = 0
            if coords.w > w:
                coords.w = w
                coords.x = 0

    # -----------------------------------------------------------------------

    def __adjust_width(self):
        """Adjust the width based on the width from constructor."""
        if self.__framing == "face":
            coeff = 0.75
        else:
            coeff = 4 / 3
        self.__width = int(self.__height * coeff)

    # -----------------------------------------------------------------------

    def __adjust_height(self):
        """Adjust the height based on the height from constructor."""
        if self.__framing == "face":
            coeff = 4 / 3
        else:
            coeff = 0.75
        self.__height = int(self.__width * coeff)

    # -----------------------------------------------------------------------

    def __resize(self, img_buffer):
        """Resize the image with width and height from constructor.

        :param img_buffer: (numpy.ndarray) The image to be processed.

        """
        if self.__width == -1 and self.__height == -1:
            return img_buffer
        else:
            new_image = resize(img_buffer, self.__width, self.__height)
            return new_image

    # -----------------------------------------------------------------------

    def __create_out(self, lenght, w, h):
        """Create csv outputs files, videos, folders.

        :param lenght: (list) The lenght of the list.
        :param w: (int) The width of the image.
        :param h: (int) The height of the image.

        """
        # if the option is True create the csv files
        if self.get_csv() is True:
            self.__out_csv(lenght)

        # if the option is True create the videos
        if self.get_video() is True:
            self.__out_video(lenght, width=w, height=h)

        # if the option is True create the folder
        if self.get_folder() is True:
            self.__out_folder(lenght)

    # -----------------------------------------------------------------------

    def __out_csv(self, value):
        """Create csv file for each person.

        :param value: (int) The number of person on the video.

        """
        value = int(value)
        if isinstance(value, int) is False:
            raise TypeError

        # Loop over the number of persons on the video
        for i in range(1, value + 1):
            # Create the path
            path = os.path.join(self.__cfile_path(i))

            # If the csv file does not exist create it
            if os.path.exists(path) is False:
                file = open(path, 'w', newline='')
                writer = csv.writer(file)
                self.__csv_output.append(writer)

    # -----------------------------------------------------------------------

    def __out_video(self, value, width=640, height=480):
        """Create video writer for each person.

        :param value: (int) The number of person to extract.
        :param width: (int) The width of the videos.
        :param height: (int) The height of the videos.

        """
        value = int(value)
        if isinstance(value, int) is False:
            raise TypeError

        # Loop over the number of persons on the video
        for i in range(1, value + 1):
            # Create the path
            path = os.path.join(self.__vfile_path(i))

            # If the output video does not exist create it
            if os.path.exists(path) is False:
                self.__video_output.append(cv2.VideoWriter(path, VideoWriter_fourcc(*'MJPG'),
                                                           self.__fps, (width, height)))
            if self.__mode == "full" or self.__draw is not None and self.__mode is None:
                break

    # -----------------------------------------------------------------------

    def __out_base(self, value, width=640, height=480):
        """Create video writer for each person.

        :param value: (int) The number of person to extract.
        :param width: (int) The width of the videos.
        :param height: (int) The height of the videos.

        """
        value = int(value)
        if isinstance(value, int) is False:
            raise TypeError

        # Loop over the number of persons on the video
        for i in range(1, value + 1):
            # Create the path
            path = os.path.join(self.__base_path(i))

            # If the output video does not exist create it
            if os.path.exists(path) is False:
                self.__base_output.append(cv2.VideoWriter(path, VideoWriter_fourcc(*'MJPG'),
                                                          self.__fps, (width, height)))

    # -----------------------------------------------------------------------

    def __out_folder(self, value):
        """Create folder for each person.

        :param value: (int) The number of person to extract.

        """
        value = int(value)
        if isinstance(value, int) is False:
            raise TypeError

        # Loop over the number of persons on the video
        for i in range(1, value + 1):
            # Create the path of a folder
            path = self.__ffile_path(i)

            # If the folder does not exist create it
            if os.path.exists(path) is False:
                os.mkdir(path)
                self.__folder_output.append(path)
            # If mode equal full create only one output
            if self.__mode == "full" or self.__draw is not None and self.__mode is None:
                break

    # -----------------------------------------------------------------------

    def __write(self, image, index, coordinate=None):
        """Write the image in csv files, videos, and folders.

        :param image: (numpy.ndarray) The image to be processed.
        :param index: (int) The index of the coordinate.
        :param coordinate: (Coordinates) The Coordinates object.

        """
        # Write the image in a csv file
        self.__write_csv(image, index, coordinate)

        # Write the image in a video
        self.__write_video(image, index)

        # Write the image in a folder
        self.__write_folder(image, index)

    # -----------------------------------------------------------------------

    def __write_csv(self, image, index, coordinate=None):
        """Write the image in a csv file.

        :param image: (numpy.ndarray) The image to be processed.
        :param index: (int) The index of the coordinate.
        :param coordinate: (Coordinates) The Coordinates object.

        """
        # If csv option is True write the image in the good csv file.
        if self.get_csv() is True:
            if coordinate is not None:
                self.__csv_output[index].writerow(
                    [self.__number, image, coordinate.x, coordinate.y, coordinate.w, coordinate.h])
            else:
                self.__csv_output[index].writerow(
                    [self.__number, image])

    # -----------------------------------------------------------------------

    def __write_video(self, image, index):
        """Write the image in a video.

        :param image: (numpy.ndarray) The image to be processed.
        :param index: (int) The index of the coordinate.

        """
        # If the video option is True write the image in the good video writer.
        if self.get_video() is True:
            # If mode equal full create only one output video
            if self.__mode == "full" or self.__draw is not None and self.__mode is None:
                index = 0
                self.__video_output[index].write(image)
            else:
                self.__video_output[index].write(image)

    # -----------------------------------------------------------------------

    def __write_folder(self, image, index):
        """Write the image in a folder.

        :param image: (numpy.ndarray) The image to be processed.
        :param index: (int) The index of the coordinate.

        """
        # If the folder option is True write the image in the good folder.
        if self.get_folder() is True:

            # If mode equal full create only one output folder
            if self.__mode == "full" or self.__draw is not None and self.__mode is None:
                index = 0
                cv2.imwrite(self.__folder_output[index] + "image" + str(self.__number) + ".jpg", image)
            else:
                cv2.imwrite(self.__folder_output[index] + "image" + str(self.__number) + ".jpg", image)

    # -----------------------------------------------------------------------

    def __write_base(self, image, index):
        """Write the image in csv files, videos, and folders.

        :param image: (numpy.ndarray) The image to be processed.
        :param index: (int) The index of the coordinate.

        """
        self.__base_output[index].write(image)

    # -----------------------------------------------------------------------

