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
audiodata: management of digital audio data.
*****************************************************************************

Requires the following other packages:

* config
* utils
* exceptions

Requires the following dependency to play audio:

* simpleaudio - https://pypi.org/project/simpleaudio/

If the audioplay feature is not enabled, the sppasEnableFeatureError() is
raised the class sppasSimpleAudioPlayer() is instantiated.

"""

import logging

from sppas.src.config import cfg
from sppas.src.exceptions import sppasEnableFeatureError
from sppas.src.exceptions import sppasPackageFeatureError

# ---------------------------------------------------------------------------


class sppasAudioPlayDataError(object):
    def __init__(self, *args, **kwargs):
        raise sppasEnableFeatureError("audioplay")

# Test if simpleaudio library is available. It is the requirement of the
# feature "audioplay".
try:
    import simpleaudio
    cfg.set_feature("audioplay", True)
    logging.info("audioplay feature enabled")
except ImportError:
    # Invalidate the feature because the package is not installed
    cfg.set_feature("audioplay", False)


# The feature "audioplay" is enabled. Check if it's really correct!
if cfg.feature_installed("audioplay") is True:

    class sppasAudioPlayDataError(object):
        def __init__(self, *args, **kwargs):
            raise sppasPackageFeatureError("simpleaudio", "audioplay")

# ---------------------------------------------------------------------------
# Either import classes or define them
# ---------------------------------------------------------------------------


from .audio import sppasAudioPCM
from .audioframes import sppasAudioFrames
from .channel import sppasChannel
from .aio import extensions

if cfg.feature_installed("audioplay") is True:
    from .audioplayer import sppasSimpleAudioPlayer
    from .audioplayer import sppasMultiAudioPlayer
else:

    class sppasSimpleAudioPlayer(sppasAudioPlayDataError):
        pass

    class sppasMultiAudioPlayer(sppasAudioPlayDataError):
        pass

# ---------------------------------------------------------------------------


audio_extensions = extensions

__all__ = (
    "sppasAudioPCM",
    "sppasAudioFrames",
    "sppasChannel",
    "sppasMultiAudioPlayer"
)
