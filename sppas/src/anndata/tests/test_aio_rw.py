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

    src.anndata.tests.test_aio_rw
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      contact@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2018  Brigitte Bigi
    :summary:      Test for reading and writing files.

"""

import unittest
import os.path
import shutil

from sppas.src.wkps.fileutils import sppasFileUtils
from ..aio.readwrite import sppasRW

# ---------------------------------------------------------------------------

TEMP = sppasFileUtils().set_random()
DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")

# ---------------------------------------------------------------------------


def compare_tiers_trs(trs1, trs2, meta=True):
    """ Compare tiers of 2 sppasTranscription().

    :param trs1: (sppasTranscription)
    :param trs2: (sppasTranscription)
    :param meta: (bool)

    """
    for t1, t2 in zip(trs1, trs2):
        if t1.get_name() != t2.get_name():
            print('Tier names differ: {:s} != {:s}'.format(t1.get_name(), t2.get_name()))
            return False
        if len(t1) != len(t2):
            print('Tier sizes differ: {:d} != {:d}'.format(len(t1), len(t2)))
            return False
        if meta is True:
            # compare metadata
            for key in t1.get_meta_keys():
                if t1.get_meta(key) != t2.get_meta(key):
                    print('Tier metadata differ for key {:s}: '
                          '{:s} != {:s}'.format(key, t1.get_meta(key), t2.get_meta(key)))
                    return False
        for a1, a2 in zip(t1, t2):
            # compare labels and location
            if a1 != a2:
                print('Annotations differ: {:s} != {:s}'.format(a1, a2))
                return False
            if meta is True:
                # compare metadata
                for key in a1.get_meta_keys():
                    if a1.get_meta(key) != a2.get_meta(key):
                        print('Annotation metadata differ for key {:s}: '
                              '{:s} != {:s}'.format(key, a1.get_meta(key), a2.get_meta(key)))
                        return False
    return True


def compare_ctrl_vocab_trs(trs1, trs2, meta=True):
    """Compare controlled vocabularies of the tiers of 2 sppasTranscription().

    :param trs1: (sppasTranscription)
    :param trs2: (sppasTranscription)
    :param meta: (bool)

    """
    for t1, t2 in zip(trs1, trs2):
        c1 = t1.get_ctrl_vocab()  # a sppasCtrlVocab() instance or None
        c2 = t2.get_ctrl_vocab()  # a sppasCtrlVocab() instance or None

        if c1 is None and c2 is None:
            continue
        if meta is True:
            return c1 == c2
        else:
            if c1.get_name() != c2.get_name():
                return False
            if c1.get_description() != c2.get_description():
                return False

            for entry in c1:
                if c2.contains(entry) is False:
                    return False
                if c1.get_tag_description(entry) != c2.get_tag_description(entry):
                    return False

            return len(c1) == len(c2)

    return True


def compare_media_trs(trs1, trs2, meta=True):
    """Compare media of the tiers of 2 sppasTranscription().

    :param trs1: (sppasTranscription)
    :param trs2: (sppasTranscription)
    :param meta: (bool)

    """
    for t1, t2 in zip(trs1, trs2):
        m1 = t1.get_media()  # a sppasMedia() instance or None
        m2 = t2.get_media()  # a sppasMedia() instance or None

        if m1 is None and m2 is None:
            continue
        if meta is True:
            return m1 == m2
        else:
            if m1.get_filename() != m2.get_filename():
                return False
            if m1.get_mime_type() != m2.get_mime_type():
                return False
    return True

# ---------------------------------------------------------------------------


class TestAIO(unittest.TestCase):

    def setUp(self):
        if os.path.exists(TEMP) is False:
            os.mkdir(TEMP)

    def tearDown(self):
        return
        shutil.rmtree(TEMP)

    # -----------------------------------------------------------------------

    def test_IO_XRA(self):
        """Read/Write/Read then compare XRA files."""

        # Read XRA file
        parser = sppasRW(os.path.join(DATA, "sample-1.2.xra"))
        trs1 = parser.read(heuristic=True)

        # Write XRA file
        parser.set_filename(os.path.join(TEMP, "sample-1.4.xra"))
        parser.write(trs1)

        # Read the XRA file
        trs2 = parser.read(heuristic=True)

        self.assertTrue(compare_tiers_trs(trs1, trs2))
        self.assertTrue(compare_ctrl_vocab_trs(trs1, trs2))
        self.assertTrue(compare_media_trs(trs1, trs2))

    # -----------------------------------------------------------------------

    def test_IO_ANTX(self):
        """Read/Write/Read then compare ANTX files."""

        # Read ANTX file
        parser = sppasRW(os.path.join(DATA, "grenelle.antx"))
        trs1 = parser.read(heuristic=True)

        # Write ANTX file
        parser.set_filename(os.path.join(TEMP, "sample.antx"))
        parser.write(trs1)

        # Read the ANTX file
        trs2 = parser.read(heuristic=True)

        self.assertTrue(compare_tiers_trs(trs1, trs2, meta=False))  # colors slightly differ...
        self.assertTrue(compare_media_trs(trs1, trs2))

        # Read ANTX file (with TGA results)
        parser = sppasRW(os.path.join(DATA, "sample-TGA.antx"))
        trs1 = parser.read(heuristic=True)

        # Write ANTX file
        parser.set_filename(os.path.join(TEMP, "sample-TGA.antx"))
        parser.write(trs1)

        # Read the ANTX file
        trs2 = parser.read(heuristic=True)

        self.assertTrue(compare_tiers_trs(trs1, trs2, meta=False))  # colors slightly differ...
        self.assertTrue(compare_media_trs(trs1, trs2))

    # -----------------------------------------------------------------------

    def test_IO_EAF(self):
        """Read/Write/Read then compare EAF files."""

        # Read file
        parser = sppasRW(os.path.join(DATA, "sample.eaf"))
        trs1 = parser.read(heuristic=True)

        # Write file
        parser.set_filename(os.path.join(TEMP, "sample.eaf"))
        parser.write(trs1)

        # Read the file
        trs2 = parser.read(heuristic=True)

        self.assertTrue(compare_tiers_trs(trs1, trs2, meta=False))  # 'id' differ...
        self.assertTrue(compare_ctrl_vocab_trs(trs1, trs2, meta=False))
        self.assertTrue(compare_media_trs(trs1, trs2, meta=False))

    # -----------------------------------------------------------------------

    def test_IO_TextGrid(self):
        """Read/Write/Read then compare TextGrid files."""

        # Read file
        parser = sppasRW(os.path.join(DATA, "sample.TextGrid"))
        trs1 = parser.read(heuristic=True)

        # Write file
        parser.set_filename(os.path.join(TEMP, "sample.TextGrid"))
        parser.write(trs1)

        # Read the file
        trs2 = parser.read(heuristic=True)

        self.assertTrue(compare_tiers_trs(trs1, trs2, meta=False))  # 'id' differ...

        # Praat reader also accepts UTF-16

        parser.set_filename(os.path.join(TEMP, "sample.TextGrid"))
        parser.read()

        # Write file
        parser.set_filename(os.path.join(TEMP, "sample.TextGrid"))
        parser.write(trs1)

        # Read the file
        trs2 = parser.read(heuristic=True)

        self.assertTrue(compare_tiers_trs(trs1, trs2, meta=False))  # 'id' differ...

    # -----------------------------------------------------------------------

    def test_IO_PitchTier(self):
        """Read/Write/Read then compare PitchTier files."""

        # Read file
        parser = sppasRW(os.path.join(DATA, "sample.PitchTier"))
        trs1 = parser.read(heuristic=True)

        # Write file
        parser.set_filename(os.path.join(TEMP, "sample.PitchTier"))
        parser.write(trs1)

        # Read the file
        trs2 = parser.read(heuristic=True)

        self.assertTrue(compare_tiers_trs(trs1, trs2, meta=False))  # 'id' differ...

    # -----------------------------------------------------------------------

    def test_IO_MRK(self):
        """Read/Write/Read then compare MRK files."""

        # Read file
        parser = sppasRW(os.path.join(DATA, "sample.mrk"))
        trs1 = parser.read(heuristic=True)

        # Write file
        parser.set_filename(os.path.join(TEMP, "sample.mrk"))
        parser.write(trs1)

        # Read the file
        trs2 = parser.read(heuristic=True)

        self.assertTrue(compare_tiers_trs(trs1, trs2, meta=False))  # 'id' differ...

    # -----------------------------------------------------------------------

    def test_IO_HZ(self):
        """Read/Write/Read then compare HZ files."""

        # Read file
        parser = sppasRW(os.path.join(DATA, "sample.hz"))
        trs1 = parser.read(heuristic=True)

        # Write file
        parser.set_filename(os.path.join(TEMP, "sample.hz"))
        parser.write(trs1)

        # Read the file
        trs2 = parser.read(heuristic=True)

        self.assertTrue(compare_tiers_trs(trs1, trs2, meta=False))  # 'id' differ...

    # -----------------------------------------------------------------------

    def test_IO_CTM(self):
        """Read/Write/Read then compare EAF files."""

        # Read file
        parser = sppasRW(os.path.join(DATA, "sample.ctm"))
        trs1 = parser.read(heuristic=True)

        # Write file
        parser.set_filename(os.path.join(TEMP, "sample.ctm"))
        parser.write(trs1)

        # Read the file
        trs2 = parser.read(heuristic=True)

        self.assertTrue(compare_tiers_trs(trs1, trs2, meta=False))  # 'id' of annotations differ...
        self.assertTrue(compare_media_trs(trs1, trs2, meta=False))

    # -----------------------------------------------------------------------

    def test_IO_STM(self):
        """Read/Write/Read then compare EAF files."""

        # Read file
        parser = sppasRW(os.path.join(DATA, "sample.stm"))
        trs1 = parser.read(heuristic=True)

        # Write file
        parser.set_filename(os.path.join(TEMP, "sample.stm"))
        parser.write(trs1)

        # Read the file
        trs2 = parser.read(heuristic=True)

        self.assertTrue(compare_tiers_trs(trs1, trs2, meta=False))  # 'id' of annotations differ...
        self.assertTrue(compare_media_trs(trs1, trs2, meta=False))

    # -----------------------------------------------------------------------

    def test_IO_SRT(self):
        """Read/Write/Read then compare EAF files."""

        # Read file
        parser = sppasRW(os.path.join(DATA, "sample.srt"))
        trs1 = parser.read(heuristic=True)

        # Write file
        parser.set_filename(os.path.join(TEMP, "sample.srt"))
        parser.write(trs1)

        # Read the file
        trs2 = parser.read(heuristic=True)

        self.assertTrue(compare_tiers_trs(trs1, trs2, meta=False))  # 'id' differ...

    # -----------------------------------------------------------------------

    def test_IO_SUB(self):
        """Read/Write/Read then compare EAF files."""

        # Read file
        parser = sppasRW(os.path.join(DATA, "sample.sub"))
        trs1 = parser.read(heuristic=True)

        # Write file
        parser.set_filename(os.path.join(TEMP, "sample.sub"))
        parser.write(trs1)

        # Read the file
        trs2 = parser.read(heuristic=True)

        self.assertTrue(compare_tiers_trs(trs1, trs2, meta=False))  # 'id' differ...

    # -----------------------------------------------------------------------

    def test_IO_TXT(self):
        """Read/Write/Read then compare EAF files."""

        # 1. Read file (transcription only)
        parser = sppasRW(os.path.join(DATA, "sample-irish-1.txt"))
        trs1 = parser.read(heuristic=True)

        # Write file
        parser.set_filename(os.path.join(TEMP, "sample-irish-1.txt"))
        parser.write(trs1)

        # Read the file
        trs2 = parser.read(heuristic=True)

        self.assertTrue(compare_tiers_trs(trs1, trs2, meta=False))  # 'id' differ...

        # 2. Read file (column-based)
        parser = sppasRW(os.path.join(DATA, "sample.txt"))
        trs1 = parser.read(heuristic=True)

        # Write file
        parser.set_filename(os.path.join(TEMP, "sample.txt"))
        parser.write(trs1)

        # Read the file
        trs2 = parser.read(heuristic=True)

        # compare
        self.assertTrue(compare_tiers_trs(trs1, trs2, meta=False))  # 'id' differ...

    # -----------------------------------------------------------------------

    def test_IO_CSV(self):
        """Read/Write/Read then compare EAF files."""

        # Read file (transcription only)
        parser = sppasRW(os.path.join(DATA, "sample-irish.csv"))
        trs1 = parser.read(heuristic=True)

        # Write file
        parser.set_filename(os.path.join(TEMP, "sample-irish.csv"))
        parser.write(trs1)

        # Read the file
        trs2 = parser.read(heuristic=True)

        # compare
        self.assertTrue(compare_tiers_trs(trs1, trs2, meta=False))  # 'id' differ...

    # -----------------------------------------------------------------------

    def test_IO_TextGrid_CSV(self):
        """Read/Write/Read then compare EAF files."""

        # Read file (transcription only)
        parser = sppasRW(os.path.join(DATA, "sample.TextGrid"))
        trs1 = parser.read(heuristic=True)

        # Write file
        parser.set_filename(os.path.join(TEMP, "sample.csv"))
        parser.write(trs1)

        # Read the file
        trs2 = parser.read(heuristic=True)

        # compare
        self.assertTrue(compare_tiers_trs(trs1, trs2, meta=False))  # 'id' differ...
