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
from sppas.src.exceptions import sppasPackageFeatureError
from sppas.src.exceptions import sppasPackageUpdateFeatureError

# Store the rectangle and a score of an image. No external dependency.
from .coordinates import sppasCoords

# ---------------------------------------------------------------------------


class sppasImageDataError(object):
    def __init__(self, *args, **kwargs):
        raise sppasEnableFeatureError("video")

# ---------------------------------------------------------------------------


try:
    import cv2
    import numpy
    cfg.set_feature("video", True)
except ImportError:
    # Invalidate the feature because the package is not installed
    cfg.set_feature("video", False)


# The feature "video" is enabled: cv2 is installed.
# Check version.
if cfg.feature_installed("video") is True:

    v = cv2.__version__.split(".")[0]
    if v != '4':
        # Invalidate the feature because the package is not up-to-date
        cfg.set_feature("video", False)

    class sppasImageDataError(object):
        def __init__(self, *args, **kwargs):
            if v != '4':
                raise sppasPackageUpdateFeatureError("cv2", "video")
            else:
                raise sppasPackageFeatureError("cv2", "video")


# ---------------------------------------------------------------------------
# Either import classes or define them
# ---------------------------------------------------------------------------

image_extensions = list()

if cfg.feature_installed("video") is True:
    # Subclass of numpy.ndarray to manipulate images
    from .image import sppasImage
    from .imageutils import sppasImageCompare
    # Write image and coordinates
    from .imgwriter import sppasImageCoordsWriter
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
        return (".png", ".jpg", ".bmp", ".dib", ".jpeg", ".jpe", ".jp2",
                ".pbm", ".pgm", ".sr", ".ras", ".tiff", ".tif")

    image_extensions.extend(opencv_extensions())

else:  # The feature "video" is not enabled or cv2 is not installed.

    class sppasImage(sppasImageDataError):
        pass


    class sppasImageCompare(sppasImageDataError):
        pass


    class sppasImageCoordsWriter(sppasImageDataError):
        pass


    class HaarCascadeDetector(sppasImageDataError):
        pass


    class NeuralNetDetector(sppasImageDataError):
        pass


    class sppasImageObjectDetection(sppasImageDataError):
        pass

# ---------------------------------------------------------------------------


__all__ = (
    "sppasCoords",
    "sppasImage",
    "sppasImageCompare",
    "sppasImageCoordsWriter",
    "image_extensions",
    "HaarCascadeDetector",
    "NeuralNetDetector",
    "sppasImageObjectDetection"
)
