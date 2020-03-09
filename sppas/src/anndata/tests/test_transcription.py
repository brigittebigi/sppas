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

    src.anndata.tests.test_transcription
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2018  Brigitte Bigi
    :summary:      Test the class sppasTranscription().

"""
import unittest
from ..anndataexc import TrsAddError
from ..anndataexc import HierarchyAssociationError

from ..ann.annlocation import sppasLocation
from ..ann.annlocation import sppasInterval
from ..ann.annlocation import sppasPoint
from ..ann.annlabel import sppasTag
from ..ann.annlabel import sppasLabel
from ..ann.annotation import sppasAnnotation
from ..tier import sppasTier
from ..transcription import sppasTranscription

from ..media import sppasMedia
from ..ctrlvocab import sppasCtrlVocab

# ---------------------------------------------------------------------------


class TestTranscription(unittest.TestCase):

    def setUp(self):
        self.trs = sppasTranscription()
        self.tier1 = self.trs.create_tier(name="tier")
        self.tier2 = self.trs.create_tier(name=" Tier")
        self.tier3 = self.trs.create_tier(name=" Tier2")

    def test_metadata(self):
        trsP = sppasTranscription()
        trsI = sppasTranscription()
        trsP.set_meta("key", "value")
        trsI.set_meta('key', "value")
        self.assertEqual(trsI.get_meta('key'), trsP.get_meta('key'))
        self.assertEqual(trsI.get_meta('toto'), '')

    def test_name(self):
        trsP = sppasTranscription()
        self.assertEqual(len(trsP.get_name()), 36)
        trsP.set_name('test')
        self.assertEqual(trsP.get_name(), 'test')
        trsP.set_name('    \r\t\ntest    \r\t\n')
        self.assertEqual(trsP.get_name(), 'test')
        trsP = sppasTier('    \r\t\ntest    \r\t\n')
        self.assertEqual(trsP.get_name(), 'test')

    def test_tier_is_empty(self):
        trs = sppasTranscription()
        self.assertTrue(trs.is_empty())
        trs.append(sppasTier())
        self.assertFalse(trs.is_empty())

    def test_find(self):
        self.assertEqual(self.trs.find(name="Tier "), self.tier2)
        self.assertEqual(self.trs.find(name="tier2 ", case_sensitive=True), None)
        self.assertEqual(self.trs.find(name="tier2 ", case_sensitive=False), self.tier3)

    def test_tier_append_pop(self):
        trs = sppasTranscription()
        tierA = sppasTier()
        self.assertEqual(len(trs), 0)
        trs.append(tierA)
        self.assertEqual(len(trs), 1)
        with self.assertRaises(TrsAddError):
            trs.append(tierA)
        tier = trs.pop(0)
        self.assertEqual(tier, tierA)
        voc = sppasCtrlVocab("Verbal Strategies")
        m = sppasMedia('filename.wav')
        tierB = sppasTier(ctrl_vocab=voc, media=m)
        trs.append(tierB)
        self.assertEqual(trs.get_ctrl_vocab_from_name("Verbal_Strategies"), voc)
        self.assertEqual(len(trs.get_media_list()), 1)

    def test_rename(self):
        trs = sppasTranscription()
        trs.append(sppasTier("tier"))
        trs.append(sppasTier("tier"))
        trs.create_tier(name="tier")
        self.assertEqual(trs[0].get_name(), u"tier")
        self.assertEqual(trs[1].get_name(), u"tier(2)")
        self.assertEqual(trs[2].get_name(), u"tier(3)")

    def test_ctrlvocab(self):
        voc1 = sppasCtrlVocab("Verbal Strategies")
        self.assertTrue(voc1.add(sppasTag("definition")))
        self.assertTrue(voc1.add(sppasTag("example")))
        self.assertTrue(voc1.add(sppasTag("comparison")))
        self.assertTrue(voc1.add(sppasTag("gap filling with sound")))
        self.assertTrue(voc1.add(sppasTag("contrast")))
        voc2 = sppasCtrlVocab("N'importe quoi")
        self.assertTrue(voc2.add(sppasTag("toto")))
        self.assertTrue(voc2.add(sppasTag("titi")))
        self.assertTrue(voc2.add(sppasTag("tutu")))
        trs = sppasTranscription()
        t1 = sppasTier("tier1")
        t2 = sppasTier("tier2")
        trs.append(t1)
        trs.append(t2)
        trs.add_ctrl_vocab(voc1)
        trs.add_ctrl_vocab(voc2)
        t1.set_ctrl_vocab(voc1)
        t2.set_ctrl_vocab(trs.get_ctrl_vocab_from_name("N'importe_quoi"))

        self.assertEqual(t1.get_ctrl_vocab(), voc1)
        self.assertEqual(t2.get_ctrl_vocab(), voc2)
        voc1.add(sppasTag('New entry'))
        self.assertTrue(t1.get_ctrl_vocab().contains(sppasTag('New entry')))
        t2.get_ctrl_vocab().add(sppasTag('Hello'))
        self.assertTrue(t2.get_ctrl_vocab().contains(sppasTag('Hello')))
        self.assertTrue(trs.get_ctrl_vocab_from_name("N'importe_quoi").contains(sppasTag('Hello')))
        self.assertEqual(trs.get_ctrl_vocab_from_name("N'importe_quoi"), voc2)

    def test_media(self):
        m1 = sppasMedia('filename.wav')
        self.trs.add_media(m1)
        self.assertEqual(len(self.trs.get_media_list()), 1)
        m2 = sppasMedia('filename.avi')
        self.trs.add_media(m2)
        self.assertEqual(len(self.trs.get_media_list()), 2)
        with self.assertRaises(ValueError):
            self.trs.add_media(m1)
        self.tier1.set_media(m1)
        self.assertEqual(self.tier1.get_media(), m1)
        self.trs.remove_media(m1)
        self.assertEqual(self.tier1.get_media(), None)

    def test_tier_split_annotation(self):
        """Test split of an annotation in a tier."""
        a = sppasAnnotation(sppasLocation(sppasInterval(sppasPoint(1), sppasPoint(3))))
        parent = sppasTier("test")
        parent.append(a)
        child = sppasTier("child")
        child.append(a.copy())

        trs = sppasTranscription()
        trs.append(parent)
        trs.append(child)

        # Hierarchy
        trs.add_hierarchy_link("TimeAssociation", parent, child)
        parent.validate()
        child.validate()

        with self.assertRaises(HierarchyAssociationError):
            parent.split(0)
        with self.assertRaises(HierarchyAssociationError):
            child.split(0)

    def test_tier_merge_annotation(self):
        """Test merge of an annotation in a tier."""
        a1 = sppasAnnotation(sppasLocation(sppasInterval(sppasPoint(1), sppasPoint(3))))
        a2 = sppasAnnotation(sppasLocation(sppasInterval(sppasPoint(4), sppasPoint(5))))
        parent = sppasTier("test")
        parent.append(a1)
        parent.append(a2)
        child = sppasTier("child")
        child.append(a1.copy())
        child.append(a2.copy())

        trs = sppasTranscription()
        trs.append(parent)
        trs.append(child)

        # Hierarchy
        trs.add_hierarchy_link("TimeAssociation", parent, child)
        parent.validate()
        child.validate()

        with self.assertRaises(HierarchyAssociationError):
            parent.merge(0, direction=1)
        with self.assertRaises(HierarchyAssociationError):
            child.merge(0, direction=1)

    def test_tier_pop(self):
        """Test pop of an annotation in a tier."""
        a = sppasAnnotation(
            sppasLocation(sppasInterval(sppasPoint(1), sppasPoint(3))))
        parent = sppasTier("parent")
        parent.append(a)
        child = sppasTier("child")
        child.append(a.copy())

        trs = sppasTranscription()
        trs.append(parent)
        trs.append(child)

        # Hierarchy
        trs.add_hierarchy_link("TimeAssociation", parent, child)
        parent.validate()
        child.validate()

        with self.assertRaises(HierarchyAssociationError):
            parent.pop(0)
        with self.assertRaises(HierarchyAssociationError):
            child.pop(0)

    def test_tier_remove(self):
        """Test pop of an annotation in a tier."""
        a = sppasAnnotation(
            sppasLocation(sppasInterval(sppasPoint(1), sppasPoint(3))))
        parent = sppasTier("parent")
        parent.append(a)
        child = sppasTier("child")
        ac = a.copy()
        child.append(ac)

        trs = sppasTranscription()
        trs.append(parent)
        trs.append(child)

        # Hierarchy
        trs.add_hierarchy_link("TimeAssociation", parent, child)
        parent.validate()
        child.validate()

        with self.assertRaises(HierarchyAssociationError):
            parent.remove(a.get_lowest_localization(), a.get_highest_localization())
        with self.assertRaises(HierarchyAssociationError):
            child.remove(1, 3)
