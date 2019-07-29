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

    src.annotations.Align.sppasalign.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""

import shutil
import os
import logging
import traceback

from sppas import NoDirectoryError
from sppas.src.config import paths
from sppas.src.config import annots
from sppas.src.config import info
from sppas.src.anndata import sppasRW
from sppas.src.anndata import sppasTranscription
from sppas.src.anndata import sppasMedia
import sppas.src.audiodata.aio as audioaio
from sppas.src.resources.mapping import sppasMapping
from sppas.src.models.acm.modelmixer import sppasModelMixer
from sppas.src.files.fileutils import sppasFileUtils

from ..baseannot import sppasBaseAnnotation
from ..searchtier import sppasFindTier
from ..annotationsexc import AnnotationOptionError
from ..annotationsexc import EmptyDirectoryError
from ..annotationsexc import NoInputError

from .tracksio import TracksReaderWriter
from .tracksgmt import TrackSegmenter

# ---------------------------------------------------------------------------

MSG_MODEL_L1_FAILED = (info(1210, "annotations"))
MSG_ALIGN_TRACK = (info(1220, "annotations"))
MSG_ALIGN_FAILED = (info(1230, "annotations"))
MSG_BASIC = (info(1240, "annotations"))
MSG_ACTION_SPLIT_INTERVALS = (info(1250, "annotations"))
MSG_ACTION_ALIGN_INTERVALS = (info(1252, "annotations"))
MSG_ACTION_MERGE_INTERVALS = (info(1254, "annotations"))
MSG_ACTION_EXTRA_TIER = (info(1256, "annotations"))
MSG_TOKENS_DISABLED = (info(1260, "annotations"))
MSG_NO_TOKENS_ALIGN = (info(1262, "annotations"))
MSG_EXTRA_TIER = (info(1270, "annotations"))
MSG_WORKDIR = (info(1280, "annotations"))

# ---------------------------------------------------------------------------


