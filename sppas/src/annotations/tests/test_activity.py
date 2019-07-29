# -*- coding: utf8 -*-

import unittest

from sppas.src.config import symbols
from sppas.src.anndata import sppasTranscription
from sppas.src.annotations.Activity.activity import sppasActivity

# ---------------------------------------------------------------------------


class TestActivity(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_create(self):

        # create an instance with the default symbols
        a = sppasActivity()
        for s in symbols.all:
            self.assertTrue(s in a)
        self.assertTrue(symbols.unk in a)
        self.assertEqual(len(a), len(symbols.all)+1)

        # try to add again the same symbols - they won't
        for s in symbols.all:
            a.append_activity(s, symbols.all[s])
        self.assertEqual(len(a), len(symbols.all) + 1)

    def test_get_tier(self):
        a = sppasActivity()
        trs = sppasTranscription()

        # No tokensTier
        with self.assertRaises(IOError):
            a.get_tier(trs)

        # Test with an empty Tokens tier
        trs.create_tier('TokensAlign')
        tier = a.get_tier(trs)
        self.assertEqual(len(tier), 0)

        # now, test with a real TokensTier
        # ...
