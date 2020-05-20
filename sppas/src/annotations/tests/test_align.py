# -*- coding: utf8 -*-
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

    src.annotations.tests.test_align.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""
import unittest
import os
import shutil
import codecs

from sppas.src.config import sg
from sppas.src.config import paths
import sppas.src.anndata.aio.aioutils as aioutils
from sppas.src.anndata import sppasRW
from sppas.src.anndata import sppasLocation
from sppas.src.anndata import sppasPoint
from sppas.src.anndata import sppasTag
from sppas.src.anndata import sppasLabel
from sppas.src.anndata import sppasAnnotation
from sppas.src.anndata import sppasTier
from sppas.src.anndata.aio import sppasXRA
from sppas.src.wkps.fileutils import sppasFileUtils
from sppas.src.resources import sppasMapping

from ..annotationsexc import SizeInputsError

from ..Align.tracksio import ListOfTracks
from ..Align.tracksio import TrackNamesGenerator
from ..Align.tracksio import TracksWriter
from ..Align.tracksio import TracksReader
from ..Align.tracksio import TracksReaderWriter
from ..Align.sppasalign import sppasAlign

# ---------------------------------------------------------------------------

TEMP = sppasFileUtils().set_random()
DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")

# ---------------------------------------------------------------------------


class TestTrackNamesGenerator(unittest.TestCase):
    """Manage names of the files for a given track number."""

    def test_names(self):
        """Test all generators: audio, phones, tokens, align."""
        # audio
        self.assertEqual("track_000001.wav",
                         TrackNamesGenerator.audio_filename("", 1))
        # phones
        self.assertEqual("track_000001.phn",
                         TrackNamesGenerator.phones_filename("", 1))
        # tokens
        self.assertEqual("track_000001.tok",
                         TrackNamesGenerator.tokens_filename("", 1))
        # aligned file
        self.assertEqual("track_000001",
                         TrackNamesGenerator.align_filename("", 1))
        self.assertEqual("track_000001.palign",
                         TrackNamesGenerator.align_filename("", 1, "palign"))

# ---------------------------------------------------------------------------


class TestListOfTracks(unittest.TestCase):
    """Write track files."""

    def setUp(self):
        if os.path.exists(TEMP) is False:
            os.mkdir(TEMP)

    def tearDown(self):
        shutil.rmtree(TEMP)

    # -----------------------------------------------------------------------

    def test_read_write(self):
        """Manage the file with a list of tracks (units, ipus...)."""
        units = [(1., 2.), (2., 3.), (3., 4.)]
        ListOfTracks.write(TEMP, units)
        read_units = ListOfTracks.read(TEMP)
        self.assertEqual(units, read_units)

        with self.assertRaises(IOError):
            ListOfTracks.read("toto")

# ---------------------------------------------------------------------------


