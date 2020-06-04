#!/usr/bin/env python
# -*- coding: utf8 -*-

import unittest
import os.path
import math
import shutil

from sppas.src.config import symbols
from sppas.src.models.slm.ngramsmodel import START_SENT_SYMBOL, END_SENT_SYMBOL
from sppas.src.models.slm.ngramsmodel import sppasNgramCounter
from sppas.src.models.slm.ngramsmodel import sppasNgramsModel
from sppas.src.models.slm.statlangmodel import sppasSLM
from sppas.src.models.slm.arpaio import sppasArpaIO
from sppas.src.resources.vocab import sppasVocabulary
from sppas.src.utils.compare import sppasCompare
from sppas.src.wkps.fileutils import sppasFileUtils

from ..modelsexc import NgramOrderValueError
from ..modelsexc import NgramCountValueError
from ..modelsexc import NgramMethodNameError
from ..modelsexc import ModelsDataTypeError

# ---------------------------------------------------------------------------

TEMP = sppasFileUtils().set_random()

# ---------------------------------------------------------------------------


class TestNgramCounter(unittest.TestCase):

    def setUp(self):
        if os.path.exists(TEMP) is False:
            os.mkdir(TEMP)
        self.corpusfile = os.path.join(TEMP, "corpus.txt")
        self.sent1 = "a a b a c a b b a a b"
        self.sent2 = "a a d c a b b a a b"
        self.sent3 = "a c a b d c d b a a b"
        f = open(self.corpusfile, "w")
        f.write(self.sent1+"\n")
        f.write(self.sent2+"\n")
        f.write(self.sent3+"\n")
        f.close()

    def tearDown(self):
        shutil.rmtree(TEMP)

    def testInit(self):
        with self.assertRaises(NgramOrderValueError):
            m = sppasNgramCounter(0)
            m = sppasNgramCounter(100)

    def testAppendSentence1(self):
        ngramcounter = sppasNgramCounter()  # default is unigram
        ngramcounter.append_sentence(self.sent1)
        self.assertEqual(ngramcounter.get_count('a'), 6)
        self.assertEqual(ngramcounter.get_count('b'), 4)
        self.assertEqual(ngramcounter.get_count('c'), 1)
        self.assertEqual(ngramcounter.get_count('d'), 0)
        self.assertEqual(ngramcounter.get_count(START_SENT_SYMBOL), 0)
        self.assertEqual(ngramcounter.get_count(END_SENT_SYMBOL), 1)
        self.assertEqual(ngramcounter.get_ncount(), 12)
        ngramcounter.append_sentence(self.sent2)
        ngramcounter.append_sentence(self.sent3)
        self.assertEqual(ngramcounter.get_count('a'), 15)
        self.assertEqual(ngramcounter.get_count('b'), 10)
        self.assertEqual(ngramcounter.get_count('c'), 4)
        self.assertEqual(ngramcounter.get_count('d'), 3)
        self.assertEqual(ngramcounter.get_count(START_SENT_SYMBOL), 0)
        self.assertEqual(ngramcounter.get_count(END_SENT_SYMBOL), 3)

    def testAppendSentence2(self):
        ngramcounter = sppasNgramCounter(2)  # bigram
        ngramcounter.append_sentence(self.sent1)
        self.assertEqual(ngramcounter.get_count('a b'), 3)
        self.assertEqual(ngramcounter.get_count('b a'), 2)
        self.assertEqual(ngramcounter.get_count('a c'), 1)
        self.assertEqual(ngramcounter.get_count('a d'), 0)
        self.assertEqual(ngramcounter.get_count(START_SENT_SYMBOL+' a'), 1)
        self.assertEqual(ngramcounter.get_count(START_SENT_SYMBOL+' b'), 0)
        self.assertEqual(ngramcounter.get_count('a '+END_SENT_SYMBOL), 0)
        self.assertEqual(ngramcounter.get_count('b '+END_SENT_SYMBOL), 1)
        ngramcounter.append_sentence(self.sent2)
        ngramcounter.append_sentence(self.sent3)
        self.assertEqual(ngramcounter.get_count('a b'), 7)
        self.assertEqual(ngramcounter.get_count('b a'), 4)
        self.assertEqual(ngramcounter.get_count(START_SENT_SYMBOL+' a'), 3)
        self.assertEqual(ngramcounter.get_count('b '+END_SENT_SYMBOL), 3)

    def testCount1(self):
        ngramcounter = sppasNgramCounter()  # default is unigram
        ngramcounter.count(self.corpusfile)
        self.assertEqual(ngramcounter.get_count('a'), 15)
        self.assertEqual(ngramcounter.get_count('b'), 10)
        self.assertEqual(ngramcounter.get_count('c'), 4)
        self.assertEqual(ngramcounter.get_count('d'), 3)
        self.assertEqual(ngramcounter.get_count(START_SENT_SYMBOL), 0)
        self.assertEqual(ngramcounter.get_count(END_SENT_SYMBOL), 3)
        ngramcounter = sppasNgramCounter(1)
        ngramcounter.count(self.corpusfile, self.corpusfile)
        self.assertEqual(ngramcounter.get_count('a'), 30)
        self.assertEqual(ngramcounter.get_count('b'), 20)
        self.assertEqual(ngramcounter.get_count('c'), 8)
        self.assertEqual(ngramcounter.get_count('d'), 6)
        self.assertEqual(ngramcounter.get_count(START_SENT_SYMBOL), 0)
        self.assertEqual(ngramcounter.get_count(END_SENT_SYMBOL), 6)

    def testCount2(self):
        ngramcounter = sppasNgramCounter(2)
        ngramcounter.count(self.corpusfile)
        self.assertEqual(ngramcounter.get_count('a b'), 7)
        self.assertEqual(ngramcounter.get_count('b a'), 4)
        self.assertEqual(ngramcounter.get_count(START_SENT_SYMBOL+' a'), 3)
        self.assertEqual(ngramcounter.get_count('b '+END_SENT_SYMBOL), 3)

    def testShave(self):
        ngramcounter = sppasNgramCounter(1)
        ngramcounter.count(self.corpusfile)
        ngramcounter.shave(4)
        self.assertEqual(ngramcounter.get_count('a'), 15)
        self.assertEqual(ngramcounter.get_count('b'), 10)
        self.assertEqual(ngramcounter.get_count('c'), 4)
        self.assertEqual(ngramcounter.get_count('d'), 0)
        self.assertEqual(ngramcounter.get_count(START_SENT_SYMBOL), 0)
        self.assertEqual(ngramcounter.get_count(END_SENT_SYMBOL), 3)

    def testVocab(self):
        wds = sppasVocabulary()
        wds.add("a")
        wds.add("b")
        wds.add("c")
        ngramcounter = sppasNgramCounter(1, wds)
        ngramcounter.count(self.corpusfile)

        self.assertEqual(ngramcounter.get_count('a'), 15)
        self.assertEqual(ngramcounter.get_count('b'), 10)
        self.assertEqual(ngramcounter.get_count('c'), 4)
        self.assertEqual(ngramcounter.get_count('d'), 0)
        self.assertEqual(ngramcounter.get_count(symbols.unk), 3)
        self.assertEqual(ngramcounter.get_count(START_SENT_SYMBOL), 0)
        self.assertEqual(ngramcounter.get_count(END_SENT_SYMBOL), 3)

