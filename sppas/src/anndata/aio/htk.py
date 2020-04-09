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

    src.anndata.aio.htk.py
    ~~~~~~~~~~~~~~~~~~~~~~~

The Hidden Markov Model Toolkit (HTK) is a portable toolkit for building
and manipulating hidden Markov models.

The first version of the HTK Hidden Markov Model Toolkit was developed at
the Speech Vision and Robotics Group of the Cambridge University Engineering
Department (CUED) in 1989 by Steve Young.

"""

import codecs

from sppas.src.config import sg

from ..anndataexc import AioMultiTiersError
from ..anndataexc import AioLocationTypeError
from ..ann.annlocation import sppasLocation
from ..ann.annlocation import sppasPoint
from ..ann.annlocation import sppasInterval
from ..ann.annlabel import sppasLabel
from ..ann.annlabel import sppasTag

from .basetrs import sppasBaseIO
from .aioutils import load
from .aioutils import serialize_labels

# ---------------------------------------------------------------------------

# time values are in multiples of 100ns
TIME_UNIT = pow(10, -7)

# ---------------------------------------------------------------------------


class sppasBaseHTK(sppasBaseIO):
    """SPPAS HTK files reader and writer.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      contact@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2018  Brigitte Bigi

    """

    def __init__(self, name=None):
        """Initialize a new sppasMLF instance.

        :param name: (str) This transcription name.

        """
        if name is None:
            name = self.__class__.__name__
        super(sppasBaseHTK, self).__init__(name)
        
        self.software = "HTK"

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
        self._accept_overlaps = False  # to be verified

    # -----------------------------------------------------------------------

    @staticmethod
    def make_point(time_string):
        """Convert data into the appropriate sppasPoint().

        No radius if data is an integer. A default radius of 0.001 if data is a
        float.

        :param time_string: (str) a time in HTK format
        :returns: sppasPoint() representing time in seconds.

        """
        v = float(TIME_UNIT) * float(time_string)
        return sppasPoint(v, radius=0.005)

    # -----------------------------------------------------------------------

    @staticmethod
    def _format_time(second_count):
        """Convert a time in seconds into HTK format."""
        return int(1. / TIME_UNIT * float(second_count))

    # -----------------------------------------------------------------------

    def _serialize_annotation(self, ann):
        """Convert an annotation into a line for HTK lab of mlf files.

        :param ann: (sppasAnnotation)
        :returns: (str)

        """
        text = serialize_labels(ann.get_labels(),
                                separator=" ",
                                empty="",
                                alt=self._accept_alt_tag)

        # no label defined, or empty label
        if len(text) == 0:
            return ""
        if ann.get_location().is_point():
            raise AioLocationTypeError('HTK Label', 'points')

        begin = sppasBaseHTK._format_time(
            ann.get_lowest_localization().get_midpoint())
        end = sppasBaseHTK._format_time(
            ann.get_highest_localization().get_midpoint())

        if ' ' not in text:
            location = "{:d} {:d}".format(begin, end)
        else:
            # one "token" at a line, and only begin at first
            location = "{:d}".format(begin)
            text = text.replace(' ', '\n')

        return "{:s} {:s}\n".format(location, text)

# ---------------------------------------------------------------------------


class sppasLab(sppasBaseHTK):
    """SPPAS LAB reader and writer.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      contact@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2018  Brigitte Bigi

    Each line of a HTK label file contains the actual label optionally
    preceded by start and end times, and optionally followed by a match score.

    [<start> <end>] <<name> [<score>]> [";" <comment>]

    Multiple alternatives are written as a sequence of separate label
    lists separated by three slashes (///).

    Examples:
        - simple transcription:

            0000000 3600000 ice
            3600000 8200000 cream

        - alternative labels:

            0000000 2200000 I
            2200000 8200000 scream
            ///
            0000000 3600000 ice
            3600000 8200000 cream
            ///
            0000000 3600000 eyes
            3600000 8200000 cream

    *************  Only simple transcription is implemented yet.  ***********

    """

    @staticmethod
    def detect(filename):
        """Check whether a file is of HTK-Lab format or not.

        :param filename: (str) Name of the file to check.
        :returns: (bool)

        """
        try:
            with codecs.open(filename, 'r', sg.__encoding__) as fp:
                line = fp.readline()
                fp.close()
        except IOError:
            return False
        except UnicodeDecodeError:
            return False

        # the first line contains at least 2 columns
        tab = line.split()
        if len(tab) < 2:
            return False
        # First column is the start time: an integer
        try:
            int(line[0])
        except ValueError:
            return False

        return sppasBaseIO.is_number(line[0])

    # -----------------------------------------------------------------------

    def __init__(self, name=None):
        """Initialize a new sppasLab instance.

        :param name: (str) This transcription name.

        """
        if name is None:
            name = self.__class__.__name__
        super(sppasLab, self).__init__(name)

        self.default_extension = "lab"

    # -----------------------------------------------------------------------

    def read(self, filename):
        """Read a transcription from a file.

        :param filename:

        """
        lines = load(filename)
        tier = self.create_tier('Trans-MLF')
        text = ""
        prev_end = sppasBaseHTK.make_point(0)

        for line in lines:
            line = line.strip().split()

            has_begin = len(line) > 0 and sppasBaseIO.is_number(line[0])
            has_end = len(line) > 1 and sppasBaseIO.is_number(line[1])

            if has_begin and has_end:
                if len(text) > 0:
                    time = sppasInterval(prev_end,
                                         sppasBaseHTK.make_point(line[0]))
                    tier.create_annotation(sppasLocation(time),
                                           sppasLabel(sppasTag(text)))

                time = sppasInterval(sppasBaseHTK.make_point(line[0]),
                                     sppasBaseHTK.make_point(line[1]))

                text = line[2]
                score = None
                if len(line) > 3:
                    try:
                        score = float(line[3])
                    except ValueError:
                        # todo: auxiliary labels or comment
                        pass

                tier.create_annotation(sppasLocation(time),
                                       sppasLabel(sppasTag(text), score))
                text = ""
                prev_end = sppasBaseHTK.make_point(line[1])

            elif has_begin:
                text = text + " " + " ".join(line[1])
                # todo: auxiliary labels or comment

            else:
                text = text + " " + " ".join(line)

    # -----------------------------------------------------------------------

    def write(self, filename):
        """Write a transcription into a file.

        :param filename: (str)

        """
        if len(self) != 1:
            raise AioMultiTiersError("HTK Label")

        with codecs.open(filename, 'w', sg.__encoding__) as fp:

            if self.is_empty() is False:
                for ann in self[0]:
                    content = self._serialize_annotation(ann)
                    if len(content) > 0:
                        fp.write(content)

            fp.close()
