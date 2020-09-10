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

    src.annotations.FaceMark.sppasfacemark.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""

from sppas.src.config import cfg
from sppas.src.exceptions import sppasEnableFeatureError
from sppas.src.imgdata import sppasImage
from sppas.src.imgdata import sppasImageWriter
from sppas.src.imgdata import image_extensions

from ..annotationsexc import AnnotationOptionError
from ..baseannot import sppasBaseAnnotation
from .facelandmark import FaceLandmark


class sppasFaceMark(sppasBaseAnnotation):
    """SPPAS integration of the automatic face landmark on an image.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2020 Brigitte Bigi

    """

    def __init__(self, log=None):
        """Create a new sppasFaceMark instance.

        Log is used for a better communication of the annotation process and its
        results. If None, logs are redirected to the default logging system.

        :param log: (sppasLog) Human-readable logs.

        """
        if cfg.dep_installed("facedetect") is False:
            raise sppasEnableFeatureError("facedetect")

        if cfg.dep_installed("facemark") is False:
            raise sppasEnableFeatureError("facemark")

        super(sppasFaceMark, self).__init__("facemark.json", log)
        self.__fl = FaceLandmark()
        self.__writer = sppasImageWriter()

    # -----------------------------------------------------------------------

    def load_resources(self, model_fd, model_lbf, *args, **kwargs):
        """Fix the model and proto files.

        :param model_fd: (str) Model for face detection
        :param model_lbf: (str) LBF model for landmark
        :param args: other models for landmark (Kazemi/LBF/AAM)

        """
        self.__fl.load_model(model_fd, model_lbf, *args)

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
                self.set_out_csv(opt.get_value())

            elif key == "tag":
                self.set_img_tag(opt.get_value())

            elif key in ("inputpattern", "outputpattern", "inputoptpattern"):
                self._options[key] = opt.get_value()

            else:
                raise AnnotationOptionError(key)

    # -----------------------------------------------------------------------
    # Getters and Setters
    # -----------------------------------------------------------------------

    def set_out_csv(self, out_csv=False):
        """The result includes a CSV file.

        :param out_csv: (bool) Create a CSV file with the coordinates

        """
        self.__writer.set_options(csv=out_csv)
        self._options["csv"] = out_csv

    # ----------------------------------------------------------------------

    def set_img_tag(self, value=True):
        """Draw the landmark points to the image.

        :param value: (bool) Tag the images

        """
        self.__writer.set_options(tag=value)
        self._options["tag"] = value

    # ----------------------------------------------------------------------
    # Apply the annotation on a given file
    # -----------------------------------------------------------------------

    def run(self, input_file, opt_input_file=None, output=None):
        """Run the automatic annotation process on an input.

        :param input_file: (list of str) Inout file is an image
        :param opt_input_file: (list of str) ignored
        :param output: (str) the output file name
        :returns: (list of points or filenames) Coordinates of detected sights

        """
        # Get the image from the input
        image = sppasImage(filename=input_file[0])

        # Search for coordinates of faces
        self.__fl.mark(image)

        # Get the output list of coordinates
        coords = [c.copy() for c in self.__fl]

        # Save result as a list of coordinates (csv) and/or a tagged image
        if output is not None:
            output_file = self.fix_out_file_ext(output, out_format="IMAGE")
            new_files = self.__writer.write(image, [coords], output_file, pattern="")
            return new_files

        return coords

    # -----------------------------------------------------------------------

    def get_input_pattern(self):
        """Pattern this annotation expects for its input filename."""
        return self._options.get("inputpattern", '-face')

    def get_pattern(self):
        """Pattern this annotation uses in an output filename."""
        return self._options.get("outputpattern", "-mark")

    @staticmethod
    def get_input_extensions():
        """Extensions that the annotation expects for its input filename."""
        return image_extensions
