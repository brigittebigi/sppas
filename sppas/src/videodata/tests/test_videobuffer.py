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

from ..video import sppasVideo
from ..videobuffer import sppasVideoBuffer

# ---------------------------------------------------------------------------


class TestVideo(unittest.TestCase):

    VIDEO = os.path.join(paths.samples, "faces", "video_sample.mp4")

    # -----------------------------------------------------------------------

    def test_init(self):
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
        self.assertEqual(960, bv.get_width())
        self.assertEqual(540, bv.get_height())
        self.assertEqual(1181, bv.get_nframes())
        self.assertEqual(47.240, bv.get_duration())

        # invalid file
        with self.assertRaises(Exception):
            bv.open("toto.xxx")
        self.assertFalse(bv.video_capture())

    # -----------------------------------------------------------------------

    def test_seek_tell(self):
        bv = sppasVideo()
        bv.open(TestVideo.VIDEO)

        bv.seek(200)
        self.assertEqual(200, bv.tell())

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


class TestVideoBuffer(unittest.TestCase):

    VIDEO = os.path.join(paths.samples, "faces", "video_sample.mp4")

    # -----------------------------------------------------------------------

    def test_init_no_video(self):
        """Test several ways to instantiate a video buffer without video."""
        bv = sppasVideoBuffer()
        self.assertEqual(bv.get_size(), sppasVideoBuffer.DEFAULT_BUFFER_SIZE)
        self.assertEqual(bv.get_overlap(), sppasVideoBuffer.DEFAULT_BUFFER_OVERLAP)
        self.assertFalse(bv.video_capture())
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
        self.assertEqual((-1, -1), bv.get_range())

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
        self.assertEqual(0, len(bv))
        self.assertEqual(25, bv.get_framerate())
        self.assertEqual(0, bv.tell())
        self.assertEqual(1181, bv.get_nframes())
        self.assertEqual((-1, -1), bv.get_range())
        self.assertEqual(960, bv.get_width())
        self.assertEqual(540, bv.get_height())

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

        # no video. so no next buffer to fill in.
        bv.next()
        self.assertEqual(0, len(bv))
        self.assertEqual((-1, -1), bv.get_range())

        # with a video file
        bv = sppasVideoBuffer(TestVideoBuffer.VIDEO, size=50, overlap=5)

        # Fill in the first buffer of images
        res = bv.next()
        self.assertEqual(50, bv.tell())
        self.assertEqual(50, len(bv))
        self.assertEqual((0, 49), bv.get_range())
        self.assertTrue(res)  # we did not reached the end of the video
        copied = list()
        for image in bv:
            self.assertIsInstance(image, np.ndarray)
            copied.append(image.copy())

        # Fill in the second buffer of images. Test the overlapped images.
        bv.next()
        self.assertEqual(95, bv.tell())
        self.assertEqual((45, 94), bv.get_range())
        self.assertEqual(50, len(bv))
        for i in range(5):
            self.assertTrue(np.array_equal(copied[45+i], bv[i]))

        # Last buffer is not full
        self.assertEqual(1181, bv.get_nframes())
        bv.seek_buffer(bv.get_nframes()-15)
        self.assertEqual(95, bv.tell())
        self.assertEqual(bv.get_nframes()-15, bv.tell_buffer())
        res = bv.next()
        # we reached the end of the video
        self.assertFalse(res)  # no next buffer can be read
        self.assertEqual(1181, bv.tell())
        self.assertEqual(15, len(bv))
        self.assertEqual((bv.get_nframes()-15, bv.get_nframes()-1), bv.get_range())

    # -----------------------------------------------------------------------

    def test_next_loop(self):
        # Loop through all the buffers
        bv = sppasVideoBuffer(TestVideoBuffer.VIDEO, size=50, overlap=0)

        read_next = 1
        while bv.next() is True:
            self.assertEqual(50*read_next, bv.tell())
            self.assertEqual(50*read_next, bv.tell_buffer())
            read_next += 1
        self.assertEqual(24, read_next)
        self.assertEqual(1181, bv.tell())

    # -----------------------------------------------------------------------

    def test_eval_max_buffer_size(self):
        bv = sppasVideoBuffer(TestVideoBuffer.VIDEO, size=50, overlap=0)

        w = bv.get_width()    # 960
        h = bv.get_height()   # 540
        nbytes = w * h * 3    # uint8 for r, g, and b
        memory_max = 1024*1024*1024
        buffer_max = memory_max // nbytes
        print(buffer_max)

