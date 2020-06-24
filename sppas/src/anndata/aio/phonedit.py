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

    src.anndata.aio.phonedit.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~

PHONEDIT Signaix is a software for the analysis of sound, aerodynamic,
articulatory and electro-physiological signals developed by the Parole
et Langage Laboratory, Aix-en-Provence, France.

It provides a complete environment for the recording, the playback, the
display, the analysis, the labeling of multi-parametric data.

http://www.lpl-aix.fr/~lpldev/phonedit/

"""
import codecs
try:  # python 3
    from configparser import ConfigParser as SafeConfigParser
except ImportError:  # python 2
    from ConfigParser import SafeConfigParser
from datetime import datetime

from sppas.src.config import sg

from ..anndataexc import AnnDataTypeError
from ..anndataexc import AioNoTiersError
from ..anndataexc import AioMultiTiersError
from ..anndataexc import AioEmptyTierError
from ..anndataexc import AioLocationTypeError
from ..anndataexc import AioError
from ..ann.annlocation import sppasLocation
from ..ann.annlocation import sppasPoint
from ..ann.annlocation import sppasInterval
from ..ann.annlabel import sppasLabel
from ..ann.annlabel import sppasTag

from .basetrsio import sppasBaseIO
from .aioutils import format_labels
from .aioutils import serialize_labels
from .aioutils import is_ortho_tier
from .aioutils import load

# ---------------------------------------------------------------------------


class sppasBasePhonedit(sppasBaseIO):
    """Readers and writers of Phonedit files.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      contact@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2018  Brigitte Bigi

    """

    def __init__(self, name=None):
        """Initialize a new sppasBasePhonedit instance.

        :param name: (str) This transcription name.

        """
        if name is None:
            name = self.__class__.__name__
        super(sppasBasePhonedit, self).__init__(name)

        self.software = "Phonedit"

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
        self._accept_gaps = True
        self._accept_overlaps = True

    # -----------------------------------------------------------------------

    @staticmethod
    def _parse(filename):
        """Parse a configuration file.

        :param filename: (string) sppasAppConfig file name.

        """
        parser = SafeConfigParser()

        # Open the file
        try:
            with codecs.open(filename, "r", encoding="ISO-8859-1") as f:
                try:  # python 3
                    parser.read_file(f)
                except:  # python 2
                    parser.readfp(f)
        except Exception:
            # MissingSectionHeaderError
            raise AioError(filename)

        return parser

    # -----------------------------------------------------------------------

    @staticmethod
    def _parse_metadata(meta_list, meta_object):
        """Parse the metadata and append into an object.

        :param meta_list: (list) tuples with (key,value)
        :param meta_object: (sppasMeta)

        """
        for entry in meta_list:
            meta_object.set_meta(entry[0], entry[1])

# ---------------------------------------------------------------------------


class sppasMRK(sppasBasePhonedit):
    """Reader and writer of Phonedit MRK files.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      contact@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2018  Brigitte Bigi

    Example of the old format:

        [DSC_LEVEL_AA]
        DSC_LEVEL_NAME="transcription"
        DSC_LEVEL_CREATION_DATE=2018/03/09 09:57:07
        DSC_LEVEL_LASTMODIF_DATE=2018/03/09 09:57:07
        DSC_LEVEL_SOFTWARE=Phonedit Application 4.2.0.8
        [LBL_LEVEL_AA]
        LBL_LEVEL_AA_000000= "#" 0.000000 2497.100755
        LBL_LEVEL_AA_000001= "ipu_1" 2497.100755 5683.888038
        LBL_LEVEL_AA_000002= "#" 5683.888038 5743.602653
        LBL_LEVEL_AA_000003= "ipu_2" 5743.602653 8460.595544

    The new MRK format includes sections for time slots.

    """

    @staticmethod
    def detect(filename):
        """Check whether a file is of CTM format or not.

        :param filename: (str) Name of the file to check.
        :returns: (bool)

        """
        try:
            sppasBasePhonedit._parse(filename)
        except Exception:
            return False
        return True

    # -----------------------------------------------------------------------

    def __init__(self, name=None):
        """Initialize a new sppasBaseSclite instance.

        :param name: (str) This transcription name.

        """
        if name is None:
            name = self.__class__.__name__
        super(sppasMRK, self).__init__(name)

        self.default_extension = "mrk"

    # -----------------------------------------------------------------------

    @staticmethod
    def make_point(midpoint):
        """In Phonedit, the localization is a time value, so a float.

        :param midpoint: (str) a time in ELAN format
        :returns: sppasPoint() representing time in seconds.

        """
        try:
            midpoint = float(midpoint)
        except ValueError:
            raise AnnDataTypeError(midpoint, "float")

        return sppasPoint(midpoint / 1000., radius=0.0005)

    # -----------------------------------------------------------------------

    @staticmethod
    def format_point(second_count):
        """Convert a time in seconds into MRK format."""
        try:
            second_count = float(second_count)
        except ValueError:
            raise AnnDataTypeError(second_count, "float")

        return 1000. * float(second_count)

    # -----------------------------------------------------------------------
    # reader
    # -----------------------------------------------------------------------

    def read(self, filename):
        """Read a Phonedit mark file.

        :param filename: intput filename.

        """
        parser = self._parse(filename)

        # Extract metadata and create tiers
        for section_name in parser.sections():
            if section_name == "Information":
                sppasBasePhonedit._parse_metadata(parser.items(section_name),
                                                  self)
            if "DSC_LEVEL_" in section_name:
                self._parse_level(parser.items(section_name), section_name)

        # Extract annotations with time values
        for section_name in parser.sections():
            if "LBL_LEVEL_" in section_name:
                self._parse_labels(parser.items(section_name))

    # -----------------------------------------------------------------------

    def _parse_level(self, data_list, level_id):
        """Parse a section DSC_LEVEL_.

        Creates a tier with the level name and add metadata.

        """
        # Fix the name of the tier.
        level_name = "unknown"
        for entry in data_list:
            if "dsc_level_name" == entry[0]:
                level_name = entry[1]
                level_name = level_name[1:-1]
                del entry

        # Create the tier
        tier = self.create_tier(level_name)
        # override the default "id" by the name of the section
        tier.set_meta("id", level_id)
        # extract metadata for this tier
        sppasBasePhonedit._parse_metadata(data_list, tier)

    # -----------------------------------------------------------------------

    @staticmethod
    def _format_text(text):
        """Remove the " at the beginning and at the end of the string."""
        text = text.strip()

        if text.endswith('"'):
            text = text[:-1]
        if text.startswith('"'):
            text = text[1:]

        return text

    # -----------------------------------------------------------------------

    def _parse_labels(self, data_list):
        """Parse labels of a section LBL_LEVEL_ ."""
        for entry in data_list:
            key = entry[0].upper()
            line = entry[1]

            # Which tier is concerned?
            tier = None
            for t in self:
                tier_id = t.get_meta('id')
                tier_id = tier_id.replace('DSC', 'LBL')
                if key.startswith(tier_id) is True:
                    tier = t
                    break
            if tier is None:
                # something went wrong...
                tier = self.create_tier(key)

            # Extract the content of the annotation
            tab_line = line.split()

            # ... localization
            begin = float(tab_line[-2])
            end = float(tab_line[-1])
            if begin < end:
                localization = sppasInterval(
                    sppasMRK.make_point(begin),
                    sppasMRK.make_point(end))
            else:
                localization = sppasMRK.make_point(begin)

            # ... tag text
            content = " ".join(tab_line[:-2])
            content = sppasMRK._format_text(content)
            if is_ortho_tier(tier.get_name()) is False:
                content = content.replace(" ", "\n")
            labels = format_labels(content, separator="\n")

            # Create/Add the annotation into the tier
            ann = tier.create_annotation(sppasLocation(localization),
                                         labels)

            # override the default "id" by the name of the attribute
            ann.set_meta("id", key)

    # -----------------------------------------------------------------------
    # writer
    # -----------------------------------------------------------------------

    def write(self, filename):
        """Write a Phonedit mark file.

        :param filename: output filename.

        """
        code_a = ord("A")
        last_modified = datetime.now().strftime("%Y/%m/%d %H:%M:%S")

        with codecs.open(filename, mode="w", encoding="ISO-8859-1") as fp:

            for index_tier, tier in enumerate(self):

                # fix information about this tier/level
                point = tier.is_point()
                level = "LEVEL_{:s}{:s}".format(
                            chr(code_a + int(index_tier / 26)),
                            chr(code_a + int(index_tier % 26)))

                # Write information about the tier
                fp.write("[DSC_{:s}]\n".format(level))
                fp.write("DSC_LEVEL_NAME=\"{:s}\"\n"
                         "".format(tier.get_name()))
                fp.write("DSC_LEVEL_SOFTWARE={:s} {:s}\n"
                         "".format(sg.__name__, sg.__version__))
                fp.write("DSC_LEVEL_LASTMODIF_DATE={:s}\n"
                         "".format(last_modified))

                # Write annotations
                fp.write("[LBL_{:s}]\n".format(level))
                for index_ann, ann in enumerate(tier):

                    text = serialize_labels(
                        ann.get_labels(), separator=" ", empty="", alt=True)
                    fp.write("LBL_{:s}_{:06d}=\"{:s}\""
                             "".format(level, index_ann, text))

                    if point:
                        # Phonedit supports degenerated intervals
                        # (instead of points)
                        b = sppasMRK.format_point(
                            ann.get_lowest_localization().get_midpoint())
                        e = b
                    else:
                        b = sppasMRK.format_point(
                            ann.get_lowest_localization().get_midpoint())
                        e = sppasMRK.format_point(
                            ann.get_highest_localization().get_midpoint())
                    fp.write(" {:s} {:s}\n".format(str(b), str(e)))

            fp.close()

