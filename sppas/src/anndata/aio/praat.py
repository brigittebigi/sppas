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

    src.anndata.aio.praat.py
    ~~~~~~~~~~~~~~~~~~~~~~~~

Praat - Doing phonetic with computers, is a GPL tool developed by:

| Paul Boersma and David Weenink
| Phonetic Sciences, University of Amsterdam
| Spuistraat 210
| 1012VT Amsterdam
| The Netherlands

See: http://www.fon.hum.uva.nl/praat/

"""
import codecs
import re

from sppas.src.config import sg
from sppas.src.utils.makeunicode import u
from sppas.src.calculus import linear_values

from ..anndataexc import AioEncodingError
from ..anndataexc import AioEmptyTierError
from ..anndataexc import AioMultiTiersError
from ..anndataexc import AioLocationTypeError
from ..anndataexc import AnnDataTypeError
from ..anndataexc import AioLineFormatError
from ..anndataexc import AioNoTiersError
from ..anndataexc import AioFormatError
from ..anndataexc import TagValueError
from ..ann.annlocation import sppasLocation
from ..ann.annlocation import sppasPoint
from ..ann.annlocation import sppasInterval
from ..ann.annlabel import sppasLabel
from ..ann.annlabel import sppasTag
from ..ann.annotation import sppasAnnotation

from .aioutils import fill_gaps
from .aioutils import merge_overlapping_annotations
from .aioutils import load
from .aioutils import format_labels
from .basetrsio import sppasBaseIO

# ---------------------------------------------------------------------------


class sppasBasePraat(sppasBaseIO):
    """Base class for readers and writers of Praat files.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      contact@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2018  Brigitte Bigi

    """

    @staticmethod
    def make_point(midpoint, radius=0.0005):
        """The localization is a time value, so a float.

        :param midpoint: (float, str, int) a time value (in seconds).
        :param radius: (float): vagueness (in seconds)
        :returns: (sppasPoint)

        """
        try:
            midpoint = float(midpoint)
            radius = float(radius)
        except ValueError:
            raise AnnDataTypeError(midpoint, "float")

        return sppasPoint(midpoint, radius)

    # -----------------------------------------------------------------------

    def __init__(self, name=None):
        """Initialize a new Praat instance.

        :param name: (str) This transcription name.

        """
        if name is None:
            name = self.__class__.__name__
        super(sppasBasePraat, self).__init__(name)

        self.software = "Praat"

        self._accept_multi_tiers = True
        self._accept_no_tiers = False
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
        self._accept_gaps = False
        self._accept_overlaps = False

    # -----------------------------------------------------------------------

    @staticmethod
    def _parse_int(line, line_number=0):
        """Parse an integer value from a line of a Praat formatted file.

        >>> sppasBasePraat._parse_int("intervals: size = 23")
        >>> 23

        :param line: (str) The line to parse and get value
        :param line_number: (int) Number of the given line
        :returns: (int)

        """
        try:
            line = line.strip()
            if line.endswith(":") is True:
                line = line[:-1]
            val = line[line.rfind(' ') + 1:]
            return int(val)
        except:
            raise AioLineFormatError(line_number, line)

    # -----------------------------------------------------------------------

    @staticmethod
    def _parse_float(line, line_number=0):
        """Parse a floating point value from a line of a Praat formatted file.

        >>> sppasBasePraat._parse_float("xmin = 11.9485310906")
        >>> 11.9485310906

        :param line: (str) The line to parse and get value
        :param line_number: (int) Number of the given line
        :returns: (float)

        """
        try:
            line = line.strip()
            val = line[line.rfind(' ') + 1:]
            return float(val)
        except:
            raise AioLineFormatError(line_number, line)

    # -----------------------------------------------------------------------

    @staticmethod
    def _parse_string(text):
        """Parse a text from one or more lines of a Praat formatted file.

        :param text: (str or list of str)
        :returns: (str)

        """
        text = text.strip()

        if text.endswith('"'):
            text = text[:-1]

        keywords = ["file type", "class", "text", "name", "xmin", "xmax", "size",
                    "number", "mark", "value", "point"]
        for k in keywords:
            if k in text.lower() and re.match('^[A-Za-z ]+=[ ]?', text):
                text = text[text.find('=') + 1:]

        text = text.strip()
        if text.startswith('"'):
            text = text[1:]

        # praat double quotes.
        return text.replace('""', '"')

    # -----------------------------------------------------------------------

    @staticmethod
    def _serialize_header(file_class, xmin, xmax):
        """Serialize the header of a Praat file.

        :param file_class: (str) Objects class in this file
        :param xmin: (float) Start time
        :param xmax: (float) End time
        :returns: (str)

        """
        header = 'File type = "ooTextFile"\n'
        header += 'Object class = "{:s}"\n'.format(file_class)
        header += '\n'
        header += 'xmin = {}\n'.format(xmin)
        header += 'xmax = {}\n'.format(xmax)
        return header

    # -----------------------------------------------------------------------

    @staticmethod
    def _serialize_labels_text(annotation):
        """Convert the annotation labels into a string."""
        text = annotation.serialize_labels(separator="\n", empty="", alt=True)

        if '"' in text:
            text = re.sub('([^"])["]([^"])', '\\1""\\2', text)

            text = re.sub('([^"])["]([^"])', '\\1""\\2', text)
            # it misses occurrences if 2 " are separated by only 1 character

            text = re.sub('([^"])["]$', '\\1""', text)
            # it misses occurrences if " is at the end of the label!

            text = re.sub('^["]([^"])', '""\\1', text)
            # it misses occurrences if " is at the beginning of the label

            text = re.sub('^""$', '""""', text)

            text = re.sub('^"$', '""', text)

        return '\t\t\ttext = "{:s}"\n'.format(text)

    # -----------------------------------------------------------------------

    @staticmethod
    def _serialize_labels_value(labels):
        """Convert a label with a numerical value into a string."""
        if len(labels) == 0:
            TagValueError('empty label')
        if len(labels) > 1:
            TagValueError('multiple labels')

        label = labels[0]
        if label is None:
            raise TagValueError('None')
        if label.get_best() is None:
            raise TagValueError('None')
        if label.get_best().is_empty():
            TagValueError('empty label')

        tag = label.get_best()
        if tag.get_type() in ['int', 'float']:
            return "\tvalue = {}\n".format(tag.get_typed_content())

        raise AioFormatError(label.get_type())

