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

    src.anndata.tests.test_label
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      contact@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2018  Brigitte Bigi
    :summary:      Test the classes of the annlabel package.

    Includes tests of sppasLabel(), sppasTag(), sppasTagCompare().

"""

import unittest

from sppas.src.config import symbols
from sppas.src.utils.makeunicode import u, b, text_type
from ..ann.annlabel import sppasTag
from ..ann.annlabel import sppasLabel
from ..ann.annlabel import sppasTagCompare

# ---------------------------------------------------------------------------

SIL_PHON = list(symbols.phone.keys())[list(symbols.phone.values()).index("silence")]
NOISE_PHON = list(symbols.phone.keys())[list(symbols.phone.values()).index("noise")]
SIL_ORTHO = list(symbols.ortho.keys())[list(symbols.ortho.values()).index("silence")]
PAUSE_ORTHO = list(symbols.ortho.keys())[list(symbols.ortho.values()).index("pause")]
NOISE_ORTHO = list(symbols.ortho.keys())[list(symbols.ortho.values()).index("noise")]

# ---------------------------------------------------------------------------


class TestTag(unittest.TestCase):
    """Represents a typed content of a label.

    A sppasTag() content can be one of the following types:

        1. string/unicode - (str)
        2. integer - (int)
        3. float - (float)
        4. boolean - (bool)
        5. a list of sppasTag(), all of the same type - (list)

    """

    def test_unicode(self):
        text = sppasTag("\têtre   \r   être être  \n  ")
        self.assertIsInstance(str(text), str)

    # -----------------------------------------------------------------------

    def test_string_content(self):
        """Test the tag if the content is a unicode/string."""

        text = sppasTag(" test ")
        self.assertEqual(text.get_content(), u("test"))

        text = sppasTag(2)
        self.assertEqual(text.get_typed_content(), "2")
        self.assertEqual(text.get_type(), "str")

        text = sppasTag(2.1)
        self.assertEqual(text.get_typed_content(), "2.1")
        self.assertEqual(text.get_type(), "str")

    # -----------------------------------------------------------------------

    def test_int_content(self):
        """Test the tag if the content is an integer."""

        # int value
        text = sppasTag(2, tag_type="int")
        self.assertEqual(text.get_typed_content(), 2)  # typed content is "int"
        self.assertEqual(text.get_content(), u("2"))   # but content is always a string
        self.assertEqual(text.get_type(), "int")

        with self.assertRaises(TypeError):
            sppasTag("uh uhm", tag_type="int")

        text_str = sppasTag("2")
        self.assertEqual(text.get_content(), text_str.get_content())
        self.assertNotEqual(text.get_typed_content(), text_str.get_typed_content())

        # with no type specified, the default is "str"
        text = sppasTag(2)
        self.assertEqual(text.get_content(), u("2"))
        self.assertEqual(text.get_typed_content(), u("2"))
        self.assertEqual(text.get_type(), "str")

    # -----------------------------------------------------------------------

    def test_float_content(self):
        """Test the tag if the content is a floating point."""

        text = sppasTag(2.10, tag_type="float")
        textstr = sppasTag("2.1")
        self.assertEqual(text.get_typed_content(), 2.1)
        self.assertEqual(text.get_content(), u("2.1"))
        self.assertNotEqual(text.get_typed_content(), textstr.get_typed_content())
        self.assertEqual(text.get_content(), textstr.get_content())

        with self.assertRaises(TypeError):
            sppasTag("uh uhm", tag_type="float")

    # -----------------------------------------------------------------------

    def test_bool_content(self):
        """Test the tag if the content is a boolean."""

        text = sppasTag("1", tag_type="bool")
        textstr = sppasTag("True")
        self.assertEqual(text.get_typed_content(), True)
        self.assertEqual(text.get_content(), u("True"))
        self.assertNotEqual(text.get_typed_content(), textstr.get_typed_content())
        self.assertEqual(text.get_content(), textstr.get_content())

    # -----------------------------------------------------------------------

    def test_set(self):
        text = sppasTag("test")
        text.set_content("toto")

    # -----------------------------------------------------------------------

    def test__eq__(self):
        text1 = sppasTag(" test    ")
        text2 = sppasTag("test\n")
        self.assertEqual(text1, text2)
        self.assertTrue(text1 == text2)

        text1 = sppasTag("")
        text2 = sppasTag("\n")
        self.assertEqual(text1, text2)
        self.assertTrue(text1 == text2)

# ---------------------------------------------------------------------------


class TestEvents(unittest.TestCase):
    """Events are labels with a specific text.

    This is a SPPAS convention!
    Test recognized events: silences, pauses, noises, etc.

    """
    def test_is_silence(self):
        label = sppasLabel(sppasTag(SIL_PHON))
        text = label.get_best()
        self.assertTrue(text.is_silence())
        self.assertFalse(text.is_silence() is False)
        label = sppasLabel(sppasTag(SIL_ORTHO))
        text = label.get_best()
        self.assertTrue(text.is_silence())

    def test_IsPause(self):
        label = sppasLabel(sppasTag(PAUSE_ORTHO))
        self.assertTrue(label.get_best().is_pause())

    def test_IsNoise(self):
        label = sppasLabel(sppasTag(NOISE_ORTHO))
        self.assertTrue(label.get_best().is_noise())
        label = sppasLabel(sppasTag(NOISE_PHON))
        self.assertTrue(label.get_best().is_noise())

    def test_IsSpeech(self):
        label = sppasLabel(sppasTag("l"))
        self.assertTrue(label.get_best().is_speech())
        label = sppasLabel(sppasTag(NOISE_PHON))
        self.assertFalse(label.get_best().is_speech())

# ---------------------------------------------------------------------------


class TestTagCompare(unittest.TestCase):
    """Test methods to compare tags."""

    def setUp(self):
        self.tc = sppasTagCompare()

    # -----------------------------------------------------------------------

    def test_members(self):
        """Test methods getter."""

        self.assertEqual(self.tc.methods['exact'], self.tc.exact)
        self.assertEqual(self.tc.get('exact'), self.tc.exact)

        self.assertEqual(self.tc.methods['iexact'], self.tc.iexact)
        self.assertEqual(self.tc.get('iexact'), self.tc.iexact)

        self.assertEqual(self.tc.methods['startswith'], self.tc.startswith)
        self.assertEqual(self.tc.get('startswith'), self.tc.startswith)

        self.assertEqual(self.tc.methods['istartswith'], self.tc.istartswith)
        self.assertEqual(self.tc.get('istartswith'), self.tc.istartswith)

        self.assertEqual(self.tc.methods['endswith'], self.tc.endswith)
        self.assertEqual(self.tc.get('endswith'), self.tc.endswith)

        self.assertEqual(self.tc.methods['iendswith'], self.tc.iendswith)
        self.assertEqual(self.tc.get('iendswith'), self.tc.iendswith)

        self.assertEqual(self.tc.methods['contains'], self.tc.contains)
        self.assertEqual(self.tc.get('contains'), self.tc.contains)

        self.assertEqual(self.tc.methods['icontains'], self.tc.icontains)
        self.assertEqual(self.tc.get('icontains'), self.tc.icontains)

        self.assertEqual(self.tc.methods['regexp'], self.tc.regexp)
        self.assertEqual(self.tc.get('regexp'), self.tc.regexp)

    # -----------------------------------------------------------------------

    def test_exact(self):
        """tag == text (case sensitive)."""

        self.assertTrue(self.tc.exact(sppasTag("abc"), u("abc")))
        self.assertFalse(self.tc.exact(sppasTag("abc"), u("ABC")))

        with self.assertRaises(TypeError):
            self.tc.exact("abc", u("ABC"))
        with self.assertRaises(TypeError):
            self.tc.exact(sppasTag("abc"), b("ABC"))

    # -----------------------------------------------------------------------

    def test_iexact(self):
        """tag == text (case in-sensitive)."""

        self.assertTrue(self.tc.iexact(sppasTag("abc"), u("ABC")))
        self.assertFalse(self.tc.iexact(sppasTag("abc"), u("AAA")))

        with self.assertRaises(TypeError):
            self.tc.iexact("abc", u("ABC"))
        with self.assertRaises(TypeError):
            self.tc.iexact(sppasTag("abc"), b("ABC"))

    # -----------------------------------------------------------------------

    def test_startswith(self):
        """tag startswith text (case sensitive)."""

        self.assertTrue(self.tc.startswith(sppasTag("abc"), u("a")))
        self.assertFalse(self.tc.startswith(sppasTag("abc"), u("b")))

        with self.assertRaises(TypeError):
            self.tc.startswith("abc", u("a"))
        with self.assertRaises(TypeError):
            self.tc.startswith(sppasTag("abc"), b("b"))

    # -----------------------------------------------------------------------

    def test_istartswith(self):
        """tag startswith text (case in-sensitive)."""

        self.assertTrue(self.tc.istartswith(sppasTag("abc"), u("A")))
        self.assertFalse(self.tc.istartswith(sppasTag("abc"), u("b")))

        with self.assertRaises(TypeError):
            self.tc.istartswith("abc", u("A"))
        with self.assertRaises(TypeError):
            self.tc.istartswith(sppasTag("abc"), b("b"))

    # -----------------------------------------------------------------------

    def test_endswith(self):
        """tag endswith text (case sensitive)."""

        self.assertTrue(self.tc.endswith(sppasTag("abc"), u("c")))
        self.assertFalse(self.tc.endswith(sppasTag("abc"), u("b")))

        with self.assertRaises(TypeError):
            self.tc.endswith("abc", u("c"))
        with self.assertRaises(TypeError):
            self.tc.endswith(sppasTag("abc"), b("b"))

    # -----------------------------------------------------------------------

    def test_iendswith(self):
        """tag endswith text (case in-sensitive)."""

        self.assertTrue(self.tc.iendswith(sppasTag("abc"), u("C")))
        self.assertFalse(self.tc.iendswith(sppasTag("abc"), u("b")))

        with self.assertRaises(TypeError):
            self.tc.iendswith("abc", u("C"))
        with self.assertRaises(TypeError):
            self.tc.iendswith(sppasTag("abc"), b("b"))

    # -----------------------------------------------------------------------

    def test_contains(self):
        """tag contains text (case sensitive)."""

        self.assertTrue(self.tc.contains(sppasTag("abc"), u("b")))
        self.assertFalse(self.tc.contains(sppasTag("abc"), u("B")))

        with self.assertRaises(TypeError):
            self.tc.contains("abc", u("b"))
        with self.assertRaises(TypeError):
            self.tc.contains(sppasTag("abc"), b("B"))

    # -----------------------------------------------------------------------

    def test_icontains(self):
        """tag contains text (case in-sensitive)."""

        self.assertTrue(self.tc.icontains(sppasTag("abc"), u("B")))
        self.assertFalse(self.tc.icontains(sppasTag("abc"), u("d")))

        with self.assertRaises(TypeError):
            self.tc.icontains("abc", u("B"))
        with self.assertRaises(TypeError):
            self.tc.icontains(sppasTag("abc"), b("d"))

    # -----------------------------------------------------------------------

    def test_regexp(self):
        """tag matches the regexp."""

        self.assertTrue(self.tc.regexp(sppasTag("abc"), "^a[a-z]"))
        self.assertFalse(self.tc.regexp(sppasTag("abc"), "d"))

        with self.assertRaises(TypeError):
            self.tc.regexp("abc", b("B"))

    # -----------------------------------------------------------------------

    def test_combine_methods(self):
        self.assertTrue(
            self.tc.startswith(sppasTag("abc"),
                               u("a")) and self.tc.endswith(sppasTag("abc"),
                                                            u("c")))
        self.assertTrue(
            self.tc.get("startswith")(sppasTag("abc"),
                                      u("a")) and self.tc.get("endswith")(sppasTag("abc"),
                                                                          u("c")))

# ---------------------------------------------------------------------------


class TestLabel(unittest.TestCase):
    """Test sppasLabel()."""

    def test_init(self):
        label = sppasLabel(None)
        self.assertIsNone(label.get_best())

        t = sppasTag("score0.5")
        label = sppasLabel(t)
        self.assertEqual(1, len(label))
        self.assertEqual([t, None], label[0])

        label = sppasLabel(t, 0.5)
        self.assertEqual(1, len(label))
        self.assertEqual([t, 0.5], label[0])

        # inconsistency between given tags and scores
        label = sppasLabel(t, [0.5, 0.5])
        self.assertIsNone(label.get_score(t))

        label = sppasLabel([t, t], 0.5)
        self.assertEqual(1, len(label))
        self.assertIsNone(label.get_score(t))

    # -----------------------------------------------------------------------

    def test_unicode(self):
        sppasLabel(sppasTag("être"))

    # -----------------------------------------------------------------------

    def test_label_type(self):
        label = sppasLabel(sppasTag(2, "int"))
        self.assertIsInstance(str(label.get_best()), str)
        self.assertIsInstance(label.get_best().get_content(), text_type)
        self.assertIsInstance(label.get_best().get_typed_content(), int)

    # -----------------------------------------------------------------------

    def test_is_label(self):
        label = sppasLabel(sppasTag(SIL_ORTHO))
        text = label.get_best()
        self.assertFalse(text.is_speech())

    # -----------------------------------------------------------------------

    def test_append(self):
        # do not add an already existing tag (test without scores)
        t = sppasTag("score0.5")
        label = sppasLabel(t)
        label.append(t)
        self.assertEqual(label.get_best().get_content(), u("score0.5"))
        self.assertIsNone(label.get_score(t))

        # do not add an already existing tag (test with scores)
        t = sppasTag("score0.5")
        label = sppasLabel(t, score=0.5)
        label.append(t)
        self.assertEqual(label.get_best().get_content(), u("score0.5"))
        self.assertEqual(label.get_score(t), 0.5)
        label.append(t, score=0.5)
        self.assertEqual(label.get_score(t), 1.)

    # -----------------------------------------------------------------------

    def test_add_tag(self):
        label = sppasLabel(sppasTag("score0.5"), score=0.5)
        self.assertEqual(label.get_best().get_content(), u("score0.5"))

        label.append(sppasTag("score0.8"), score=0.8)
        self.assertEqual(label.get_best().get_content(), u("score0.8"))

        label.append(sppasTag("score1.0"), score=1.0)
        self.assertEqual(label.get_best().get_content(), u("score1.0"))

        # expect error (types inconsistency):
        text1 = sppasTag(2.1)
        self.assertEqual(text1.get_type(), "str")
        text2 = sppasTag(2.10, tag_type="float")
        self.assertEqual(text2.get_type(), "float")
        label.append(text1, score=0.8)
        with self.assertRaises(TypeError):
            label.append(text2, score=0.2)

    # -----------------------------------------------------------------------

    def test_is_empty(self):
        label = sppasLabel(sppasTag(""), score=0.5)
        self.assertTrue(label.get_best().is_empty())

        label.append(sppasTag("text"), score=0.8)
        self.assertFalse(label.get_best().is_empty())

    # -----------------------------------------------------------------------

    def test_equal(self):
        label = sppasLabel(sppasTag(""), score=0.5)
        self.assertTrue(label == label)
        self.assertEqual(label, label)
        self.assertTrue(label == sppasLabel(sppasTag(""), score=0.5))
        self.assertFalse(label == sppasLabel(sppasTag(""), score=0.7))
        self.assertFalse(label == sppasLabel(sppasTag("a"), score=0.5))

    # -----------------------------------------------------------------------

    def test_set_score(self):
        tag = sppasTag("toto")
        label = sppasLabel(tag, score=0.5)
        self.assertEqual(label.get_score(tag), 0.5)
        label.set_score(tag, 0.8)
        self.assertEqual(label.get_score(tag), 0.8)

    # -----------------------------------------------------------------------

    def test_match(self):
        """Test if a tag matches some functions."""

        t = sppasTagCompare()
        l = sppasLabel(sppasTag("para"))

        self.assertFalse(l.match([(t.exact, u("par"), False)]))
        self.assertTrue(l.match([(t.exact, u("par"), True)]))

        f1 = (t.startswith, u("p"), False)
        f2 = (t.iendswith, u("O"), False)
        self.assertTrue(l.match([f1, f2], logic_bool="or"))
        self.assertFalse(l.match([f1, f2], logic_bool="and"))

        l.append(sppasTag("pata"))
        self.assertTrue(l.match([(t.endswith, u("ta"), False)]))
