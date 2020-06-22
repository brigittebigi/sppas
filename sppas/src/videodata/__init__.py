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
videodata: management of video files
*****************************************************************************

Requires the following other packages:

* config
* exceptions

If the video feature is not enabled, the sppasEnableFeatureError() is raised
when a class is instantiated.

"""

from sppas.src.config import cfg
from sppas.src.exceptions import sppasEnableFeatureError


# ---------------------------------------------------------------------------
# Define classes in case opencv&numpy are not installed.
# ---------------------------------------------------------------------------


class sppasVideodataError(object):
    def __init__(self, *args, **kwargs):
        raise sppasEnableFeatureError("video")


class sppasVideoCoordsWriter(sppasVideodataError):
    pass


class FaceTracking(sppasVideodataError):
    pass


class VideoBuffer(sppasVideodataError):
    pass


class PersonsBuffer(sppasVideodataError):
    pass


class VideoLandmark(sppasVideodataError):
    pass


class Manager(sppasVideodataError):
    pass


extensions = list()


# ---------------------------------------------------------------------------
# Import the classes in case the "video" feature is enabled: opencv&numpy
# are both installed and the automatic detections can work.
# ---------------------------------------------------------------------------


if cfg.dep_installed("video"):
    from .coordswriter import sppasVideoCoordsWriter
    from .facetracking import FaceTracking
    from .videobuffer import VideoBuffer
    from .personsbuffer import PersonsBuffer

    def opencv_extensions():
        """Return the list of supported file extensions in lower case.

        TODO: make the full list of supported video file extensions

        """
        return (".mp4", ".avi")

# ---------------------------------------------------------------------------


__all__ = (
    "sppasVideoCoordsWriter",
    "FaceTracking",
    "VideoBuffer",
    "PersonsBuffer",
    "extensions"
)