# ---------------------------------------------------------------------------


class sppasTextGrid(sppasBasePraat):
    """SPPAS TextGrid reader and writer.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      contact@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2018  Brigitte Bigi

    TextGrid supports multiple tiers in a file.
    TextGrid does not support empty files (file with no tiers).
    TextGrid does not support alternatives labels nor locations. Only the ones
    with the best score are saved.
    TextGrid does not support controlled vocabularies.
    TextGrid does not support hierarchy.
    TextGrid does not support metadata.
    TextGrid does not support media assignment.
    TextGrid supports points and intervals.
    TextGrid does not support disjoint intervals.
    TextGrid does not support alternative tags (here called "text").
    TextGrid does not support radius.

    Both "short TextGrid" and "long TextGrid" file formats are supported.

    """

    @staticmethod
    def _detect(fp):
        line = fp.readline()
        file_type = sppasBasePraat._parse_string(line)
        line = fp.readline()
        object_class = sppasBasePraat._parse_string(line)
        return file_type.startswith("ooTextFile") and object_class == "TextGrid"

    @staticmethod
    def detect(filename):
        """Check whether a file is of TextGrid format or not.

        Try first to open the file with the default sppas encoding,
        then UTF-16.

        :param filename: (str) Name of the file to check.
        :returns: (bool)

        """
        detected = False
        try:
            with codecs.open(filename, 'r', sg.__encoding__) as fp:
                detected = sppasTextGrid._detect(fp)
                fp.close()
        except UnicodeError:
            try:
                with codecs.open(filename, 'r', 'UTF-16') as fp:
                    detected = sppasTextGrid._detect(fp)
                    fp.close()
            except UnicodeError:
                return False
        except IOError:
            pass

        return detected

    # -----------------------------------------------------------------------

    def __init__(self, name=None):
        """Initialize a new sppasTextGrid instance.

        :param name: (str) This transcription name.

        """
        if name is None:
            name = self.__class__.__name__
        super(sppasTextGrid, self).__init__(name)

        self.default_extension = "TextGrid"

        self._accept_point = True
        self._accept_interval = True

    # -----------------------------------------------------------------------

    def read(self, filename):
        """Read a TextGrid file.

        :param filename: is the input file name, ending by ".TextGrid"

        """
        if not self.detect(filename):
            raise IOError('{:s} is not of the expected {:s} format.'
                          ''.format(filename, self.default_extension))

        # get the content of the file

        try:
            lines = load(filename, sg.__encoding__)
        except AioEncodingError:
            try:
                lines = load(filename, "UTF-16")
            except AioEncodingError:
                raise AioEncodingError(filename, "", sg.__encoding__+"/UTF-16")

        # parse the header of the file
        if len(lines[2].strip()) == 0:
            has_blank = 1
        else:
            has_blank = 0

        # if the size isn't named, it is a short TextGrid file
        is_long = not lines[5+has_blank].strip().isdigit()

        last_line = len(lines) - 1
        cur_line = 6 + has_blank
        if is_long is True:
            # Ignore the line 'item []:'
            cur_line += 1

        # parse all lines of the file

        while cur_line < last_line:
            # Ignore the line: 'item [1]:'
            # with the tier number between the brackets
            if is_long is True:
                cur_line += 1
            cur_line = self._parse_tier(lines, cur_line, is_long)

    # -----------------------------------------------------------------------

    def _parse_tier(self, lines, start_line, is_long):
        """Parse a tier from the content of a TextGrid file.

        :param lines: the contents of the file.
        :param start_line: index in lines when the tier content starts.
        :param is_long: (bool) False if the TextGrid is in short form.
        :returns: (int) Number of lines of this tier

        """
        # Parse the header of the tier

        tier_type = sppasBasePraat._parse_string(lines[start_line])
        tier_name = sppasBasePraat._parse_string(lines[start_line+1])
        tier_size = sppasBasePraat._parse_int(lines[start_line+4])
        tier = self.create_tier(tier_name)

        if tier_type == "IntervalTier":
            is_interval = True
        elif tier_type == "TextTier":
            is_interval = False
        else:
            raise AioLineFormatError(start_line+1, lines[start_line])

        # Parse the content of the tier
        start_line += 5
        end = len(lines) - 1

        while start_line < end and len(tier) < tier_size:
            # Ignore the line: 'intervals [1]:'
            # with the interval number between the brackets
            if is_long is True:
                start_line += 1
            ann, start_line = self._parse_annotation(lines,
                                                     start_line,
                                                     is_interval)
            tier.add(ann)

        return start_line

    # -----------------------------------------------------------------------

    @staticmethod
    def _parse_annotation(lines, start_line, is_interval):
        """Read an annotation from an IntervalTier in the content of lines.

        :param lines: (list) the contents of the file.
        :param start_line: (int) index in lines when the tier content starts.
        :param is_interval: (bool)
        :returns: number of lines for this annotation in the file

        """
        # Parse the localization
        localization, start_line = \
            sppasTextGrid._parse_localization(lines, start_line, is_interval)
        if start_line >= len(lines):
            raise AioLineFormatError(start_line - 1, lines[-1])

        # Parse the tag
        labels, start_line = \
            sppasTextGrid._parse_text(lines, start_line)

        ann = sppasAnnotation(sppasLocation(localization),
                              labels)

        return ann, start_line

    # -----------------------------------------------------------------------

    @staticmethod
    def _parse_localization(lines, start_line, is_interval):
        """Parse the localization (point or interval)."""
        midpoint = sppasBasePraat._parse_float(lines[start_line], start_line+1)
        start_line += 1
        if is_interval is True:
            if start_line >= len(lines):
                raise AioLineFormatError(start_line-1, lines[-1])
            end = sppasBasePraat._parse_float(lines[start_line], start_line+1)
            start_line += 1
            localization = sppasInterval(sppasBasePraat.make_point(midpoint),
                                         sppasBasePraat.make_point(end))
        else:
            localization = sppasBasePraat.make_point(midpoint)

        return localization, start_line

    # -----------------------------------------------------------------------

    @staticmethod
    def _parse_text(lines, start_line):
        """Parse the text entry. Returns a list of sppasLabel().

        text can be on several lines.
        we save each line in an individual label.

        """
        # read one line
        line = lines[start_line].strip()

        # The text can starts with a carriage return... so line is:
        # text = "
        first = line.find('"')
        last = line.rfind('"')

        # parse this line
        text = sppasBasePraat._parse_string(line)
        start_line += 1

        # if the text continue on the following lines
        while first == last:   # line.endswith('"') is False:
            line = lines[start_line].strip()
            first = line.find('"')
            last = line.rfind('"')

            text += "\n" + sppasBasePraat._parse_string(line)
            start_line += 1
            if line.endswith('"'):
                break
            if start_line >= len(lines):
                raise AioLineFormatError(start_line-1, lines[-1])

        return format_labels(text, separator="\n"), start_line

    # -----------------------------------------------------------------------
    # Writer
    # -----------------------------------------------------------------------

    def write(self, filename):
        """Write a TextGrid file.

        :param filename: (str)

        """
        if self.is_empty():
            raise AioNoTiersError("TextGrid")

        min_time_point = self.get_min_loc()
        max_time_point = self.get_max_loc()
        if min_time_point is None or max_time_point is None:
            # only empty tiers in the transcription
            raise AioNoTiersError("TextGrid")

        # we have to remove the hierarchy because instead we can't fill gaps
        hierarchy_backup = self.get_hierarchy().copy()
        for tier in self:
            self.get_hierarchy().remove_tier(tier)

        with codecs.open(filename, 'w', sg.__encoding__, buffering=8096) as fp:

            # Write the header
            fp.write(sppasTextGrid._serialize_textgrid_header(
                min_time_point.get_midpoint(),
                max_time_point.get_midpoint(),
                len(self)))

            # Write each tier
            for i, tier in enumerate(self):

                if tier.is_disjoint() is True:
                    continue

                # intervals of annotations must be in a continuum
                # (this won't do anything if it's not necessary...)
                new_tier = fill_gaps(tier, min_time_point, max_time_point)
                new_tier = merge_overlapping_annotations(new_tier)

                # Write the header of the tier
                try:
                    fp.write(sppasTextGrid._serialize_tier_header(new_tier,
                                                                  i+1))
                except:
                    fp.close()
                    raise

                # Write annotations of the tier
                is_point = new_tier.is_point()
                for a, annotation in enumerate(new_tier):
                    if is_point is True:
                        fp.write(sppasTextGrid._serialize_point_annotation(
                            annotation, a+1))
                    else:
                        fp.write(sppasTextGrid._serialize_interval_annotation(
                            annotation, a+1))

            fp.close()

        # restore the hierarchy...
        self._hierarchy = hierarchy_backup

    # -----------------------------------------------------------------------

    @staticmethod
    def _serialize_textgrid_header(xmin, xmax, size):
        """Create a string with the header of the textgrid."""
        content = sppasBasePraat._serialize_header("TextGrid", xmin, xmax)
        content += 'tiers? <exists>\n'
        content += 'size = {:d}\n'.format(size)
        content += 'item []:\n'
        return content

    # -----------------------------------------------------------------------

    @staticmethod
    def _serialize_tier_header(tier, tier_number):
        """Create the string with the header for a new tier."""
        if len(tier) == 0:
            raise AioEmptyTierError("TextGrid", tier.get_name())

        content = '\titem [{:d}]:\n'.format(tier_number)
        content += '\t\tclass = "{:s}"\n'.format('IntervalTier'
                                                 if tier.is_interval()
                                                 else 'TextTier')
        content += '\t\tname = "{:s}"\n'.format(tier.get_name())
        content += '\t\txmin = {}\n'.format(
            tier.get_first_point().get_midpoint())
        content += '\t\txmax = {}\n'.format(
            tier.get_last_point().get_midpoint())
        content += '\t\tintervals: size = {:d}\n'.format(len(tier))
        return content

    # -----------------------------------------------------------------------

    @staticmethod
    def _serialize_interval_annotation(annotation, number):
        """Convert an annotation consisting of intervals to the TextGrid format.

        A time value can be written with a maximum of 18 digits, like in Praat.

        :param annotation: (sppasAnnotation)
        :param number: (int) the index of the annotation in the tier + 1.
        :returns: (unicode)

        """
        content = '\t\tintervals [{:d}]:\n'.format(number)
        content += '\t\t\txmin = {}\n'.format(
            annotation.get_lowest_localization().get_midpoint())
        content += '\t\t\txmax = {}\n'.format(
            annotation.get_highest_localization().get_midpoint())
        content += sppasBasePraat._serialize_labels_text(annotation)
        return u(content)

    # -----------------------------------------------------------------------

    @staticmethod
    def _serialize_point_annotation(annotation, number):
        """Convert an annotation consisting of points to the TextGrid format.

        :param annotation: (sppasAnnotation)
        :param number: (int) the index of the annotation in the tier + 1.
        :returns: (unicode)

        """
        text = sppasBasePraat._serialize_labels_text(annotation)
        text = text.replace("text =", "mark =")

        content = '\t\t\tpoints [{:d}]:\n'.format(number)
        content += '\t\t\ttime = {}\n'.format(
            annotation.get_lowest_localization().get_midpoint())
        content += text
        return u(content)