class TestTracksWriter(unittest.TestCase):
    """Write track files."""

    def setUp(self):
        if os.path.exists(TEMP) is False:
            os.mkdir(TEMP)

    def tearDown(self):
        shutil.rmtree(TEMP)

    # -----------------------------------------------------------------------

    def test_write_tokens(self):
        """Write the tokenization of a track in a file."""
        # test to write an annotation with complex labels
        l1 = sppasLabel([sppasTag("option1"), sppasTag("alt1")])
        l2 = sppasLabel([sppasTag("option2"), sppasTag("alt2")])
        ann = sppasAnnotation(sppasLocation(sppasPoint(1)), [l1, l2])
        TracksWriter._write_tokens(ann, TEMP, 1)
        fn = os.path.join(TEMP, "track_000001.tok")
        self.assertTrue(os.path.exists(fn))
        with codecs.open(fn, "r", sg.__encoding__) as fp:
            lines = fp.readlines()
            fp.close()
        self.assertEqual(1, len(lines))
        self.assertEqual("{option1|alt1} {option2|alt2}", lines[0])

        # test to write an annotation with already serialized labels
        sentence = "A serialized list of {labels|tags}"
        ann = sppasAnnotation(
            sppasLocation(sppasPoint(1)),
            sppasLabel(sppasTag(sentence)))
        TracksWriter._write_tokens(ann, TEMP, 2)
        fn = os.path.join(TEMP, "track_000002.tok")
        self.assertTrue(os.path.exists(fn))
        with codecs.open(fn, "r", sg.__encoding__) as fp:
            lines = fp.readlines()
            fp.close()
        self.assertEqual(1, len(lines))
        self.assertEqual(sentence, lines[0])

    # -----------------------------------------------------------------------

    def test_write_phonemes(self):
        """Write the phonetization of a track in a file."""
        # test to write an annotation with complex labels
        l1 = sppasLabel([sppasTag("j"), sppasTag("S")])
        l2 = sppasLabel([sppasTag("e"), sppasTag("E")])
        ann = sppasAnnotation(sppasLocation(sppasPoint(1)), [l1, l2])
        TracksWriter._write_phonemes(ann, TEMP, 1)
        fn = os.path.join(TEMP, "track_000001.phn")
        self.assertTrue(os.path.exists(fn))
        with codecs.open(fn, "r", sg.__encoding__) as fp:
            lines = fp.readlines()
            fp.close()
        self.assertEqual(1, len(lines))
        self.assertEqual("{j|S} {e|E}", lines[0])

        # test to write an annotation with already serialized labels
        sentence = "A serialized list of {labels|tags}"
        ann = sppasAnnotation(
            sppasLocation(sppasPoint(1)),
            sppasLabel(sppasTag(sentence)))
        TracksWriter._write_phonemes(ann, TEMP, 2)
        fn = os.path.join(TEMP, "track_000002.phn")
        self.assertTrue(os.path.exists(fn))
        with codecs.open(fn, "r", sg.__encoding__) as fp:
            lines = fp.readlines()
            fp.close()
        self.assertEqual(1, len(lines))
        self.assertEqual(sentence, lines[0])

    # -----------------------------------------------------------------------

    def test_create_tok_tier(self):
        """Create a tier with tokens like 'w_1 w_2...w_n' from phonemes."""
        l1 = sppasLabel([sppasTag("j"), sppasTag("S")])
        l2 = sppasLabel([sppasTag("e"), sppasTag("E")])
        tier = sppasTier("phonemes")
        tier.create_annotation(sppasLocation(sppasPoint(1)),
                               [l1, l2])
        tier.create_annotation(sppasLocation(sppasPoint(2)),
                               sppasLabel(sppasTag("{j|S} {e|E}")))
        tok_tier = TracksWriter._create_tok_tier(tier)
        self.assertEqual(2, len(tok_tier))
        content_a1 = tok_tier[0].get_best_tag().get_content()
        self.assertEqual("w_1 w_2", content_a1)
        content_a2 = tok_tier[1].get_best_tag().get_content()
        self.assertEqual("w_1 w_2", content_a2)

    # -----------------------------------------------------------------------

    def test_write_text_tracks(self):
        """Write tokenization and phonetization into separated track files."""
        l1 = sppasLabel([sppasTag("j"), sppasTag("S")])
        l2 = sppasLabel([sppasTag("e"), sppasTag("E")])
        tier_phn = sppasTier("phonemes")
        tier_phn.create_annotation(sppasLocation(sppasPoint(1)),
                                   [l1, l2])
        tier_phn.create_annotation(sppasLocation(sppasPoint(2)),
                                   sppasLabel(sppasTag("j-e s-H-i")))
        tier_tok = sppasTier("tokens")
        tier_tok.create_annotation(sppasLocation(sppasPoint(1)),
                                   sppasLabel(sppasTag("j' ai")))
        tier_tok.create_annotation(sppasLocation(sppasPoint(2)),
                                   sppasLabel(sppasTag('je suis')))

        with self.assertRaises(SizeInputsError):
            TracksWriter._write_text_tracks(tier_phn, sppasTier('toto'), TEMP)

        dir_tracks = os.path.join(TEMP, "test_write_text_tracks_1")
        os.mkdir(dir_tracks)
        TracksWriter._write_text_tracks(tier_phn, None, dir_tracks)
        created_files = os.listdir(dir_tracks)
        self.assertEqual(4, len(created_files))
        lines = list()
        for fn in created_files:
            with codecs.open(os.path.join(dir_tracks, fn), "r", sg.__encoding__) as fp:
                new_lines = fp.readlines()
                fp.close()
            self.assertEqual(1, len(new_lines))
            lines.append(new_lines[0])
        self.assertTrue("w_1 w_2" in lines)
        self.assertTrue("{j|S} {e|E}" in lines)
        self.assertTrue("j-e s-H-i" in lines)

        dir_tracks = os.path.join(TEMP, "test_write_text_tracks_2")
        os.mkdir(dir_tracks)
        TracksWriter._write_text_tracks(tier_phn, tier_tok, dir_tracks)
        created_files = os.listdir(dir_tracks)
        self.assertEqual(4, len(created_files))
        lines = list()
        for fn in created_files:
            with codecs.open(os.path.join(dir_tracks, fn), "r", sg.__encoding__) as fp:
                new_lines = fp.readlines()
                fp.close()
            self.assertEqual(1, len(new_lines))
            lines.append(new_lines[0])
        self.assertTrue("j' ai" in lines)
        self.assertTrue("je suis" in lines)
        self.assertTrue("{j|S} {e|E}" in lines)
        self.assertTrue("j-e s-H-i" in lines)

    # -----------------------------------------------------------------------

    def test_write_audio_tracks(self):
        """Write the first channel of an audio file into separated track files."""
        pass

    # -----------------------------------------------------------------------

    def test_write_tracks(self):
        """Main method to write tracks from the given data."""
        pass

