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

    src.anndata.aio.audacity.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~

Audacity is a multi-platform, free, easy-to-use, multi-track audio editor
and recorder. Audacity is free software, developed by a group of
volunteers and distributed under the GNU General Public License (GPL).

See: http://www.audacityteam.org/

"""
import codecs
import xml.etree.cElementTree as ET

from .basetrs import sppasBaseIO
from ..anndataexc import AnnDataTypeError
from ..ann.annotation import sppasAnnotation
from ..ann.annlocation import sppasLocation
from ..ann.annlocation import sppasPoint
from ..ann.annlocation import sppasInterval

from .aioutils import format_labels

# ---------------------------------------------------------------------------


class sppasAudacity(sppasBaseIO):
    """
    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      contact@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2018  Brigitte Bigi
    :summary:      Readers of Audacity files.

    Can work on both Audacity projects and Audacity Label tracks.

    """
    @staticmethod
    def detect(filename):
        """Check whether a file is of AUP format or not.
        AUP files are encoded in UTF-8 without BOM.

        :param filename: (str) Name of the file to check.
        :returns: (bool)

        """
        try:
            with codecs.open(filename, 'r', "UTF-8") as fp:
                fp.readline()
                doctype_line = fp.readline().strip()
                fp.close()
        except IOError:
            return False
        except UnicodeDecodeError:
            return False

        return 'audacityproject' in doctype_line

    # -----------------------------------------------------------------------

    @staticmethod
    def make_point(midpoint):
        """The localization is a time value, so a float."""

        try:
            midpoint = float(midpoint)
        except ValueError:
            raise AnnDataTypeError(midpoint, "float")

        return sppasPoint(midpoint, radius=0.0005)

    # -----------------------------------------------------------------------

    def __init__(self, name=None):
        """Initialize a new sppasAudacity instance.

        :param name: (str) This transcription name.

        """
        if name is None:
            name = self.__class__.__name__
        super(sppasAudacity, self).__init__(name)

        self.default_extension = "aup"
        self.software = "Audacity"

        self._accept_multi_tiers = True
        self._accept_no_tiers = True
        self._accept_metadata = True
        self._accept_ctrl_vocab = False
        self._accept_media = True
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

    def read(self, filename):
        """Read an AUP file and fill the Transcription.

        <!ELEMENT project (tags, (wavetrack | labeltrack | timetrack)*)>

        :param filename: (str)

        """
        tree = ET.parse(filename)
        root = tree.getroot()

        # Get metadata for self
        self._parse_metadata(root)

        # Tags
        self._parse_tags(root.find('tags'))

        # The tiers are stored in labeltrack elements
        for node in root.getiterator():
            name = sppasAudacity.normalize(node.tag)
            if name == "labeltrack":
                self._parse_labeltrack(node)

        # The audio files are stored in wavetrack elements
        for node in root.getiterator():
            name = sppasAudacity.normalize(node.tag)
            if name == "wavetrack":
                self._parse_wavetrack(node)

        # timetrack elements
        for node in root.getiterator():
            name = sppasAudacity.normalize(node.tag)
            if name == "timetrack":
                self._parse_timetrack(node)

    # -----------------------------------------------------------------------

    @staticmethod
    def normalize(name):
        """Provide namespaces in element names.

        Example:
            <Element '{http://audacity.sourceforge.net/xml/}simpleblockfile' at 0x03270230>
            <Element '{http://audacity.sourceforge.net/xml/}envelope' at 0x032702C0>
            <Element '{http://audacity.sourceforge.net/xml/}labeltrack' at 0x03270C50>
            <Element '{http://audacity.sourceforge.net/xml/}label' at 0x032701E8>

        See: http://effbot.org/zone/element-namespaces.htm

        """
        if name[0] == "{":
            uri, tag = name[1:].split("}")
            return tag
        else:
            return name

    # -----------------------------------------------------------------------

    def _parse_metadata(self, root):
        """
        <!ATTLIST project projname CDATA #REQUIRED>
        <!ATTLIST project version CDATA #REQUIRED>
        <!ATTLIST project audacityversion CDATA #REQUIRED>
        <!ATTLIST project sel0 CDATA #REQUIRED>
        <!ATTLIST project sel1 CDATA #REQUIRED>
        <!ATTLIST project vpos CDATA #REQUIRED>
        <!ATTLIST project h CDATA #REQUIRED>
        <!ATTLIST project zoom CDATA #REQUIRED>
        <!ATTLIST project rate CDATA #REQUIRED>

        :param root: (ET) Main XML Element tree root of a TRS file.
        :returns:

        """
        pass

    # -----------------------------------------------------------------------

    def _parse_tags(self, tags_root):
        """
        <!ELEMENT tags EMPTY>
        <!ATTLIST tags title CDATA #REQUIRED>
        <!ATTLIST tags artist CDATA #REQUIRED>
        <!ATTLIST tags album CDATA #REQUIRED>
        <!ATTLIST tags track CDATA #REQUIRED>
        <!ATTLIST tags year CDATA #REQUIRED>
        <!ATTLIST tags genre CDATA #REQUIRED>
        <!ATTLIST tags comments CDATA #REQUIRED>
        <!ATTLIST tags id3v2 (0|1) #REQUIRED>

        but ... the DTD does not match what is observed in files.

        :param root: XML Element tree root for the tags.

        """
        pass

    # -----------------------------------------------------------------------

    def _parse_labeltrack(self, tier_root):
        """

        The DTD:
            <!ELEMENT labeltrack (label*)>
            <!ATTLIST labeltrack name CDATA #REQUIRED>
            <!ATTLIST labeltrack numlabels CDATA #REQUIRED>

        but an example:
        <labeltrack name="Piste de marqueurs" numlabels="3" height="73" minimized="0" isSelected="0">

        <!ELEMENT label EMPTY>
        <!ATTLIST label t CDATA #REQUIRED>
        <!ATTLIST label t1 CDATA #REQUIRED>
        <!ATTLIST label title CDATA #REQUIRED>

        :param tier_root: XML Element tree root for a label track.

        """
        tier = self.create_tier(tier_root.attrib['name'])

        # Attributes are stored as metadata
        if 'height' in tier_root.attrib:
            tier.set_meta("tier_height", tier_root.attrib["height"])

        if 'minimized' in tier_root.attrib:
            minimized = tier_root.attrib['minimized']
            if minimized == "0":
                tier.set_meta("tier_is_closed", "false")
            else:
                tier.set_meta("tier_is_closed", "true")

        if 'isSelected' in tier_root.attrib:
            selected = tier_root.attrib['isSelected']
            if selected == "0":
                tier.set_meta("tier_is_selected", "false")
            else:
                tier.set_meta("tier_is_selected", "true")

        # Annotations are labels.
        # Attention: Audacity accepts mixed localizations.
        point_anns = list()
        interval_anns = list()

        for node in tier_root.iter():
            name = sppasAudacity.normalize(node.tag)
            if name == "label":
                # get annotation information
                labels = format_labels(node.attrib['title'])
                begin = sppasAudacity.make_point(node.attrib['t'])
                end = sppasAudacity.make_point(node.attrib['t1'])

                # create the annotation
                if begin == end:
                    new_a = sppasAnnotation(sppasLocation(begin), labels)
                    point_anns.append(new_a)
                else:
                    new_a = sppasAnnotation(sppasLocation(sppasInterval(begin, end)), labels)
                    interval_anns.append(new_a)

        # Fill the tier(s) with the annotations
        if len(point_anns) > 0 and len(interval_anns) > 0:
            point_tier = tier.copy()
            point_tier.set_name(tier_root.attrib['name']+"-points")
            self.append(point_tier)
            tier.set_name(tier_root.attrib['name'] + "-intervals")
            sppasAudacity.__fill_tier(tier, interval_anns)
            sppasAudacity.__fill_tier(point_tier, point_anns)

        elif len(point_anns) > 0:
            sppasAudacity.__fill_tier(tier, point_anns)

        elif len(interval_anns) > 0:
            sppasAudacity.__fill_tier(tier, interval_anns)

    # -----------------------------------------------------------------------

    def _parse_wavetrack(self, wave_root):
        """Not implemented.

        <!ELEMENT wavetrack (waveclip*)>

        :param wave_root: XML Element tree root for a wave track.

        """
        pass

    # -----------------------------------------------------------------------

    def _parse_timetrack(self, time_root):
        """Not implemented.

        <!ELEMENT timetrack (envelope)>
        <!ATTLIST timetrack name CDATA #REQUIRED>
        <!ATTLIST timetrack channel CDATA #REQUIRED>
        <!ATTLIST timetrack offset CDATA #REQUIRED>

        :param time_root: XML Element tree root for a time track.

        """
        pass

    # -----------------------------------------------------------------------
    # Private
    # -----------------------------------------------------------------------

    @staticmethod
    def __fill_tier(tier, annotations):
        for ann in annotations:
            tier.add(ann)
