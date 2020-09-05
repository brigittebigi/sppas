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

    src.annotations.phonetize.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""

import re

from sppas.src.config import symbols
from sppas.src.config import separators
from sppas.src.config import annots
from sppas.src.utils.makeunicode import sppasUnicode, u
from sppas.src.resources import sppasMapping
from sppas.src.resources import sppasDictPron

from .phonunk import sppasPhonUnk
from .dagphon import sppasDAGPhonetizer

# ---------------------------------------------------------------------------

SIL = list(symbols.phone.keys())[list(symbols.phone.values()).index("silence")]

# ---------------------------------------------------------------------------


class sppasDictPhonetizer(object):
    """Dictionary-based automatic phonetization.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2018  Brigitte Bigi

    Grapheme-to-phoneme conversion is a complex task, for which a number of
    diverse solutions have been proposed. It is a structure prediction task;
    both the input and output are structured, consisting of sequences of
    letters and phonemes, respectively.

    This phonetization system is entirely designed to handle multiple
    languages and/or tasks with the same algorithms and the same tools.
    Only resources are language-specific, and the approach is based on the
    simplest resources as possible:
    this automatic annotation is using a dictionary-based approach.

    The dictionary can contain words with a set of pronunciations (the
    canonical one, and optionally some common reductions, etc).
    In this approach, it is then assumed that most of the words of the speech
    transcription and their phonetic variants are mentioned in
    the pronunciation dictionary. If a word is missing, our system is based
    on the idea that given enough examples it should be possible to predict
    the pronunciation of unseen words purely by analogy.

    """

    def __init__(self, pdict, maptable=None):
        """Create a sppasDictPhonetizer instance.

        :param pdict: (sppasDictPron) The pronunciation dictionary.
        :param maptable: (Mapping) A mapping table for phones.

        """
        self._pdict = None
        self._phonunk = None
        self._map_table = sppasMapping()
        self._dag_phon = sppasDAGPhonetizer()

        self.set_dict(pdict)
        self.set_maptable(maptable)

    # -----------------------------------------------------------------------

    def get_dict_filename(self):
        if self._pdict is None:
            return ""
        return self._pdict.get_filename()

    # -----------------------------------------------------------------------

    def set_dict(self, pron_dict):
        """Set the pronunciation dictionary.

        :param pron_dict: (sppasDictPron) The pronunciation dictionary.

        """
        if pron_dict is None:
            pron_dict = sppasDictPron()

        if isinstance(pron_dict, sppasDictPron) is False:
            raise TypeError('Expected a sppasDictPron instance.')

        self._pdict = pron_dict
        self._phonunk = sppasPhonUnk(self._pdict)

    # -----------------------------------------------------------------------

    def set_maptable(self, map_table):
        """Set the mapping table dictionary.

        :param map_table: (Mapping) The mapping table dictionary.

        """
        if map_table is not None:
            if isinstance(map_table, sppasMapping) is False:
                raise TypeError('Expected a Mapping instance.')
        else:
            map_table = sppasMapping()

        self._map_table = map_table
        self._map_table.set_keep_miss(False)

    # -----------------------------------------------------------------------

    def set_unk_variants(self, value):
        """Fix the maximum number of variants for unknown entries.

        :param value: (int) If v is set to 0, all variants will be returned.

        """
        self._dag_phon.set_variants(value)

    # -----------------------------------------------------------------------

    def get_phon_entry(self, entry):
        """Return the phonetization of an entry.

        Unknown entries are not automatically phonetized.
        This is a pure dictionary-based method.

        :param entry: (str) The entry to be phonetized.
        :returns: A string with the phonetization of the given entry or
        the unknown symbol.

        """
        entry = sppasUnicode(entry).to_strip()

        # Specific strings... for the italian transcription...
        # For the participation at the CLIPS-Evalita 2011 campaign.
        if entry.startswith(u("<")) is True and entry.endswith(u(">")) is True:
            entry = entry[1:-1]

        # No entry! Nothing to do.
        if len(entry) == 0:
            return ""

        # Specific strings used in the CID transcriptions...
        # CID is Corpus of Interactionnal Data, http://sldr.org/sldr000720
        if entry.startswith(u("gpf_")) is True:
            return SIL
        if entry.startswith(u("gpd_")) is True:
            return ""

        # Specific strings used in SPPAS IPU segmentation...
        if entry.startswith(u("ipu_")):
            return ""

        # Find entry in the dict as it is given
        _strphon = self._pdict.get_pron(entry)

        # OK, the entry is properly phonetized.
        if _strphon != self._pdict.get_unkstamp():
            return self._map_phonentry(_strphon)

        return self._pdict.get_unkstamp()

    # -----------------------------------------------------------------------

    def get_phon_tokens(self, tokens, phonunk=True):
        """Return the phonetization of a list of tokens, with the status.

        Unknown entries are automatically phonetized if `phonunk` is set
        to True.

        :param tokens: (list) The list of tokens to be phonetized.
        :param phonunk: (bool) Phonetize unknown words (or not).

        TODO: EOT is not fully supported.

        :returns: A list with the tuple (token, phon, status).

        """
        tab = list()

        for entry in tokens:
            entry = entry.strip()
            phon = self._pdict.get_unkstamp()
            status = annots.ok

            # Enriched Orthographic Transcription Convention:
            # entry can be already in SAMPA.
            if entry.startswith("/") is True and entry.endswith("/") is True:
                phon = entry.strip("/")
                # It must use X-SAMPA,
                # including minus character to separate phonemes.

            else:

                phon = self.get_phon_entry(entry)

                if phon == self._pdict.get_unkstamp():
                    status = annots.error

                    # A missing compound word?
                    if "-" in entry or "'" in entry or "_" in entry:
                        _tabpron = [self.get_phon_entry(w)
                                    for w in re.split("[-'_]", entry)]

                        # OK, finally the entry is in the dictionary?
                        if self._pdict.get_unkstamp() not in _tabpron:
                            # ATTENTION: each part can have variants!
                            # must be decomposed.
                            self._dag_phon.variants = 4
                            phon = sppasUnicode(
                                self._dag_phon.decompose(" ".join(_tabpron))).to_strip()
                            status = annots.warning

                    if phon == self._pdict.get_unkstamp() and phonunk is True:
                        try:
                            phon = self._phonunk.get_phon(entry)
                            status = annots.warning
                        except:
                            phon = self._pdict.get_unkstamp()
                            status = annots.error

            if len(phon) > 0:
                tab.append((entry, phon, status))

        return tab

    # -----------------------------------------------------------------------

    def phonetize(self, utterance, phonunk=True, delimiter=" "):
        """Return the phonetization of an utterance.

        :param utterance: (str) The utterance string to be phonetized.
        :param phonunk: (bool) Phonetize unknown words (or not).
        :param delimiter: (char) The character to be used to separate entries
        in the result and which was used in the given utterance.

        :returns: A string with the phonetization of the given utterance.

        """
        if len(delimiter) > 1:
            raise TypeError('Delimiter must be a character.')

        su = sppasUnicode(utterance)
        utt = su.to_strip()
        tab = self.get_phon_tokens(utt.split(delimiter), phonunk)
        tab_phon = [t[1] for t in tab]
        phonetization = delimiter.join(tab_phon)

        return phonetization.strip()

    # -----------------------------------------------------------------------
    # Private
    # -----------------------------------------------------------------------

    def _map_phonentry(self, phonentry):
        """Map phonemes of a phonetized entry.

        :param phonentry: (str) Phonetization of an entry.

        """
        if self._map_table.is_empty() is True:
            return phonentry

        tab = [self._map_variant(v)
               for v in phonentry.split(separators.variants)]

        return separators.variants.join(tab)

    # -----------------------------------------------------------------------

    def _map_variant(self, phonvariant):
        """Map phonemes of only one variant of a phonetized entry.

        :param phonvariant: (str) One phonetization variant of an entry.

        """
        phones = self._map_split_variant(phonvariant)
        subs = []
        # Single phonemes
        for p in phones:
            mapped = self._map_table.map_entry(p)
            if len(mapped) > 0:
                subs.append(p + separators.variants + mapped)
            else:
                subs.append(p)

        self._dag_phon.variants = 0
        phon = sppasUnicode(
            self._dag_phon.decompose(" ".join(subs))).to_strip()

        # Remove un-pronounced phonemes!!!
        # By convention, they are represented by an underscore in the
        # mapping table.
        tmp = []
        for p in phon.split(separators.variants):
            r = [x for x in p.split(separators.phonemes) if x != "_"]
            tmp.append(separators.phonemes.join(r))

        return separators.variants.join(set(tmp))

    # -----------------------------------------------------------------------

    def _map_split_variant(self, phon_variant):
        """Return a list of the longest phone sequences.

        :param phon_variant: (str) One phonetization variant of an entry.

        """
        phones = phon_variant.split(separators.phonemes)
        if len(phones) == 1:
            return phones

        tab = list()
        idx = 0
        maxidx = len(phones)

        while idx < maxidx:
            # Find the index of the longest phone sequence that can be mapped
            left_index = self.__longestlr(phones[idx:maxidx])
            # Append such a longest sequence in tab
            s = separators.phonemes
            tab.append(s.join(phones[idx:idx+left_index]))
            idx += left_index

        return tab

    # -----------------------------------------------------------------------

    def __longestlr(self, tabentry):
        """Select the longest map of an entry."""
        i = len(tabentry)
        while i > 0:
            # Find in the map table a substring from 0 to i
            entry = separators.phonemes.join(tabentry[:i])
            if self._map_table.is_key(entry):
                return i
            i -= 1

        # Did not find any map for this entry! Return the shortest.
        return 1
