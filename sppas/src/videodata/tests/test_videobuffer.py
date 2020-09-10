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

from ..videobuffer import sppasVideoReaderBuffer

# ---------------------------------------------------------------------------


class TestVideoBuffer(unittest.TestCase):

    VIDEO = os.path.join(paths.samples, "faces", "video_sample.mp4")

    # -----------------------------------------------------------------------

    def test_init_no_video(self):
        """Test several ways to instantiate a video buffer without video."""
        bv = sppasVideoReaderBuffer()
        self.assertEqual(bv.get_buffer_size(), sppasVideoReaderBuffer.DEFAULT_BUFFER_SIZE)
        self.assertEqual(bv.get_buffer_overlap(), sppasVideoReaderBuffer.DEFAULT_BUFFER_OVERLAP)
        self.assertFalse(bv.is_opened())
        self.assertEqual(0, bv.get_framerate())
        self.assertEqual(0, bv.tell())

        bv = sppasVideoReaderBuffer(size=12)
        self.assertEqual(bv.get_buffer_size(), 12)
        self.assertEqual(bv.get_buffer_overlap(), sppasVideoReaderBuffer.DEFAULT_BUFFER_OVERLAP)
        self.assertFalse(bv.is_opened())

        bv = sppasVideoReaderBuffer(overlap=2)
        self.assertEqual(bv.get_buffer_size(), sppasVideoReaderBuffer.DEFAULT_BUFFER_SIZE)
        self.assertEqual(bv.get_buffer_overlap(), 2)
        self.assertFalse(bv.is_opened())

        bv = sppasVideoReaderBuffer(size=10, overlap=2)
        self.assertEqual(bv.get_buffer_size(), 10)
        self.assertEqual(bv.get_buffer_overlap(), 2)
        self.assertFalse(bv.is_opened())
        self.assertEqual((-1, -1), bv.get_buffer_range())

        with self.assertRaises(ValueError):
            sppasVideoReaderBuffer(size=10, overlap=10)

        with self.assertRaises(ValueError):
            sppasVideoReaderBuffer(size=-1)

        with self.assertRaises(ValueError):
            sppasVideoReaderBuffer(overlap=-1)

        with self.assertRaises(ValueError):
            sppasVideoReaderBuffer(overlap="xx")

        with self.assertRaises(ValueError):
            sppasVideoReaderBuffer(size="xx")

    # -----------------------------------------------------------------------

    def test_init_video(self):
        """Test several ways to instantiate a video buffer with a video."""
        self.assertTrue(os.path.exists(TestVideoBuffer.VIDEO))
        bv = sppasVideoReaderBuffer(TestVideoBuffer.VIDEO)
        self.assertTrue(bv.is_opened())
        self.assertEqual(0, len(bv))
        self.assertEqual(25, bv.get_framerate())
        self.assertEqual(0, bv.tell())
        self.assertEqual(1181, bv.get_nframes())
        self.assertEqual((-1, -1), bv.get_buffer_range())
        self.assertEqual(960, bv.get_width())
        self.assertEqual(540, bv.get_height())

    # -----------------------------------------------------------------------

    def test_constant(self):
        self.assertEqual(200, sppasVideoReaderBuffer.DEFAULT_BUFFER_SIZE)
        self.assertEqual(0, sppasVideoReaderBuffer.DEFAULT_BUFFER_OVERLAP)

    # -----------------------------------------------------------------------

    def test_subclassing(self):

        class subclassVideoBuffer(sppasVideoReaderBuffer):
            def __init__(self, video=None,
                         size=sppasVideoReaderBuffer.DEFAULT_BUFFER_SIZE):
                super(subclassVideoBuffer, self).__init__(video, size, overlap=0)

        bv = subclassVideoBuffer()
        self.assertEqual(bv.get_buffer_size(), sppasVideoReaderBuffer.DEFAULT_BUFFER_SIZE)
        self.assertEqual(bv.get_buffer_overlap(), sppasVideoReaderBuffer.DEFAULT_BUFFER_OVERLAP)
        self.assertFalse(bv.is_opened())
        self.assertEqual(0, bv.get_framerate())
        self.assertEqual(0, bv.tell())

    # -----------------------------------------------------------------------

    def test_buffer_size(self):
        bv = sppasVideoReaderBuffer(TestVideoBuffer.VIDEO)
        self.assertEqual(bv.get_buffer_size(), sppasVideoReaderBuffer.DEFAULT_BUFFER_SIZE)

        bv.set_buffer_size(1000)
        self.assertEqual(1000, bv.get_buffer_size())

        with self.assertRaises(ValueError):
            bv.set_buffer_size(100000)

        with self.assertRaises(ValueError):
            bv.set_buffer_size("a")

        bv.set_buffer_overlap(100)
        with self.assertRaises(ValueError):
            bv.set_buffer_size(99)

    # -----------------------------------------------------------------------

    def test_buffer_overlap(self):
        bv = sppasVideoReaderBuffer(TestVideoBuffer.VIDEO)
        self.assertEqual(bv.get_buffer_overlap(), sppasVideoReaderBuffer.DEFAULT_BUFFER_OVERLAP)

        bv.set_buffer_overlap(100)
        self.assertEqual(100, bv.get_buffer_overlap())

        with self.assertRaises(ValueError):
            bv.set_buffer_overlap("a")

        with self.assertRaises(ValueError):
            bv.set_buffer_overlap(sppasVideoReaderBuffer.DEFAULT_BUFFER_SIZE)

    # -----------------------------------------------------------------------

    def test_next(self):
        bv = sppasVideoReaderBuffer()

        # no video. so no next buffer to fill in.
        bv.next()
        self.assertEqual(0, len(bv))
        self.assertEqual((-1, -1), bv.get_buffer_range())

        # with a video file
        bv = sppasVideoReaderBuffer(TestVideoBuffer.VIDEO, size=50, overlap=5)

        # Fill in the first buffer of images
        res = bv.next()
        self.assertEqual(50, bv.tell())
        self.assertEqual(50, len(bv))
        self.assertEqual((0, 49), bv.get_buffer_range())
        self.assertTrue(res)  # we did not reached the end of the video
        copied = list()
        for image in bv:
            self.assertIsInstance(image, np.ndarray)
            copied.append(image.copy())

        # Fill in the second buffer of images. Test the overlapped images.
        bv.next()
        self.assertEqual(95, bv.tell())
        self.assertEqual((45, 94), bv.get_buffer_range())
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
        self.assertEqual((bv.get_nframes()-15, bv.get_nframes()-1), bv.get_buffer_range())

    # -----------------------------------------------------------------------

    def test_next_loop(self):
        # Loop through all the buffers
        bv = sppasVideoReaderBuffer(TestVideoBuffer.VIDEO, size=50, overlap=0)

        read_next = 1
        while bv.next() is True:
            self.assertEqual(50*read_next, bv.tell())
            self.assertEqual(50*read_next, bv.tell_buffer())
            read_next += 1
        self.assertEqual(24, read_next)
        self.assertEqual(1181, bv.tell())

    # -----------------------------------------------------------------------

    def test_eval_max_buffer_size(self):
        bv = sppasVideoReaderBuffer(TestVideoBuffer.VIDEO, size=50, overlap=0)

        w = bv.get_width()    # 960
        h = bv.get_height()   # 540
        nbytes = w * h * 3    # uint8 for r, g, and b
        memory_max = 1024*1024*1024
        buffer_max = memory_max // nbytes
        print(buffer_max)

