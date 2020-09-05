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

        self.__video_buffer = sppasFacesVideoBuffer(size=10)
        self.__ft = FaceTracking()
        self.__video_writer = sppasVideoWriter()

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
                self._options["nbest"] = opt.get_value()
                self.__video_buffer.set_filter_best(opt.get_value())

            elif key == "score":
                self._options["score"] = opt.get_value()
                self.__video_buffer.set_filter_confidence(opt.get_value())

            elif key == "csv":
                self._options["csv"] = opt.get_value()
                self.__video_writer.set_options(csv=opt.get_value())

            elif key == "tag":
                self._options["tag"] = opt.get_value()
                self.__video_writer.set_options(tag=opt.get_value())

            elif key == "crop":
                self._options["crop"] = opt.get_value()
                self.__video_writer.set_options(crop=opt.get_value())

            elif key == "video":
                self._options["video"] = opt.get_value()
                self.__video_writer.set_options(video=opt.get_value())

            elif key == "folder":
                self._options["folder"] = opt.get_value()
                self.__video_writer.set_options(folder=opt.get_value())

            elif key == "width":
                self._options["width"] = opt.get_value()
                self.__video_writer.set_options(width=opt.get_value())

            elif key == "height":
                self._options["height"] = opt.get_value()
                self.__video_writer.set_options(height=opt.get_value())

            elif key in ("inputpattern", "outputpattern", "inputoptpattern"):
                self._options[key] = opt.get_value()

            else:
                raise AnnotationOptionError(key)

    # ----------------------------------------------------------------------
    # Apply the annotation on a given file
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
        self.logfile.print_message(" ... A video buffer contains {:d} images"
                                   "".format(bsize))

        # Browse the video using the buffer of images
        result = list()
        read_next = True
        nb = 0

        self.__video_writer.set_options(csv=None, tag=None, crop=None, width=None, height=None, video=None, folder=None)

        while read_next is True:
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

        self.__video_buffer.close()
        self.__video_buffer.reset()
        self.__video_writer.close()
        return result

    # -----------------------------------------------------------------------

    def get_pattern(self):
        """Pattern this annotation uses in an output filename."""
        return self._options.get("outputpattern", "-face")

    @staticmethod
    def get_input_extensions():
        """Extensions that the annotation expects for its input filename."""
        return video_extensions
