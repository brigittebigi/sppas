# -*- coding: UTF-8 -*-
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

    src.annotations.FaceTracking.sppasfacetrack.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""

import logging
from sppas.src.config import cfg
from sppas.src.exceptions import sppasEnableFeatureError
from sppas.src.exceptions import sppasError
from sppas.src.exceptions import sppasTypeError
from sppas.src.videodata import video_extensions

from ..FaceDetection import FaceDetection
from ..FaceMark import FaceLandmark
from ..annotationsexc import AnnotationOptionError
from ..baseannot import sppasBaseAnnotation

from .facebuffer import sppasFacesVideoBuffer
from .facetrack import FaceTracking
from .videowriter import sppasVideoWriter

# ---------------------------------------------------------------------------


class sppasFaceTrack(sppasBaseAnnotation):
    """SPPAS integration of the automatic face tracking on a video.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2020 Brigitte Bigi

    """

    def __init__(self, log=None):
        """Create a new sppasFaceTrack instance.

        Log is used for a better communication of the annotation process and its
        results. If None, logs are redirected to the default logging system.

        :param log: (sppasLog) Human-readable logs.

        """
        if cfg.dep_installed("facedetect") is False:
            raise sppasEnableFeatureError("facedetect")

        if cfg.dep_installed("facemark") is False:
            raise sppasEnableFeatureError("facemark")

        super(sppasFaceTrack, self).__init__("facetrack.json", log)

        # The objects to store the input data and the results
        self.__video_buffer = sppasFacesVideoBuffer(size=10)
        self.__video_writer = sppasVideoWriter()

        # The detector
        self.__ft = FaceTracking()

    # -----------------------------------------------------------------------

    def load_resources(self, *args, **kwargs):
        """Fix models for face detection and face landmark.

        """
        # Load the models for Face Detection
        models_fd = list()
        for model_name in args:
            try:
                ff = FaceDetection()
                ff.load_model(model_name)
            except IOError:
                pass
            except sppasError:
                pass
            else:
                models_fd.append(model_name)
        if len(models_fd) == 0:
            raise sppasError("At least a valid model is required.")
        self.__video_buffer.load_fd_model(models_fd[0], *models_fd[1:])

        # Load the models for Face Landmarks
        models_fl = list()
        for model_name in args:
            if model_name not in models_fd:
                try:
                    ff = FaceLandmark()
                    ff.load_model(models_fd[0], model_name)
                except IOError:
                    pass
                except sppasError:
                    pass
                else:
                    models_fl.append(model_name)

        if len(models_fl) > 0:
            self.__video_buffer.load_fl_model(models_fd[0], *models_fl)

        logging.debug("FaceTracking loaded {:d} models for face detection"
                      "".format(len(models_fd)))
        logging.debug("FaceTracking loaded {:d} models for face landmark"
                      "".format(len(models_fl)))

    # -----------------------------------------------------------------------
    # Methods to fix options
    # -----------------------------------------------------------------------

    def fix_options(self, options):
        """Fix all options.

        :param options: (sppasOption)

        """
        for opt in options:

            key = opt.get_key()
            if key == "nbest":
                self.set_max_faces(opt.get_value())

            elif key == "score":
                self.set_min_score(opt.get_value())

            elif key == "csv":
                self.set_out_csv(opt.get_value())

            elif key == "video":
                self.set_out_video(opt.get_value())

            elif key == "folder":
                self.set_out_images(opt.get_value())

            elif key == "tag":
                self.set_img_tag(opt.get_value())

            elif key == "crop":
                self.set_img_crop(opt.get_value())

            elif key == "width":
                self.set_img_width(opt.get_value())

            elif key == "height":
                self.set_img_height(opt.get_value())

            elif key in ("inputpattern", "outputpattern", "inputoptpattern"):
                self._options[key] = opt.get_value()

            else:
                raise AnnotationOptionError(key)

    # ----------------------------------------------------------------------
    # Getters and setters
    # -----------------------------------------------------------------------

    def set_max_faces(self, value):
        """Fix the maximum number of faces the video contains.

        :param value: (int) Number of persons

        """
        self.__video_buffer.set_filter_best(value)
        self._options["nbest"] = value

    # -----------------------------------------------------------------------

    def set_min_score(self, value):
        """Fix the minimum score to accept a face in the video.

        :param value: (float) Min confidence score for face detection

        """
        self.__video_buffer.set_filter_confidence(value)
        self._options["score"] = value

    # -----------------------------------------------------------------------

    def set_out_csv(self, out_csv=False):
        """The result includes a CSV file.

        :param out_csv: (bool) Create a CSV file when detecting

        """
        self.__video_writer.set_options(csv=out_csv)
        self._options["csv"] = out_csv

    # -----------------------------------------------------------------------

    def set_out_video(self, out_video=False):
        """The result includes a VIDEO file.

        :param out_video: (bool) Create a VIDEO file when detecting

        """
        self.__video_writer.set_options(video=out_video)
        self._options["video"] = out_video

    # -----------------------------------------------------------------------

    def set_out_images(self, out_folder=False):
        """The result includes a folder with image files.

        :param out_folder: (bool) Create a folder with image files when detecting

        """
        self.__video_writer.set_options(folder=out_folder)
        self._options["folder"] = out_folder

    # -----------------------------------------------------------------------

    def set_img_tag(self, value=True):
        """Surround the faces with a square.

        :param value: (bool) Tag the images

        """
        self.__video_writer.set_options(tag=value)
        self._options["tag"] = value

    # -----------------------------------------------------------------------

    def set_img_crop(self, value=True):
        """Create an image/video for each detected person.

        :param value: (bool) Crop the images

        """
        self.__video_writer.set_options(crop=value)
        self._options["crop"] = value

    # -----------------------------------------------------------------------

    def set_img_width(self, value):
        """Width of the resulting images/video.

        :param value: (int) Number of pixels

        """
        self.__video_writer.set_options(width=value)
        self._options["width"] = value

    # -----------------------------------------------------------------------

    def set_img_height(self, value):
        """Height of the resulting images/video.

        :param value: (int) Number of pixel

        """
        self.__video_writer.set_options(height=value)
        self._options["height"] = value

    # -----------------------------------------------------------------------

    def set_videos(self, video_buffer, video_writer, options=False):
        """Assign a video buffer and a video writer.

        Either:

        -options=True: The configuration of the video buffer and writer is
        changed to match the ones defined by the options of this class.
        -options=False: The options of this class are changed to match the
        configuration of the video buffer and writer.

        :param video_buffer: (sppasVideoBuffer)
        :param video_writer: (sppasVideoWriter)
        :param options: (bool) options priority

        """
        if isinstance(video_buffer, sppasFacesVideoBuffer) is False:
            raise sppasTypeError(video_buffer, "sppasFacesVideoBuffer")
        if isinstance(video_writer, sppasVideoWriter) is False:
            raise sppasTypeError(video_writer, "sppasVideoWriter")

        self.__video_buffer = video_buffer
        self.__video_writer = video_writer

        if options is True:
            # Priority is given to the existing options:
            self.__video_buffer.set_filter_best(self._options["nbest"])
            self.__video_buffer.set_filter_confidence(self._options["score"])
            self.__video_writer.set_options(
                csv=self._options["csv"],
                video=self._options["video"],
                folder=self._options["folder"],
                tag=self._options["tag"],
                crop=self._options["crop"],
                width=self._options["width"],
                height=self._options["height"]
            )
        else:
            # The existing options are overridden by the video configuration:
            self._options["nbest"] = self.__video_buffer.get_filter_best()
            self._options["score"] = self.__video_buffer.get_filter_confidence()
            self._options["csv"] = self.__video_writer.get_csv_output()
            self._options["video"] = self.__video_writer.get_video_output()
            self._options["folder"] = self.__video_writer.get_folder_output()
            self._options["tag"] = self.__video_writer.get_tag_output()
            self._options["crop"] = self.__video_writer.get_crop_output()
            self._options["width"] = self.__video_writer.get_output_width()
            self._options["height"] = self.__video_writer.get_output_height()

    # -----------------------------------------------------------------------
    # Apply the annotation on a given file
    # -----------------------------------------------------------------------

    def detect(self, output_file=None):
        """Browse the video and store results.

        """
        # Browse the video using the buffer of images
        result = list()
        read_next = True
        nb = 0

        # Cancel any previous result
        self.__video_buffer.reset()
        self.__video_buffer.seek_buffer(0)

        while read_next is True:
            if self.logfile is not None:
                self.logfile.print_message("Read buffer number {:d}".format(nb))

            # fill-in the buffer with 'size'-images of the video
            read_next = self.__video_buffer.next()

            # face detection&landmarks on the current images of the buffer
            # and associate a face to a person
            self.__ft.detect_buffer(self.__video_buffer)

            # save the current results
            if output_file is not None:
                self.__video_writer.write(self.__video_buffer,
                                          output_file,
                                          pattern=self.get_pattern())
            for i in range(len(self.__video_buffer)):
                faces = self.__video_buffer.get_detected_faces(i)
                result.append(faces)
            nb += 1

        return result

    # -----------------------------------------------------------------------

    def run(self, input_file, opt_input_file=None, output_file=None):
        """Run the automatic annotation process on an input.

        :param input_file: (list of str) (image)
        :param opt_input_file: (list of str) ignored
        :param output_file: (str) the output base name for files
        :returns: (list of points) Coordinates of detected faces

        """
        # Get and open the video filename from the input
        video = input_file[0]
        self.__video_buffer.open(video)
        self.__video_writer.set_fps(self.__video_buffer.get_framerate())
        bsize = self.__video_buffer.get_size()

        # Print information about the video in the report
        if self.logfile:
            self.logfile.print_message("Video information: {}"
                                       "".format(input_file[0]),
                                       indent=0)
            self.logfile.print_message(
                "Video: {:.3f} seconds, {:d} fps, {:d}x{:d}".format(
                    self.__video_buffer.get_duration(),
                    self.__video_buffer.get_framerate(),
                    self.__video_buffer.get_width(),
                    self.__video_buffer.get_height()
                ), indent=1)
            self.logfile.print_message(
                "A video buffer contains {:d} images".format(bsize),
                indent=1)

        result = self.detect(output_file)

        # Quit properly
        self.__video_buffer.close()
        self.__video_buffer.reset()
        self.__video_writer.close()
        return result

    # -----------------------------------------------------------------------

    def get_pattern(self):
        """Pattern this annotation adds to the output filename."""
        return self._options.get("outputpattern", "-face")

    @staticmethod
    def get_input_extensions():
        """Extensions that the annotation expects for its input filename."""
        return video_extensions
