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

    src.annotations.Align.tracksio.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""
import os
import codecs
import logging
import traceback

from sppas import NoDirectoryError
from sppas.src.anndata import sppasTier
from sppas.src.anndata import sppasLocation
from sppas.src.anndata import sppasInterval
from sppas.src.anndata import sppasPoint
from sppas.src.anndata.aio.aioutils import serialize_labels

from sppas.src.config import sg
from sppas.src.config import separators
from sppas.src.resources.mapping import sppasMapping
from sppas.src.utils.makeunicode import sppasUnicode
from sppas.src.anndata import sppasTag, sppasLabel
import sppas.src.audiodata.autils as autils

from ..annotationsexc import BadInputError
from ..annotationsexc import SizeInputsError

from .aligners.alignerio import AlignerIO

# ------------------------------------------------------------------


class TracksReaderWriter(object):
    """Manager for tracks from/to tiers.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2018  Brigitte Bigi

    """

    DELIMITERS = (" ", separators.variants, separators.phonemes)

    # ------------------------------------------------------------------------

    def __init__(self, mapping):
        """Create a new TracksReaderWriter instance.

        :param mapping: (Mapping) a mapping table to convert the phone set

        """
        # Mapping system for the phonemes
        if mapping is None:
            mapping = sppasMapping()
        if isinstance(mapping, sppasMapping) is False:
            raise TypeError('Expected a sppasMapping() as argument.'
                            'Got {:s} instead.'.format(type(mapping)))
        self._mapping = mapping

    # ------------------------------------------------------------------------

    def get_units(self, dir_name):
        """Return the time units of all tracks.

        :param dir_name: (str) Input directory to get files.

        """
        return ListOfTracks.read(dir_name)

    # ------------------------------------------------------------------------
    # Read files
    # ------------------------------------------------------------------------

    def read_aligned_tracks(self, dir_name):
        """Read time-aligned tracks in a directory.

        :param dir_name: (str) Input directory to get files.
        :returns: (sppasTier, sppasTier, sppasTier)

        """
        tier_phn, tier_tok, tier_pron = \
            TracksReader.read_aligned_tracks(dir_name)

        # map-back phonemes
        self._mapping.set_keep_miss(True)
        self._mapping.set_reverse(False)

        # Map-back time-aligned phonemes to SAMPA
        # include the mapping of alternative tags
        for ann in tier_phn:
            labels = list()
            for label in ann.get_labels():
                tags = list()
                scores = list()
                for tag, score in label:
                    text = tag.get_content()
                    tags.append(sppasTag(self._mapping.map_entry(text)))
                    scores.append(score)
                labels.append(sppasLabel(tags, scores))
            ann.set_labels(labels)

        for ann in tier_pron:
            labels = list()
            for label in ann.get_labels():
                tags = list()
                scores = list()
                for tag, score in label:
                    text = tag.get_content()
                    tags.append(sppasTag(
                        self._mapping.map(text, [separators.phonemes])))
                    scores.append(score)
                labels.append(sppasLabel(tags, scores))
            ann.set_labels(labels)
        return tier_phn, tier_tok, tier_pron

    # ------------------------------------------------------------------------
    # Write files
    # ------------------------------------------------------------------------

    def split_into_tracks(self, input_audio, phon_tier, tok_tier, tok_rescue_tier, dir_align):
        """Write tracks from the given data.

        :param input_audio: (str) Audio file name. Or None if no needed (basic alignment).
        :param phon_tier: (sppasTier) The phonetization tier.
        :param tok_tier: (sppasTier) The tokens tier, or None.
        :param tok_rescue_tier: (sppasTier) The tokens rescue tier, or None.
        :param dir_align: (str) Output directory to store files.

        :returns: PhonAlign, TokensAlign

        """
        # Map phonemes from SAMPA to the expected ones.
        self._mapping.set_keep_miss(True)
        self._mapping.set_reverse(True)

        # Map phonetizations (even the alternatives)
        for ann in phon_tier:
            text = serialize_labels(ann.get_labels(), separator="\n", empty="", alt=True)
            tab = text.split('\n')
            content = list()
            for item in tab:
                item = item.replace('|', separators.variants)
                if item.startswith('{') and item.endswith('}'):
                    content.append(item[1:-1])
                else:
                    content.append(item)

            mapped = self._mapping.map(" ".join(content),
                                       TracksReaderWriter.DELIMITERS)
            ann.set_labels(sppasLabel(sppasTag(mapped)))

        try:
            TracksWriter.write_tracks(input_audio, phon_tier, tok_tier, tok_rescue_tier, dir_align)
        except SizeInputsError:
            # number of intervals are not matching
            TracksWriter.write_tracks(input_audio, phon_tier, None, None, dir_align)
        except BadInputError:
            # either phonemes or tokens is wrong... re-try with phonemes only
            TracksWriter.write_tracks(input_audio, phon_tier, None, None, dir_align)

    # ------------------------------------------------------------------------

    @staticmethod
    def get_filenames(track_dir, track_number):
        """Return file names corresponding to a given track.

        :param track_dir: (str)
        :param track_number: (int)
        :returns: (audio, phn, tok, align) file names

        """
        audio = TrackNamesGenerator.audio_filename(track_dir, track_number)
        phn = TrackNamesGenerator.phones_filename(track_dir, track_number)
        tok = TrackNamesGenerator.tokens_filename(track_dir, track_number)
        align = TrackNamesGenerator.align_filename(track_dir, track_number)
        return audio, phn, tok, align