# ---------------------------------------------------------------------------


class sppasBaseNumericalTier(sppasBasePraat):
    """SPPAS PitchTier, IntensityTier, etc reader and writer.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      contact@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2018  Brigitte Bigi

    Support of Praat file formats with only one tier of numerical values like
    pitch, intensity, etc.

    """

    def __init__(self, name=None):
        """Initialize a new sppasBaseNumericalTier instance.

        :param name: (str) This transcription name.

        """
        if name is None:
            name = self.__class__.__name__
        super(sppasBaseNumericalTier, self).__init__(name)

        self._accept_multi_tiers = False
        self._accept_no_tiers = False
        self._accept_metadata = False
        self._accept_ctrl_vocab = False
        self._accept_media = False
        self._accept_hierarchy = False
        self._accept_interval = False
        self._accept_disjoint = False
        self._accept_alt_localization = False
        self._accept_alt_tag = False
        self._accept_radius = False
        self._accept_gaps = False
        self._accept_overlaps = False

    # -----------------------------------------------------------------------

    def _read(self, filename):
        """Read a file of any numerical file type.

        :param filename: (str) the input file name

        """
        # get the content of the file
        lines = load(filename, sg.__encoding__)
        if len(lines) < 7:
            raise AioLineFormatError(len(lines), lines[-1])

        # parse the header of the file
        file_type = sppasBasePraat._parse_string(lines[1])
        tier = self.create_tier(file_type)

        last_line = len(lines) - 1
        cur_line = 6
        # if the size isn't named, it is a short numerical file
        is_long = not lines[5].strip().isdigit()

        # parse all lines of the file
        while cur_line < last_line:
            # Ignore the line: 'points [1]:'
            if is_long:
                cur_line += 1
                if cur_line > len(lines):
                    raise AioLineFormatError(cur_line, lines[-1])

            # Parse the localization
            midpoint = sppasBasePraat._parse_float(
                lines[cur_line], cur_line + 1)
            localization = sppasBasePraat.make_point(midpoint)
            cur_line += 1
            if cur_line >= len(lines):
                raise AioLineFormatError(cur_line, lines[-1])

            # Parse the tag value
            value = sppasBasePraat._parse_float(lines[cur_line], cur_line + 1)
            tag = sppasTag(value, tag_type="float")

            tier.create_annotation(sppasLocation(localization),
                                   sppasLabel(tag))
            cur_line += 1

    # -----------------------------------------------------------------------

    def _write(self, filename, file_type):
        """Write a file of the given file type.

        :param filename: (str)
        :param file_type: (str) Name of the file type
        (PitchTier, IntensityTier...)

        """
        if self.is_empty():
            raise AioNoTiersError(file_type)

        # Search for the tier
        if len(self) != 1:
            tier = self.find(file_type, case_sensitive=False)
            if tier is None:
                raise AioMultiTiersError("Praat "+file_type)
        else:
            tier = self[0]

        # we expect a not empty tier
        if self.is_empty() is True:
            raise AioEmptyTierError("Praat "+file_type, tier.get_name())

        # we expect a tier with only sppasPoint
        if tier.is_point() is False:
            raise AioLocationTypeError(file_type, "intervals")

        # right... we can write (numerical value will be tested time-to-time)
        min_time_point = tier.get_first_point()
        max_time_point = tier.get_last_point()

        with codecs.open(filename, 'w', sg.__encoding__, buffering=8096) as fp:

            # Write the header
            fp.write(sppasBasePraat._serialize_header(
                file_type,
                min_time_point.get_midpoint(),
                max_time_point.get_midpoint()))
            fp.write(
                "points: size = {:d}\n".format(len(tier)))

            # Write the annotations
            for a, annotation in enumerate(tier):

                content = 'points [{:d}]:\n'.format(a+1)
                content += '\tnumber = {}\n'.format(
                    annotation.get_lowest_localization().get_midpoint())
                content += sppasBasePraat._serialize_labels_value(
                    annotation.get_labels())
                fp.write(content)

            fp.close()