class sppasAlign(sppasBaseAnnotation):
    """SPPAS integration of the Alignment automatic annotation.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2019  Brigitte Bigi

    This class can produce 1 up to 5 tiers with names:

        - PhonAlign
        - TokensAlign (if tokens are given in the input)
        - PhnTokAlign - option (if tokens are given in the input)

    How to use sppasAlign?

    >>> a = sppasAlign()
    >>> a.set_aligner('julius')
    >>> a.load_resources(model_dirname)
    >>> a.run([phones], [audio, tokens], output)

    """

    def __init__(self, log=None):
        """Create a new sppasAlign instance.

        Log is used for a better communication of the annotation process and
        its results.
        If None, logs are redirected to the default logging system.

        :param log: (sppasLog) Human-readable logs.

        """
        sppasBaseAnnotation.__init__(self, "alignment.json", log)
        self.mapping = sppasMapping()
        self._segmenter = TrackSegmenter(model=None, aligner_name="basic")
        self._tracksrw = TracksReaderWriter(sppasMapping())

    # -----------------------------------------------------------------------

    def load_resources(self, model, model_L1=None, **kwargs):
        """Fix the acoustic model directory.

        Create a SpeechSegmenter and AlignerIO.

        :param model: (str) Directory of the acoustic model of the language
        of the text
        :param model_L1: (str) Directory of the acoustic model of
        the mother language of the speaker

        """
        if model_L1 is not None:
            try:
                model_mixer = sppasModelMixer()
                model_mixer.read(model, model_L1)
                output_dir = os.path.join(paths.resources,
                                          "models", "models-mix")
                model_mixer.mix(output_dir, gamma=0.6)
                model = output_dir
            except Exception as e:
                self.logfile.print_message(
                    MSG_MODEL_L1_FAILED.format(str(e)), indent=2,
                    status=annots.warning)

        # Map phoneme names from model-specific to SAMPA and vice-versa
        mapping_filename = os.path.join(model, "monophones.repl")
        if os.path.isfile(mapping_filename):
            try:
                mapping = sppasMapping(mapping_filename)
            except:
                mapping = sppasMapping()
                logging.warning('No mapping file was found in model {:s}'
                                ''.format(model))
        else:
            mapping = sppasMapping()

        # Managers of the automatic alignment task
        self._tracksrw = TracksReaderWriter(mapping)
        self._segmenter.set_model(model)

    # -----------------------------------------------------------------------
    # Methods to fix options
    # -----------------------------------------------------------------------

    def fix_options(self, options):
        """Fix all options.

        Available options are:

            - clean
            - basic
            - aligner

        :param options: (sppasOption)

        """
        for opt in options:

            key = opt.get_key()

            if "clean" == key:
                self.set_clean(opt.get_value())

            elif "basic" == key:
                self.set_basic(opt.get_value())

            elif "aligner" == key:
                self.set_aligner(opt.get_value())

            elif key in ("inputpattern", "outputpattern", "inputoptpattern"):
                self._options[key] = opt.get_value()

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

    def set_aligner(self, aligner_name):
        """Fix the name of the aligner.

        :param aligner_name: (str) Case-insensitive name of the aligner.

        """
        self._options['aligner'] = aligner_name

    # -----------------------------------------------------------------------

    def set_basic(self, basic):
        """Fix the basic option.

        :param basic: (bool) If basic is set to True, a basic segmentation
        will be performed if the main aligner fails.

        """
        self._options['basic'] = basic

    # -----------------------------------------------------------------------
    # Automatic Speech Segmentation
    # -----------------------------------------------------------------------

    def _segment_track_with_basic(self, audio, phn, token, align):
        """Segmentation of a track with the basic alignment system."""
        self.logfile.print_message(MSG_BASIC, indent=2)
        aligner_id = self._segmenter.get_aligner_name()
        self._segmenter.set_aligner('basic')
        msg = self._segmenter.segment(audio, phn, token, align)
        if len(msg) > 0:
            self.logfile.print_message(msg, indent=2, status=annots.info)
        self._segmenter.set_aligner(aligner_id)

    # -----------------------------------------------------------------------

    def _segment_tracks(self, workdir):
        """Call the Aligner to align each unit of a directory.

        :param workdir: (str) directory to get units and put alignments.

        """
        # Search for the number of tracks
        nb_tracks = len(self._tracksrw.get_units(workdir))
        if nb_tracks == 0:
            raise EmptyDirectoryError(workdir)

        # Align each track
        track_number = 0
        while track_number < nb_tracks:

            # Fix track number (starts from 1)
            track_number += 1
            self.logfile.print_message(
                MSG_ALIGN_TRACK.format(number=track_number), indent=1)

            # Fix the expected filenames for this track
            (audio, phn, token, align) = \
                self._tracksrw.get_filenames(workdir, track_number)

            # Perform speech segmentation
            try:
                msg = self._segmenter.segment(audio, phn, token, align)
                if len(msg) > 0:
                    self.logfile.print_message(msg, indent=2, status=annots.info)

            except Exception as e:
                # Something went wrong and the aligner failed
                self.logfile.print_message(
                    MSG_ALIGN_FAILED.format(
                        name=self._segmenter.get_aligner_name()),
                    indent=2,
                    status=annots.error)
                self.logfile.print_message(str(e), indent=3, status=annots.info)
                logging.error(traceback.format_exc())

                # Execute BasicAlign
                if self._options['basic'] is True:
                    self._segment_track_with_basic(audio, phn, token, align)
                # or Create an empty alignment,
                # to get an empty interval in the final result
                else:
                    self._segmenter.segment(audio, None, None, align)

    # -----------------------------------------------------------------------

    def convert(self, phon_tier, tok_tier, input_audio, workdir):
        """Perform speech segmentation of data.

        :param phon_tier: (Tier) phonetization.
        :param tok_tier: (Tier) tokenization, or None.
        :param input_audio: (str) Audio file name.
        :param workdir: (str) The working directory

        :returns: tier_phn, tier_tok

        """
        self._segmenter.set_aligner(self._options['aligner'])
        self._options['aligner'] = self._segmenter.get_aligner_name()

        # Verify if the directory exists
        if os.path.exists(workdir) is False:
            raise NoDirectoryError(workdir)

        # Split input into tracks
        self.logfile.print_message(MSG_ACTION_SPLIT_INTERVALS, indent=1)
        if os.path.exists(workdir) is False:
            os.mkdir(workdir)
        self._tracksrw.split_into_tracks(
            input_audio, phon_tier, tok_tier, workdir)

        # Align each track
        self._segment_tracks(workdir)

        # Merge track alignment results
        self.logfile.print_message(MSG_ACTION_MERGE_INTERVALS, indent=1)
        tier_phn, tier_tok, tier_pron = \
            self._tracksrw.read_aligned_tracks(workdir)

        return tier_phn, tier_tok, tier_pron

    # -----------------------------------------------------------------------

    @staticmethod
    def fix_workingdir(inputaudio=None):
        """Fix the working directory to store temporarily the data.

        :param inputaudio: (str) Audio file name

        """
        sf = sppasFileUtils()
        workdir = sf.set_random()
        while os.path.exists(workdir) is True:
            workdir = sf.set_random()
        os.mkdir(workdir)

        if inputaudio is not None:

            audio_file = os.path.basename(inputaudio)
            sf = sppasFileUtils(audio_file)
            formatted_audio_file = sf.format()
            shutil.copy(inputaudio, os.path.join(workdir, formatted_audio_file))

        return workdir

    # -----------------------------------------------------------------------

    def run(self, input_file, opt_input_file=None, output_file=None):
        """Run the automatic annotation process on an input.

        Important: options could be changed!

        :param input_file: (list of str) (phonemes)
        :param opt_input_file: (list of str) (audio, tokens)
        :param output_file: (str) the output file name
        :returns: (sppasTranscription)

        """
        # Get the phonemes tier to be time-aligned
        parser = sppasRW(input_file[0])
        trs_input = parser.read()
        phon_tier = sppasFindTier.phonetization(trs_input)
        if phon_tier is None:
            raise NoInputError

        # Get the tokens tier to be time-aligned
        try:
            parser = sppasRW(opt_input_file[1])
            trs_input_tok = parser.read()
            tok_tier = sppasFindTier.tokenization(trs_input_tok, "std")
        except:   # IOError, AttributeError:
            tok_tier = None
            self.logfile.print_message(
                MSG_TOKENS_DISABLED, indent=2, status=annots.warning)

        # Get the audio file (check it first)
        input_audio_filename = None
        if opt_input_file is not None and len(opt_input_file) > 0 and\
           opt_input_file[0] is not None:
            try:
                audio = audioaio.open(opt_input_file[0])
                audio.close()
                input_audio_filename = opt_input_file[0]
            except Exception as e:
                self.logfile.print_message(
                    "Error with audio file: "+str(e), indent=2,
                    status=annots.error)

        if input_audio_filename is None:
            self.logfile.print_message(
                "Audio is unavailable. Aligner is set to 'basic' and "
                "no extra option available.",
                indent=1, status=annots.warning)
            # Disable the alignment with audio but perform with basic.
            self._options['aligner'] = "basic"

        # Prepare data
        workdir = sppasAlign.fix_workingdir(input_audio_filename)
        if self._options['clean'] is False:
            self.logfile.print_message(
                MSG_WORKDIR.format(dirname=workdir), indent=3, status=None)

        # Set media
        media = None
        if input_audio_filename is not None:
            extm = os.path.splitext(input_audio_filename)[1].lower()[1:]
            media = sppasMedia(input_audio_filename, mime_type="audio/"+extm)

        # Processing...
        try:
            tier_phn, tier_tok, tier_pron = self.convert(
                phon_tier,
                tok_tier,
                input_audio_filename,
                workdir
            )
            if media is not None:
                tier_phn.set_media(media)

            trs_output = sppasTranscription(self.name)
            trs_output.append(tier_phn)
            if tier_tok is not None:
                tier_tok.set_media(media)
                trs_output.append(tier_tok)
                try:
                    trs_output.add_hierarchy_link(
                        "TimeAlignment", tier_phn, tier_tok)
                except:
                    logging.error('No hierarchy was created between'
                                  'phonemes and tokens')

            if tier_pron is not None:
                tier_pron.set_media(media)
                trs_output.append(tier_pron)
                try:
                    if tier_tok is not None:
                        trs_output.add_hierarchy_link(
                            "TimeAssociation", tier_tok, tier_pron)
                    else:
                        trs_output.add_hierarchy_link(
                            "TimeAlignment", tier_phn, tier_pron)
                except:
                    logging.error('No hierarchy was created between'
                                  'phonemes and tokens')

        except Exception as e:
            self.logfile.print_message(str(e))
            if self._options['clean'] is True:
                shutil.rmtree(workdir)
            raise

        # Save results
        if output_file is not None:
            try:
                # Save in a file
                parser = sppasRW(output_file)
                parser.write(trs_output)
            except Exception:
                if self._options['clean'] is True:
                    shutil.rmtree(workdir)
                raise

        # Remove the working directory we created
        if self._options['clean'] is True:
            shutil.rmtree(workdir)

        return trs_output

    # -----------------------------------------------------------------------

    def get_pattern(self):
        """Pattern this annotation uses in an output filename."""
        return self._options.get("outputpattern", "-palign")

    def get_input_pattern(self):
        """Pattern this annotation expects for its input filename."""
        return self._options.get("inputpattern", "-phon")

    def get_opt_input_pattern(self):
        """Pattern that the annotation can optionally use as input."""
        return self._options.get("inputoptpattern", '-token')
