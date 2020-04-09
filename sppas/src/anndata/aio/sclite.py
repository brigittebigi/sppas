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

    src.anndata.aio.sclite.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~

Sclite readers and writers: ctm, stm file formats.
The program sclite is a tool for scoring and evaluating the output of
speech recognition systems.

Sclite is part of the NIST SCTK Scoring Tookit:
https://www.nist.gov/itl/iad/mig/tools

File formats description:
http://www1.icsi.berkeley.edu/Speech/docs/sctk-1.2/infmts.htm#ctm_fmt_name_0

Remark:
=======

Because comments are possible, this class uses this function as an
opportunity to store metadata.

"""
import logging
import codecs
import os.path

from sppas.src.config import sg

from sppas.src.utils.makeunicode import sppasUnicode
from ..anndataexc import AioLocationTypeError
from ..anndataexc import AnnDataTypeError
from ..anndataexc import AioLineFormatError
from ..ann.annotation import sppasAnnotation
from ..ann.annlocation import sppasLocation
from ..ann.annlocation import sppasPoint
from ..ann.annlocation import sppasInterval
from ..ann.annlabel import sppasLabel
from ..ann.annlabel import sppasTag

from .text import sppasBaseText
from .aioutils import format_labels, is_ortho_tier
from .aioutils import load

# ---------------------------------------------------------------------------


class sppasBaseSclite(sppasBaseText):
    """SPPAS base Sclite reader and writer.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2018  Brigitte Bigi

    * * * * * Current version does not fully support alternations. * * * * *

    """

    def __init__(self, name=None):
        """Initialize a new sppasBaseSclite instance.

        :param name: (str) This transcription name.

        """
        if name is None:
            name = self.__class__.__name__
        super(sppasBaseSclite, self).__init__(name)

        self.software = "SCTK"

        # override all
        self._accept_multi_tiers = True
        self._accept_no_tiers = True
        self._accept_metadata = False
        self._accept_ctrl_vocab = False
        self._accept_media = True
        self._accept_hierarchy = False
        self._accept_point = False
        self._accept_interval = True
        self._accept_disjoint = False
        self._accept_alt_localization = False
        self._accept_alt_tag = True
        self._accept_radius = False
        self._accept_gaps = True
        self._accept_overlaps = True

    # -----------------------------------------------------------------------

    @staticmethod
    def make_point(midpoint):
        """The localization is a time value, so always a float."""
        try:
            midpoint = float(midpoint)
        except ValueError:
            raise AnnDataTypeError(midpoint, "float")

        return sppasPoint(midpoint, radius=0.005)


# ---------------------------------------------------------------------------


class sppasCTM(sppasBaseSclite):
    """SPPAS ctm reader and writer.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2018  Brigitte Bigi

    This is the reader/writer of the time marked conversation input files to
    be used for scoring the output of speech recognizers via the NIST sclite()
    program. This file format is as follow (in BNF):

    CTM :== <F> <C> <BT> <DUR> word [ <CONF> ]

    where:
        <F> -> The waveform filename.
            NOTE: no path-names or extensions are expected.
        <C> -> The waveform channel. Either "A" or "B".
            The text of the waveform channel is not restricted by sclite.
            The text can be any text string without whitespace so long as the
            matching string is found in both the reference and hypothesis
            input files.
        <BT> -> The begin time (seconds) of the word, measured from the
            start time of the file.
        <DUR> -> The duration (seconds) of the word.
        <CONF> -> Optional confidence score.

    The file must be sorted by the first three columns: the first and the
    second in ASCII order, and the third by a numeric order.

    Lines beginning with ';;' are considered comments and ignored by sclite.
    Blank lines are also ignored.

    * * *  NOT IMPLEMENTED * * *
    ============================

    Alternations are also accepted in some extended CTM.
    Examples:

        ;;
        7654 A * * <ALT_BEGIN>
        7654 A 12.00 0.34 UM
        7654 A * * <ALT>
        7654 A 12.00 0.34 UH
        7654 A * * <ALT_END>
        ;;
        5555 A * * <ALT_BEGIN>
        5555 A 222.77 0.32 BYEBYE
        5555 A * * <ALT>
        5555 A 222.78 0.12 BYE
        5555 A 222.93 0.16 BYE
        5555 A * * <ALT_END>
        ;;
        5555 A * * <ALT_BEGIN>
        5555 A 186.32 0.01 D-
        5555 A * * <ALT>
        5555 A * * <ALT_END>

    """

    @staticmethod
    def detect(filename):
        """Check whether a file is of CTM format or not.

        :param filename: (str) Name of the file to check.
        :returns: (bool)

        """
        # Open and load the content.
        try:
            lines = load(filename)
        except:
            return False

        # Check each line
        for line in lines:
            line = line.strip()
            try:
                # a comment, a blank line, an annotation
                sppasCTM.check_line(line)
            except AioLineFormatError:
                # not the right number of columns
                return False
            except ValueError:
                # can't convert begin/duration into float
                return False

        return True

    # -----------------------------------------------------------------------

    @staticmethod
    def check_line(line, line_number=0):
        """Check whether a line is an annotation or not.

        Raises AioLineFormatError() or ValueError() in case of a
        malformed line.

        :param line: (str)
        :param line_number: (int)
        :returns: (bool)

        """
        # Comment
        if sppasBaseSclite.is_comment(line):
            return False

        # Blank line
        if len(line) == 0:
            return False

        # A column-delimited line
        tab_line = line.split()
        if len(tab_line) < 4 or len(tab_line) > 6:
            raise AioLineFormatError(line_number, line)

        # An alternation
        if tab_line[2] != "*":
            float(tab_line[2])  # begin
            float(tab_line[3])  # duration

        return True

    # -----------------------------------------------------------------------

    def __init__(self, name=None):
        """Initialize a new CTM instance.

        :param name: (str) This transcription name.

        """
        if name is None:
            name = self.__class__.__name__
        super(sppasCTM, self).__init__(name)

        self.default_extension = "ctm"

    # -----------------------------------------------------------------------
    # proceedReader
    # -----------------------------------------------------------------------

    def get_tier(self, line):
        """Return the tier related to the given line.

        Find the tier or create it.

        :param line: (str)
        :returns: (sppasTier)

        """
        tab_line = line.split()
        tier_name = tab_line[0] + "-" + tab_line[1]
        tier = self.find(tier_name)

        if tier is None:
            # Create the media linked to the tier
            media = sppasBaseText.create_media(tab_line[0].strip(), self)

            # Create the tier and set metadata
            tier = self.create_tier(tier_name, media=media)
            tier.set_meta("media_channel", tab_line[1])

            # Do some communication
            if is_ortho_tier(tier_name) is False:
                logging.info(
                    'Tier {:s} is not an orthographic transcription. '
                    'Whitespace in annotations are interpreted as a '
                    'label separator.'.format(tier_name))

        return tier

    # -----------------------------------------------------------------------

    @staticmethod
    def get_score(line):
        """Return the score of the label of a given line.

        :param line: (str)
        :returns: (float) or None if no score is given

        """
        tab_line = line.split()
        score = None
        if len(tab_line) > 5:
            try:
                score = float(tab_line[-1])
            except ValueError:
                pass

        return score

    # -----------------------------------------------------------------------

    def read(self, filename):
        """Read a ctm file and fill the Transcription.

        It creates a tier for each media-channel observed in the file.

        :param filename: (str)

        """
        content = load(filename)
        self._parse_lines(content)

    # -----------------------------------------------------------------------

    def _parse_lines(self, lines):
        """Fill the transcription from the lines of the CTM file."""
        # the number of the current alternation
        in_alt = 0
        # the annotations of the alternations
        alternates = dict()
        # the current tier to fill
        tier = None

        # Extract rows, create tiers and metadata.
        for i, line in enumerate(lines):
            line = sppasUnicode(line).to_strip()

            # a comment can contain metadata
            if sppasBaseSclite.is_comment(line):
                if tier is None:
                    sppasBaseSclite._parse_comment(line, self)
                else:
                    sppasBaseSclite._parse_comment(line, tier)
            # ignore comments and blank lines
            if sppasCTM.check_line(line, i+1) is False:
                continue

            # check for the tier (find it or create it)
            tier = self.get_tier(line)

            # extract information of this annotation
            tab_line = line.strip().split()
            wavname, channel, begin, duration, word = tab_line[:5]
            score = sppasCTM.get_score(line)

            # check for an alternative annotation
            if begin == "*":
                if word == "<ALT_BEGIN>":
                    alternates = dict()
                    in_alt = 1
                    alternates[in_alt] = list()
                elif word == "<ALT>":
                    in_alt += 1
                    alternates[in_alt] = list()
                else:
                    # todo: we SHOULD add ALL the alternations into the tier
                    # but we add only the first one...
                    sppasCTM._add_alt_annotations(tier, alternates[1])
                    # re-init
                    alternates = dict()
                    in_alt = 0
            else:
                ann = sppasCTM._create_annotation(begin, duration, word, score)
                if in_alt == 0:
                    tier.add(ann)
                else:
                    alternates[in_alt].append(ann)

    # -----------------------------------------------------------------------

    @staticmethod
    def _add_alt_annotations(tier, annotations):
        """Add the annotations into the tier.

        :TODO: deal with annotation alternations.

        """
        try:
            for ann in annotations:
                tier.add(ann)
        except Exception:
            pass

    # -----------------------------------------------------------------------

    @staticmethod
    def _create_annotation(begin, duration, word, score):
        """Return the annotation corresponding to data of a line."""
        word = sppasUnicode(word).clear_whitespace()
        label = sppasLabel(sppasTag(word), score)
        begin = float(begin)
        end = begin + float(duration)
        location = sppasLocation(
            sppasInterval(sppasBaseSclite.make_point(begin),
                          sppasBaseSclite.make_point(end)))
        return sppasAnnotation(location, label)

    # -----------------------------------------------------------------------
    # Writer
    # -----------------------------------------------------------------------

    def write(self, filename):
        """Write a transcription into a file.

        :param filename: (str)

        """
        with codecs.open(filename, 'w', sg.__encoding__, buffering=8096) as fp:

            # write an header with the metadata
            fp.write(sppasBaseSclite.serialize_header(filename, self))

            for i, tier in enumerate(self):

                # fix the name of the waveform (for 1st column)
                waveform = "waveform-"+str(i)
                if tier.get_media() is not None:
                    waveform = os.path.basename(
                        tier.get_media().get_filename())

                # fix the name of the channel (for 2nd column)
                channel = "A"
                if tier.is_meta_key('media_channel'):
                    channel = tier.get_meta('media_channel')

                # serialize annotations
                for ann in tier:
                    if ann.get_location().is_point():
                        raise AioLocationTypeError('Sclite CTM', 'points')
                    fp.write(sppasCTM._serialize_annotation(ann,
                                                            waveform,
                                                            channel))

                # write the metadata of this tier
                fp.write(sppasBaseText.serialize_metadata(tier))
                fp.write('\n')

            fp.close()

    # -----------------------------------------------------------------------

    @staticmethod
    def _serialize_annotation(ann, waveform, channel):
        """Convert an annotation into lines for CTM files.

        Empty labels are replaced by "@".

        :param ann: (sppasAnnotation)
        :returns: (str)

        """
        # fix location information
        begin = ann.get_location().get_best().get_begin().get_midpoint()
        duration = ann.get_location().get_best().get_end().get_midpoint() - \
                   begin

        # no label
        if len(ann.get_labels()) == 0:
            content = sppasCTM._serialize_tag(waveform,
                                              channel,
                                              begin,
                                              duration,
                                              sppasTag(""))
        else:
            content = ""
            # all labels will have the same begin/duration.
            # todo: check if sequences of labels are supported by CTM.
            for label in ann.get_labels():

                # only one tag in the label: no alternation
                if len(label) == 1:
                    tag = ann.get_best_tag()
                    score = label.get_score(tag)
                    content += sppasCTM._serialize_tag(waveform,
                                                       channel,
                                                       begin,
                                                       duration,
                                                       tag,
                                                       score)

                # label with alternation tags
                else:
                    content = "{:s} {:s} * * <ALT_BEGIN>\n".format(waveform,
                                                                   channel)
                    for tag, score in label:
                        content += sppasCTM._serialize_tag(waveform,
                                                           channel,
                                                           begin,
                                                           duration,
                                                           tag,
                                                           score)
                        content += "{:s} {:s} * * <ALT>\n".format(waveform,
                                                                  channel)
                    content = content[:-2]
                    content += "_END>\n"

        return content

    # -----------------------------------------------------------------------

    @staticmethod
    def _serialize_tag(waveform, channel, begin, duration, tag, score=None):
        """Convert a tag with its score into a line for CTM files."""
        if tag.is_empty():
            tag_content = "@"
        else:
            tag_content = tag.get_content()

        # serialize the content
        content = "{:s} {:s} {:s} {:s} {:s}" \
                  "".format(waveform,
                            channel,
                            str(begin),
                            str(duration),
                            tag_content)
        if score is not None:
            content += " {:s}" \
                       "".format(str(score))

        return content+"\n"

# ---------------------------------------------------------------------------


class sppasSTM(sppasBaseSclite):
    """SPPAS stm reader and writer.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2018  Brigitte Bigi

    This is the reader/writer for the segment time marked files to be used
    for scoring the output of speech recognizers via the NIST sclite() program.

    STM :== <F> <C> <S> <BT> <ET> [ <LABEL> ] transcript . . .

    where:
        <F> -> The waveform filename.
            NOTE: no pathnames or extensions are expected.
        <C> -> The waveform channel. Either "A" or "B".
            The text of the waveform channel is not restricted by sclite.
            The text can be any text string without whitespace so long as the
            matching string is found in both the reference and hypothesis
            input files.
        <S> -> The speaker id, no restrictions apply to this name.
        <BT> -> The begin time (seconds) of the word, measured from the
            start time of the file.
        <ET> -> The end time (seconds) of the segment.
        <LABEL> -> A comma separated list of subset identifiers enclosed
            in angle brackets
        transcript -> The transcript can take on two forms:
            1) a whitespace separated list of words, or
            2) the string "IGNORE_TIME_SEGMENT_IN_SCORING".
            The list of words can contain a transcript alternation using
            the following BNF format:
                ALTERNATE :== "{" <text> ALT+ "}"
                ALT :== "|" <text>
                TEXT :== 1 thru n words | "@" | ALTERNATE

    The file must be sorted by the first and second columns in ASCII order,
    and the fourth in numeric order.

    Lines beginning with ';;' are considered comments and are ignored.
    Blank lines are also ignored.

    """

    @staticmethod
    def detect(filename):
        """Check whether a file is of STM format or not.

        :param filename: (str) Name of the file to check.
        :returns: (bool)

        """
        # Open and load the content.
        try:
            lines = load(filename)
        except:
            return False

        # Check each line
        for line in lines:
            line = line.strip()
            try:
                # a comment, a blank line, an annotation
                sppasSTM.check_line(line)
            except AioLineFormatError:
                # not the right number of columns
                return False
            except ValueError:
                # can't convert begin/end into float
                return False

        return True

    # -----------------------------------------------------------------------

    @staticmethod
    def check_line(line, line_number=0):
        """Check whether a line is an annotation or not.

        Raises AioLineFormatError() or ValueError() in case of a
        malformed line.

        :param line: (str)
        :param line_number: (int)
        :returns: (bool)

        """
        # Comment
        if sppasBaseSclite.is_comment(line):
            return False

        # Blank line
        if len(line) == 0:
            return False

        # A column-delimited line
        tab_line = line.split()
        if len(tab_line) < 6:
            raise AioLineFormatError(line_number, line)

        float(tab_line[3])  # begin
        float(tab_line[4])  # end

        return True

    # -----------------------------------------------------------------------

    def __init__(self, name=None):
        """Initialize a new STM instance.

        :param name: (str) This transcription name.

        """
        if name is None:
            name = self.__class__.__name__
        super(sppasSTM, self).__init__(name)

        self.default_extension = "stm"

    # -----------------------------------------------------------------------
    # proceedReader
    # -----------------------------------------------------------------------

    def get_tier(self, line):
        """Return the tier related to the given line.

        Find the tier or create it.

        :param line: (str)
        :returns: (sppasTier)

        """
        tab_line = line.split()
        tier_name = tab_line[0] + "-" + tab_line[1] + "-" + tab_line[2]
        tier = self.find(tier_name)

        if tier is None:
            # Create the media linked to the tier
            media = sppasBaseSclite.create_media(tab_line[0].strip(), self)

            # Create the tier and set metadata
            tier = self.create_tier(tier_name, media=media)
            tier.set_meta("media_channel", tab_line[1])
            tier.set_meta("speaker_id", tab_line[2])

        return tier

    # -----------------------------------------------------------------------

    def read(self, filename):
        """Read a ctm file and fill the Transcription.

        It creates a tier for each media-channel observed in the file.

        :param filename: (str)

        """
        content = load(filename)
        self._parse_lines(content)

    # -----------------------------------------------------------------------

    def _parse_lines(self, lines):
        """Fill the transcription from the lines of the STM file."""
        # the current tier to fill
        tier = None

        # Extract rows, create tiers and metadata.
        for i, line in enumerate(lines):
            line = sppasUnicode(line).to_strip()

            # a comment can contain metadata
            if sppasBaseSclite.is_comment(line):
                if tier is None:
                    sppasBaseSclite._parse_comment(line, self)
                else:
                    sppasBaseSclite._parse_comment(line, tier)
            # ignore comments and blank lines
            if sppasSTM.check_line(line, i+1) is False:
                continue

            # check for the tier (find it or create it)
            tier = self.get_tier(line)

            # extract information of this annotation
            tab_line = line.split()
            utterance = " ".join(tab_line[5:])

            if is_ortho_tier(tier.get_name()) is False:
                utterance = utterance.replace(" ", "\n")

            sppasSTM._create_annotation(tab_line[3],
                                        tab_line[4],
                                        utterance,
                                        tier)

    # -----------------------------------------------------------------------

    @staticmethod
    def _create_annotation(begin, end, utterance, tier):
        """Add into the tier the annotation corresponding to data of a line."""
        labels = format_labels(utterance, separator="\n")

        location = sppasLocation(
            sppasInterval(sppasBaseSclite.make_point(begin),
                          sppasBaseSclite.make_point(end)))
        tier.create_annotation(location, labels)

    # -----------------------------------------------------------------------
    # Writer
    # -----------------------------------------------------------------------

    def write(self, filename):
        """Write a transcription into a file.

        :param filename: (str)

        """
        with codecs.open(filename, 'w', sg.__encoding__, buffering=8096) as fp:

            # write an header with the metadata
            fp.write(sppasBaseSclite.serialize_header(filename, self))

            for i, tier in enumerate(self):

                # fix the name of the waveform (for 1st column)
                waveform = "waveform-"+str(i)
                if tier.get_media() is not None:
                    waveform = os.path.basename(
                        tier.get_media().get_filename())

                # fix the name of the channel (for 2nd column)
                channel = "A"
                if tier.is_meta_key('media_channel'):
                    channel = tier.get_meta('media_channel')

                # fix the speaker
                speaker = "A"
                if tier.is_meta_key('speaker_id'):
                    speaker = tier.get_meta('speaker_id')
                elif tier.is_meta_key('speaker_name'):
                    speaker = tier.get_meta('speaker_name')

                # serialize annotations
                for ann in tier:
                    if ann.get_location().is_point():
                        raise AioLocationTypeError('Sclite STM', 'points')
                    fp.write(sppasSTM._serialize_annotation(ann,
                                                            waveform,
                                                            channel,
                                                            speaker))

                # write the metadata of this tier
                fp.write(sppasBaseText.serialize_metadata(tier))
                fp.write('\n')

            fp.close()

    # -----------------------------------------------------------------------

    @staticmethod
    def _serialize_annotation(ann, waveform, channel, speaker):
        """Convert an annotation into lines for STM files.

        Empty labels are replaced by "IGNORE_TIME_SEGMENT_IN_SCORING".
        Alternative tags are included.

        :param ann: (sppasAnnotation)
        :returns: (str)

        """
        # fix location information
        begin = ann.get_location().get_best().get_begin().get_midpoint()
        end = ann.get_location().get_best().get_end().get_midpoint()

        # fix label information
        content = serialize_labels(
            ann.get_labels(),
            separator=" ", empty="IGNORE_TIME_SEGMENT_IN_SCORING", alt=True)

        return "{wav} {cha} {spk} {beg} {end} {lab}\n".format(
            wav=waveform,
            cha=channel,
            spk=speaker,
            beg=str(begin),
            end=str(end),
            lab=content
        )
