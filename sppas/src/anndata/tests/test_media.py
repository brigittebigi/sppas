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

    src.anndata.tests.test_media
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2018  Brigitte Bigi
    :summary:      Test the class sppasMedia().

"""
import unittest

from ..media import sppasMedia

# ---------------------------------------------------------------------------


class TestMedia(unittest.TestCase):
    """Generic representation of a media file.
    The audio file is not loaded.

    """
    def setUp(self):
        pass

    def test_media_audio(self):
        m = sppasMedia("toto.wav")
        self.assertEqual(m.get_filename(), "toto.wav")
        self.assertIn(m.get_mime_type(), ["audio/wav", "audio/x-wav"])
        self.assertEqual(len(m.get_meta('id')), 36)

    def test_media_video(self):
        m = sppasMedia("toto.mp4")
        self.assertEqual(m.get_filename(), "toto.mp4")
        self.assertEqual(m.get_mime_type(), "video/mp4")
        self.assertEqual(len(m.get_meta('id')), 36)

    def test_media_mime_error(self):
        m = sppasMedia("toto.xxx")
        self.assertEqual(m.get_filename(), "toto.xxx")
        self.assertEqual(m.get_mime_type(), "audio/basic")
        self.assertEqual(len(m.get_meta('id')), 36)

    def test_media_metadata(self):
        m = sppasMedia("toto.wav")
        m.set_meta("channel", "1")
        self.assertEqual(m.get_meta("channel"), "1")
        self.assertEqual(m.get_meta("canal"), "")