# ---------------------------------------------------------------------------


class TestTracksReader(unittest.TestCase):
    """Read time-aligned track files."""

    def test_read(self):
        tier_phn, tier_tok, tier_pron = TracksReader.read_aligned_tracks(DATA)
        self.assertEqual(36, len(tier_phn))
        self.assertEqual(12, len(tier_tok))
        self.assertEqual(12, len(tier_pron))

        self.assertEqual("dh", aioutils.serialize_labels(tier_phn[1]))
        self.assertEqual("ax", aioutils.serialize_labels(tier_phn[2]))
        self.assertEqual("f", aioutils.serialize_labels(tier_phn[3]))
        self.assertEqual("l", aioutils.serialize_labels(tier_phn[4]))
        self.assertEqual("ay", aioutils.serialize_labels(tier_phn[5]))
        self.assertEqual("t", aioutils.serialize_labels(tier_phn[6]))

        self.assertEqual("dh-ax", aioutils.serialize_labels(tier_pron[1]))
        self.assertEqual("f-l-ay-t", aioutils.serialize_labels(tier_pron[2]))

# ---------------------------------------------------------------------------


class TestTracksReaderWriter(unittest.TestCase):
    """Read/Write track files."""

    def setUp(self):
        if os.path.exists(TEMP) is False:
            os.mkdir(TEMP)

    def tearDown(self):
        shutil.rmtree(TEMP)

    # -----------------------------------------------------------------------

    def test_init(self):
        with self.assertRaises(TypeError):
            TracksReaderWriter("")
        t1 = TracksReaderWriter(sppasMapping())
        t2 = TracksReaderWriter(None)

    # -----------------------------------------------------------------------

    def test_split_into_tracks_without_mapping(self):
        """Test to read and write tracks without mapping."""
        audio = os.path.join(DATA, "oriana1.wav")
        phon = os.path.join(DATA, "oriana1-phon.xra")
        token = os.path.join(DATA, "oriana1-token.xra")
        t = sppasXRA()
        t.read(phon)
        t.read(token)
        phn_tier = t.find('Phones')
        tok_tier = t.find('Tokens')

        trks = TracksReaderWriter(None)  # no mapping table
        temp = os.path.join(TEMP, "test_split1")
        os.mkdir(temp)

        trks.split_into_tracks(audio, phn_tier, tok_tier, temp)
        created_files = os.listdir(temp)
        self.assertEqual(22, len(created_files))   # 21 tracks + List

        # Tokenization of the 1st IPU
        with codecs.open(os.path.join(temp, "track_000002.tok"),
                         "r", sg.__encoding__) as fp:
            new_lines = fp.readlines()
            fp.close()
        self.assertEqual(1, len(new_lines))
        self.assertEqual("the flight was twelve hours long and "
                         "we really got bored",
                         new_lines[0])

        # Phonetization of the 1st IPU
        with codecs.open(os.path.join(temp, "track_000002.phn"),
                         "r", sg.__encoding__) as fp:
            new_lines = fp.readlines()
            fp.close()
        self.assertEqual(1, len(new_lines))
        self.assertEqual("D-@|D-i:|D-V "
                         "f-l-aI-t "
                         "w-@-z|w-V-z|w-O:-z|w-A-z "
                         "t-w-E-l-v "
                         "aU-3:r-z|aU-r\-z "
                         "l-O:-N "
                         "{-n-d|@-n-d "
                         "w-i: "
                         "r\-I-l-i:|r\-i:-l-i: "
                         "g-A-t "
                         "b-O:-r\-d",
                         new_lines[0])

    # -----------------------------------------------------------------------

    def test_split_into_tracks_with_mapping(self):
        """Test to read and write tracks with mapping."""
        audio = os.path.join(DATA, "oriana1.wav")
        phon = os.path.join(DATA, "oriana1-phon.xra")
        token = os.path.join(DATA, "oriana1-token.xra")
        t = sppasXRA()
        t.read(phon)
        t.read(token)
        phn_tier = t.find('Phones')
        tok_tier = t.find('Tokens')

        trks = TracksReaderWriter(sppasMapping(
            os.path.join(DATA, "monophones.repl")
        ))
        temp = os.path.join(TEMP, "test_split2")
        os.mkdir(temp)

        trks.split_into_tracks(audio, phn_tier, tok_tier, temp)
        created_files = os.listdir(temp)
        self.assertEqual(22, len(created_files))  # 21 tracks + List

        # Tokenization of the 1st IPU
        with codecs.open(os.path.join(temp, "track_000002.tok"),
                         "r", sg.__encoding__) as fp:
            new_lines = fp.readlines()
            fp.close()
        self.assertEqual(1, len(new_lines))
        self.assertEqual("the flight was twelve hours long and "
                         "we really got bored",
                         new_lines[0])

        # Phonetization of the 1st IPU
        with codecs.open(os.path.join(temp, "track_000002.phn"),
                         "r", sg.__encoding__) as fp:
            new_lines = fp.readlines()
            fp.close()
        self.assertEqual(1, len(new_lines))
        self.assertEqual("dh-ax|dh-iy|dh-ah "
                         "f-l-ay-t "
                         "w-ax-z|w-ah-z|w-ao-z|w-aa-z "
                         "t-w-eh-l-v "
                         "aw-er-z|aw-r-z "
                         "l-ao-ng "
                         "ae-n-d|ax-n-d "
                         "w-iy "
                         "r-ih-l-iy|r-iy-l-iy "
                         "g-aa-t "
                         "b-ao-r-d",
                         new_lines[0])

    # -----------------------------------------------------------------------

    def test_read_aligned_tracks(self):
        trks = TracksReaderWriter(sppasMapping(
            os.path.join(DATA, "monophones.repl")
        ))

        tier_phn, tier_tok, tier_pron = trks.read_aligned_tracks(DATA)
        self.assertEqual(36, len(tier_phn))
        self.assertEqual(12, len(tier_tok))
        self.assertEqual(12, len(tier_pron))

        self.assertEqual("D", aioutils.serialize_labels(tier_phn[1]))
        self.assertEqual("@", aioutils.serialize_labels(tier_phn[2]))
        self.assertEqual("f", aioutils.serialize_labels(tier_phn[3]))
        self.assertEqual("l", aioutils.serialize_labels(tier_phn[4]))
        self.assertEqual("aI", aioutils.serialize_labels(tier_phn[5]))
        self.assertEqual("t", aioutils.serialize_labels(tier_phn[6]))

        self.assertEqual("D-@", aioutils.serialize_labels(tier_pron[1]))
        self.assertEqual("f-l-aI-t", aioutils.serialize_labels(tier_pron[2]))

