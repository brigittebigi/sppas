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

from sppas.src.config import cfg
from sppas.src.exceptions import sppasEnableFeatureError
from sppas.src.videodata import video_extensions

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

        if cfg.dep_installed("facetrack") is False:
            raise sppasEnableFeatureError("facetrack")

        super(sppasFaceTrack, self).__init__("facetrack.json", log)

        self.__video_buffer = sppasFacesVideoBuffer()
        self.__ft = FaceTracking()
        self.__video_writer = sppasVideoWriter()

    # -----------------------------------------------------------------------

    def load_resources(self, model_fd, model_lbf, *args, **kwargs):
        """Fix the model and proto files.

        :param model_fd: (str) Model for face detection
        :param model_lbf: (str) LBF model for landmark

        """
        self.__video_buffer.load_fd_model(model_fd)
        self.__video_buffer.load_fd_model(model_lbf)

    # -----------------------------------------------------------------------
    # Methods to fix options
    # -----------------------------------------------------------------------

    def fix_options(self, options):
        """Fix all options.

        :param options: (sppasOption)

        """
        for opt in options:

            key = opt.get_key()
            if key == "csv":
                self._options["csv"] = opt.get_value()
                self.__video_writer.set_options(csv=opt.get_value())

            elif key == "tag":
                self._options["tag"] = opt.get_value()
                self.__video_writer.set_options(tag=opt.get_value())

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
        :param output_file: (str) the output file name
        :returns: (list of points) Coordinates of detected landmarks

        """
        # Get and open the video filename from the input
        video = input_file[0]
        self.__video_buffer.open(video)
        self.__video_writer.set_fps(self.__video_buffer.get_framerate())

        # Browse the video using the buffer of images
        read_next = True
        while read_next is True:
            # fill-in the buffer with 'size'-images of the video
            read_next = self.__video_buffer.next()
            # face detection&landmarks on the current images of the buffer
            # and associate a face to a person
            self.__ft.detect_buffer(self.__video_buffer)
            # save the current results
            self.__video_writer.write(self.__video_buffer,
                                      output_file,
                                      person=None,
                                      pattern=self.get_pattern())

        self.__video_buffer.close()
        self.__video_buffer.reset()
        self.__video_writer.close()
        return

    # -----------------------------------------------------------------------

    def get_pattern(self):
        """Pattern this annotation uses in an output filename."""
        return self._options.get("outputpattern", "-face")

    @staticmethod
    def get_input_extensions():
        """Extensions that the annotation expects for its input filename."""
        return video_extensions