# ----------------------------------------------------------------------------


class TrackNamesGenerator:
    """Manage names of the files for a given track number.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2018  Brigitte Bigi

    """

    @staticmethod
    def audio_filename(track_dir, track_number):
        """Return the name of the audio file."""
        return os.path.join(track_dir,
                            "track_{:06d}.wav".format(track_number))

    @staticmethod
    def phones_filename(track_dir, track_number):
        """Return the name of the file with Phonetization."""
        return os.path.join(track_dir,
                            "track_{:06d}.phn".format(track_number))

    @staticmethod
    def tokens_filename(track_dir, track_number):
        """Return the name of the file with Tokenization."""
        return os.path.join(track_dir,
                            "track_{:06d}.tok".format(track_number))

    @staticmethod
    def align_filename(track_dir, track_number, ext=None):
        """Return the name of the time-aligned file, without extension."""
        if ext is None:
            return os.path.join(track_dir,
                                "track_{:06d}".format(track_number))
        return os.path.join(track_dir,
                            "track_{:06d}.{:s}".format(track_number, ext))

# ----------------------------------------------------------------------------


class TracksReader:
    """Read time-aligned tracks.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2018  Brigitte Bigi

    Manage tracks for the time-aligned phonemes and tokens.

    """

    RADIUS = 0.005  # Half-size of a frame in the acoustic model

    # ------------------------------------------------------------------------

    @staticmethod
    def read_aligned_tracks(dir_name):
        """Read a set of alignment files and set as tiers.

        :param dir_name: (str) input directory containing a set of units
        :returns: PhonAlign, TokensAlign

        """
        # Read the time values of each track from a file
        units = ListOfTracks.read(dir_name)

        # Check if the directory exists
        if os.path.exists(dir_name) is False:
            raise NoDirectoryError(dirname=dir_name)

        # Create new tiers
        tier_phn = sppasTier("PhonAlign")
        tier_tok = sppasTier("TokensAlign")
        tier_pron = sppasTier("PronTokAlign")

        # Explore each unit to get alignments
        track_number = 1
        for unit_start, unit_end in units:

            # Fix filename to read, and load the content
            basename = \
                TrackNamesGenerator.align_filename(dir_name, track_number)
            try:
                _phons, _words, _prons = AlignerIO.read_aligned(basename)
            except IOError:
                _phons, _words, _prons = [], [], []

            # Append alignments in tiers
            TracksReader._add_aligned_track_into_tier(tier_phn, _phons, unit_start, unit_end)
            TracksReader._add_aligned_track_into_tier(tier_tok, _words, unit_start, unit_end)
            TracksReader._add_aligned_track_into_tier(tier_pron, _prons, unit_start, unit_end)

            track_number += 1

        return tier_phn, tier_tok, tier_pron

    # ------------------------------------------------------------------------

    @staticmethod
    def _add_aligned_track_into_tier(tier, tdata, delta, unitend):
        """Append a list of (start, end, text, score) into the tier.

        Shift start/end of a delta value and set the last end value.

        """
        try:

            for i, t in enumerate(tdata):

                # fix the location - an interval
                (loc_s, loc_e, contents, scores) = t
                loc_s += delta
                loc_e += delta
                if i == (len(tdata)-1):
                    loc_e = unitend
                location = sppasLocation(
                        sppasInterval(
                            sppasPoint(loc_s, TracksReader.RADIUS),
                            sppasPoint(loc_e, TracksReader.RADIUS)
                        ))

                # fix the label
                # allow to work with alternative tags
                tags = [sppasTag(c) for c in contents.split('|')]
                if scores is not None:
                    tag_scores = [float(s) for s in scores.split('|')]
                else:
                    tag_scores = None
                label = sppasLabel(tags, tag_scores)

                tier.create_annotation(location, label)

        except:
            logging.error('The following data were not added to the tier '
                          '{:s} at position {:f}: {:s}'
                          ''.format(tier.get_name(), delta, str(tdata)))
            logging.error(traceback.format_exc())
            return False

        return True

