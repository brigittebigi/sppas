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

    anndata.aio.anvil.py
    ~~~~~~~~~~~~~~~~~~~~

ANVIL is a free video annotation tool.

| Kipp, M. (2012)
| Multimedia Annotation, Querying and Analysis in ANVIL.
| In: M. Maybury (ed.) Multimedia Information Extraction,
| Chapter 21, John Wiley & Sons, pp: 351-368.

BE AWARE that the support of anvil files by SPPAS has to be verified,
tested and extended!!!

"""
import xml.etree.cElementTree as ET

from ..anndataexc import AnnDataTypeError
from ..ann.annlocation import sppasLocation
from ..ann.annlocation import sppasPoint
from ..ann.annlocation import sppasInterval

from .basetrsio import sppasBaseIO
from .aioutils import format_labels

# ---------------------------------------------------------------------------


class sppasAnvil(sppasBaseIO):
    """ANVIL (partially) reader.

    :author:       Brigitte Bigi, Jibril Saffi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      contact@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2018  Brigitte Bigi

    """

    @staticmethod
    def detect(filename):
        """Check whether a file is of ANVIL format or not.

        :param filename: (str) Name of the file to check.
        :returns: (bool)

        """
        try:
            tree = ET.parse(filename)
            root = tree.getroot()
        except IOError:
            return False
        except UnicodeDecodeError:
            return False

        return root.find('body') is not None

    # -----------------------------------------------------------------------

    @staticmethod
    def make_point(midpoint):
        """The localization is a time value, so always a float."""
        try:
            midpoint = float(midpoint)
        except ValueError:
            raise AnnDataTypeError(midpoint, "float")

        return sppasPoint(midpoint, radius=0.005)

    # -----------------------------------------------------------------------

    def __init__(self, name=None):
        """Initialize a new ANVIL instance.

        :param name: (str) This transcription name.

        """
        if name is None:
            name = self.__class__.__name__
        super(sppasAnvil, self).__init__(name)

        self._accept_multi_tiers = True
        self._accept_no_tiers = True
        self._accept_metadata = True
        self._accept_ctrl_vocab = False  # to be verified
        self._accept_media = True        # to be verified
        self._accept_hierarchy = True
        self._accept_point = False
        self._accept_interval = True
        self._accept_disjoint = False
        self._accept_alt_localization = False
        self._accept_alt_tag = False
        self._accept_radius = False
        self._accept_gaps = True        # to be verified
        self._accept_overlaps = False   # to be verified

        self.default_extension = "anvil"
        self.software = "Anvil"

    # -----------------------------------------------------------------------

    def read(self, filename):
        """Read an ANVIL file and fill the Transcription.

        :param filename: (str)

        """
        tree = ET.parse(filename)
        root = tree.getroot()

        # FIXME we ought to get the ctrl vocabs in the spec file
        # there also ought to be a representation of the hiererchy,
        # but since we have multiple, non aligned tiers,
        # it's not trivial to implement

        body_root = root.find('body')
        self._read_tracks(body_root)

    # -----------------------------------------------------------------------

    def _read_tracks(self, body_root):
        for track_root in body_root.findall('track'):
            if(track_root.attrib['type'] == "primary" or
               track_root.attrib['type'] == "primarypoint"):
                self._read_primary_track(track_root)

            elif track_root.attrib['type'] == "singleton":
                self._read_singleton_track(track_root, body_root)

            elif track_root.attrib['type'] == "span":
                self._read_span_track(track_root, body_root)

            elif track_root.attrib['type'] == "subdivision":
                self._read_subdivision_track(track_root, body_root)

            else:
                raise Exception('unknown track type')

    # -----------------------------------------------------------------------

    def _read_primary_track(self, track_root):
        """Read a primary track (primary or primarypoint).

        :param track_root:

        """
        # Create tiers of the primary track.
        self.__create_tier_from_attribute(track_root)

        # Parse elements and create annotations
        for el_root in track_root.findall('el'):

            if track_root.attrib['type'] == 'primary':
                begin = float(el_root.attrib['start'])
                end = float(el_root.attrib['end'])
                if begin > end:
                    begin, end = end, begin
                elif begin == end:
                    continue

                localization = sppasInterval(sppasAnvil.make_point(begin),
                                             sppasAnvil.make_point(end))

            elif track_root.attrib['type'] == 'primarypoint':
                time = float(el_root.attrib['time'])
                localization = sppasAnvil.make_point(time)

            else:
                raise Exception('unknown primary track type')

            self.__create_annotation_from_el(track_root, el_root, localization)

    # -----------------------------------------------------------------------

    def _read_singleton_track(self, track_root, body_root):
        # find ref
        ref_root = body_root.find(
            "track[@name='%s']" %
            track_root.attrib['ref'])

        self.__create_tier_from_attribute(track_root)

        for el_root in track_root.findall('el'):

            ref_el = ref_root.find(
                "el[@index='%s']" %
                el_root.attrib['ref'])

            begin = float(ref_el.attrib['start'])
            end = float(ref_el.attrib['end'])
            if begin > end:
                begin, end = end, begin
            elif begin == end:
                continue

            localization = sppasInterval(sppasAnvil.make_point(begin),
                                         sppasAnvil.make_point(end))

            self.__create_annotation_from_el(track_root, el_root, localization)

    # -----------------------------------------------------------------------

    def _read_span_track(self, track_root, body_root):
        # find ref
        ref_root = body_root.find(
            "track[@name='%s']" %
            track_root.attrib['ref'])

        self.__create_tier_from_attribute(track_root)

        for el_root in track_root.findall('el'):

            begin_ref = el_root.attrib['start']
            end_ref = el_root.attrib['end']
            begin_el = ref_root.find(
                "el[@index='%s']" %
                begin_ref)
            end_el = ref_root.find(
                "el[@index='%s']" %
                end_ref)

            begin = float(begin_el.attrib['start'])
            end = float(end_el.attrib['end'])
            if begin > end:
                begin, end = end, begin
            elif begin == end:
                continue

            localization = sppasInterval(sppasAnvil.make_point(begin),
                                         sppasAnvil.make_point(end))

            self.__create_annotation_from_el(track_root, el_root, localization)

    # -----------------------------------------------------------------------

    def _read_subdivision_track(self, track_root, body_root):
        # find ref
        ref_root = body_root.find(
            "track[@name='%s']" %
            track_root.attrib['ref'])

        self.__create_tier_from_attribute(track_root)

        for el_group_root in track_root.findall('el-group'):

            ref_el = ref_root.find(
                "el[@index='%s']" %
                el_group_root.attrib['ref'])

            time_slots = list()
            time_slots.append(float(ref_el.attrib['start']))
            for el_root in el_group_root.findall('el'):
                if 'start' in el_root.attrib:
                    time_slots.append(float(el_root.attrib['start']))
            time_slots.append(float(ref_el.attrib['end']))

            b = 0
            e = 1

            for el_root in el_group_root.findall('el'):
                begin = time_slots[b]
                b += 1
                end = time_slots[e]
                e += 1
                localization = sppasInterval(sppasAnvil.make_point(begin),
                                             sppasAnvil.make_point(end))

                self.__create_annotation_from_el(track_root,
                                                 el_root,
                                                 localization)

    # -----------------------------------------------------------------------

    def __create_tier_from_attribute(self, track_root):
        """Create a set of tiers from 'attribute' of 'track'.

        :param track_root:

        """
        for attribute_node in track_root.iter('attribute'):
            tier_name = sppasAnvil.__fix_tier_name(track_root, attribute_node)
            if self.find(tier_name) is None:
                self.create_tier(tier_name)

    # -----------------------------------------------------------------------

    def __create_annotation_from_el(self, track_root, el_root, localization):
        """Create a set of annotations from 'attribute' of 'el'.

        :param track_root:
        :param el_root:
        :param localization:

        """
        for attribute_node in el_root.findall('attribute'):
            labels = format_labels(attribute_node.text)
            tier = self.find(sppasAnvil.__fix_tier_name(track_root,
                                                        attribute_node))
            tier.create_annotation(sppasLocation(localization),
                                   labels)

    # -----------------------------------------------------------------------

    @staticmethod
    def __fix_tier_name(track_root, attribute_node):
        return track_root.attrib['name'] + \
               '.' + \
               attribute_node.attrib['name']
