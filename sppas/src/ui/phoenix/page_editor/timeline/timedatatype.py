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

    ui.phoenix.page_editor.timeline.timedatatype.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""

import os
import mimetypes

from sppas.src.anndata import sppasRW
from sppas.src.ui.players.pstate import PlayerType

# ---------------------------------------------------------------------------


class TimelineType(object):
    """Enum all types of supported data by the timeline viewers.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2020 Brigitte Bigi

    :Example:

        >>>with TimelineType() as tt:
        >>>    print(tt.audio)

    This class is a solution to mimic an 'Enum' but is compatible with both
    Python 2.7 and Python 3+.

    """

    def __init__(self):
        """Create the dictionary."""
        with PlayerType() as pt:
            self.__dict__ = dict(
                unknown=pt.unknown,
                audio=pt.audio,
                video=pt.video,
                trs=10,
                image=20,   # currently not supported. to do...
                folder=30   # idem.
            )

    # -----------------------------------------------------------------------

    def __enter__(self):
        return self

    # -----------------------------------------------------------------------

    def __exit__(self, exc_type, exc_value, traceback):
        pass

    # -----------------------------------------------------------------------

    def guess_type(self, filename):
        """Return the expected media type of the given filename.

        :return: (MediaType) Integer value of the media type

        """
        mime_type = "unknown"
        if filename is not None:
            m = mimetypes.guess_type(filename)
            if m[0] is not None:
                mime_type = m[0]

        if "video" in mime_type:
            return self.video

        if "audio" in mime_type:
            return self.audio

        fn, fe = os.path.splitext(filename)
        if fe.startswith("."):
            fe = fe[1:]
        if fe.lower() in [e.lower() for e in sppasRW(None).extensions()]:
            return self.transcription

        return self.unknown
