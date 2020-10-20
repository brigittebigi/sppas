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

    src.anndata.aio.tests.test_aio_utils.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2018  Brigitte Bigi
    :summary:      Utilities for readers and writers.

"""
import os.path
import unittest

from ..tier import sppasTier
from ..ann.annotation import sppasAnnotation
from ..ann.annlocation import sppasLocation
from ..ann.annlocation import sppasPoint
from ..ann.annlocation import sppasInterval
from ..ann.annlabel import sppasLabel
from ..ann.annlabel import sppasTag

from ..aio.aioutils import fill_gaps, check_gaps, unfill_gaps
from ..aio.aioutils import merge_overlapping_annotations
from ..aio.aioutils import load
from ..aio.aioutils import format_labels, serialize_labels

# ---------------------------------------------------------------------------

DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")

# ---------------------------------------------------------------------------


class TestUtils(unittest.TestCase):

    def test_load(self):
        """Load a file into lines."""

        lines = load(os.path.join(DATA, "sample.ctm"))
        self.assertEqual(len(lines), 45)

        with self.assertRaises(UnicodeDecodeError):
            load(os.path.join(DATA, "sample-utf16.TextGrid"))

        with self.assertRaises(IOError):
            load(os.path.join(DATA, "not-exists"))

    # -----------------------------------------------------------------------

    def test_format_labels(self):
        """Convert a string into a list of labels."""

        # Without score
        self.assertEqual([], format_labels(""))

        self.assertEqual([sppasLabel(sppasTag("toto"))],
                         format_labels("toto"))

        self.assertEqual([sppasLabel(sppasTag("toto")), sppasLabel(sppasTag("toto"))],
                         format_labels("toto\ntoto"))

        self.assertEqual([sppasLabel(sppasTag("toto")), sppasLabel(sppasTag("toto"))],
                         format_labels("toto toto", separator=" "))

        self.assertEqual([sppasLabel(sppasTag("toto toto"))],
                         format_labels("toto\ntoto", separator=" "))

        # With score
        self.assertEqual([sppasLabel(sppasTag("toto"), 0.5)],
                         format_labels("toto=0.5"))

        self.assertEqual([sppasLabel(sppasTag("toto=x"))],
                         format_labels("toto=x"))

        self.assertEqual([sppasLabel([sppasTag("toto"), sppasTag("titi")], [0.6, 0.4])],
                         format_labels("{toto=0.6|titi=0.4}"))

    # -----------------------------------------------------------------------

    def test_serialize_labels(self):
        """... Convert the label into a string."""

        label = sppasLabel(sppasTag(""))
        s = serialize_labels([label])
        self.assertEqual("", s)

        label = sppasLabel(sppasTag("IGNORE_TIME_SEGMENT_IN_SCORING"))
        s = serialize_labels([label])
        self.assertEqual("IGNORE_TIME_SEGMENT_IN_SCORING", s)

        label = sppasLabel(sppasTag("toto"))
        s = serialize_labels([label])
        self.assertEqual("toto", s)

        tag1 = sppasTag("uh")
        tag2 = sppasTag("um")
        label = sppasLabel([tag1, tag2])
        s = serialize_labels([label])
        self.assertEqual("{uh|um}", s)

        tag1 = sppasTag("uh")
        tag2 = sppasTag("um")
        label = sppasLabel([tag1, tag2], [0.6, 0.4])
        s = serialize_labels([label])
        self.assertEqual("{uh=0.6|um=0.4}", s)

    # -----------------------------------------------------------------------

    def test_check_gaps(self):
        """Check if there are holes between annotations."""

        tier = sppasTier("empty")
        self.assertTrue(check_gaps(tier))

    # -----------------------------------------------------------------------

    def test_fill_gaps(self):
        """Return the tier in which the temporal gaps between annotations are
        filled with an un-labelled annotation."""

        # integers
        tier = sppasTier()
        anns = [sppasAnnotation(
                        sppasLocation(sppasInterval(sppasPoint(1), sppasPoint(2))),
                        sppasLabel(sppasTag("bar"))),
                sppasAnnotation(
                        sppasLocation(sppasInterval(sppasPoint(3), sppasPoint(4))),
                        sppasLabel(sppasTag("foo"))),
                sppasAnnotation(
                        sppasLocation(sppasInterval(sppasPoint(5), sppasPoint(6))),
                        sppasLabel(sppasTag("fiz"))),
                ]
        for a in anns:
            tier.append(a)
        self.assertEqual(len(tier), 3)
        self.assertEqual(tier.get_first_point().get_midpoint(), 1)
        self.assertEqual(tier.get_last_point().get_midpoint(), 6)
        filled_tier = fill_gaps(tier, sppasPoint(0), sppasPoint(10))
        self.assertEqual(len(filled_tier), 7)
        self.assertEqual(filled_tier.get_first_point().get_midpoint(), 0)
        self.assertEqual(filled_tier.get_last_point().get_midpoint(), 10)

        # float
        tier = sppasTier()
        anns = [sppasAnnotation(
            sppasLocation(sppasInterval(sppasPoint(1.), sppasPoint(2.))),
            sppasLabel(sppasTag("bar"))),
            sppasAnnotation(
                sppasLocation(sppasInterval(sppasPoint(3.), sppasPoint(4.))),
                sppasLabel(sppasTag("foo"))),
            sppasAnnotation(
                sppasLocation(sppasInterval(sppasPoint(5.), sppasPoint(6.))),
                sppasLabel(sppasTag("fiz"))),
        ]
        for a in anns:
            tier.append(a)
        self.assertEqual(len(tier), 3)
        self.assertEqual(tier.get_first_point().get_midpoint(), 1.)
        self.assertEqual(tier.get_last_point().get_midpoint(), 6.)
        filled_tier = fill_gaps(tier, sppasPoint(0.), sppasPoint(10.))
        self.assertEqual(len(filled_tier), 7)
        self.assertEqual(filled_tier.get_first_point().get_midpoint(), 0.)
        self.assertEqual(filled_tier.get_last_point().get_midpoint(), 10.)

        # empty tier
        tier = sppasTier("empty")
        filled_tier = fill_gaps(tier, sppasPoint(0.), sppasPoint(10.))
        self.assertEqual(filled_tier.get_first_point().get_midpoint(), 0.)
        self.assertEqual(filled_tier.get_last_point().get_midpoint(), 10.)
        self.assertEqual(1, len(filled_tier))

    # -----------------------------------------------------------------------

    def test_unfill_gaps(self):
        """Return the tier in which un-labelled annotations are removed."""

        # integers
        tier = sppasTier()
        anns = [sppasAnnotation(
                        sppasLocation(sppasInterval(sppasPoint(1), sppasPoint(2))),
                        sppasLabel(sppasTag("bar"))),
                sppasAnnotation(
                        sppasLocation(sppasInterval(sppasPoint(2), sppasPoint(3))),
                        sppasLabel(sppasTag(""))),
                sppasAnnotation(
                        sppasLocation(sppasInterval(sppasPoint(3), sppasPoint(4))),
                        sppasLabel(sppasTag("foo"))),
                sppasAnnotation(
                        sppasLocation(sppasInterval(sppasPoint(4), sppasPoint(5)))
                ),
                sppasAnnotation(
                        sppasLocation(sppasInterval(sppasPoint(5), sppasPoint(6))),
                        sppasLabel(sppasTag("fiz"))),
                ]
        for a in anns:
            tier.append(a)
        self.assertEqual(len(tier), 5)
        self.assertEqual(tier.get_first_point().get_midpoint(), 1)
        self.assertEqual(tier.get_last_point().get_midpoint(), 6)
        new_tier = unfill_gaps(tier)
        self.assertEqual(len(new_tier), 3)

    # -----------------------------------------------------------------------

    def test_check_overlaps(self):
        """Check whether some annotations are overlapping or not."""
        pass

    # -----------------------------------------------------------------------

    def test_merge_overlapping_annotations(self):
        """Merge overlapping annotations. The labels of 2 overlapping
        annotations are appended."""

        tier = sppasTier()
        localizations = [sppasInterval(sppasPoint(1.), sppasPoint(2.)),    # 0
                         sppasInterval(sppasPoint(1.5), sppasPoint(2.)),   # 1
                         sppasInterval(sppasPoint(1.8), sppasPoint(2.)),   # 2
                         sppasInterval(sppasPoint(1.8), sppasPoint(2.5)),  # 3
                         sppasInterval(sppasPoint(2.), sppasPoint(2.3)),   # 4
                         sppasInterval(sppasPoint(2.), sppasPoint(2.5)),   # 5
                         sppasInterval(sppasPoint(2.), sppasPoint(3.)),    # 6
                         sppasInterval(sppasPoint(2.4), sppasPoint(4.)),   # 7
                         sppasInterval(sppasPoint(2.5), sppasPoint(3.))    # 8
                         ]
        annotations = [sppasAnnotation(sppasLocation(t), sppasLabel(sppasTag(i))) for i, t in enumerate(localizations)]
        for i, a in enumerate(annotations):
            tier.add(a)
            self.assertEqual(len(tier), i + 1)

        copy_tier = tier.copy()
        new_tier = merge_overlapping_annotations(tier)

        # we expect the original tier was not modified
        for ann, copy_ann in zip(tier, copy_tier):
            self.assertEqual(ann, copy_ann)

        expected_tier = sppasTier()
        expected_tier.create_annotation(sppasLocation(sppasInterval(sppasPoint(1.), sppasPoint(1.5))),
                                        sppasLabel(sppasTag("0")))
        expected_tier.create_annotation(sppasLocation(sppasInterval(sppasPoint(1.5), sppasPoint(1.8))),
                                        [sppasLabel(sppasTag("0")),
                                         sppasLabel(sppasTag("1"))])
        expected_tier.create_annotation(sppasLocation(sppasInterval(sppasPoint(1.8), sppasPoint(2.0))),
                                        [sppasLabel(sppasTag("0")),
                                         sppasLabel(sppasTag("1")),
                                         sppasLabel(sppasTag("2")),
                                         sppasLabel(sppasTag("3"))])
        expected_tier.create_annotation(sppasLocation(sppasInterval(sppasPoint(2.0), sppasPoint(2.3))),
                                        [sppasLabel(sppasTag("3")),
                                         sppasLabel(sppasTag("4")),
                                         sppasLabel(sppasTag("5")),
                                         sppasLabel(sppasTag("6"))])
        expected_tier.create_annotation(sppasLocation(sppasInterval(sppasPoint(2.3), sppasPoint(2.4))),
                                        [sppasLabel(sppasTag("3")),
                                         sppasLabel(sppasTag("5")),
                                         sppasLabel(sppasTag("6"))])
        expected_tier.create_annotation(sppasLocation(sppasInterval(sppasPoint(2.4), sppasPoint(2.5))),
                                        [sppasLabel(sppasTag("3")),
                                         sppasLabel(sppasTag("5")),
                                         sppasLabel(sppasTag("6")),
                                         sppasLabel(sppasTag("7"))])
        expected_tier.create_annotation(sppasLocation(sppasInterval(sppasPoint(2.5), sppasPoint(3.))),
                                        [sppasLabel(sppasTag("6")),
                                         sppasLabel(sppasTag("7")),
                                         sppasLabel(sppasTag("8"))])
        expected_tier.create_annotation(sppasLocation(sppasInterval(sppasPoint(3.), sppasPoint(4.))),
                                        sppasLabel(sppasTag("7")))
        self.assertEqual(len(expected_tier), len(new_tier))
        for new_ann, expected_ann in zip(new_tier, expected_tier):
            self.assertEqual(new_ann, expected_ann)