# ---------------------------------------------------------------------------


class TestAlign(unittest.TestCase):
    """SPPAS Alignment."""

    def setUp(self):
        if os.path.exists(TEMP) is False:
            os.mkdir(TEMP)

    def tearDown(self):
        shutil.rmtree(TEMP)

    # -----------------------------------------------------------------------

    def test_init(self):
        model = os.path.join(paths.resources, "models", 'models-eng')
        model1 = os.path.join(paths.resources, "models", 'models-fra')
        s = sppasAlign()
        s.load_resources(model)
        s.load_resources(model, model1)
        # with self.assertRaises(IOError):
        #     s.load_resources("toto")

    # -----------------------------------------------------------------------

    def test_convert(self):
        model = os.path.join(paths.resources, "models", 'models-eng')
        audio = os.path.join(DATA, "oriana1.wav")
        phon = os.path.join(DATA, "oriana1-phon.xra")
        token = os.path.join(DATA, "oriana1-token.xra")
        t = sppasXRA()
        t.read(phon)
        t.read(token)
        phn_tier = t.find('Phones')
        tok_tier = t.find('Tokens')

        a = sppasAlign()
        a.load_resources(model)

        tier_phn, tier_tok, tier_pron = a.convert(phn_tier, tok_tier, audio, TEMP)

        self.assertEqual(123, len(tier_phn))
        self.assertEqual(39, len(tier_tok))
        self.assertEqual(39, len(tier_pron))

        self.assertEqual("D", aioutils.serialize_labels(tier_phn[1]))
        self.assertEqual("@", aioutils.serialize_labels(tier_phn[2]))
        self.assertEqual("f", aioutils.serialize_labels(tier_phn[3]))
        self.assertEqual("l", aioutils.serialize_labels(tier_phn[4]))
        self.assertEqual("aI", aioutils.serialize_labels(tier_phn[5]))
        self.assertEqual("t", aioutils.serialize_labels(tier_phn[6]))
        self.assertEqual("{", aioutils.serialize_labels(tier_phn[21]))
        self.assertEqual("{-n-d", aioutils.serialize_labels(tier_pron[7]))

    # -----------------------------------------------------------------------

    def test_samples_fra(self):
        """... Compare if the current result is the same as the existing one."""
        self.compare_samples("fra")

    # -----------------------------------------------------------------------
    #
    def test_samples_cat(self):
        """... Compare if the current result is the same as the existing one."""
        self.compare_samples("cat")

    # -----------------------------------------------------------------------

    def test_samples_cmn(self):
        """... Compare if the current result is the same as the existing one."""
        self.compare_samples("cmn")

    # -----------------------------------------------------------------------

    def test_samples_eng(self):
        """... Compare if the current result is the same as the existing one."""
        self.compare_samples("eng")

    # -----------------------------------------------------------------------
    # internal
    # -----------------------------------------------------------------------

    def compare_samples(self, lang):
        samples_folder = os.path.join(paths.samples, "samples-"+lang)

        # the place where are the existing results samples.
        expected_result_dir = os.path.join(paths.samples,
                                           "annotation-results",
                                           "samples-" + lang)

        # Create an Aligner for the given set of samples of the given language
        sa = sppasAlign()
        sa.load_resources(os.path.join(paths.resources, "models", "models-"+lang))
        self.compare_folders(samples_folder, expected_result_dir, sa)

    # -----------------------------------------------------------------------

    def compare_folders(self, samples_folder, expected_result_dir, sa):
        # Apply Alignment on each sample
        for filename in os.listdir(os.path.join(paths.samples, samples_folder)):
            if filename.endswith(".wav") is False:
                continue

            # Get the expected result
            expected_result_filename = os.path.join(
                expected_result_dir,
                filename[:-4] + "-palign.xra")
            if os.path.exists(expected_result_filename) is False:
                print("no existing alignment result {:s}".format(expected_result_filename))
                continue
            parser = sppasRW(expected_result_filename)
            expected_result = parser.read()
            expected_tier_phones = expected_result.find('PhonAlign')
            if expected_tier_phones is None:
                print("malformed alignment result for:", filename)
                continue

            # Estimate a result and check if it's like expected.
            audio_file = os.path.join(paths.samples, samples_folder, filename)
            phn_file = os.path.join(expected_result_dir, filename.replace('.wav', '-phon.xra'))
            tok_file = os.path.join(expected_result_dir, filename.replace('.wav', '-token.xra'))
            result_file = os.path.join(paths.samples, samples_folder, filename.replace('.wav', '-palign.xra'))
            expected_result = sa.run([audio_file, phn_file], [tok_file], result_file)
            print('Evaluate:', audio_file)

            self.compare_tiers(expected_tier_phones,
                               expected_result.find('PhonAlign'))

    # -----------------------------------------------------------------------

    def compare_tiers(self, expected, result):
        self.assertEqual(len(expected), len(result))
        for a1, a2 in zip(expected, result):
            self.assertEqual(a1.get_location(), a2.get_location())
            self.assertEqual(len(a1.get_labels()), len(a2.get_labels()))
            for l1, l2 in zip(a1.get_labels(), a2.get_labels()):
                self.assertEqual(l1, l2)
            for key in a1.get_meta_keys():
                if key != 'id':
                    self.assertEqual(a1.get_meta(key), a2.get_meta(key))
        for key in expected.get_meta_keys():
            if key != 'id':
                self.assertEqual(expected.get_meta(key), result.get_meta(key))
