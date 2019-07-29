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

    src.annotations.tests.test_normalize.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2019  Brigitte Bigi
    :summary:      Test the SPPAS Text Normalization.

"""
import unittest
import os.path

from sppas.src.config import paths

from sppas.src.anndata.anndataexc import AioEncodingError
from sppas.src.utils.makeunicode import u
from sppas.src.resources.vocab import sppasVocabulary
from sppas.src.resources.dictrepl import sppasDictRepl
from sppas.src.anndata import sppasRW

from ..TextNorm.normalize import TextNormalizer
from ..TextNorm.orthotranscription import sppasOrthoTranscription
from ..TextNorm.tokenize import sppasTokenSegmenter
from ..TextNorm.splitter import sppasSimpleSplitter
from ..TextNorm.sppastextnorm import sppasTextNorm

# ---------------------------------------------------------------------------


class TestOrthoTranscription(unittest.TestCase):
    """Test of the class sppasOrthoTranscription.
    Manager of an orthographic transcription.

    """

    def test_clean_toe(self):
        """... Clean Enriched Orthographic Transcription to get a standard ortho."""

        s = sppasOrthoTranscription().clean_toe(u('(il) (ne) faut pas rêver'))
        self.assertEqual(u("faut pas rêver"), s)

        s = sppasOrthoTranscription().clean_toe(u('i(l) (ne) faut pas réver'))
        self.assertEqual(u("i(l) faut pas réver"), s)

        s = sppasOrthoTranscription().clean_toe(u('i(l) (ne) faut pas réver'))
        self.assertEqual(u("i(l) faut pas réver"), s)

        s = sppasOrthoTranscription().clean_toe(u(' (il) faut pas réver i(l)'))
        self.assertEqual(u("faut pas réver i(l)"), s)

        s = sppasOrthoTranscription().clean_toe(u(' euh [je sais, ché] pas '))
        self.assertEqual(u("euh [je_sais,ché] pas"), s)

        s = sppasOrthoTranscription().clean_toe(u("  j'[ avais,  avé ] "))
        self.assertEqual(u("j' [avais,avé]"), s)

        s = sppasOrthoTranscription().clean_toe(u("  [j(e) sais,  ché ] "))
        self.assertEqual(u("[je_sais,ché]"), s)

        s = sppasOrthoTranscription().clean_toe(u("  [peut-êt(re),  pe êt] "))
        self.assertEqual(u("[peut-être,peêt]"), s)

        s = sppasOrthoTranscription().clean_toe(u(" (pu)tai(n) j'ai"))
        self.assertEqual(u("(pu)tai(n) j'ai"), s)

        s = sppasOrthoTranscription().clean_toe(u("gpd_100y en a un  qu(i) est devenu complèt(e)ment  "))
        self.assertEqual(u("y en a un qu(i) est devenu complèt(e)ment"), s)

        s = sppasOrthoTranscription().clean_toe(u("[$Londre, T/$, Londreu]"))
        self.assertEqual(u("[Londre,Londreu]"), s)

        s = sppasOrthoTranscription().clean_toe(u("t(u) vois [$Isabelle,P /$, isabelleu] $Armelle,P /$ t(out) ça"))
        self.assertEqual(u("t(u) vois [Isabelle,isabelleu] Armelle t(out) ça"), s)

        s = sppasOrthoTranscription().clean_toe(u("gpd_1324ah euh"))
        self.assertEqual(u("ah euh"), s)

        s = sppasOrthoTranscription().clean_toe(u("ipu_1324ah euh"))
        self.assertEqual(u("ah euh"), s)

        s = sppasOrthoTranscription().clean_toe(u("ah a/b euh"))
        self.assertEqual(u("ah a/b euh"), s)

    # -----------------------------------------------------------------------

    def test_toe_spelling(self):
        """... Create a specific spelling from an Enriched Orthographic Transcription."""

        s = sppasOrthoTranscription().toe_spelling(u('je, fais: "un essai".'))
        self.assertEqual(u('je , fais : " un essai " .'), s)

        s = sppasOrthoTranscription().toe_spelling(u('€&serie de punctuations!!!):-)".'))
        self.assertEqual(u('€ & serie de punctuations ! ! ! ) : - ) " .'), s)

        s = sppasOrthoTranscription().toe_spelling(u('123,2...'))
        self.assertEqual(u('123,2 . . .'), s)

        # this is sampa to be sent directly to the phonetizer
        s = sppasOrthoTranscription().toe_spelling(u(" /l-e-f-o~-n/ "))
        self.assertEqual(u('/l-e-f-o~-n/'), s)

        # this is not sampa, because sampa can't contain whitespace.
        s = sppasOrthoTranscription().toe_spelling(u('/le mot/'))
        self.assertEqual(u('/ le mot /'), s)

        s = sppasOrthoTranscription().toe_spelling(u('(/'))
        self.assertEqual(u('( / '), s)

    # -----------------------------------------------------------------------

    def test_toe(self):
        """... Apply both clean_toe then toe_spelling."""

        s = sppasOrthoTranscription().clean_toe(u(" /l-e-f-o~-n/ "))
        s = sppasOrthoTranscription().toe_spelling(s)
        self.assertEqual(u('/l-e-f-o~-n/'), s)

        s = sppasOrthoTranscription().clean_toe(u(" /le mot/ "))
        s = sppasOrthoTranscription().toe_spelling(s)
        self.assertEqual(u('/ le mot /'), s)

# ---------------------------------------------------------------------------


class TestSimpleSplitter(unittest.TestCase):
    """Test of Utterance splitter."""

    def test_split_characters(self):
        """... Split a character-based string."""

        splitter = sppasSimpleSplitter("cmn")
        result = splitter.split_characters("干脆就把那部蒙人的闲法给废了拉倒")
        expected = u("干 脆 就 把 那 部 蒙 人 的 闲 法 给 废 了 拉 倒")
        self.assertEqual(expected, result)

        result = splitter.split_characters("abc123")
        expected = u(" abc123 ")
        self.assertEqual(expected, result)

    # -----------------------------------------------------------------------

    def test_split(self):
        """... Split a character-based or romanized string."""

        splitter = sppasSimpleSplitter("cmn")
        result = splitter.split("干脆就把那部蒙人.的闲法给废了拉倒")
        expected = u("干 脆 就 把 那 部 蒙 人 . 的 闲 法 给 废 了 拉 倒")
        self.assertEqual(expected.split(), result)

        splitter = sppasSimpleSplitter("fra")
        result = splitter.split("abc~ /sa~mpa/")
        expected = u("abc~ /sa~mpa/")
        self.assertEqual(expected.split(), result)

        result = splitter.split("abc. abc")
        expected = u("abc. abc")
        self.assertEqual(expected.split(), result)

# ---------------------------------------------------------------------------


class TestNormalizer(unittest.TestCase):

    def setUp(self):
        dict_dir = os.path.join(paths.resources, "vocab")
        vocab_file = os.path.join(dict_dir, "fra.vocab")
        punct_file = os.path.join(dict_dir, "Punctuations.txt")
        wds = sppasVocabulary(vocab_file)
        puncts = sppasVocabulary(punct_file)
        self.tok = TextNormalizer(wds, "fra")
        self.tok.set_punct(puncts)

    # -----------------------------------------------------------------------

    def test_replace(self):
        """... Examine tokens and performs some replacements."""

        repl = sppasDictRepl(os.path.join(paths.resources, "repl", "fra.repl"), nodump=True)
        self.tok.set_repl(repl)
        s = self.tok.replace([u("un"), u("taux"), u("de"), u("croissance"), u("de"), u("0,5"), u("%")])
        self.assertEqual(s, [u("un"), u("taux"), u("de"), u("croissance"), u("de"), u("0"), u("virgule"), u("5"),
                              u("pourcents")])

        text = [u("² % °c  km/h  etc   €  ¥ $ ")]

        repl = sppasDictRepl(os.path.join(paths.resources, "repl", "eng.repl"), nodump=True)
        self.tok.set_repl(repl)
        s = self.tok.replace(text)
        self.assertEqual(u("square percent degrees_Celsius km/h etc euros yens dollars"),
                          " ".join(s))

        repl = sppasDictRepl(os.path.join(paths.resources, "repl", "spa.repl"), nodump=True)
        self.tok.set_repl(repl)
        s = self.tok.replace(text)
        self.assertEqual(u("quadrados por_ciento grados_Celsius km/h etc euros yens dollars"),
                          " ".join(s))

        repl = sppasDictRepl(os.path.join(paths.resources, "repl", "fra.repl"), nodump=True)
        self.tok.set_repl(repl)
        s = self.tok.replace(text)
        self.assertEqual(u("carrés pourcents degrés_celcius kilomètres_heure etcetera euros yens dollars"),
                          " ".join(s))

        repl = sppasDictRepl(os.path.join(paths.resources, "repl", "ita.repl"), nodump=True)
        self.tok.set_repl(repl)
        s = self.tok.replace(text)
        self.assertEqual(u("quadrato percento gradi_Celsius km/h etc euros yens dollars"),
                          " ".join(s))

        repl = sppasDictRepl(os.path.join(paths.resources, "repl", "cmn.repl"), nodump=True)
        self.tok.set_repl(repl)
        s = self.tok.replace(text)
        self.assertEqual(u("的平方 个百分比 摄氏度 公里每小时 etc € ¥ $"),
                          " ".join(s))

    # -----------------------------------------------------------------------

    def test_tokenize(self):
        """... Tokenize is the text segmentation, i.e. to segment into tokens."""

        self.tok.set_lang("fra")
        splitfra = self.tok.tokenize(u("l'assiette l'abat-jour paris-brest et paris-marseille").split())
        self.assertEqual(splitfra, u("l' assiette l' abat-jour paris-brest et paris - marseille").split())

        self.assertEqual(u("ah a/b euh").split(), self.tok.normalize(u("ah a/b euh")))

        # sampa
        self.assertEqual([u('/l-e-f-o~-n/')], self.tok.normalize(u("/l-e-f-o~-n/")))

        # not sampa...
        self.assertEqual(u('le mot').split(), self.tok.normalize(u("/le mot/")))

    # -----------------------------------------------------------------------

    def test_num2letter(self):
        """... Integration of num2letter into the TextNormalizer."""

        num = sppasDictRepl(os.path.join(paths.resources, "num", "fra_num.repl"), nodump=True)
        repl = sppasDictRepl(os.path.join(paths.resources, "repl", "fra.repl"), nodump=True)
        self.tok.set_repl(repl)
        self.tok.set_num(num)
        self.tok.set_lang("fra")

        self.assertEqual([u("cent_vingt_trois")], self.tok.normalize(u("123")))

        self.assertEqual([u("un")], self.tok.normalize(u("1")))
        self.assertEqual([u("vingt_quatre")], self.tok.normalize(u("24")))
        self.assertEqual(u("un virgule vingt_quatre").split(), self.tok.normalize(u("1,24")))

        # self.tok.set_lang("deu")
        # with self.assertRaises(ValueError):
        #     self.tok.normalize(u("123"))

    # -----------------------------------------------------------------------

    def test_remove_punct(self):
        """... Remove data of an utterance if included in a dictionary."""

        self.tok.set_lang("fra")
        self.assertEqual(u("un deux").split(), self.tok.normalize(u("/un, deux!!!")))

    # -----------------------------------------------------------------------

    def test_stick(self):
        """... Token Segmenter on compound words."""

        t = sppasTokenSegmenter(self.tok.vocab)
        s = t.bind([u("123")])
        self.assertEqual(s, [u("123")])
        s = t.bind([u("au fur et à mesure")])
        self.assertEqual(s, [u("au_fur_et_à_mesure")])
        s = t.bind([u("rock'n roll")])   # not in lexicon
        self.assertEqual(s, [u("rock'n")])

    # -----------------------------------------------------------------------

    def test_sampa(self):
        """... X-SAMPA included into the ortho transcription."""

        repl = sppasDictRepl(os.path.join(paths.resources, "repl", "fra.repl"), nodump=True)
        self.tok.set_repl(repl)

        self.assertEqual([u("/lemot/")], self.tok.normalize(u("[le mot,/lemot/]"), []))
        self.assertEqual([u("le_mot")], self.tok.normalize(u("[le mot,/lemot/]"), ["std"]))
        self.assertEqual([u("/lemot/")], self.tok.normalize(u("[le mot,/lemot/]")))

        # minus is accepted in sampa transcription (it is the phonemes separator)
        self.assertEqual([u("/l-e-f-o~-n/")], self.tok.normalize(u(" /l-e-f-o~-n/ ")))
        self.assertEqual([u("/le~/")], self.tok.normalize(u(" /le~/ ")))

        # whitespace is not accepted in sampa transcription
        self.assertEqual(u("le mot").split(), self.tok.normalize(u(" /le mot/ ")))

    # -----------------------------------------------------------------------

    def test_code_switching(self):
        """... [TO DO] support of language switching."""

        dictdir = os.path.join(paths.resources, "vocab")
        vocabfra = os.path.join(dictdir, "fra.vocab")
        vocabcmn = os.path.join(dictdir, "cmn.vocab")

        wds = sppasVocabulary(vocabfra)
        wds.load_from_ascii(vocabcmn)
        self.assertEqual(len(wds), 456382)

        #self.tok.set_vocab(wds)
        #splitswitch = self.tok.tokenize(u'et il m\'a dit : "《干脆就把那部蒙人的闲法给废了拉倒！》RT @laoshipukong : 27日"')
        #self.assertEqual(splitswitch, u"et il m' a dit 干脆 就 把 那 部 蒙 人 的 闲 法 给 废 了 拉倒 rt @ laoshipukong 二十七 日")

    # -----------------------------------------------------------------------
    #
    # def test_acronyms(self):
    #
    #     self.tok.set_lang("fra")
    #     # todo

# ---------------------------------------------------------------------------


class TestTextNorm(unittest.TestCase):
    """Test the SPPAS integration of the TextNormalizer."""

    def test_samples(self):
        """... Compare the current result is the same as the existing one."""
        # Test the automatic annotation with its default parameters only.

        for samples_folder in os.listdir(paths.samples):
            if samples_folder.startswith("samples-") is False:
                continue

            # the place where are the existing results samples.
            expected_result_dir = os.path.join(paths.samples,
                                               "annotation-results",
                                               samples_folder)
            if os.path.exists(expected_result_dir) is False:
                continue

            # Create a TextNormalizer for the given set of samples
            lang = samples_folder[-3:]
            vocab = os.path.join(paths.resources, "vocab", lang+".vocab")
            tn = sppasTextNorm()
            tn.load_resources(vocab, lang=lang)
            tn.set_faked(True)
            tn.set_std(True)
            tn.set_custom(True)

            # Apply TextNormalization on each sample
            for filename in os.listdir(os.path.join(paths.samples, samples_folder)):
                if filename.endswith(".TextGrid") is False:
                    continue

                # Get the expected result
                expected_result_filename = os.path.join(expected_result_dir,
                                                        filename[:-9] + "-token.xra")
                if os.path.exists(expected_result_filename) is False:
                    continue

                try:
                    parser = sppasRW(expected_result_filename)
                    expected_result = parser.read()
                except AioEncodingError:
                    continue

                # Estimate the result and check if it's like expected.
                input_file = os.path.join(paths.samples, samples_folder, filename)
                result = tn.run([input_file])

                expected_tier_tokens = expected_result.find('Tokens')
                if expected_tier_tokens is not None:
                    self.compare_tiers(expected_tier_tokens, result.find('Tokens'))

                expected_tier_tokens = expected_result.find('TokensStd')
                if expected_tier_tokens is not None:
                    self.compare_tiers(expected_tier_tokens, result.find('TokensStd'))

                expected_tier_tokens = expected_result.find('TokensCustom')
                if expected_tier_tokens is not None:
                    self.compare_tiers(expected_tier_tokens, result.find('TokensCustom'))

    # -----------------------------------------------------------------------

    def compare_tiers(self, expected, result):
        self.assertEqual(len(expected), len(result))
        # compare annotations
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
