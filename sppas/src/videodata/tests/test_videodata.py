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

    src.videodata.tests.test_videobuffer.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""

import unittest
import os
import numpy as np

from sppas.src.config import paths
from sppas.src.imgdata import sppasImage

from ..video import sppasVideo
from ..videobuffer import sppasVideoBuffer

# ---------------------------------------------------------------------------


class TestVideo(unittest.TestCase):

    VIDEO = os.path.join(paths.samples, "faces", "video_sample.mkv")

    # -----------------------------------------------------------------------

    def test_init(self):
        """Test several ways to instantiate a video without video."""
        bv = sppasVideo()
        self.assertFalse(bv.video_capture())
        self.assertEqual(0, bv.get_framerate())
        self.assertEqual(0, bv.tell())

    # -----------------------------------------------------------------------

    def test_open(self):
        bv = sppasVideo()

        # invalid file
        with self.assertRaises(Exception):
            bv.open("toto.xxx")
        self.assertFalse(bv.video_capture())

        # correct video file
        self.assertTrue(os.path.exists(TestVideo.VIDEO))
        bv.open(TestVideo.VIDEO)
        self.assertTrue(bv.video_capture())
        self.assertEqual(25, bv.get_framerate())
        self.assertEqual(0, bv.tell())
        self.assertEqual(0, bv.get_ms())
        self.assertEqual(960, bv.get_width())
        self.assertEqual(540, bv.get_height())
        self.assertEqual(1181, bv.get_nframes())

        # invalid file
        with self.assertRaises(Exception):
            bv.open("toto.xxx")
        self.assertFalse(bv.video_capture())

    # -----------------------------------------------------------------------

    def test_read(self):
        bv = sppasVideo()
        # No video opened. Nothing to be read...
        frame = bv.read()
        self.assertIsNone(frame)

        # Open the video
        bv.open(TestVideo.VIDEO)
        self.assertTrue(bv.video_capture())

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
        self.assertEqual(c, bv.tell())
        self.assertEqual(10, len(frames))

        # we reached the end. Try to read again...
        frame = bv.read()
        self.assertIsNone(frame)

# ---------------------------------------------------------------------------


class TestVideoBuffer(unittest.TestCase):

    VIDEO = os.path.join(paths.samples, "faces", "video_sample.mkv")

    # -----------------------------------------------------------------------

    def test_init_no_video(self):
        """Test several ways to instantiate a video buffer without video."""
        bv = sppasVideoBuffer()
        self.assertEqual(bv.get_size(), sppasVideoBuffer.DEFAULT_BUFFER_SIZE)
        self.assertEqual(bv.get_overlap(), sppasVideoBuffer.DEFAULT_BUFFER_OVERLAP)
        self.assertFalse(bv.video_capture())
        self.assertTrue(bv.eov)
        self.assertEqual(0, bv.get_framerate())
        self.assertEqual(0, bv.tell())

        bv = sppasVideoBuffer(size=12)
        self.assertEqual(bv.get_size(), 12)
        self.assertEqual(bv.get_overlap(), sppasVideoBuffer.DEFAULT_BUFFER_OVERLAP)
        self.assertFalse(bv.video_capture())

        bv = sppasVideoBuffer(overlap=2)
        self.assertEqual(bv.get_size(), sppasVideoBuffer.DEFAULT_BUFFER_SIZE)
        self.assertEqual(bv.get_overlap(), 2)
        self.assertFalse(bv.video_capture())

        bv = sppasVideoBuffer(size=10, overlap=2)
        self.assertEqual(bv.get_size(), 10)
        self.assertEqual(bv.get_overlap(), 2)
        self.assertFalse(bv.video_capture())

        with self.assertRaises(ValueError):
            sppasVideoBuffer(size=10, overlap=10)

        with self.assertRaises(ValueError):
            sppasVideoBuffer(size=-1)

        with self.assertRaises(ValueError):
            sppasVideoBuffer(overlap=-1)

        with self.assertRaises(ValueError):
            sppasVideoBuffer(overlap="xx")

        with self.assertRaises(ValueError):
            sppasVideoBuffer(size="xx")

    # -----------------------------------------------------------------------

    def test_init_video(self):
        """Test several ways to instantiate a video buffer with a video."""
        self.assertTrue(os.path.exists(TestVideoBuffer.VIDEO))
        bv = sppasVideoBuffer(TestVideoBuffer.VIDEO)
        self.assertTrue(bv.video_capture())
        self.assertTrue(bv.eov)
        self.assertEqual(0, len(bv))
        self.assertEqual(25, bv.get_framerate())
        self.assertEqual(0, bv.tell())
        self.assertEqual(0, bv.get_ms())
        self.assertEqual(960, bv.get_width())
        self.assertEqual(540, bv.get_height())
        self.assertEqual(1181, bv.get_nframes())

    # -----------------------------------------------------------------------

    def test_buffer_size(self):
        bv = sppasVideoBuffer(TestVideoBuffer.VIDEO)
        self.assertEqual(bv.get_size(), sppasVideoBuffer.DEFAULT_BUFFER_SIZE)

        bv.set_size(1000)
        self.assertEqual(1000, bv.get_size())

        with self.assertRaises(ValueError):
            bv.set_size(100000)

        with self.assertRaises(ValueError):
            bv.set_size("a")

        bv.set_overlap(100)
        with self.assertRaises(ValueError):
            bv.set_size(99)

    # -----------------------------------------------------------------------

    def test_buffer_overlap(self):
        bv = sppasVideoBuffer(TestVideoBuffer.VIDEO)
        self.assertEqual(bv.get_overlap(), sppasVideoBuffer.DEFAULT_BUFFER_OVERLAP)

        bv.set_overlap(100)
        self.assertEqual(100, bv.get_overlap())

        with self.assertRaises(ValueError):
            bv.set_overlap("a")

        with self.assertRaises(ValueError):
            bv.set_overlap(sppasVideoBuffer.DEFAULT_BUFFER_SIZE)

    # -----------------------------------------------------------------------

    def test_next(self):
        bv = sppasVideoBuffer()
        bv.next()
        self.assertEqual(0, len(bv))

        bv = sppasVideoBuffer(TestVideoBuffer.VIDEO, size=50, overlap=5)

        # Fill in the first buffer of images
        bv.next()
        self.assertEqual(50, len(bv))
        copied = list()
        for image in bv:
            self.assertIsInstance(image, np.ndarray)
            copied.append(image.copy())

        # Fill in the second buffer of images. Test the overlapped images.
        bv.next()
        self.assertEqual(50, len(bv))
        for i in range(5):
            self.assertTrue(np.array_equal(copied[45+i], bv[i]))

        # Last buffer is not full
        bv.seek_buffer(bv.get_nframes()-15)
        bv.next()
        self.assertEqual(15, len(bv))

    # -----------------------------------------------------------------------

    def test_previous(self):
        bv = sppasVideoBuffer()
        bv.previous()
        self.assertEqual(0, len(bv))
