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

    src.anndata.tests.test_aio_xra.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2018  Brigitte Bigi
    :summary:      Test the class sppasXRA().

    To read and write SPPAS XRA files.

"""
import unittest
import os.path
import shutil

from ..aio.xra import sppasXRA
from sppas.src.wkps.fileutils import sppasFileUtils

# ---------------------------------------------------------------------------

TEMP = sppasFileUtils().set_random()
DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")

# ---------------------------------------------------------------------------


class TestXRA(unittest.TestCase):
    """
    Represents an XRA file, the native format of SPPAS.

    """
    def setUp(self):
        if os.path.exists(TEMP) is False:
            os.mkdir(TEMP)

    def tearDown(self):
        shutil.rmtree(TEMP)

    # -----------------------------------------------------------------------

    def test_members(self):
        xra = sppasXRA()
        self.assertTrue(xra.multi_tiers_support())
        self.assertTrue(xra.no_tiers_support())
        self.assertTrue(xra.metadata_support())
        self.assertTrue(xra.ctrl_vocab_support())
        self.assertTrue(xra.media_support())
        self.assertTrue(xra.hierarchy_support())
        self.assertTrue(xra.point_support())
        self.assertTrue(xra.interval_support())
        self.assertTrue(xra.disjoint_support())
        self.assertTrue(xra.alternative_localization_support())
        self.assertTrue(xra.alternative_tag_support())
        self.assertTrue(xra.radius_support())
        self.assertTrue(xra.gaps_support())
        self.assertTrue(xra.overlaps_support())

    # -----------------------------------------------------------------------

    def test_read1(self):
        xra3 = sppasXRA()
        xra3.read(os.path.join(DATA, "sample-1.1.xra"))
        # Tiers
        self.assertEqual(len(xra3), 3)
        # ... First Tier
        self.assertEqual(len(xra3[0]), 2)
        self.assertEqual(xra3.get_tier_index("Intonation"), 0)
        self.assertEqual(xra3[0].get_id(), "t1")
        self.assertTrue(xra3[0].is_point())
        # ... Second Tier
        self.assertEqual(len(xra3[1]), 3)
        self.assertEqual(xra3.get_tier_index("TokensAlign"), 1)
        self.assertEqual(xra3[1].get_id(), "t2")
        self.assertTrue(xra3[1].is_interval())
        # ... 3rd Tier
        self.assertEqual(len(xra3[2]), 1)
        self.assertEqual(xra3.get_tier_index("IPU"), 2)
        self.assertEqual(xra3[2].get_id(), "t3")
        self.assertTrue(xra3[2].is_interval())
        # Controlled vocabulary
        self.assertEqual(len(xra3.get_ctrl_vocab_list()), 1)
        self.assertIsNotNone(xra3.get_ctrl_vocab_from_name("v0"))
        # Hierarchy
        #self.assertEqual(len(xra3.hierarchy), 2)

    # -----------------------------------------------------------------------

    def test_read2(self):
        xra3 = sppasXRA()
        xra3.read(os.path.join(DATA, "sample-1.2.xra"))
        # Metadata
        self.assertEqual(xra3.get_meta("created"), "2015-08-03")
        self.assertEqual(xra3.get_meta("license"), "GPL v3")
        # Media
        self.assertEqual(len(xra3.get_media_list()), 3)
        self.assertIsNotNone(xra3.get_media_from_id("m1"))
        self.assertIsNotNone(xra3.get_media_from_id("m2"))
        self.assertIsNotNone(xra3.get_media_from_id("m3"))
        self.assertIsNone(xra3.get_media_from_id("m4"))
        # Tiers
        self.assertEqual(len(xra3), 3)
        # ... First Tier
        self.assertEqual(len(xra3[0]), 2)
        self.assertEqual(xra3.get_tier_index("Intonation"), 0)
        self.assertEqual(xra3[0].get_id(), "t1")
        self.assertTrue(xra3[0].is_point())
        # ... Second Tier
        self.assertEqual(len(xra3[1]), 3)
        self.assertEqual(xra3.get_tier_index("TokensAlign"), 1)
        self.assertEqual(xra3[1].get_id(), "t2")
        self.assertTrue(xra3[1].is_interval())
        # ... 3rd Tier
        self.assertEqual(len(xra3[2]), 1)
        self.assertEqual(xra3.get_tier_index("IPU"), 2)
        self.assertEqual(xra3[2].get_id(), "t3")
        self.assertTrue(xra3[2].is_interval())
        # Controlled vocabulary
        self.assertEqual(len(xra3.get_ctrl_vocab_list()), 1)
        self.assertIsNotNone(xra3.get_ctrl_vocab_from_name("v0"))
        # Hierarchy
        #self.assertEqual(len(xra3.hierarchy), 2)

    # -----------------------------------------------------------------------

    def test_read3(self):
        xra3 = sppasXRA()
        xra3.read(os.path.join(DATA, "sample-1.3.xra"))
        # Metadata
        self.assertEqual(xra3.get_meta("created"), "2017-03-06")
        self.assertEqual(xra3.get_meta("license"), "GPL v3")
        # Media
        self.assertEqual(len(xra3.get_media_list()), 3)
        self.assertIsNotNone(xra3.get_media_from_id("m1"))
        self.assertIsNotNone(xra3.get_media_from_id("m2"))
        self.assertIsNotNone(xra3.get_media_from_id("m3"))
        self.assertIsNone(xra3.get_media_from_id("m4"))
        # Tiers
        self.assertEqual(len(xra3), 3)
        # ... First Tier
        self.assertEqual(len(xra3[0]), 2)
        self.assertEqual(xra3.get_tier_index("Intonation"), 0)
        self.assertEqual(xra3[0].get_id(), "t1")
        self.assertTrue(xra3[0].is_point())
        # ... Second Tier
        self.assertEqual(len(xra3[1]), 3)
        self.assertEqual(xra3.get_tier_index("TokensAlign"), 1)
        self.assertEqual(xra3[1].get_id(), "t2")
        self.assertTrue(xra3[1].is_interval())
        # ... 3rd Tier
        self.assertEqual(len(xra3[2]), 1)
        self.assertEqual(xra3.get_tier_index("IPU"), 2)
        self.assertEqual(xra3[2].get_id(), "t3")
        self.assertTrue(xra3[2].is_interval())
        # Controlled vocabulary
        self.assertEqual(len(xra3.get_ctrl_vocab_list()), 2)
        self.assertIsNotNone(xra3.get_ctrl_vocab_from_name("v0"))
        self.assertIsNotNone(xra3.get_ctrl_vocab_from_name("intensity"))
        # Hierarchy
        #self.assertEqual(len(xra3.hierarchy), 2)

    # -----------------------------------------------------------------------

    def test_read_write(self):
        xra = sppasXRA()
        xra.read(os.path.join(DATA, "sample-1.4.xra"))
        xra.write(os.path.join(TEMP, "sample-1.4.xra"))
        xra2 = sppasXRA()
        xra2.read(os.path.join(TEMP, "sample-1.4.xra"))

        # Compare annotations of original xra and xra2
        for t1, t2 in zip(xra, xra2):
            self.assertEqual(len(t1), len(t2))
            for a1, a2 in zip(t1, t2):
                # compare labels and location
                self.assertEqual(a1, a2)
                # compare metadata
                for key in a1.get_meta_keys():
                    self.assertEqual(a1.get_meta(key), a2.get_meta(key))

        # Compare media
        # Compare hierarchy
        # Compare controlled vocabularies
        for t1, t2 in zip(xra, xra2):
            ctrl1 = t1.get_ctrl_vocab()  # a sppasCtrlVocab() instance or None
            ctrl2 = t2.get_ctrl_vocab()  # a sppasCtrlVocab() instance or None
            if ctrl1 is None and ctrl2 is None:
                continue
            self.assertEqual(len(ctrl1), len(ctrl2))
            for entry in ctrl1:
                self.assertTrue(ctrl2.contains(entry))
