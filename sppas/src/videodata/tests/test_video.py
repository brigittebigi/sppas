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

    src.videodata.tests.test_video.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""

import unittest
import os
import numpy as np

from sppas.src.config import paths

from ..video import sppasVideoReader
from ..video import sppasVideoWriter

# ---------------------------------------------------------------------------


class TestVideoReader(unittest.TestCase):

    VIDEO = os.path.join(paths.samples, "faces", "video_sample.mp4")

    # -----------------------------------------------------------------------

    def test_init(self):
        bv = sppasVideoReader()
        self.assertFalse(bv.is_opened())
        self.assertEqual(0, bv.get_framerate())
        self.assertEqual(0, bv.tell())

    # -----------------------------------------------------------------------

    def test_open(self):
        bv = sppasVideoReader()

        # invalid file
        with self.assertRaises(Exception):
            bv.open("toto.xxx")
        self.assertFalse(bv.is_opened())

        # correct video file
        self.assertTrue(os.path.exists(TestVideoReader.VIDEO))
        bv.open(TestVideoReader.VIDEO)
        self.assertTrue(bv.is_opened())
        self.assertEqual(25, bv.get_framerate())
        self.assertEqual(0, bv.tell())
        self.assertEqual(960, bv.get_width())
        self.assertEqual(540, bv.get_height())
        self.assertEqual(1181, bv.get_nframes())
        self.assertEqual(47.240, bv.get_duration())

        # can't re-open a file: video stream was not released
        with self.assertRaises(Exception):
            bv.open(TestVideoReader.VIDEO)

        # invalid file
        with self.assertRaises(Exception):
            bv.open("toto.xxx")

        # The correct video is still open
        self.assertTrue(bv.is_opened())

    # -----------------------------------------------------------------------

    def test_seek_tell(self):
        bv = sppasVideoReader()
        bv.open(TestVideoReader.VIDEO)

        bv.seek(200)
        self.assertEqual(200, bv.tell())

    # -----------------------------------------------------------------------

    def test_read(self):
        bv = sppasVideoReader()
        # No video opened. Nothing to be read...
        frame = bv.read()
        self.assertIsNone(frame)

        # Open the video
        bv.open(TestVideoReader.VIDEO)
        self.assertTrue(bv.is_opened())

        # Read one frame from the current position
        frame = bv.read()
        self.assertEqual(1, bv.tell())
        self.assertIsNotNone(frame)
        self.assertTrue(isinstance(frame, np.ndarray))

        # Read 10 frames from the current position
        frames = bv.read(from_pos=-1, to_pos=bv.tell()+10)
        self.assertEqual(11, bv.tell())
        self.assertEqual(10, len(frames))
        for frame in frames:
            self.assertTrue(isinstance(frame, np.ndarray))

        # Read the: 10 last frames of the video
        c = bv.get_nframes()
        frames = bv.read(from_pos=c-10, to_pos=-1)
        self.assertIsNotNone(frames)
        self.assertEqual(10, len(frames))
        self.assertEqual(c, bv.tell())

        # we reached the end. Try to read again...
        frame = bv.read()
        self.assertIsNone(frame)

        # Try to read after seek
        bv.seek(bv.get_nframes()-5)
        x = 0
        while bv.read() is not None:
            x += 1
        self.assertEqual(5, x)

# ---------------------------------------------------------------------------


class TestVideoWriter(unittest.TestCase):

    VIDEO = os.path.join(paths.samples, "faces", "video_test.mp4")

    # -----------------------------------------------------------------------

    def test_init(self):
        vw = sppasVideoWriter()

    # -----------------------------------------------------------------------

    def test_open(self):
        bv = sppasVideoWriter()

        # invalid file
        with self.assertRaises(Exception):
            bv.open("toto.xxx")
        self.assertFalse(bv.is_opened())

        # correct video file
        self.assertFalse(os.path.exists(TestVideoWriter.VIDEO))
        bv.open(TestVideoWriter.VIDEO)
        self.assertTrue(bv.is_opened())
        self.assertTrue(os.path.exists(TestVideoWriter.VIDEO))

        self.assertEqual(25, bv.get_framerate())
        self.assertEqual(704, bv.get_width())
        self.assertEqual(576, bv.get_height())
        self.assertEqual(0, bv.get_nframes())
        self.assertEqual(0., bv.get_duration())

        # can't re-open a file: video stream was not released
        with self.assertRaises(Exception):
            bv.open(TestVideoWriter.VIDEO)

        # invalid file
        with self.assertRaises(Exception):
            bv.open("toto.xxx")

        # The correct video is still open
        self.assertTrue(bv.is_opened())

        bv.close()
        os.remove(TestVideoWriter.VIDEO)

    # -----------------------------------------------------------------------

    def test_getters(self):
        bv = sppasVideoWriter()
        extensions = bv.get_extensions()
        self.assertTrue(".mp4" in extensions)
        self.assertTrue(".avi" in extensions)

        self.assertEqual("mpv4", bv.get_fourcc(".mp4"))
        self.assertEqual("mpv4", bv.get_fourcc("MP4"))

        self.assertEqual(".mp4", bv.get_ext("mpv4"))

    # -----------------------------------------------------------------------

    def test_resolution(self):
        bv = sppasVideoWriter()
        w, h = bv.get_size()
        self.assertEqual(704, w)
        self.assertEqual(576, h)
        self.assertEqual(25, bv.get_framerate())

        bv.set_resolution("HD")
        w, h = bv.get_size()
        self.assertEqual(1920, w)
        self.assertEqual(1080, h)

        with self.assertRaises(Exception):
            bv.set_resolution("toto")

    # -----------------------------------------------------------------------

    def test_write(self):
        pass
