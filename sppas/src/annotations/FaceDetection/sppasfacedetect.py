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

    src.annotations.FaceDetection.sppasfacedetect.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""

import logging
import os
from sppas.src.config import cfg
from sppas.src.config import annots
from sppas.src.exceptions import sppasEnableFeatureError

from sppas.src.imgdata import image_extensions
from sppas.src.imgdata import sppasImage
from sppas.src.imgdata import sppasImageWriter

from ..annotationsexc import AnnotationOptionError
from ..baseannot import sppasBaseAnnotation
from .facedetection import FaceDetection

# ----------------------------------------------------------------------------


class sppasFaceDetection(sppasBaseAnnotation):
    """SPPAS integration of the automatic face detection on an image.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2020 Brigitte Bigi

    """

    def __init__(self, log=None):
        """Create a new sppasRMS instance.

        Log is used for a better communication of the annotation process and its
        results. If None, logs are redirected to the default logging system.

        :param log: (sppasLog) Human-readable logs.

        """
        if cfg.dep_installed("facedetect") is False:
            raise sppasEnableFeatureError("facedetect")

        super(sppasFaceDetection, self).__init__("facedetect.json", log)
        self.__fd = FaceDetection()
        self.__writer = sppasImageWriter()

    # -----------------------------------------------------------------------

    def load_resources(self, model1, *args, **kwargs):
        """Fix the model file.

        :param model1: (str) Filename of a model
        :param args: other models for face detection

        """
        self.__fd.load_model(model1, *args)

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

            elif key == "score":
                self._options["score"] = opt.get_value()

            elif key == "csv":
                self._options["csv"] = opt.get_value()
                self.__writer.set_options(csv=opt.get_value())

            elif key == "tag":
                self._options["tag"] = opt.get_value()
                self.__writer.set_options(tag=opt.get_value())

            elif key == "crop":
                self._options["crop"] = opt.get_value()
                self.__writer.set_options(crop=opt.get_value())

            elif key == "portrait":
                self._options["portrait"] = opt.get_value()

            elif key == "width":
                self._options["width"] = opt.get_value()
                self.__writer.set_options(width=opt.get_value())

            elif key == "height":
                self._options["height"] = opt.get_value()
                self.__writer.set_options(height=opt.get_value())

            elif key in ("inputpattern", "outputpattern", "inputoptpattern"):
                self._options[key] = opt.get_value()

            else:
                raise AnnotationOptionError(key)

    # -----------------------------------------------------------------------
    # Getters and Setters
    # -----------------------------------------------------------------------

    # ----------------------------------------------------------------------
    # Apply the annotation on a given file
    # -----------------------------------------------------------------------

    def run(self, input_file, opt_input_file=None, output_file=None):
        """Run the automatic annotation process on an input.

        :param input_file: (list of str) (image)
        :param opt_input_file: (list of str) ignored
        :param output_file: (str) the output file name
        :returns: (list of sppasCoords) Coordinates of detected faces

        """
        # Get the image from the input
        image = sppasImage(filename=input_file[0])

        # Search for coordinates of faces
        self.__fd.detect(image)
        self.logfile.print_message(str(len(self.__fd)) + " faces found.",
                                   indent=2, status=annots.info)

        # Filter coordinates (number of faces / score)
        if self._options["nbest"] != 0:
            self.__fd.filter_best(self._options["nbest"])
        self.__fd.filter_confidence(self._options["score"])

        # Make the output list of coordinates
        if self._options["portrait"] is True:
            try:
                self.__fd.to_portrait(image)
            except Exception as e:
                self.logfile.print_message(
                    "Faces can't be scaled to portrait: {}".format(str(e)),
                    indent=2, status=annots.error)
        coords = [c.copy() for c in self.__fd]

        # Save result as a list of coordinates (csv), a tagged image
        # and/or a list of images (face or portrait) in a folder
        if output_file is not None:
            self.__writer.write(image, coords, output_file, self.get_pattern())

        return coords

    # -----------------------------------------------------------------------

    def get_pattern(self):
        """Pattern this annotation uses in an output filename."""
        return self._options.get("outputpattern", "-face")

    @staticmethod
    def get_input_extensions():
        """Extensions that the annotation expects for its input filename."""
        return image_extensions
