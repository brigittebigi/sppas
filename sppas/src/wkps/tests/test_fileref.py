
import unittest
import sppas
import os

from sppas.src.wkps.fileref import FileReference, sppasAttribute
from sppas.src.wkps.filebase import States

# ---------------------------------------------------------------------------


class TestsAttribute(unittest.TestCase):

    def test_init(self):
        att = sppasAttribute("toto")

# ---------------------------------------------------------------------------


class TestsReference(unittest.TestCase):

    def test_init(self):
        ref = FileReference("toto")



