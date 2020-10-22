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
from sppas.src.exceptions import sppasPackageFeatureError
from sppas.src.exceptions import sppasPackageUpdateFeatureError

# ---------------------------------------------------------------------------


class sppasVideodataError(object):
    def __init__(self, *args, **kwargs):
        raise sppasEnableFeatureError("video")


# The feature "video" is enabled. Check if it's really correct!
if cfg.feature_installed("video") is True:
    v = '4'
    try:
        import cv2
    except ImportError:
        # Invalidate the feature because the package is not installed
        cfg.set_feature("video", False)

    else:
        v = cv2.__version__.split(".")[0]
        if v != '4':
            # Invalidate the feature because the package is not up-to-date
            cfg.set_feature("video", False)

    class sppasVideoDataError(object):
        def __init__(self, *args, **kwargs):
            if v != '4':
                raise sppasPackageUpdateFeatureError("cv2", "video")
            else:
                raise sppasPackageFeatureError("cv2", "video")

else:
    # The feature "video" is not enabled or unknown.
    cfg.set_feature("video", False)

# ---------------------------------------------------------------------------


if cfg.feature_installed("video") is True:
    from .video import sppasVideoReader
    from .video import sppasVideoWriter
    from .videobuffer import sppasVideoReaderBuffer
    from .videoplayer import sppasSimpleVideoPlayer

else:
    # Define classes in case opencv&numpy are not installed.

    class sppasVideoWriter(sppasVideodataError):
        MAX_FPS = 0
        FOURCC = dict()
        RESOLUTIONS = dict()


    class sppasVideoReader(sppasVideodataError):
        pass


    class sppasVideoReaderBuffer(sppasVideodataError):
        DEFAULT_BUFFER_SIZE = 0
        DEFAULT_BUFFER_OVERLAP = 0
        MAX_MEMORY_SIZE = 0
        pass

    class sppasSimpleVideoPlayer(sppasVideodataError):
        QUEUE_SIZE = 128
        pass

video_extensions = tuple(sppasVideoWriter.FOURCC.keys())

# ---------------------------------------------------------------------------

__all__ = (
    "sppasVideoReader",
    "sppasVideoWriter",
    "sppasVideoReaderBuffer",
    "video_extensions",
)