# ---------------------------------------------------------------------------


class TestNgramsModel(unittest.TestCase):

    def setUp(self):
        if os.path.exists(TEMP) is False:
            os.mkdir(TEMP)
        self.corpusfile = os.path.join(TEMP, "corpus.txt")
        self.sent1 = "a a b a c a b b a a b"
        self.sent2 = "a a d c a b b a a b"
        self.sent3 = "a c a b d c d b a a b"
        f = open(self.corpusfile, "w")
        f.write(self.sent1+"\n")
        f.write(self.sent2+"\n")
        f.write(self.sent3+"\n")
        f.close()

    def tearDown(self):
        shutil.rmtree(TEMP)

    def testInit(self):
        with self.assertRaises(NgramOrderValueError):
            m = sppasNgramsModel(0)
            m = sppasNgramsModel(100)
        m = sppasNgramsModel(1)
        with self.assertRaises(NgramCountValueError):
            m.set_min_count(0)
            m.set_min_count("a")
        with self.assertRaises(NgramMethodNameError):
            p = m.probabilities(method="toto")

    def testCount(self):
        model = sppasNgramsModel(2)
        model.count(self.corpusfile)
        self.assertEqual(len(model._ngramcounts), 2)
        ngramcounter = model._ngramcounts[0]
        self.assertEqual(ngramcounter.get_count('a'), 15)
        self.assertEqual(ngramcounter.get_count('b'), 10)
        self.assertEqual(ngramcounter.get_count('c'), 4)
        self.assertEqual(ngramcounter.get_count('d'), 3)
        self.assertEqual(ngramcounter.get_count(START_SENT_SYMBOL), 0)
        self.assertEqual(ngramcounter.get_count(END_SENT_SYMBOL), 3)
        ngramcounter = model._ngramcounts[1]
        self.assertEqual(ngramcounter.get_count('a b'), 7)
        self.assertEqual(ngramcounter.get_count('b a'), 4)
        self.assertEqual(ngramcounter.get_count('d b'), 1)
        self.assertEqual(ngramcounter.get_count('d c'), 2)
        self.assertEqual(ngramcounter.get_count(START_SENT_SYMBOL+' a'), 3)
        self.assertEqual(ngramcounter.get_count('b ' + END_SENT_SYMBOL), 3)

    def testShave(self):
        model = sppasNgramsModel(2)
        model.count(self.corpusfile)
        self.assertEqual(len(model._ngramcounts), 2)
        model.set_min_count(2)
        ngramcounter = model._ngramcounts[0]
        self.assertEqual(ngramcounter.get_count('a'), 15)
        self.assertEqual(ngramcounter.get_count('b'), 10)
        self.assertEqual(ngramcounter.get_count('c'), 4)
        self.assertEqual(ngramcounter.get_count('d'), 3)
        self.assertEqual(ngramcounter.get_count(START_SENT_SYMBOL), 0)
        self.assertEqual(ngramcounter.get_count(END_SENT_SYMBOL), 3)
        ngramcounter = model._ngramcounts[1]
        self.assertEqual(ngramcounter.get_count('a b'), 7)
        self.assertEqual(ngramcounter.get_count('b a'), 4)
        self.assertEqual(ngramcounter.get_count('d b'), 0)
        self.assertEqual(ngramcounter.get_count('d c'), 2)
        self.assertEqual(ngramcounter.get_count(START_SENT_SYMBOL+' a'), 3)
        self.assertEqual(ngramcounter.get_count('b '+END_SENT_SYMBOL), 3)

    def testRawProbabilities(self):
        model = sppasNgramsModel(2)
        model.count(self.corpusfile)
        probas = model.probabilities(method="raw")
        self.assertEqual(len(probas), 2)

        unigram = probas[0]
        for token, value, bo in unigram:
            if token == "a":
                self.assertEqual(value, 15)
            if token == 'b':
                self.assertEqual(value, 10)
            if token == 'c':
                self.assertEqual(value, 4)
            if token == 'd':
                self.assertEqual(value, 3)
            if token == START_SENT_SYMBOL:
                self.assertEqual(value, 0)
            if token == END_SENT_SYMBOL:
                self.assertEqual(value, 3)

        bigram = probas[1]
        for token, value, bo in bigram:
            if token == "a b":
                self.assertEqual(value, 7)
            if token == "b a":
                self.assertEqual(value, 4)
            if token == START_SENT_SYMBOL+' a':
                self.assertEqual(value, 3)
            if token == 'b '+END_SENT_SYMBOL:
                self.assertEqual(value, 3)

        probas = model.probabilities(method="lograw")
        self.assertEqual(len(probas), 2)

        unigram = probas[0]
        for token, value, bo in unigram:
            if token == "a":
                self.assertEqual(value, math.log(15, 10))
            if token == 'b':
                self.assertEqual(value, math.log(10, 10))
            if token == 'c':
                self.assertEqual(value, math.log(4, 10))
            if token == 'd':
                self.assertEqual(value, math.log(3, 10))
            if token == START_SENT_SYMBOL:
                self.assertEqual(value, -99)
            if token == END_SENT_SYMBOL:
                self.assertEqual(value, math.log(3, 10))

        bigram = probas[1]
        for token, value, bo in bigram:
            if token == "a b":
                self.assertEqual(value, math.log(7, 10))
            if token == "b a":
                self.assertEqual(value, math.log(4, 10))
            if token == START_SENT_SYMBOL+' a':
                self.assertEqual(value, math.log(3, 10))
            if token == 'b '+END_SENT_SYMBOL:
                self.assertEqual(value, math.log(3, 10))

    def testMaximumLikelihoodProbabilities(self):
        model = sppasNgramsModel(3)
        model.count(self.corpusfile)
        probas = model.probabilities(method="ml")
        self.assertEqual(len(probas), 3)

        unigram = probas[0]
        for token, value, bo in unigram:
            if token == "a":
                self.assertEqual(round(value, 6), 0.428571)
            if token == "b":
                self.assertEqual(round(value, 6), 0.285714)
            if token == "c":
                self.assertEqual(round(value, 6), 0.114286)
            if token == "d":
                self.assertEqual(round(value, 6), 0.085714)
            if token == START_SENT_SYMBOL:
                self.assertEqual(round(value, 6), 0.)
            if token == END_SENT_SYMBOL:
                self.assertEqual(round(value, 6), 0.085714)

        bigram = probas[1]
        for token, value, bo in bigram:
            if token == "a b":
                self.assertEqual(round(value, 6), 0.466667)
            if token == "b a":
                self.assertEqual(round(value, 6), 0.400000)

        trigram = probas[2]
        for token, value, bo in trigram:
            if token == "a b a":
                self.assertEqual(round(value, 6), 0.142857)
            if token == START_SENT_SYMBOL+"a a":
                self.assertEqual(round(value, 6), 0.500000)
            if token == "a b"+END_SENT_SYMBOL:
                self.assertEqual(round(value, 6), 0.428571)

        probas = model.probabilities(method="logml")
        self.assertEqual(len(probas), 3)

        unigram = probas[0]
        for token, value, bo in unigram:
            if token == "a":
                self.assertEqual(round(value, 6), round(math.log(0.42857143, 10), 6))
            if token == "b":
                self.assertEqual(round(value, 6), round(math.log(0.28571429, 10), 6))
            if token == "c":
                self.assertEqual(round(value, 6), round(math.log(0.11428571, 10), 6))
            if token == "d":
                self.assertEqual(round(value, 6), round(math.log(0.08571429, 10), 6))
            if token == START_SENT_SYMBOL:
                self.assertEqual(round(value, 6), -99.000000)
            if token == END_SENT_SYMBOL:
                self.assertEqual(round(value, 6), round(math.log(0.08571429, 10), 6))

        bigram = probas[1]
        for token, value, bo in bigram:
            if token == "a b":
                self.assertEqual(round(value, 6), round(math.log(0.466667, 10), 6))
            if token == "b a":
                self.assertEqual(round(value, 6), round(math.log(0.400000, 10), 6))

        trigram = probas[2]
        for token, value, bo in trigram:
            if token == "a b a":
                self.assertEqual(round(value, 6), round(math.log(0.142857, 10), 6))
            if token == START_SENT_SYMBOL+"a a":
                self.assertEqual(round(value, 6), round(math.log(0.500000, 10), 6))
            if token == "a b"+END_SENT_SYMBOL:
                self.assertEqual(round(value, 6), round(math.log(0.428571, 10), 6))