# ---------------------------------------------------------------------------


class TracksWriter:
    """Write non-aligned track files.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2018  Brigitte Bigi

    Manage tracks for the audio, the phonetization and the tokenization.

    """

    @staticmethod
    def write_tracks(input_audio, phon_tier, tok_tier, tok_rescue_tier, dir_align):
        """Main method to write tracks from the given data.

        :param input_audio: (src) File name of the audio file.
        :param phon_tier: (Tier) Tier with phonetization to split.
        :param tok_tier: (Tier) Tier with tokenization to split.
        :param tok_rescue_tier: (Tier) Tier with tokens to split.
        :param dir_align: (str) Directory to put units.

        :returns: List of tracks with (start-time end-time)

        """
        # In any case, the phonetization is written
        TracksWriter._write_text_tracks(phon_tier, tok_tier, tok_rescue_tier, dir_align)

        # No need of an audio if basic alignment
        if input_audio is not None:
            if phon_tier.is_interval() is False:
                raise BadInputError

            if tok_tier is not None:
                if tok_tier.is_interval() is False:
                    if tok_rescue_tier.is_interval() is False:
                        raise BadInputError

            tracks = phon_tier.get_midpoint_intervals()
            TracksWriter._write_audio_tracks(input_audio, tracks, dir_align)

        else:
            if phon_tier.is_interval() is True:
                tracks = phon_tier.get_midpoint_intervals()
            else:
                # probably basic alignment of a written text!
                tracks = phon_tier.get_midpoint_points()

        # Write the time values of each track into a file
        ListOfTracks.write(dir_align, tracks)

    # ------------------------------------------------------------------------

    @staticmethod
    def _write_audio_tracks(input_audio, units, dir_align, silence=0.):
        """Write the first channel of an audio file into separated track files.

        Re-sample to 16000 Hz, 16 bits.

        :param input_audio: (src) File name of the audio file.
        :param units: (list) List of tuples (start-time,end-time) of tracks.
        :param dir_align: (str) Directory to write audio tracks.
        :param silence: (float) Duration of a silence to surround the tracks.

        """
        channel = autils.extract_audio_channel(input_audio, 0)
        channel = autils.format_channel(channel, 16000, 2)

        for track, u in enumerate(units):
            (s, e) = u
            track_channel = \
                autils.extract_channel_fragment(channel, s, e, silence)
            track_name = \
                TrackNamesGenerator.audio_filename(dir_align, track + 1)
            autils.write_channel(track_name, track_channel)

    # ------------------------------------------------------------------------

    @staticmethod
    def _write_text_tracks(phon_tier, tok_tier, tok_rescue_tier, dir_align):
        """Write tokenization and phonetization into separated track files.

        :param phon_tier: (sppasTier) time-aligned tier with phonetization
        :param tok_tier: (sppasTier) time-aligned tier with tokenization
        :param tok_rescue_tier: (sppasTier) time-aligned tier with tokenization
        :param dir_align: (str) the directory to write tracks.

        """
        last_chance_tier = TracksWriter._create_tok_tier(phon_tier)
        if tok_rescue_tier is None:
            tok_rescue_tier = last_chance_tier
        if tok_tier is None:
            tok_tier = tok_rescue_tier

        if len(phon_tier) != len(tok_tier):
            if len(phon_tier) != len(tok_rescue_tier):
                raise SizeInputsError(len(phon_tier), len(tok_tier))

        for i in range(len(phon_tier)):
            phon_ann = phon_tier[i]
            phon_ann_labels = serialize_labels(phon_ann.get_labels())
            TracksWriter._write_phonemes(phon_ann, dir_align, i + 1)

            tok_ann = tok_tier[i]
            tok_ann_labels = serialize_labels(tok_ann.get_labels())
            if len(phon_ann_labels.split()) != len(tok_ann_labels.split()):
                tok_ann = tok_rescue_tier[i]
                tok_ann_labels = serialize_labels(tok_ann.get_labels())
                logging.warning("Alignment of tokens rescued at interval {}".format(i))
                if len(phon_ann_labels.split()) != len(tok_ann_labels.split()):
                    tok_ann = last_chance_tier[i]
            TracksWriter._write_tokens(tok_ann, dir_align, i + 1)

    # ------------------------------------------------------------------------

    @staticmethod
    def _create_tok_tier(phon_tier):
        """Create a tier with tokens like 'w_1 w_2...w_n' from phonemes.

        :param phon_tier: (sppasTier) time-aligned tier with phonetization
        :returns: (sppasTier)

        """
        tok_tier = phon_tier.copy()
        for ann in tok_tier:
            tag = ann.get_best_tag()
            if tag.is_silence() is False:
                phonemes = serialize_labels(ann.get_labels(), " ", "", alt=True)
                nb_phonemes = len(phonemes.split(' '))
                tokens = " ".join(
                    ["w_" + str(i + 1) for i in range(nb_phonemes)]
                )
                ann.set_labels([sppasLabel(sppasTag(tokens))])

        return tok_tier

    # ------------------------------------------------------------------------

    @staticmethod
    def _write_phonemes(annotation, dir_align, number):
        """Write the phonetization of a track in a file.

        :param annotation: (sppasAnnotation)
        :param dir_align: (str)
        :param number: (int)

        """
        phonemes = annotation.serialize_labels(
            separator=" ",
            empty="",
            alt=True
        )
        fnp = TrackNamesGenerator.phones_filename(dir_align, number)
        with codecs.open(fnp, "w", sg.__encoding__) as fp:
            fp.write(phonemes)

    # ------------------------------------------------------------------------

    @staticmethod
    def _write_tokens(annotation, dir_align, number):
        """Write the tokenization of a track in a file.

        :param annotation: (sppasAnnotation)
        :param dir_align: (str)
        :param number: (int)

        """
        tokens = annotation.serialize_labels(
            separator=" ",
            empty="",
            alt=True
        )
        fnt = TrackNamesGenerator.tokens_filename(dir_align, number)
        with codecs.open(fnt, "w", sg.__encoding__) as fp:
            fp.write(tokens)