# ---------------------------------------------------------------------------


class sppasPitchTier(sppasBaseNumericalTier):
    """SPPAS PitchTier reader and writer.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      contact@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2018  Brigitte Bigi

    """

    @staticmethod
    def detect(filename):
        """Check whether a file is of PitchTier format or not.

        :param filename: (str) Name of the file to check.
        :returns: (bool)

        """
        try:
            with codecs.open(filename, 'r', sg.__encoding__) as fp:
                file_type = sppasBasePraat._parse_string(fp.readline())
                object_class = sppasBasePraat._parse_string(fp.readline())
                fp.close()
                return file_type == "ooTextFile" and \
                       object_class == "PitchTier"
        except IOError:
            return False
        except UnicodeDecodeError:
            return False

    # -----------------------------------------------------------------------

    def __init__(self, name=None):
        """Initialize a new sppasPitchTier instance.

        :param name: (str) This transcription name.

        """
        if name is None:
            name = self.__class__.__name__
        super(sppasPitchTier, self).__init__(name)

        self.default_extension = "PitchTier"

    # -----------------------------------------------------------------------

    def read(self, filename):
        """Read a PitchTier file.

        :param filename: (str) the input file name

        """
        self._read(filename)

    # -----------------------------------------------------------------------

    def write(self, filename):
        """Write a PitchTier file.

        :param filename: (str)

        """
        self._write(filename, "PitchTier")

    # -----------------------------------------------------------------------

    def to_pitch(self):
        """Convert the PitchTier to Pitch values.

        :returns: list of pitch values with delta = 0.01

        """
        if self.is_empty():
            raise AioNoTiersError("PitchTier")
        pt = self.find("PitchTier")
        if pt is None:
            raise AioNoTiersError("PitchTier")
        if len(pt) < 2:
            raise AioEmptyTierError("PitchTier", "PitchTier")

        return sppasPitchTier.__to_pitch(pt)

    # -----------------------------------------------------------------------

    @staticmethod
    def __to_pitch(tier):
        """Linear interpolation between annotations of tier to get pitch."""
        delta = 0.01

        # from 0 to the first value
        time1 = round(tier[0].get_lowest_localization().get_midpoint(), 6)
        pitch1 = tier[0].get_best_tag().get_typed_content()
        pitch2 = 0.
        steps = int(time1 / delta) - 1
        pitch = [0.] * steps

        # inside the range of the annotations
        for ann in tier[1:]:

            time2 = round(ann.get_lowest_localization().get_midpoint(), 6)
            pitch2 = ann.get_best_tag().get_typed_content()

            # estimates a linear fct (slope and intercept) to
            # get values from p1 to p2 (both included into the result)
            intermediate_values = linear_values(delta,
                                                (time1, pitch1),
                                                (time2, pitch2),
                                                rounded=6)
            pitch.extend(intermediate_values[:-1])

            time1 = time2
            pitch1 = pitch2

        # last annotation
        pitch.append(round(pitch2, 6))

        return pitch

