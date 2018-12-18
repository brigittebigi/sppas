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

    src.annotations.Chuncks.sppaschunks.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""
import shutil
import os

from sppas.src.anndata import sppasRW
from sppas.src.anndata import sppasMedia

from ..baseannot import sppasBaseAnnotation
from ..annutils import fix_audioinput, fix_workingdir
from ..annotationsexc import AnnotationOptionError
from ..searchtier import sppasFindTier

from .chunks import Chunks

# ----------------------------------------------------------------------------


class sppasChunks(sppasBaseAnnotation):
    """SPPAS integration of the Chunk Alignment automatic annotation.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2018  Brigitte Bigi

    """
    def __init__(self, model, logfile=None):
        """Create a new sppasChunks instance.

        :param model: (str) the acoustic model directory
        :param logfile: (sppasLog)

        """
        super(sppasChunks, self).__init__(logfile, "Chunks")

        self.chunks = Chunks(model)

        # List of options to configure this automatic annotation
        self._options['clean'] = True  # Remove temporary files
        self._options['silences'] = self.chunks.get_silences()
        self._options['anchors'] = self.chunks.get_anchors()
        self._options['ngram'] = self.chunks.get_ngram_init()
        self._options['ngrammin'] = self.chunks.get_ngram_min()
        self._options['windelay'] = self.chunks.get_windelay_init()
        self._options['windelaymin'] = self.chunks.get_windelay_min()
        self._options['chunksize'] = self.chunks.get_chunk_maxsize()

    # -----------------------------------------------------------------------
    # Methods to fix options
    # -----------------------------------------------------------------------

    def fix_options(self, options):
        """Fix all options.

        Available options are:

            - clean
            - silences
            - anchors
            - ngram
            - ngrammin
            - windelay
            - windelaymin
            - chunksize

        :param options: (sppasOption)

        """
        for opt in options:

            key = opt.get_key()

            if "clean" == key:
                self.set_clean(opt.get_value())

            elif "silences" == key:
                self.chunks.set_silences(opt.get_value())
                self._options['silences'] = opt.get_value()

            elif "anchors" == key:
                self.chunks.set_anchors(opt.get_value())
                self._options['anchors'] = opt.get_value()

            elif "ngram" == key:
                self.chunks.set_ngram_init(opt.get_value())
                self._options['ngram'] = opt.get_value()

            elif "ngrammin" == key:
                self.chunks.set_ngram_min(opt.get_value())
                self._options['ngrammin'] = opt.get_value()

            elif "windelay" == key:
                self.chunks.set_windelay_init(opt.get_value())
                self._options['windelay'] = opt.get_value()

            elif "windelaymin" == key:
                self.chunks.set_windelay_min(opt.get_value())
                self._options['windelaymin'] = opt.get_value()

            elif "chunksize" == key:
                self.chunks.set_chunk_maxsize(opt.get_value())
                self._options['chunksize'] = opt.get_value()

            else:
                raise AnnotationOptionError(key)

    # -----------------------------------------------------------------------

    def set_clean(self, clean):
        """Fix the clean option.

        :param clean: (bool) If clean is set to True then temporary files
        will be removed.

        """
        self._options['clean'] = clean

    # -----------------------------------------------------------------------

    @staticmethod
    def get_phonestier(trs_input):
        """Return the tier with phonetization, or None.

        :param trs_input: (Transcription)
        :returns: (tier)

        """
        if len(trs_input) == 1 and trs_input[0].get_name().lower() == "rawtranscription":
            return trs_input[0]
        if len(trs_input) == 1 and trs_input[0].get_name().lower() == "phonetization":
            if trs_input[0].is_interval():
                return None
            return trs_input[0]

        return None

    # ------------------------------------------------------------------------

    def run(self, phonesname, tokensname, audioname, outputfilename=None):
        """Execute SPPAS Chunks alignment.

        :param phonesname (str) file containing the phonetization
        :param tokensname (str) file containing the tokenization
        :param audioname (str) Audio file name
        :param outputfilename (str) the file name with the result

        :returns: sppasTranscription

        """
        self.print_options()
        self.print_diagnosis(audioname, phonesname, tokensname)

        # Get the tiers to be time-aligned
        # -------------------------------------------------------------------

        parser = sppasRW(phonesname)
        trs_input = parser.read(phonesname)
        phontier = sppasChunks.get_phonestier(trs_input)
        if phontier is None:
            raise IOError("No tier with the raw phonetization was found.")

        try:
            parser.set_filename(tokensname)
            trs_inputtok = parser.read(tokensname)
            toktier = sppasFindTier.tokenization(trs_inputtok)
        except Exception:
            raise IOError("No tier with the raw tokenization was found.")

        # Prepare data
        # -------------------------------------------------------------------

        inputaudio = fix_audioinput(audioname)
        workdir = fix_workingdir(inputaudio)
        if self._options['clean'] is False:
            self.print_message("Working directory is {:s}".format(workdir),
                               indent=3, status=None)

        # Processing...
        # -------------------------------------------------------------------

        try:
            trsoutput = self.chunks.create_chunks(
                inputaudio, phontier, toktier, workdir)
        except Exception as e:
            self.print_message(str(e))
            self.print_message("WORKDIR: {:s}".format(workdir))
            if self._options['clean'] is True:
                shutil.rmtree(workdir)
            raise

        # Set media
        # -------------------------------------------------------------------

        extm = os.path.splitext(audioname)[1].lower()[1:]
        media = sppasMedia(audioname, None, "audio/"+extm)
        trsoutput.add_media(media)
        for tier in trsoutput:
            tier.SetMedia(media)

        # Save results
        # -------------------------------------------------------------------
        if outputfilename is not None:
            try:
                self.print_message("Save automatic chunk alignment: ",
                                   indent=3)
                parser = sppasRW(outputfilename)
                # Save in a file
                parser.write(trsoutput)
            except Exception:
                if self._options['clean'] is True:
                    shutil.rmtree(workdir)
                raise

        # Clean!
        # -------------------------------------------------------------------
        # if the audio file was converted.... remove the tmpaudio
        if inputaudio != audioname:
            os.remove(inputaudio)
        # Remove the working directory we created
        if self._options['clean'] is True:
            shutil.rmtree(workdir)

        return trsoutput

    # -----------------------------------------------------------------------

    @staticmethod
    def get_pattern():
        """Return the pattern this annotation uses in an output filename."""
        return '-chunks'

    @staticmethod
    def get_replace_pattern():
        """Return the pattern this annotation expects for its input filename."""
        return '-phon'
