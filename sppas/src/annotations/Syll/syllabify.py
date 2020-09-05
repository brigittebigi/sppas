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

    src.annotations.lpckeys.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""
from sppas.src.config import separators
from .rules import SyllRules

# ----------------------------------------------------------------------------


class Syllabifier(object):
    """Syllabification of a sequence of phonemes.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2018  Brigitte Bigi

    """

    def __init__(self, rules_filename=None):
        """Create a new Syllabifier instance.

        Load rules from a text file, depending on the language and phonemes
        encoding. See documentation for details about this file.

        :param rules_filename: (str) Name of the file with the list of rules.

        """
        self.rules = SyllRules(rules_filename)

    # -----------------------------------------------------------------------

    def annotate(self, phonemes):
        """Return the syllable boundaries of a sequence of phonemes.

        >>> phonemes = ['a', 'p', 's', 'k', 'm', 'w', 'a']
        >>> Syllabifier("fra-config-file").annotate(phonemes)
        >>> [(0, 3), (4, 6)]

        :param phonemes: (list)
        :returns: list of tuples (begin index, end index)

        """
        # Convert a list of phonemes into a list of classes.
        classes = [self.rules.get_class(p) for p in phonemes]
        syllables = list()

        # Find the first vowel = first nucleus
        nucleus = Syllabifier._fix_nucleus(classes, 0)
        if nucleus == -1:
            return list()

        end_syll = -1
        while nucleus != -1:

            start_syll = self._fix_start_syll(classes, end_syll, nucleus)
            next_nucleus = Syllabifier._find_next_vowel(classes, nucleus+1)
            next_break = Syllabifier._find_next_break(classes, nucleus)

            if next_break != -1 and \
                    (next_break < next_nucleus or next_nucleus == -1):
                # no rule to apply if the next event is a break.
                # ie next break occurs before next nucleus or
                # no next nucleus
                syllables.append((start_syll, next_break-1))

            elif next_break == -1 and next_nucleus == -1:
                # no rule to apply if current nucleus concerns
                # the last syllable
                end_syll = len(phonemes) - 1
                syllables.append((start_syll, end_syll))

            else:
                # apply the exception rule or the general one
                end_syll = self._apply_class_rules(classes,
                                                   nucleus,
                                                   next_nucleus)
                # apply the specific rules on phonemes to shift the end
                end_syll = self._apply_phon_rules(phonemes,
                                                  end_syll,
                                                  nucleus,
                                                  next_nucleus)
                syllables.append((start_syll, end_syll))

            nucleus = next_nucleus

        return syllables

    # -----------------------------------------------------------------------

    @staticmethod
    def phonetize_syllables(phonemes, syllables):
        """Return the phonetized sequence of syllables.

        >>> phonemes = ['a', 'p', 's', 'k', 'm', 'w', 'a']
        >>> syllables = Syllabifier("fra-config-file").annotate(phonemes)
        >>> Syllabifier.phonetize_syllables(phonemes, syllables)
        >>> "a-p-s-k.m-w-a"

        :param phonemes: (list) List of phonemes
        :param syllables: list of tuples (begin index, end index)
        :returns: (str) String representing the syllables segmentation

        """
        str_syll = list()
        for (begin, end) in syllables:
            str_syll.append(separators.phonemes.join(phonemes[begin:end+1]))

        return separators.syllables.join(str_syll)

    # -----------------------------------------------------------------------

    def classes_phonetized(self, phonetized_syllable):
        """Return the classes of a phonetized syllable.

        >>> syllable = "a-p-s-k"
        >>> syllabifier.classes_phonetized(syllable)
        >>> "V-P-F-P"

        """
        c = list()
        for p in phonetized_syllable.split(separators.phonemes):
            c.append(self.rules.get_class(p))

        return separators.phonemes.join(c)

    # -----------------------------------------------------------------------
    # Private
    # -----------------------------------------------------------------------

    @staticmethod
    def _fix_nucleus(classes, from_index):
        """Search for the next nucleus of a syllable."""
        next_nucleus = -1
        next_break = -1
        while next_break <= next_nucleus:
            next_nucleus = Syllabifier._find_next_vowel(classes, from_index)
            next_break = Syllabifier._find_next_break(classes, from_index)
            if next_nucleus == -1:
                return -1
            if next_break == -1:
                return next_nucleus
            from_index = next_nucleus
        return next_nucleus

    # -----------------------------------------------------------------------

    @staticmethod
    def _fix_start_syll(classes, end_previous, nucleus):
        """Search for the index of the first phoneme of the syllable."""
        # should not occur
        if end_previous == nucleus:
            return nucleus

        for i in reversed(range(end_previous, nucleus)):
            if i == -1:
                return 0
            if classes[i] in ("V", "W", SyllRules.BREAK_SYMBOL):
                return i+1

        # no break nor vowel between the end of the previous syllable
        # and the current nucleus
        return end_previous+1

    # -----------------------------------------------------------------------

    @staticmethod
    def _find_next_vowel(classes, from_index):
        """Find the index of the next vowel.

        -1 is returned if no longer vowel is existing.

        :param classes: (list) List of phoneme classes
        :param from_index: (int) the position where the search will begin
        (this from index is included in).
        :returns: the position of the next vowel or -1

        """
        for i in range(from_index, len(classes)):
            if classes[i] in ("V", "W"):
                return i
        return -1

    # -----------------------------------------------------------------------

    @staticmethod
    def _find_next_break(classes, from_index):
        """Find the index of the next break.

        -1 is returned if no longer break is existing.

        :param classes: (list) List of phoneme classes
        :param from_index: (int) the position where the search will begin
        :returns: the position of the next break or -1

        """
        for i in range(from_index, len(classes)):
            if classes[i] == SyllRules.BREAK_SYMBOL:
                return i
        return -1

    # -----------------------------------------------------------------------

    def _apply_class_rules(self, classes, v1, v2):
        """Apply the syllabification rules between v1 and v2."""
        sequence = "".join(classes[v1:v2+1])
        return v1 + self.rules.get_class_rules_boundary(sequence)

    # -----------------------------------------------------------------------

    def _apply_phon_rules(self, phonemes, end_syll, v1, v2):
        """Apply the specific phoneme-based syllabification rules.

        Applied between v1 and v2.

        """
        _str = ""
        nb = v2-v1
        if nb > 1:
            # specific rules are sequences of 5 consonants max
            if nb == 5:
                _str = "V "
            if nb < 5:
                _str = "ANY "*(5-nb) + "V "
            for i in range(1, nb):
                _str = _str + phonemes[v1+i] + " "
        _str = _str.strip()

        if len(_str) > 0:
            d = self.rules.get_gap(_str)
            if d != 0:
                # check validity before assigning...
                new_end = end_syll + d
                if v2 >= new_end >= v1:
                    end_syll = new_end

        return end_syll
