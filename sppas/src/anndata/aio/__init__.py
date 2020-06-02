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

    anndata.aio
    ~~~~~~~~~~~

    Readers and writers of annotated data.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2018  Brigitte Bigi

"""

from .annotationpro import sppasANT
from .annotationpro import sppasANTX
from .anvil import sppasAnvil
from .audacity import sppasAudacity
from .elan import sppasEAF
from .htk import sppasLab
from .phonedit import sppasMRK
from .phonedit import sppasSignaix
from .praat import sppasTextGrid
from .praat import sppasIntensityTier
from .praat import sppasPitchTier
from .sclite import sppasCTM
from .sclite import sppasSTM
from .subtitle import sppasSubRip
from .subtitle import sppasSubViewer
from .subtitle import sppasWebVTT
from .text import sppasRawText
from .text import sppasCSV
from .weka import sppasARFF
from .weka import sppasXRFF
from .xtrans import sppasTDF
from .xra import sppasXRA

# ----------------------------------------------------------------------------
# Variables
# ----------------------------------------------------------------------------

# The use os these variables is DEPRECATED:
# Now: get extension of each format from the sppasRW() parser

ext_sppas = ['.xra', '.[Xx][Rr][Aa]']
ext_praat = ['.TextGrid', '.PitchTier', '.[Tt][eE][xX][tT][Gg][Rr][Ii][dD]','.[Pp][Ii][tT][cC][hH][Tt][Ii][Ee][rR]']
ext_transcriber = ['.trs','.[tT][rR][sS]']
ext_elan = ['.eaf', '[eE][aA][fF]']
ext_ascii = ['.txt', '.csv', '.[cC][sS][vV]', '.[tT][xX][Tt]', '.info']
ext_phonedit = ['.mrk', '.[mM][rR][kK]']
ext_signaix = ['.hz', '.[Hh][zZ]']
ext_sclite = ['.stm', '.ctm', '.[sScC][tT][mM]']
ext_htk = ['.lab', '.mlf']
ext_subtitles = ['.sub', '.srt', '.[sS][uU][bB]', '.[sS][rR][tT]']
ext_anvil = ['.anvil', '.[aA][aN][vV][iI][lL]']
ext_annotationpro = ['.antx', '.[aA][aN][tT][xX]']
ext_xtrans = ['.tdf', '.[tT][dD][fF]']
ext_audacity = ['.aup']
ext_weka = ['.arff', '.xrff']


primary_in = ['.hz', '.PitchTier']
annotations_in = ['.xra', '.TextGrid', '.eaf', '.csv', '.mrk', '.txt', '.stm', '.ctm', '.lab', '.mlf', '.sub', '.srt', '.antx', '.anvil', '.aup', '.trs', '.tdf']

extensions = ['.xra', '.textgrid', '.pitchtier', '.hz', '.eaf', '.trs', '.csv', '.mrk', '.txt', '.mrk', '.stm', '.ctm', '.lab', '.mlf', '.sub', '.srt', 'anvil', '.antx', '.tdf', '.arff', '.xrff']
extensionsul = ext_sppas + ext_praat + ext_transcriber + ext_elan + ext_ascii + ext_phonedit + ext_signaix + ext_sclite + ext_htk + ext_subtitles + ext_anvil + ext_annotationpro + ext_xtrans + ext_audacity + ext_weka
extensions_in = primary_in + annotations_in
extensions_out = ['.xra', '.TextGrid', '.eaf', '.csv', '.mrk', '.txt', '.stm', '.ctm', '.lab', '.mlf', '.sub', '.srt', '.antx', '.arff', '.xrff']
extensions_out_multitiers = ['.xra', '.TextGrid', '.eaf', '.csv', '.mrk', '.antx', '.arff', '.xrff']

# ----------------------------------------------------------------------------


__all__ = (
    "sppasANT",
    "sppasANTX",
    "sppasAnvil",
    "sppasAudacity",
    "sppasEAF",
    "sppasLab",
    "sppasMRK",
    "sppasSignaix",
    "sppasTextGrid",
    "sppasIntensityTier",
    "sppasPitchTier",
    "sppasCTM",
    "sppasSTM",
    "sppasSubRip",
    "sppasSubViewer",
    "sppasWebVTT",
    "sppasRawText",
    "sppasCSV",
    "sppasARFF",
    "sppasXRFF",
    "sppasTDF",
    "sppasXRA",
    "extensions",
    "extensions_in",
    "extensions_out"
)