# ---------------------------------------------------------------------------


class sppasSignaix(sppasBaseIO):
    """Reader and writer of F0 values from LPL-Signaix.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      contact@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2018  Brigitte Bigi

    """

    @staticmethod
    def detect(filename):
        """Check whether a file is of CTM format or not.

        :param filename: (str) Name of the file to check.
        :returns: (bool)

        """
        try:
            lines = load(filename)
        except:
            return False

        for line in lines:
            line = line.strip()
            if len(line) > 0:
                if sppasBaseIO.is_number(line) is False:
                    return False
        return True

    # -----------------------------------------------------------------------

    def __init__(self, name=None):
        """Initialize a new sppasSignaix instance.

        :param name: (str) This transcription name.

        """
        if name is None:
            name = self.__class__.__name__
        super(sppasSignaix, self).__init__(name)

        self.default_extension = "hz"
        self.software = "Und"

        self._accept_multi_tiers = False
        self._accept_no_tiers = False
        self._accept_metadata = False
        self._accept_ctrl_vocab = False
        self._accept_media = False
        self._accept_hierarchy = False
        self._accept_point = True
        self._accept_interval = False
        self._accept_disjoint = False
        self._accept_alt_localization = False
        self._accept_alt_tag = False
        self._accept_radius = False
        self._accept_gaps = False
        self._accept_overlaps = False

    # -----------------------------------------------------------------------

    def read(self, filename, delta=0.01):
        """Read a file with Pitch values sampled at delta seconds.

        The file contains one value at a line.
        If the audio file is 30 seconds long and delta is 0.01, we expect:
        100 * 30 = 3,000 lines in the file

        :param filename: (str) intput filename.
        :param delta: (float) sampling of the file. Default is one F0
        value each 10ms, so 100 values / second

        """
        delta = float(delta)
        lines = load(filename)

        tier = self.create_tier("Pitch")
        # The reference time point of each interval is the middle.
        # The radius allows to cover the delta range.
        radius = delta / 2.
        # Start time
        current_time = delta / 2.
        for line in lines:
            # ignore blank lines
            line = line.strip()
            if len(line) == 0:
                continue
            # create an annotation from the given line
            location = sppasLocation(sppasPoint(current_time, radius))
            label = sppasLabel(sppasTag(line, tag_type='float'))
            tier.create_annotation(location, label)
            current_time += delta

    # -----------------------------------------------------------------------

    def write(self, filename):
        """Write a file with pitch values.

        :param filename: (str) output filename

        """
        if self.is_empty():
            raise AioNoTiersError(".hz")

        if len(self) > 1:
            tier = self.find("Pitch", case_sensitive=False)
            if tier is None:
                raise AioMultiTiersError("Signaix-Pitch")
        else:
            tier = self[0]

        # we expect a not empty tier
        if self.is_empty() is True:
            raise AioEmptyTierError(".hz", tier.get_name())

        # we expect a tier with only sppasPoint
        if tier.is_point() is False:
            raise AioLocationTypeError(".hz", "intervals")

        # check if the tier is really pitch values
        # or at least, float values sampled at a delta time.
        if tier.is_float() is False:
            raise AnnDataTypeError(tier.get_name(), "float")

        if len(tier) > 1:
            delta = tier[1].get_location().get_best().get_midpoint() - \
                    tier[0].get_location().get_best().get_midpoint()
            delta = round(delta, 6)
            for i in range(1, len(tier)):

                current_delta = tier[i].get_location().get_best().get_midpoint() - \
                                tier[i-1].get_location().get_best().get_midpoint()
                current_delta = round(current_delta, 6)
                if delta != current_delta:
                    raise AnnDataTypeError(tier.get_name(),
                                           "points in delta range")

        # ok. write the data into the file.
        with open(filename, "w", buffering=8096) as fp:
            for ann in tier:
                fp.write("{:s}\n"
                         "".format(ann.get_labels()[0].get_best().get_content()))
            fp.close()