# ---------------------------------------------------------------------------


class ListOfTracks:
    """Manage the file with a list of tracks (units, ipus...).

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2018  Brigitte Bigi

    """

    DEFAULT_FILENAME = "tracks.list"

    # ------------------------------------------------------------------

    @staticmethod
    def read(dir_name):
        """Return a list of (start-time end-time).

        :param dir_name: Name of the directory with the file to read.
        :returns: list of units

        """
        filename = os.path.join(dir_name, ListOfTracks.DEFAULT_FILENAME)
        if os.path.exists(filename) is False:
            raise IOError('The list of tracks is missing of the directory '
                          '{:s}'.format(dir_name))

        with open(filename, 'r') as fp:
            lines = fp.readlines()
            fp.close()

        # Each line corresponds to a track,
        # with a couple 'start end' of float values.
        _units = list()
        for line in lines:
            s = sppasUnicode(line)
            line = s.to_strip()
            _tab = line.split()
            if len(_tab) >= 2:
                _units.append((float(_tab[0]), float(_tab[1])))

        return _units

    # ------------------------------------------------------------------

    @staticmethod
    def write(dir_name, units):
        """Write a list file (start-time end-time).

        :param dir_name: Name of the directory with the file to read.
        :param units: List of units to write.

        """
        if len(units) == 0:
            raise IOError('No filled tracks were founds in the annotations.')

        # convert points into intervals.
        u = units[0]
        if isinstance(u, (tuple, list)) is False:
            u = list()
            for i in range(1, len(units)+1):
                u.append((i, i+1))
            units = u

        filename = os.path.join(dir_name, ListOfTracks.DEFAULT_FILENAME)
        with open(filename, 'w') as fp:
            for start, end in units:
                fp.write("{:6f} {:6f}\n".format(start, end))
            fp.close()
