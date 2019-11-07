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

    src.anndata.aio.subtitle.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~

SubViewer is a utility for adding and synchronizing subtitles to video
content. It was created by David Dolinski in 1999.
Precision in time is 10ms.

SubRip is a free software program for Windows which "rips" (extracts)
subtitles and their timings from video. It is free software, released
under the GNU GPL. SubRip is also the name of the widely used and broadly
compatible subtitle text file format created by this software.
Precision in time is 1ms.

"""
import codecs
import datetime

from sppas import sg
from sppas.src.utils import b
from .basetrs import sppasBaseIO
from ..anndataexc import AnnDataTypeError
from ..anndataexc import AioMultiTiersError
from ..ann.annotation import sppasAnnotation
from ..ann.annlocation import sppasLocation
from ..ann.annlocation import sppasPoint
from ..ann.annlocation import sppasInterval

from .aioutils import format_labels

# ---------------------------------------------------------------------------


class sppasBaseSubtitles(sppasBaseIO):
    """SPPAS base class for subtitle formats.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      contact@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2019  Brigitte Bigi

    """

    def __init__(self, name=None):
        """Initialize a new sppasBaseSubtitles instance.

        :param name: (str) This transcription name.

        """
        if name is None:
            name = self.__class__.__name__
        super(sppasBaseSubtitles, self).__init__(name)

        self._accept_multi_tiers = False
        self._accept_no_tiers = True
        self._accept_metadata = False
        self._accept_ctrl_vocab = False
        self._accept_media = False
        self._accept_hierarchy = False
        self._accept_point = False
        self._accept_interval = True
        self._accept_disjoint = False
        self._accept_alt_localization = False
        self._accept_alt_tag = False
        self._accept_radius = False
        self._accept_gaps = True
        self._accept_overlaps = False

    # -----------------------------------------------------------------------

    @staticmethod
    def _parse_time(time_string):
        """Convert a time in "%H:%M:%S,%m" format into seconds."""
        time_string = time_string.strip()
        dt = (datetime.datetime.strptime(time_string, '%H:%M:%S,%f') -
              datetime.datetime.strptime('', ''))
        return dt.total_seconds()

    # -----------------------------------------------------------------------

    @staticmethod
    def _format_time(second_count):
        """Convert a time in seconds into "%H:%M:%S" format."""
        dt = datetime.datetime.utcfromtimestamp(second_count)
        return dt.strftime('%H:%M:%S,%f')[:-3]

    # -----------------------------------------------------------------------

    @staticmethod
    def make_point(midpoint):
        """In subtitles, the localization is a time value, so a float."""
        try:
            midpoint = float(midpoint)
        except ValueError:
            raise AnnDataTypeError(midpoint, "float")
        return sppasPoint(midpoint, radius=0.02)

    # -----------------------------------------------------------------------

    @staticmethod
    def _format_text(text):
        """Remove HTML tags, etc."""
        text = text.replace('<b>', '')
        text = text.replace('<B>', '')
        text = text.replace('</b>', '')
        text = text.replace('</B>', '')

        text = text.replace('<i>', '')
        text = text.replace('<I>', '')
        text = text.replace('</i>', '')
        text = text.replace('</I>', '')

        text = text.replace('<u>', '')
        text = text.replace('<U>', '')
        text = text.replace('</u>', '')
        text = text.replace('</U>', '')

        text = text.replace('<font>', '')
        text = text.replace('<FONT>', '')
        text = text.replace('</font>', '')
        text = text.replace('</FONT>', '')

        text = text.replace('[br]', '\n')

        return text

    # -----------------------------------------------------------------------

    @staticmethod
    def _serialize_location(ann, precision=3):
        """Extract location to serialize the timestamps.

        :param ann: (sppasAnnotation)
        :param precision: (int) precision in time (expected value is 2 or 3)

        """
        if ann.location_is_point() is False:
            begin = sppasBaseSubtitles._format_time(
                round(ann.get_lowest_localization().get_midpoint(),
                      precision))
            end = sppasBaseSubtitles._format_time(
                round(ann.get_highest_localization().get_midpoint(),
                      precision))

        else:
            # SubRip does not support point based annotation
            # so we'll make a 1 second subtitle
            begin = sppasBaseSubtitles._format_time(
                round(ann.get_lowest_localization().get_midpoint(),
                      precision))
            end = sppasBaseSubtitles._format_time(
                round(ann.get_highest_localization().get_midpoint(),
                      precision) + 1.)

        return '{:s} --> {:s}\n'.format(begin, end)

# ---------------------------------------------------------------------------


class sppasSubRip(sppasBaseSubtitles):
    """SPPAS reader/writer for SRT format.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      contact@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2019  Brigitte Bigi

    The SubRip text file format (SRT) is used by the SubRip program to save
    subtitles ripped from video files or DVDs.
    It is free software, released under the GNU GPL.

    Each subtitle is represented as a group of lines. Subtitles are separated
    subtitles by a blank line.

        - first line of a subtitle is an index (starting from 1);
        - the second line is a timestamp interval,
          in the format %H:%M:%S,%m and the start and end of
          the range separated by -->;
        - optionally: a specific positioning by pixels, in the form
          X1:number Y1:number X2:number Y2:number;
        - the third line is the label.
          The HTML <b>, <i>, <u>, and <font> tags are allowed.

    """

    def __init__(self, name=None):
        """Initialize a new sppasSubRip instance.

        :param name: (str) This transcription name.

        """
        if name is None:
            name = self.__class__.__name__
        super(sppasSubRip, self).__init__(name)

        self.default_extension = "srt"
        self.software = "SubRip"

    # -----------------------------------------------------------------------

    def read(self, filename):
        """Read a SRT file and fill the Transcription.

        :param filename: (str)

        """
        with codecs.open(filename, 'r', sg.__encoding__) as fp:
            lines = fp.readlines()
            fp.close()

        tier = self.create_tier('Trans-SubRip')

        # Ignore BOM
        if b(lines[0]).startswith(codecs.BOM_UTF8):
            lines[0] = lines[0][1:]

        # Ignore an optional header (or blank lines)
        i = 0
        while sppasBaseIO.is_number(lines[i].strip()[0:1]) is False:
            i += 1

        # Content of the file
        while i < len(lines):
            ann_lines = list()
            while i < len(lines) and lines[i].strip() != '':
                ann_lines.append(lines[i].strip())
                i += 1
            a = sppasSubRip._parse_subtitle(ann_lines)
            if a is not None:
                tier.append(a)
            i += 1

    # -----------------------------------------------------------------------

    @staticmethod
    def _parse_subtitle(lines):
        """Parse a single subtitle.

        The subtitle can be written on several lines. In this case, one
        sppasLabel() is created for each line.

        :param lines: (list) the lines of a subtitle (index, timestamps, label)

        """
        if len(lines) < 3:
            return None

        # time stamps
        start, stop = map(sppasBaseSubtitles._parse_time,
                          lines[1].split('-->'))
        time = sppasInterval(sppasBaseSubtitles.make_point(start),
                             sppasBaseSubtitles.make_point(stop))

        # create the annotation without label
        a = sppasAnnotation(sppasLocation(time))

        # optional position (in pixels), saved as metadata of the annotation
        if 'X1' in lines[2] and 'Y1' in lines[2]:
            # parse position: X1:number Y1:number X2:number Y2:number
            positions = lines[2].split(" ")
            for position in positions:
                coord, value = position.split(':')
                a.set_meta("position_pixel_"+coord, value)
            lines.pop(2)

        # labels
        text = ""
        for line in lines[2:]:
            text += sppasBaseSubtitles._format_text(line) + "\n"
        labels = format_labels(text.rstrip(), separator="\n")
        if len(labels) > 0:
            a.set_labels(labels)

        return a

    # -----------------------------------------------------------------------

    def write(self, filename):
        """Write a transcription into a file.

        :param filename: (str)

        """
        if len(self) != 1:
            raise AioMultiTiersError("SubRip")

        with codecs.open(filename, 'w', sg.__encoding__, buffering=8096) as fp:

            if self.is_empty() is False:
                number = 1
                last = len(self[0])
                for ann in self[0]:

                    text = ann.serialize_labels(separator="\n",
                                                empty="",
                                                alt=True)

                    # no label defined, or empty label -> no subtitle!
                    if len(text) == 0:
                        continue

                    subtitle = ""
                    # first line: the number of the annotation
                    subtitle += str(number) + "\n"
                    # 2nd line: the timestamps
                    subtitle += sppasBaseSubtitles._serialize_location(
                        ann,
                        precision=3)
                    # 3rd line: optionally the position on screen
                    subtitle += sppasSubRip._serialize_metadata(ann)
                    # the text
                    subtitle += text + "\n"
                    if number < last:
                        # a blank line
                        subtitle += "\n"

                    # next!
                    fp.write(subtitle)
                    number += 1

            fp.close()

    # -----------------------------------------------------------------------

    @staticmethod
    def _serialize_metadata(ann):
        """Extract metadata to serialize the position on screen."""
        text = ""
        if ann.is_meta_key("position_pixel_X1"):
            x1 = ann.get_meta("position_pixel_X1")
            if ann.is_meta_key("position_pixel_Y1"):
                y1 = ann.get_meta("position_pixel_Y1")
                if ann.is_meta_key("position_pixel_X2"):
                    x2 = ann.get_meta("position_pixel_X2")
                    if ann.is_meta_key("position_pixel_Y2"):
                        y2 = ann.get_meta("position_pixel_Y2")
                        text += "X1:{:s} Y1:{:s} X2:{:s} Y2:{:s}\n" \
                                "".format(x1, y1, x2, y2)
        return text

# ---------------------------------------------------------------------------


class sppasSubViewer(sppasBaseSubtitles):
    """SPPAS reader/writer for SUB format.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      contact@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2018  Brigitte Bigi

    The SubViewer text file format (SUB) is used by the SubViewer program to
    save subtitles of videos.

    """

    def __init__(self, name=None):
        """Initialize a new sppasBaseSubtitles instance.

        :param name: (str) This transcription name.

        """
        if name is None:
            name = self.__class__.__name__
        super(sppasSubViewer, self).__init__(name)

        self.default_extension = "sub"
        self.software = "SubViewer"

    # -----------------------------------------------------------------------

    def read(self, filename):
        """Read a SUB file and fill the Transcription.

        :param filename: (str)

        """
        with codecs.open(filename, 'r', sg.__encoding__) as fp:
            lines = fp.readlines()
            fp.close()

        tier = self.create_tier('Trans-SubViewer')

        # Ignore BOM
        if b(lines[0]).startswith(codecs.BOM_UTF8):
            lines[0] = lines[0][1:]

        # Header
        i = 0
        header_lines = list()
        while sppasBaseIO.is_number(lines[i].strip()[0:1]) is False:
            header_lines.append(lines[i].strip())
            i += 1
        self._parse_header(header_lines)

        # Content of the file
        while i < len(lines):
            ann_lines = list()
            while i < len(lines) and lines[i].strip() != '':
                ann_lines.append(lines[i].strip())
                i += 1
            a = sppasSubViewer._parse_subtitle(ann_lines)
            if a is not None:
                tier.append(a)
            i += 1

    # -----------------------------------------------------------------------

    def _parse_header(self, lines):
        """Parse the header lines to get metadata.

        [INFORMATION]
        [TITLE]SubViewer file example
        [AUTHOR]FK
        [SOURCE]FK
        [PRG]gedit
        [FILEPATH]/extdata
        [DELAY]0
        [CD TRACK]0
        [COMMENT]
        [END INFORMATION]
        [SUBTITLE]
        [COLF]&HFFFFFF,[STYLE]bd,[SIZE]18,[FONT]Arial

        """
        for line in lines:
            if line.startswith('[TITLE]'):
                self.set_name(line[7:])
            elif line.startswith('[AUTHOR]'):
                self.set_meta('annotator_name', line[8:])
            elif line.startswith('[PRG]'):
                self.set_meta("prg_editor_name", line[4:])
            elif line.startswith('[FILEPATH]'):
                self.set_meta("file_path", line[:10])
            elif line.startswith('[DELAY]'):
                self.set_meta("media_shift_delay", line[:7])

    # -----------------------------------------------------------------------

    @staticmethod
    def _parse_subtitle(lines):
        """Parse a single subtitle.

        :param lines: (list) the lines of a subtitle (index, timestamps, label)

        """
        if len(lines) < 2:
            return None

        # time stamps
        time_stamp = lines[0].replace(",", " ")
        time_stamp = time_stamp.replace(".", ",")
        start, stop = map(sppasBaseSubtitles._parse_time, time_stamp.split())
        time = sppasInterval(sppasBaseSubtitles.make_point(start),
                             sppasBaseSubtitles.make_point(stop))

        # labels
        text = ""
        for line in lines[1:]:
            text += sppasBaseSubtitles._format_text(line) + "\n"
        labels = format_labels(text.rstrip(), separator="\n")

        return sppasAnnotation(sppasLocation(time), labels)

    # -----------------------------------------------------------------------

    def write(self, filename):
        """Write a transcription into a file.

        :param filename: (str)

        """
        if len(self) != 1:
            raise AioMultiTiersError("SubViewer")

        with codecs.open(filename, 'w', sg.__encoding__, buffering=8096) as fp:

            fp.write(self._serialize_header())
            if self.is_empty() is False:
                for ann in self[0]:

                    text = ann.serialize_labels(separator="[br]",
                                                empty="",
                                                alt=True)

                    # no label defined, or empty label -> no subtitle!
                    if len(text) == 0:
                        continue

                    # the timestamps
                    subtitle = sppasBaseSubtitles._serialize_location(
                        ann,
                        precision=2)
                    subtitle = subtitle.replace(",", ".")
                    subtitle = subtitle.replace(" --> ", ",")
                    # the text
                    subtitle += text + "\n"
                    # a blank line
                    subtitle += "\n"

                    # next!
                    fp.write(subtitle)

            fp.close()

    # -----------------------------------------------------------------------

    def _serialize_header(self):
        """Convert metadata into an header.

        [INFORMATION]
        [TITLE]SubViewer file example
        [AUTHOR]FK
        [SOURCE]FK
        [PRG]gedit
        [FILEPATH]/extdata
        [DELAY]0
        [CD TRACK]0
        [COMMENT]
        [END INFORMATION]
        [SUBTITLE]
        [COLF]&HFFFFFF,[STYLE]bd,[SIZE]18,[FONT]Arial

        """
        header = "[INFORMATION]"
        header += "\n"
        header += "[TITLE]"
        header += self.get_name()
        header += "\n"
        header += "[AUTHOR]"
        if self.get_metadata().is_meta_key("annotator_name"):
            header += self.get_meta("annotator_name")
        header += "\n"
        header += "[SOURCE]"
        header += "\n"
        header += "[PRG]"
        header += "\n"
        header += "[FILEPATH]"
        header += "\n"
        header += "[DELAY]"
        header += "\n"
        header += "[CD TRACK]"
        header += "\n"
        header += "[COMMENT]"
        header += "\n"
        header += "[END INFORMATION]"
        header += "\n"
        header += "[SUBTITLE]"
        header += "\n"
        header += "[COLF]&HFFFFFF,[STYLE]bd,[SIZE]18,[FONT]Arial"
        header += "\n"
        header += "\n"

        return header
