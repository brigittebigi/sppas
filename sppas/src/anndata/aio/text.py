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

    src.anndata.aio.text.py
    ~~~~~~~~~~~~~~~~~~~~~~~

Text readers and writers for raw text, column-based text, csv.

"""

import codecs
import os
import datetime
import re

from sppas.src.config import sg
from sppas.src.utils.makeunicode import sppasUnicode
from sppas.src.utils.datatype import sppasType

from ..anndataexc import AioMultiTiersError
from ..anndataexc import AioLineFormatError
from ..ann.annlocation import sppasLocation
from ..ann.annlocation import sppasPoint
from ..ann.annlocation import sppasInterval
from ..media import sppasMedia

from .basetrs import sppasBaseIO
from .aioutils import format_labels, is_ortho_tier, serialize_labels
from .aioutils import load

# ---------------------------------------------------------------------------

COLUMN_SEPARATORS = [' ', ',', ';', ':', '\t']

# ---------------------------------------------------------------------------


class sppasBaseText(sppasBaseIO):
    """SPPAS base text reader and writer.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      contact@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2019  Brigitte Bigi

    """

    def __init__(self, name=None):
        """Initialize a new sppasBaseText instance.

        :param name: (str) This transcription name.

        """
        if name is None:
            name = self.__class__.__name__
        super(sppasBaseText, self).__init__(name)

        self.software = ""

        self._accept_multi_tiers = True
        self._accept_no_tiers = True
        self._accept_metadata = False
        self._accept_ctrl_vocab = False
        self._accept_media = False
        self._accept_hierarchy = False
        self._accept_point = True
        self._accept_interval = True
        self._accept_disjoint = False
        self._accept_alt_localization = False
        self._accept_alt_tag = False
        self._accept_radius = False
        self._accept_gaps = True
        self._accept_overlaps = True

    # -----------------------------------------------------------------------

    @staticmethod
    def make_point(data):
        """Convert data into the appropriate sppasPoint().

        No radius is fixed if data is an integer.
        A default radius of 0.001 seconds if data is a float.

        :param data: (any type)
        :returns: sppasPoint().

        """
        try:
            if data.isdigit() is True:
                return sppasPoint(int(data))
        except AttributeError:
            # data is not a string
            data = float(data)

        return sppasPoint(data, radius=0.001)

    # -----------------------------------------------------------------------

    @staticmethod
    def is_comment(line):
        """Check if the line is a comment, ie starts with ';;'.

        :param line: (str/unicode)
        :returns: boolean

        """
        sp = sppasUnicode(line)
        line = sp.to_strip()

        return line.startswith(";;")

    # -----------------------------------------------------------------------

    @staticmethod
    def format_quotation_marks(text):
        """Remove initial and final quotation mark.

        :param text: (str/unicode) Text to clean
        :returns: (unicode) the text without initial and final quotation mark.

        """
        text = sppasUnicode(text).to_strip()
        if len(text) >= 2:
            if (text.startswith('"') and text.endswith('"')) \
              or (text.startswith("'") and text.endswith("'")):
                text = text[1:-1]

        return text

    # -----------------------------------------------------------------------

    @staticmethod
    def split_lines(lines, separator=" "):
        """Split the lines with the given separator.

        :param lines: (list) List of lines
        :param separator: (char) a character used to separate columns of the lines
        :returns: Lines (list) separated by columns (list) or None if error.

        """
        line_columns = list()
        nb_col = -1

        for line in lines:
            # do not use sppasUnicode().to_strip() which will format
            # all separators... So, use the standard strip() method.
            line = line.strip()

            # ignore empty lines and comments
            if len(line) == 0 or line.startswith(';;'):
                continue

            # estimate the number of columns and
            # check if it matches with the previous ones
            split_line = line.split(separator)

            if nb_col == -1:
                nb_col = len(split_line)
            elif nb_col != len(split_line):
                return None

            line_columns.append(split_line)

        return line_columns

    # -----------------------------------------------------------------------

    @staticmethod
    def _parse_comment(comment, meta_object):
        """Parse a comment and eventually fill metadata.

        :param comment: (str) A line of a file
        :param meta_object: (sppasMeta)

        """
        comment = comment.replace(";;", "")
        comment = comment.strip()
        if '=' in comment:
            tab_comment = comment.split('=')
            if len(tab_comment) == 2:
                meta_key = tab_comment[0].strip()
                meta_val = tab_comment[1].strip()
                meta_object.set_meta(meta_key, meta_val)

    # -----------------------------------------------------------------------

    @staticmethod
    def fix_location(content_begin, content_end):
        """Fix the location from the content of the data.

        :param content_begin: (str) The content of a column representing
        the begin of a localization.
        :param content_end: (str) The content of a column representing
        the end of a localization.
        :returns: sppasLocation or None

        """
        begin = sppasBaseText.format_quotation_marks(content_begin)
        end = sppasBaseText.format_quotation_marks(content_end)

        has_begin = len(begin.strip()) > 0
        has_end = len(end.strip()) > 0

        if has_begin and has_end:
            b = sppasBaseText.make_point(begin)
            e = sppasBaseText.make_point(end)
            if b == e:
                localization = b
            else:
                localization = sppasInterval(b, e)

        elif has_begin:
            localization = sppasBaseText.make_point(begin)

        elif has_end:
            localization = sppasBaseText.make_point(end)

        else:
            return None

        return sppasLocation(localization)

    # -----------------------------------------------------------------------

    @staticmethod
    def serialize_header(filename, meta_object):
        """Create a comment with the metadata to be written.

        :param filename: (str) Name of the file to serialize.
        :param meta_object: (sppasMeta)

        """
        header = sppasBaseText.serialize_header_software()
        header += ";; file_writer={:s}\n".format(meta_object.__class__.__name__)
        header += ";; file_name={:s}\n".format(os.path.basename(filename))
        header += ";; file_path={:s}\n".format(os.path.dirname(filename))
        header += ";; file_ext={:s}\n".format(os.path.splitext(filename)[1])
        header += ";;\n"
        header += sppasBaseText.serialize_metadata(meta_object)
        header += ";;\n"

        return header

    # -----------------------------------------------------------------------

    @staticmethod
    def serialize_header_software():
        """Serialize the header of a file with SPPAS information."""
        comment = ";; \n"
        comment += ";; software_name={:s}\n".format(sg.__name__)
        comment += ";; software_version={:s}\n".format(sg.__version__)
        comment += ";; software_url={:s}\n".format(sg.__url__)
        comment += ";; software_contact={:s}\n".format(sg.__contact__)
        comment += ";; software_copyright={:s}\n".format(sg.__copyright__)
        comment += ";; \n"
        now = datetime.datetime.now()
        comment += ";; file_write_date={:d}-{:d}-{:d}\n" \
                   "".format(now.year, now.month, now.day)

        return comment

    # -----------------------------------------------------------------------

    @staticmethod
    def serialize_metadata(meta_object):
        """Serialize the metadata of an object in a multi-lines comment."""
        meta_keys = ["file_write_date", "file_writer",
                     "file_name", "file_path", "file_ext"]
        comment = ""
        for meta in meta_object.get_meta_keys():
            if "software" not in meta and meta not in meta_keys:
                comment += ';; {:s}={:s}\n'.format(meta, meta_object.get_meta(meta))

        return comment

    # -----------------------------------------------------------------------

    @staticmethod
    def create_media(media_url, meta_object):
        """Return the media of the given name (create it if necessary).

        :param media_url: (str) Name (url) of the media to search/create
        :param meta_object: (sppasTranscription)
        :returns: (sppasMedia)

        """
        media = None
        idt = media_url

        # Search the media in the object
        for m in meta_object.get_media_list():
            if m.get_filename() == idt:
                media = m

        if media is None:
            # Create a new media
            media = sppasMedia(idt)
            # Add the newly created media in the given object
            meta_object.add_media(media)

        return media

    # -----------------------------------------------------------------------

    @staticmethod
    def get_lines_columns(lines):
        """Column-delimited? Search for the relevant separator.

        :param lines: (list of str)
        :returns: lines (list) of columns (list of str)

        """
        nb_col = 0
        columns = None
        sep = None

        for separator in COLUMN_SEPARATORS:
            columns = sppasBaseText.split_lines(lines, separator)
            if columns is not None and \
                    len(columns) > 0 and \
                    len(columns[0]) > nb_col:
                sep = separator
        if sep is not None:
            columns = sppasBaseText.split_lines(lines, sep)

        return columns

# ----------------------------------------------------------------------------


class sppasRawText(sppasBaseText):
    """SPPAS raw text reader and writer.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      contact@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2018  Brigitte Bigi

    RawText does not support multiple tiers for writing (ok for reading).
    RawText accepts no tiers.
    RawText does not support alternatives labels nor locations. Only the ones
    with the best score are saved.
    RawText can save only one tier.
    RawText does not support controlled vocabularies.
    RawText does not support hierarchy.
    RawText does not support metadata.
    RawText does not support media assignment.
    RawText supports points and intervals. It does not support disjoint intervals.
    RawText does not support alternative tags.
    RawText does not support radius.

    RawText supports comments: such lines are starting with ';;'.

    """

    @staticmethod
    def detect(filename):
        """Detect if file is text."""
        # Open and load the content.
        try:
            with codecs.open(filename, 'r', sg.__encoding__) as fp:
                fp.readline()
                fp.close()
        except IOError:
            # can't open the file
            return False
        except UnicodeDecodeError:
            # can't open with SPPAS default encoding
            return False

        return True

    # -----------------------------------------------------------------------

    def __init__(self, name=None):
        """Initialize a new sppasRawText instance.

        :param name: (str) This transcription name.

        """
        if name is None:
            name = self.__class__.__name__
        super(sppasRawText, self).__init__(name)

        self.default_extension = "txt"

        self._accept_multi_tiers = False

    # -----------------------------------------------------------------------

    def read(self, filename):
        """Read a raw file and fill the Transcription.

        The file can be a simple raw text (without location information).
        It can also be a column-based (table-style) file, so that each
        column represents the annotation of a tier (1st and 2nd columns
        are indicating the location).

        :param filename: (str)

        """
        lines = load(filename, sg.__encoding__)
        self._parse_lines(lines)

    # -----------------------------------------------------------------------

    def _parse_lines(self, lines):
        """Fill the transcription from the lines of the TXT file."""
        columns = sppasBaseText.get_lines_columns(lines)

        if columns is None:
            self.__format_raw_lines(lines)

        if len(columns) == 0:
            return
        if len(columns[0]) == 1:
            self.__format_raw_lines(lines)
        else:
            self.__format_columns(columns)

    # -----------------------------------------------------------------------

    def __format_raw_lines(self, lines):
        """Format lines of a raw text.

        - Each 'CR/LF' is a unit separator, NOT added into the transcription.
        - Each '#' is a unit separator, added as a silence mark into the
          transcription.
        - Each line starting by ";;" is considered a comment.
        - Blank lines are ignored.

        :param lines: (list) List of lines.

        """
        tier = self.create_tier('RawTranscription')

        n = 1
        for line in lines:

            line = sppasUnicode(line).to_strip()

            # ignore blank lines
            if len(line) == 0:
                continue

            # a comment can contain metadata
            if sppasBaseText.is_comment(line):
                sppasBaseText._parse_comment(line, self)
                continue

            if "#" in line:
                phrases = map(lambda s: s.strip(), re.split('(#)', line))
                # The separator '#' is included in the tab
                for phrase in phrases:
                    if len(phrase) > 0:
                        self._create_annotation(tier, n, phrase)
                        n += 1

            elif len(line) > 0:
                self._create_annotation(tier, n, line)
                n += 1

    # -----------------------------------------------------------------------

    @staticmethod
    def _create_annotation(tier, rank, utterance):
        """Add the annotation corresponding to data of a line."""
        labels = format_labels(utterance)
        location = sppasLocation(sppasPoint(rank))
        tier.create_annotation(location, labels)

    # -----------------------------------------------------------------------

    def __format_columns(self, columns):
        """Format columns of a column-based text.

        :param columns: (list) List of columns (list).

        - 1st column: the begin localization (required)
        - 2nd column: the end localization (required)
        - 3rd column: the label of the 1st tier (optional)
        - 4th column: the label of the 2nd tier (optional)
        - ...
        or
        - the label is in the 1st column
        - 2nd/3rd columns are begin/end

        """
        nb_col = len(columns[0])
        # Create the tiers (one tier per column) but
        # the name of the tiers are unknown...
        self.create_tier('Transcription')
        for i in range(3, nb_col):
            self.create_tier('Tier-{:d}'.format(i-2))

        # Create the annotations of the tiers
        for instance in columns:
            if nb_col == 3 and sppasBaseIO.is_number(instance[0]) is False:
                location = sppasBaseText.fix_location(instance[1], instance[2])
                labels = format_labels(instance[0])
                self[0].create_annotation(location, labels)
            else:
                location = sppasBaseText.fix_location(instance[0], instance[1])
                for i in range(2, nb_col):
                    labels = format_labels(instance[i])
                    self[i-2].create_annotation(location, labels)

    # -----------------------------------------------------------------------

    def write(self, filename):
        """Write a RawText file.

        Labels are preserved, ie. separated by whitespace and alternative tags included.

        :param filename: (str)

        """
        if len(self._tiers) > 1:
            raise AioMultiTiersError(self.__class__.__name__)

        with codecs.open(filename, 'w', sg.__encoding__, buffering=8096) as fp:

            # no tier in the file.
            if self.is_empty() is True:
                return

            # write an header with the metadata
            fp.write(sppasBaseText.serialize_header(filename, self))

            tier = self[0]
            point = tier.is_point()
            if tier.is_empty():
                return

            if tier.get_name() == "RawTranscription":
                for ann in tier:
                    t = serialize_labels(ann.get_labels(), " ", "", True)
                    fp.write(t + '\n')
            else:
                for ann in tier:
                    t = serialize_labels(
                        ann.get_labels(), separator=" ", empty="", alt=True)
                    if point:
                        mp = ann.get_lowest_localization().get_midpoint()
                        fp.write("{}\t\t{}\n".format(mp, t))
                    else:
                        b = ann.get_lowest_localization().get_midpoint()
                        e = ann.get_highest_localization().get_midpoint()
                        fp.write("{}\t{}\t{}\n".format(b, e, t))

            fp.close()

# ----------------------------------------------------------------------------


class sppasCSV(sppasBaseText):
    """SPPAS CSV reader and writer.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      contact@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2018  Brigitte Bigi

    """

    @staticmethod
    def detect(filename):
        """Check whether a file is of CSV format or not.

        :param filename: (str) Name of the file to check.
        :returns: (bool)

        """
        csv_line = re.compile(
            '^(("([^"]|"")*"|[^",]*),)+("([^"]|"")*"|[^",]*)$')

        # Open and load the content.
        try:
            lines = load(filename)
        except:
            return False

        for line in lines:
            if not csv_line.match(line):
                return False
        return True

    # -----------------------------------------------------------------------

    def __init__(self, name=None):
        """Initialize a new CSV instance.

        :param name: (str) This transcription name.

        """
        if name is None:
            name = self.__class__.__name__
        super(sppasCSV, self).__init__(name)

        self.default_extension = "csv"

        self._accept_multi_tiers = True

    # -----------------------------------------------------------------------

    def read(self, filename, signed=True):
        """Read a CSV file.

        :param filename: (str)
        :param signed: (bool) Indicate if the encoding is UTF-8 signed.
        If False, the default encoding is used.

        """
        enc = sg.__encoding__
        if signed is True:
            enc = 'utf-8-sig'

        lines = load(filename, enc)
        if len(lines) > 0:
            self.format_columns_lines(lines)

    # -----------------------------------------------------------------------

    def format_columns_lines(self, lines):
        """Append lines content into self.

        The algorithm doesn't suppose that the file is sorted by tiers

        :param lines: (list)

        """
        for separator in COLUMN_SEPARATORS:

            i = 0
            for line in lines:

                row = line.split(separator)
                if len(row) < 4:
                    continue

                col1 = sppasBaseText.format_quotation_marks(row[0])
                col2 = sppasBaseText.format_quotation_marks(row[1])
                col3 = sppasBaseText.format_quotation_marks(row[2])
                content = sppasBaseText.format_quotation_marks(
                    " ".join(row[3:]))

                if sppasType.is_number(col1):  # and sppasType.is_number(col2):
                    begin = col1
                    end = col2
                    tier_name = col3
                elif sppasType.is_number(col2):  # and sppasType.is_number(col3):
                    begin = col2
                    end = col3
                    tier_name = col1
                else:
                    continue

                # Fix the name of the tier (column 1)
                tier = self.find(tier_name)
                if tier is None:
                    tier = self.create_tier(tier_name)

                # Fix the location (columns 2 and 3)
                location = sppasBaseText.fix_location(begin, end)
                if location is None:
                    continue

                # Add the new annotation.
                if is_ortho_tier(tier_name):
                    label = format_labels(content, separator="\n")
                else:
                    label = format_labels(content, separator=" ")
                tier.create_annotation(location, label)

                i += 1

            # we have found the good separator
            if i == len(lines):
                return separator

        # we failed to find a separator to get the same number of columns
        # in each line
        raise AioLineFormatError(1, lines[0])

    # -----------------------------------------------------------------------

    def write(self, filename, signed=True):
        """Write a CSV file.

        Because the labels can be only on one line, the whitespace is used
        to separate labels (instead of CR in other formats like textgrid).

        :param filename: (str)
        :param signed: (bool) Indicate if the encoding is UTF-8 signed.
        If False, the default encoding is used.

        """
        enc = sg.__encoding__
        if signed is True:
            enc = 'utf-8-sig'

        with codecs.open(filename, 'w', enc, buffering=8096) as fp:

            for tier in self._tiers:

                name = tier.get_name()
                point = tier.is_point()

                for ann in tier:
                    content = serialize_labels(
                        ann.get_labels(), separator=" ", empty="", alt=True)
                    if point:
                        mp = ann.get_lowest_localization().get_midpoint()
                        fp.write('"{}",{},,"{}"\n'
                                 ''.format(name, mp, content))
                    else:
                        b = ann.get_lowest_localization().get_midpoint()
                        e = ann.get_highest_localization().get_midpoint()
                        fp.write('"{}",{},{},"{}"\n'
                                 ''.format(name, b, e, content))
            fp.close()
