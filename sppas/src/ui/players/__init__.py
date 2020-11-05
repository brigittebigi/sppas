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

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2020  Brigitte Bigi

*****************************************************************************
ui.players: players & viewers of digital audio/video data.
*****************************************************************************

Requires the following other packages:

* config
* utils
* exceptions

Requires the following dependency to play audio or video:

* simpleaudio - https://pypi.org/project/simpleaudio/
* opencv - https://opencv.org/


"""

from sppas.src.config import cfg
from sppas.src.exceptions import sppasEnableFeatureError
from sppas.src.exceptions import sppasPackageFeatureError

# ---------------------------------------------------------------------------


class sppasAudioPlayerError(object):
    def __init__(self, *args, **kwargs):
        raise sppasEnableFeatureError("audioplay")


class sppasVideoPlayerError(object):
    def __init__(self, *args, **kwargs):
        raise sppasEnableFeatureError("video")

# Test if simpleaudio library is available. It is the requirement of the
# feature "audioplay".
try:
    import simpleaudio
    cfg.set_feature("audioplay", True)
except ImportError:
    # Invalidate the feature because the package is not installed
    cfg.set_feature("audioplay", False)

# Test if opencv library is available. It is the requirement of the
# feature "video".
try:
    import cv2
    cfg.set_feature("video", True)
except ImportError:
    # Invalidate the feature because the package is not installed
    cfg.set_feature("video", False)
else:
    v = cv2.__version__.split(".")[0]
    if v != '4':
        # Invalidate the feature because the package is not up-to-date
        cfg.set_feature("video", False)


if cfg.feature_installed("audioplay") is True:

    class sppasAudioPlayerError(object):
        def __init__(self, *args, **kwargs):
            raise sppasPackageFeatureError("simpleaudio", "audioplay")

if cfg.feature_installed("video") is True:

    class sppasVideoPlayerError(object):
        def __init__(self, *args, **kwargs):
            raise sppasPackageFeatureError("cv2", "video")

# ---------------------------------------------------------------------------
# Either import classes or define them
# ---------------------------------------------------------------------------


if cfg.feature_installed("audioplay") is True:
    from .audiomplayer import sppasMultiAudioPlayer
else:

    # Either the FeatureError or PackageError will be raised if the class
    # is instantiated, but no error is raised at the time of init/import.

    class sppasSimpleAudioPlayer(sppasAudioPlayerError):
        pass

    class sppasMultiAudioPlayer(sppasAudioPlayerError):
        pass


if cfg.feature_installed("video") is True:
    from .videoplayer import sppasSimpleVideoPlayer
else:

    class sppasSimpleVideoPlayer(sppasVideoPlayerError):
        QUEUE_SIZE = 128
        pass

# ---------------------------------------------------------------------------


__all__ = (
    "sppasSimpleAudioPlayer",
    "sppasMultiAudioPlayer",
    "sppasSimpleVideoPlayer"
)