# ---------------------------------------------------------------------------


class sppasIntensityTier(sppasPitchTier):
    """SPPAS IntensityTier reader and writer.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      contact@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2018  Brigitte Bigi

    """

    @staticmethod
    def detect(filename):
        """Check whether a file is of IntensityTier format or not.

        :param filename: (str) Name of the file to check.
        :returns: (bool)

        """
        try:
            with codecs.open(filename, 'r', sg.__encoding__) as fp:
                file_type = sppasBasePraat._parse_string(fp.readline())
                object_class = sppasBasePraat._parse_string(fp.readline())
                fp.close()
                return file_type == "ooTextFile" \
                       and object_class == "IntensityTier"
        except IOError:
            return False
        except UnicodeDecodeError:
            return False

    # -----------------------------------------------------------------------

    def __init__(self, name=None):
        """Initialize a new sppasIntensityTier instance.

        :param name: (str) This transcription name.

        """
        if name is None:
            name = self.__class__.__name__
        super(sppasIntensityTier, self).__init__(name)

        self.default_extension = "IntensityTier"

    # -----------------------------------------------------------------------

    def read(self, filename):
        """Read a IntensityTier file.

        :param filename: (str) the input file name

        """
        self._read(filename)

    # -----------------------------------------------------------------------

    def write(self, filename):
        """Write a IntensityTier file.

        :param filename: (str)

        """
        self._write(filename, "IntensityTier")
