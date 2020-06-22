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

*****************************************************************************
imgdata: management of image files
*****************************************************************************

Requires the following other packages:

* config
* exceptions

If the video feature is not enabled, the sppasEnableFeatureError() is raised
when a class is instantiated.

"""

from sppas.src.config import cfg
from sppas.src.exceptions import sppasEnableFeatureError

# Store the rectangle and a score of an image
from .coordinates import sppasCoords


# ---------------------------------------------------------------------------
# Define classes in case opencv&numpy are not installed.
# ---------------------------------------------------------------------------


class sppasImageDataError(object):
    def __init__(self, *args, **kwargs):
        raise sppasEnableFeatureError("video")


class sppasImage(sppasImageDataError):
    pass


class sppasImageWriter(sppasImageDataError):
    pass


class HaarCascadeDetector(sppasImageDataError):
    pass


class NeuralNetDetector(sppasImageDataError):
    pass


class sppasImageObjectDetection(sppasImageDataError):
    pass


extensions = list()

# ---------------------------------------------------------------------------
# Import the classes in case the "video" feature is enabled: opencv&numpy
# are both installed and the automatic detections can work.
# ---------------------------------------------------------------------------


if cfg.dep_installed("video"):
    # Subclass of numpy.ndarray to manipulate images
    from .image import sppasImage
    # Write image and coordinates
    from .imgwriter import sppasImageWriter
    # Automatically detect objects in an image
    from .objdetec import HaarCascadeDetector
    from .objdetec import NeuralNetDetector
    from .objdetec import sppasImageObjectDetection

    def opencv_extensions():
        """Return the list of supported file extensions in lower case.

            Windows bitmaps - *.bmp, *.dib (always supported)
            JPEG files - *.jpeg, *.jpg, *.jpe (see the Notes section)
            JPEG 2000 files - *.jp2 (see the Notes section)
            Portable Network Graphics - *.png (see the Notes section)
            Portable image format - *.pbm, *.pgm, *.ppm (always supported)
            Sun rasters - *.sr, *.ras (always supported)
            TIFF files - *.tiff, *.tif (see the Notes section)

        """
        return (".jpg", ".bmp", ".dib", ".jpeg", ".jpe", ".jp2", ".png",
                ".pbm", ".pgm", ".sr", ".ras", ".tiff", ".tif")

    extensions.extend(opencv_extensions())

# ---------------------------------------------------------------------------


__all__ = (
    "sppasCoords",
    "sppasImage",
    "sppasImageWriter",
    "extensions",
    "HaarCascadeDetector",
    "NeuralNetDetector",
    "sppasImageObjectDetection"
)