# ---------------------------------------------------------------------------


class TestSLM(unittest.TestCase):

    def setUp(self):
        if os.path.exists(TEMP) is False:
            os.mkdir(TEMP)
        self.corpusfile = os.path.join(TEMP, "corpus.txt")
        self.sent1 = "a a b a c a b b a a b"
        self.sent2 = "a a d c a b b a a b"
        self.sent3 = "a c a b d c d b a a b"
        f = open(self.corpusfile, "w")
        f.write(self.sent1+"\n")
        f.write(self.sent2+"\n")
        f.write(self.sent3+"\n")
        f.close()

    def tearDown(self):
        shutil.rmtree(TEMP)

    def testARPA(self):
        arpaio = sppasArpaIO()
        with self.assertRaises(ModelsDataTypeError):
            arpaio.set("toto")
            arpaio.set([])
            arpaio.set([[], 0])

        fn1 = os.path.join(TEMP, "model1.arpa")
        fn2 = os.path.join(TEMP, "model2.arpa")
        model = sppasNgramsModel(3)
        model.count(self.corpusfile)
        probas = model.probabilities("logml")
        arpaio.set(probas)
        arpaio.save(fn1)

        slm1 = sppasSLM()
        slm1.load_from_arpa(fn1)
        slm1.save_as_arpa(fn2)

        slm2 = sppasSLM()
        slm2.load_from_arpa(fn2)

        m1 = slm1.model
        m2 = slm2.model
        sp = sppasCompare()
        self.assertTrue(sp.equals(m1, m2))
