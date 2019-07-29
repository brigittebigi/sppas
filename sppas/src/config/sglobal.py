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

    config.sglobal.py
    ~~~~~~~~~~~~~~~~~

"""
import os
import json
from .settings import sppasBaseSettings

# ---------------------------------------------------------------------------


class sppasPathSettings(sppasBaseSettings):
    """Representation of global non-modifiable paths of SPPAS.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2019  Brigitte Bigi

    """

    def __init__(self):
        """Create the sppasPathSettings dictionary."""
        super(sppasPathSettings, self).__init__()

        sppas_dir = os.path.dirname(os.path.dirname(
            os.path.dirname(os.path.abspath(__file__))))

        self.__dict__ = dict(
            sppas=sppas_dir,
            cli=os.path.join(sppas_dir, "bin"),
            etc=os.path.join(sppas_dir, "etc"),
            po=os.path.join(sppas_dir, "po"),
            src=os.path.join(sppas_dir, "src"),
            plugins=os.path.join(os.path.dirname(sppas_dir), "plugins"),
            resources=os.path.join(os.path.dirname(sppas_dir), "resources"),
            samples=os.path.join(os.path.dirname(sppas_dir), "samples"),
            logs=os.path.join(os.path.dirname(sppas_dir), ".logs"),
            wkps=os.path.join(os.path.dirname(sppas_dir), "workspaces"),
            trash=os.path.join(os.path.dirname(sppas_dir), ".trash"),
        )

# ---------------------------------------------------------------------------


class sppasGlobalSettings(object):
    """Representation of global non-modifiable settings of SPPAS.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2019  Brigitte Bigi

    Includes the version, name, author, copyright, etc.

    """

    def __init__(self):
        """Create the dictionary and load the main config file."""
        self.__dict__ = dict()
        self.load()

    # -----------------------------------------------------------------------

    def __enter__(self):
        return self

    # -----------------------------------------------------------------------

    def __exit__(self, exc_type, exc_value, traceback):
        pass

    # -----------------------------------------------------------------------

    def load(self):
        """Load the dictionary of settings from a file."""
        with sppasPathSettings() as sp:
            config = os.path.join(sp.etc, "sppas.json")
            if os.path.exists(config) is False:
                raise OSError("No such file or directory: {:s}".format(config))
            else:
                with open(config) as cfg:
                    self.__dict__ = json.load(cfg)

# ---------------------------------------------------------------------------


class sppasSymbolSettings(sppasBaseSettings):
    """Representation of global non-modifiable symbols of SPPAS.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2019  Brigitte Bigi

    This class defines:

        - unk: the default symbol used by annotations and resources to
          represent unknown entries
        - ortho: symbols used in an orthographic transcription, or after
          a text normalization
        - phone: symbols used to represent events in grapheme to phoneme
          conversion.
        - all: ortho+phone (i.e. all known symbols)

    """

    def __init__(self):
        """Create the sppasSymbolSettings dictionary."""
        super(sppasSymbolSettings, self).__init__()

        self.__dict__ = dict(
            unk="<UNK>",
            phone=sppasSymbolSettings.__phone_symbols(),
            ortho=sppasSymbolSettings.__ortho_symbols(),
            all=sppasSymbolSettings.__all_symbols()
        )

    @staticmethod
    def __ortho_symbols():
        return {
            '#': "silence",
            '+': "pause",
            '*': "noise",
            '@': "laugh",
            'dummy': 'dummy'
        }

    @staticmethod
    def __phone_symbols():
        return {
            'sil': "silence",
            'sp': "pause",
            'noise': "noise",
            'laugh': "laugh",
            'dummy': 'dummy'
        }

    @staticmethod
    def __all_symbols():
        s = dict()
        s.update(sppasSymbolSettings.__ortho_symbols())
        s.update(sppasSymbolSettings.__phone_symbols())
        return s

# ---------------------------------------------------------------------------


class sppasSeparatorSettings(sppasBaseSettings):
    """Representation of global non-modifiable separators of SPPAS.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2019  Brigitte Bigi

    """

    def __init__(self):
        """Create the sppasSeparatorSettings dictionary."""
        super(sppasSeparatorSettings, self).__init__()
        self.__dict__ = dict(
            phonemes="-",    # X-SAMPA standard
            syllables=".",   # X-SAMPA standard
            variants="|"     # used for all alternative tags
        )

# ---------------------------------------------------------------------------


class sppasAnnotationsSettings(sppasBaseSettings):
    """Representation of global non-modifiable settings of annotations.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2019  Brigitte Bigi

    """

    def __init__(self):
        """Create the sppasAnnotationsSettings dictionary."""
        super(sppasAnnotationsSettings, self).__init__()
        self.__dict__ = dict(
            error=-1,
            ok=0,
            warning=1,
            ignore=2,
            info=3,

            extension=".xra",

            # all the types of the annotations implemented into SPPAS
            types=("STANDALONE", "SPEAKER", "INTERACTION"),

            # standard iso639-3 code for an undetermined language.
            UNDETERMINED="und"

        )
