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

    src.annotations.FaceDetection
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :author:       Brigitte Bigi, Florian Hocquet
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2020  Brigitte Bigi

Track faces of a video.
This package requires video feature, for opencv and numpy dependencies.

TODO:

1. Debug et completer VideoWriter:
    1a. gestion du pattern comme pour les images (personne AVANT pattern)
    1b. ajout colonne and export CSV avec numero du buffer

2. FaceDetection: au moment de la fusion, faire le filtrage selon
   overlap apres passage en portrait

3. GUI:
    3a. ajouter une icone pour les video et gestion des extensions dans FileManager
    3b. titre de la fenetre des annotations: "Configurer..." -> "annot_configure"

"""

from sppas.src.config import cfg
from sppas.src.exceptions import sppasEnableFeatureError

# ---------------------------------------------------------------------------
# Define classes in case opencv&numpy are not installed.
# ---------------------------------------------------------------------------


class FaceTracking(object):
    def __init__(self):
        raise sppasEnableFeatureError("video")


class sppasFaceTrack(object):
    def __init__(self, *args, **kwargs):
        raise sppasEnableFeatureError("video")


# ---------------------------------------------------------------------------
# Import the classes in case the "video" feature is enabled: opencv&numpy
# are both installed and the automatic detections can work.
# ---------------------------------------------------------------------------


if cfg.dep_installed("video"):
    from .facetrack import FaceTracking
    from .sppasfacetrack import sppasFaceTrack

__all__ = (
    "FaceTracking",
    "sppasFaceTrack"
)
