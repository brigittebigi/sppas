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

    src.anndata.tests.test_aio_weka
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2018  Brigitte Bigi
    :summary:      Test the class sppasWEKA().

    To write ARFF and XRFF files.

"""
import unittest
import os.path
import shutil
import io

from ..aio.weka import sppasWEKA, sppasARFF, sppasXRFF
from ..transcription import sppasTranscription
from ..ann.annlocation import sppasInterval
from ..ann.annlocation import sppasPoint
from ..ann.annlabel import sppasTag
from ..ann.annlabel import sppasLabel
from ..ann.annotation import sppasAnnotation
from ..ann.annlocation import sppasLocation

from sppas.src.files.fileutils import sppasFileUtils
from sppas.src.utils.makeunicode import u

# ---------------------------------------------------------------------------

TEMP = sppasFileUtils().set_random()
DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")

# ---------------------------------------------------------------------------


class TestWEKA(unittest.TestCase):
    """
    Represents a WEKA instance test sets.

    """
    def test_members(self):
        weka = sppasWEKA()
        self.assertTrue(weka.multi_tiers_support())
        self.assertFalse(weka.no_tiers_support())
        self.assertTrue(weka.metadata_support())
        self.assertTrue(weka.ctrl_vocab_support())
        self.assertFalse(weka.media_support())
        self.assertFalse(weka.hierarchy_support())
        self.assertTrue(weka.point_support())
        self.assertTrue(weka.interval_support())
        self.assertTrue(weka.disjoint_support())
        self.assertFalse(weka.alternative_localization_support())
        self.assertTrue(weka.alternative_tag_support())
        self.assertFalse(weka.radius_support())
        self.assertTrue(weka.gaps_support())
        self.assertTrue(weka.overlaps_support())

        self.assertEqual(weka._uncertain_annotation_tag, "?")
        self.assertEqual(weka._epsilon_proba, 0.001)

    # -----------------------------------------------------------------------

    def test_setters(self):
        weka = sppasWEKA()
        self.assertEqual(weka.get_max_class_tags(), 10)
        weka.set_max_class_tags(5)
        self.assertEqual(weka.get_max_class_tags(), 5)
        with self.assertRaises(IOError):
            weka.set_max_class_tags(1)
        with self.assertRaises(IOError):
            sppasWEKA.check_max_class_tags(110)

        self.assertEqual(weka._max_attributes_tags, 20)
        weka.set_max_attributes_tags(5)
        self.assertEqual(weka._max_attributes_tags, 5)
        with self.assertRaises(ValueError):
            weka.set_max_attributes_tags(0)
        with self.assertRaises(ValueError):
            sppasWEKA.check_max_attributes_tags(210)

        self.assertEqual(weka._empty_annotation_tag, "none")
        weka.set_empty_annotation_tag("toto")
        self.assertEqual(weka._empty_annotation_tag, "toto")
        with self.assertRaises(ValueError):
            weka.set_empty_annotation_tag(" \n")

        self.assertEqual(weka._uncertain_annotation_tag, "?")
        weka.set_uncertain_annotation_tag("~")
        self.assertEqual(weka._uncertain_annotation_tag, "~")
        with self.assertRaises(ValueError):
            weka.set_uncertain_annotation_tag(" \n")

    # -----------------------------------------------------------------------

    def test_check_metadata(self):
        """Check the metadata and fix the variable members."""

        weka = sppasWEKA()
        t = sppasTranscription()
        weka.set(t)

        self.assertEqual(weka.get_max_class_tags(), 10)
        self.assertEqual(weka._max_attributes_tags, 20)
        self.assertEqual(weka._empty_annotation_tag, "none")
        self.assertEqual(weka._uncertain_annotation_tag, "?")

        weka.set_meta("weka_max_class_tags", "50")
        weka.set_meta("weka_max_attributes_tags", "30")
        weka.set_meta("weka_empty_annotation_tag", "~")
        weka.set_meta("weka_uncertain_annotation_tag", "%")
        weka.check_metadata()

        self.assertEqual(weka.get_max_class_tags(), 50)
        self.assertEqual(weka._max_attributes_tags, 30)
        self.assertEqual(weka._empty_annotation_tag, "~")
        self.assertEqual(weka._uncertain_annotation_tag, "%")

        weka.set_meta("weka_max_class_tags", "0")
        with self.assertRaises(IOError):
            weka.check_metadata()
        weka.set_meta("weka_max_attributes_tags", "0")
        with self.assertRaises(IOError):
            weka.check_metadata()
        weka.set_meta("weka_empty_annotation_tag", "")
        with self.assertRaises(IOError):
            weka.check_metadata()
        weka.set_meta("weka_uncertain_annotation_tag", "")
        with self.assertRaises(IOError):
            weka.check_metadata()

    # -----------------------------------------------------------------------

    def test_validate_annotations(self):
        """Prepare data to be compatible."""

        weka = sppasWEKA()
        t = sppasTranscription()
        weka.set(t)
        tier1 = t.create_tier("The name")

        # TODO: unittest of validate_annotations() method.

    # -----------------------------------------------------------------------

    def test_validate(self):
        """Check the tiers to verify if everything is ok."""

        weka = sppasWEKA()
        t = sppasTranscription()
        weka.set(t)
        with self.assertRaises(IOError):   # Empty transcription
            weka.validate()
        tier1 = t.create_tier(name="tier1")
        with self.assertRaises(IOError):   # Not enough tiers
            weka.validate()
        tier2 = t.create_tier(name="tier2")
        with self.assertRaises(IOError):   # No class
            weka.validate()
        tier1.set_meta("weka_class", "")
        with self.assertRaises(IOError):   # No attribute
            weka.validate()
        tier2.set_meta("weka_attribute", "")
        with self.assertRaises(IOError):   # Empty class tier
            weka.validate()
        tier1.set_ctrl_vocab(None)
        tier1.append(sppasAnnotation(sppasLocation(sppasInterval(sppasPoint(1), sppasPoint(4))),
                                     sppasLabel(sppasTag('a'))))
        tier1.create_ctrl_vocab()
        with self.assertRaises(IOError):   # Not enough annotations in class tier
            weka.validate()
        tier1.set_ctrl_vocab(None)
        tier1.append(sppasAnnotation(sppasLocation(sppasInterval(sppasPoint(4), sppasPoint(6))),
                                     sppasLabel(sppasTag('b'))))
        tier1.create_ctrl_vocab()
        with self.assertRaises(IOError):   # Empty attribute tier
            weka.validate()
        tier2.append(sppasAnnotation(sppasLocation(sppasInterval(sppasPoint(1), sppasPoint(3)))))

        with self.assertRaises(IOError):  # No instance time step nor anchor
            weka.validate()

        weka.set_meta("weka_instance_step", "0.04")

        # yes! it sounds good!
        weka.validate()

    # -----------------------------------------------------------------------

    def test_tier_is_attribute(self):
        """Check if a tier is an attribute for the classification."""

        t = sppasTranscription()
        tier1 = t.create_tier(name="tier1")
        is_att, is_num = sppasWEKA._tier_is_attribute(tier1)
        self.assertFalse(is_att)
        self.assertFalse(is_num)
        tier1.set_meta("weka_attribute", "")
        is_att, is_num = sppasWEKA._tier_is_attribute(tier1)
        self.assertTrue(is_att)
        self.assertFalse(is_num)
        tier1.set_meta("weka_attribute", "numeric")
        is_att, is_num = sppasWEKA._tier_is_attribute(tier1)
        self.assertTrue(is_att)
        self.assertTrue(is_num)

    # -----------------------------------------------------------------------

    def test_get_class_tier(self):
        """Return the tier which is the class."""

        weka = sppasWEKA()
        t = sppasTranscription()
        weka.set(t)
        tier1 = t.create_tier(name="tier1")
        self.assertIsNone(weka._get_class_tier())
        tier1.set_meta("weka_class", "")
        self.assertEqual(weka._get_class_tier(), tier1)

    # -----------------------------------------------------------------------

    def test_get_anchor_tier(self):
        """Return the tier which will be used to create the instances."""

        weka = sppasWEKA()
        t = sppasTranscription()
        weka.set(t)
        tier1 = t.create_tier(name="tier1")
        self.assertIsNone(weka._get_anchor_tier())
        tier1.set_meta("weka_instance_anchor", "")
        self.assertEqual(weka._get_anchor_tier(), tier1)

    # -----------------------------------------------------------------------

    def test_get_labels(self):
        """Return the sppasLabel() at the given time in the given tier.
            Return the empty label if no label was assigned at the given time.

        """
        empty = sppasLabel(sppasTag("none"))
        weka = sppasWEKA()
        t = sppasTranscription()
        weka.set(t)

        # Interval tier
        tier = t.create_tier(name="tierIntervals")
        tier.create_annotation(sppasLocation(sppasInterval(sppasPoint(1.), sppasPoint(3.))))
        tier.create_annotation(sppasLocation(sppasInterval(sppasPoint(2.5), sppasPoint(4.))),
                               sppasLabel(sppasTag('toto')))
        self.assertEqual(weka._get_labels(sppasPoint(0.), tier), [empty])
        self.assertEqual(weka._get_labels(sppasPoint(1.), tier), [empty])
        self.assertEqual(weka._get_labels(sppasPoint(2.), tier), [empty])
        self.assertEqual(weka._get_labels(sppasPoint(3.), tier), [sppasLabel(sppasTag('toto'))])
        self.assertEqual(weka._get_labels(sppasPoint(4.), tier), [empty])
        self.assertEqual(weka._get_labels(sppasPoint(5.), tier), [empty])
        tier[0].add_tag(sppasTag('titi'))
        self.assertTrue(tier[0].contains_tag(sppasTag('titi')))
        self.assertEqual(weka._get_labels(sppasPoint(2.), tier), [sppasLabel(sppasTag('titi'))])
        self.assertEqual(weka._get_labels(sppasPoint(2.5), tier), [sppasLabel(sppasTag('titi'))])
        self.assertEqual(weka._get_labels(sppasPoint(2.6), tier), [sppasLabel(sppasTag('titi'))])
        self.assertEqual(weka._get_labels(sppasPoint(3.), tier), [sppasLabel(sppasTag('toto'))])

        # Point tier
        tierp = t.create_tier(name="tierPoints")
        tierp.create_annotation(sppasLocation(sppasPoint(1.)))
        tierp.create_annotation(sppasLocation(sppasPoint(5.)), sppasLabel(sppasTag('H*')))
        tierp.create_annotation(sppasLocation(sppasPoint(12.)), sppasLabel(sppasTag('')))
        self.assertEqual(weka._get_labels(sppasPoint(5.), tierp), [sppasLabel(sppasTag('H*'))])
        self.assertEqual(weka._get_labels(sppasPoint(0.), tierp), [empty])
        self.assertEqual(weka._get_labels(sppasPoint(1.), tierp), [empty])
        self.assertEqual(weka._get_labels(sppasPoint(12.), tierp), [empty])

    # -----------------------------------------------------------------------

    def test_fix_all_possible_instance_steps(self):
        """Fix all the possible time-points of the instances."""

        t = sppasTranscription()
        tier = t.create_tier(name="tier")
        tier.append(sppasAnnotation(sppasLocation(sppasInterval(sppasPoint(1.), sppasPoint(2.)))))
        tier.append(sppasAnnotation(sppasLocation(sppasInterval(sppasPoint(4.), sppasPoint(5.))),
                                    sppasLabel(sppasTag("toto"))))
        tier.append(sppasAnnotation(sppasLocation(sppasInterval(sppasPoint(5.), sppasPoint(6.))),
                                    sppasLabel(sppasTag("none"))))

        all_points = sppasWEKA._fix_all_possible_instance_steps(0., 10., time_step=0.01)  # phoneme frames
        self.assertEqual(len(all_points), 1000)
        all_points = sppasWEKA._fix_all_possible_instance_steps(0., 10., time_step=0.04)  # video frames
        self.assertEqual(len(all_points), 250)

        all_points = sppasWEKA._fix_all_possible_instance_steps(0., 10., anchor_tier=tier)
        self.assertEqual(len(all_points), 2)
        self.assertTrue(sppasPoint(4.5, 0.5) in all_points)
        self.assertTrue(sppasPoint(5.5, 0.5) in all_points)

    # -----------------------------------------------------------------------

    def test_fix_instance_steps(self):
        """Fix the time-points to create the instances and the
            tag of the class to predict by the classification system.
        """

        weka = sppasWEKA()
        t = sppasTranscription()
        weka.set(t)
        tier = t.create_tier(name="tier")
        tier.set_meta('weka_class', '')
        tier.create_annotation(sppasLocation(sppasInterval(sppasPoint(1.), sppasPoint(2.))))
        tier.create_annotation(sppasLocation(sppasInterval(sppasPoint(4.), sppasPoint(5.))),
                               sppasLabel(sppasTag("toto")))
        tier.create_annotation(sppasLocation(sppasInterval(sppasPoint(5.), sppasPoint(6.))),
                               sppasLabel(sppasTag("none")))

        weka.set_meta('weka_instance_step', '0.1')
        all_points = sppasWEKA._fix_all_possible_instance_steps(1., 6., time_step=0.1)
        self.assertEqual(len(all_points), 50)
        instances = weka._fix_instance_steps()
        self.assertEqual(len(instances), 10)  # only "toto", with 10 steps

        weka.pop_meta('weka_instance_step')
        instances = weka._fix_instance_steps()
        self.assertEqual(len(instances), 0)

        tier.set_meta('weka_instance_anchor', '')
        instances = weka._fix_instance_steps()
        self.assertEqual(len(instances), 1)  # only "toto
        self.assertEqual(instances[0], (sppasPoint(4.5, 0.5), "toto"))

    # -----------------------------------------------------------------------

    def test_scores_to_probas(self):
        """Convert scores of a set of tags to probas."""

        self.assertFalse(sppasWEKA._scores_to_probas([]))

        tags = dict()

        # only one tag, without score (the most common situation)
        tag = sppasTag("")
        tags[tag] = None
        sppasWEKA._scores_to_probas(tags)
        self.assertEqual(tags[tag], 1.)

        # only one tag, with a score (numerical or string)
        tags[tag] = 3
        sppasWEKA._scores_to_probas(tags)
        self.assertEqual(tags[tag], 1.)

        # several tags, all with scores
        tag1 = sppasTag("a")
        tag2 = sppasTag("b")
        tag3 = sppasTag("c")
        tags = dict()
        tags[tag1] = 3
        tags[tag2] = 2
        tags[tag3] = 5
        sppasWEKA._scores_to_probas(tags)
        self.assertEqual(tags[tag1], 0.3)
        self.assertEqual(tags[tag2], 0.2)
        self.assertEqual(tags[tag3], 0.5)

        # several tags, all without scores
        tags = dict()
        tags[tag1] = None
        tags[tag2] = None
        sppasWEKA._scores_to_probas(tags)
        self.assertEqual(tags[tag1], 0.5)
        self.assertEqual(tags[tag2], 0.5)

        # several tags, some without scores
        tags = dict()
        tags[tag1] = 7
        tags[tag2] = 2
        tags[tag3] = None   # score will be 1 (half of the min)
        sppasWEKA._scores_to_probas(tags)
        self.assertEqual(tags[tag1], 0.7)
        self.assertEqual(tags[tag2], 0.2)
        self.assertEqual(tags[tag3], 0.1)

    # -----------------------------------------------------------------------

    def test_fix_data_instance(self):
        """Fix the data content of an instance."""

        weka = sppasWEKA()
        t = sppasTranscription()
        tier1 = t.create_tier(name="tier1")
        tier2 = t.create_tier(name="tier2")
        tier3 = t.create_tier(name="tier3")
        weka.set(t)
        weka.set_meta("weka_instance_step", "0.1")
        tier1.set_meta("weka_class", "")
        tier2.set_meta("weka_attribute", "string")
        tier3.set_meta("weka_attribute", "numeric")

        tier1.append(sppasAnnotation(sppasLocation(sppasInterval(sppasPoint(1.), sppasPoint(2.)))))
        tier1.append(sppasAnnotation(sppasLocation(sppasInterval(sppasPoint(4.), sppasPoint(5.))),
                                     sppasLabel(sppasTag("toto"))))
        tier1.append(sppasAnnotation(sppasLocation(sppasInterval(sppasPoint(5.), sppasPoint(6.))),
                                     sppasLabel(sppasTag("none"))))
        tier1.append(sppasAnnotation(sppasLocation(sppasInterval(sppasPoint(7.), sppasPoint(10.))),
                                     sppasLabel(sppasTag("titi"))))

        tier2.append(sppasAnnotation(sppasLocation(sppasInterval(sppasPoint(1), sppasPoint(3)))))
        tier2.append(sppasAnnotation(sppasLocation(sppasInterval(sppasPoint(3), sppasPoint(5))),
                                     sppasLabel(sppasTag('a'))))
        tier2.append(sppasAnnotation(sppasLocation(sppasInterval(sppasPoint(8), sppasPoint(10))),
                                     sppasLabel(sppasTag('b'))))

        tier3.append(sppasAnnotation(sppasLocation(sppasInterval(sppasPoint(1), sppasPoint(3))),
                                     sppasLabel(sppasTag('b'))))
        tier3.append(sppasAnnotation(sppasLocation(sppasInterval(sppasPoint(3), sppasPoint(5))),
                                     sppasLabel(sppasTag('a'))))
        tier3.append(sppasAnnotation(sppasLocation(sppasInterval(sppasPoint(8), sppasPoint(10))),
                                     sppasLabel(sppasTag('b'))))
        tier1.create_ctrl_vocab()
        tier2.create_ctrl_vocab()
        tier3.create_ctrl_vocab()

        instance_steps = weka._fix_instance_steps()
        for point, class_str in instance_steps:
            data = weka._fix_data_instance(point)
            if 4. < point < 5.:
                self.assertEqual(class_str, "toto")
                self.assertEqual(data[0], u("a"))
            elif 7. < point < 8.:
                self.assertEqual(class_str, "titi")
                self.assertEqual(data[0], u("none"))
            elif 8. < point < 10.:
                self.assertEqual(class_str, "titi")
                self.assertEqual(data[0], u("b"))

# ---------------------------------------------------------------------------


class TestFileFormats(unittest.TestCase):
    """
    Represents an ARFF or XRFF file, the native formats of WEKA.

    TODO: test XRFF output.

    """
    def setUp(self):
        if os.path.exists(TEMP) is False:
            os.mkdir(TEMP)
        self.trs = sppasTranscription()
        self.tier1 = self.trs.create_tier(name="tier1")
        self.tier1.append(sppasAnnotation(sppasLocation(sppasInterval(sppasPoint(1), sppasPoint(3)))))
        self.tier2 = self.trs.create_tier(name="tier2")
        self.tier2.append(sppasAnnotation(sppasLocation(sppasInterval(sppasPoint(1), sppasPoint(3)))))

    def tearDown(self):
        shutil.rmtree(TEMP)

    # -----------------------------------------------------------------------

    def test_write_header(self):
        """Write the creator, etc. in the header of an ARFF file."""

        lines = sppasARFF._serialize_header()
        self.assertEqual(len(lines.split("\n")), 7)
        self.assertTrue("creator" in lines)
        self.assertTrue("version" in lines)
        self.assertTrue("date" in lines)
        self.assertTrue("author" in lines)
        self.assertTrue("license" in lines)

    # -----------------------------------------------------------------------

    def test_write_meta(self):
        """Write the metadata of the Transcription object
        in the header of an ARFF file.

        """
        arff = sppasARFF()
        arff.set(self.trs)
        lines = arff._serialize_metadata()
        nb_lines = len(lines.split("\n"))

        arff.set_meta("weka_instance_step", "0.04")
        lines = arff._serialize_metadata()
        self.assertEqual(len(lines.split("\n")), nb_lines+1)  # 1 more meta data
        self.assertTrue("weka_instance_step" in lines)
        self.assertTrue("0.04" in lines)

    # -----------------------------------------------------------------------

    def test_write_relation(self):
        """Write the name of the relation."""

        # test ARFF
        arff = sppasARFF()
        arff.set(self.trs)
        lines = arff._serialize_relation()
        self.assertEqual(len(lines.split("\n")), 3)  # 1 blank line + 1 relation data
        self.assertTrue("@RELATION" in lines)
        self.assertTrue(self.trs.get_name() in lines)

    # -----------------------------------------------------------------------

    def test_write_attributes(self):
        """Write the list of attributes."""

        # test ARFF
        arff = sppasARFF()
        arff.set(self.trs)
        self.tier1.set_meta("weka_class", "")
        self.tier2.set_meta("weka_attribute", "string")
        self.tier1.create_ctrl_vocab()
        self.tier2.create_ctrl_vocab()
        lines = arff._serialize_attributes()
        self.assertTrue("@ATTRIBUTES" in lines)
        # self.assertTrue(self.tier1.get_name() in lines)
        # self.assertTrue(self.tier2.get_name() in lines)

        # test XRFF
        xrff = sppasXRFF()
        xrff.set(self.trs)
        #relation = xrff._serialize_relation()

    # -----------------------------------------------------------------------

    def test_write_data(self):
        """Write the list of attributes."""

        t = sppasTranscription()
        tier1 = t.create_tier(name="tier1")
        tier2 = t.create_tier(name="tier2")
        tier1.append(sppasAnnotation(sppasLocation(sppasInterval(sppasPoint(1.), sppasPoint(2.)))))
        tier1.append(sppasAnnotation(sppasLocation(sppasInterval(sppasPoint(4.), sppasPoint(5.))),
                                     sppasLabel(sppasTag("toto"))))
        tier1.append(sppasAnnotation(sppasLocation(sppasInterval(sppasPoint(5.), sppasPoint(6.))),
                                     sppasLabel(sppasTag("none"))))
        tier1.append(sppasAnnotation(sppasLocation(sppasInterval(sppasPoint(7.), sppasPoint(10.))),
                                     sppasLabel(sppasTag("titi"))))
        tier2.append(sppasAnnotation(sppasLocation(sppasInterval(sppasPoint(1), sppasPoint(3)))))
        tier2.append(sppasAnnotation(sppasLocation(sppasInterval(sppasPoint(3), sppasPoint(5)))))
        tier2.append(sppasAnnotation(sppasLocation(sppasInterval(sppasPoint(8), sppasPoint(10)))))
        tier1.create_ctrl_vocab()
        tier2.create_ctrl_vocab()

        weka = sppasWEKA()
        weka.set(t)
        weka.set_meta("weka_instance_step", "0.1")
        tier1.set_meta("weka_class", "")
        tier2.set_meta("weka_attribute", "numeric")

        # test ARFF
        arff = sppasARFF()
        arff.set(weka)
        output = io.BytesIO()
        arff._write_data(output)
        # TODO: test output.getvalue() content

        # test XRFF (with the same data exactly!)
        xrff = sppasXRFF()
        xrff.set(weka)
        output = io.BytesIO()
        xrff._write_instances(output)
        # TODO: test output.getvalue() content
