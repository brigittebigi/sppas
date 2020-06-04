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

    src.annotations.keyrules.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~

"""
from sppas.src.config import symbols
from sppas.src.config import separators
from sppas.src.utils.makeunicode import sppasUnicode

# ----------------------------------------------------------------------------


class SyllRules(object):
    """Manager of a set of rules for syllabification.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2018  Brigitte Bigi

    The rules we propose follow usual phonological statements for most of the
    corpus. A configuration file indicates phonemes, classes and rules.
    This file can be edited and modified to adapt the syllabification.

    The syllable configuration file is a simple ASCII text file that the user
    can change as needed.

    """

    BREAK_SYMBOL = "#"

    # -----------------------------------------------------------------------

    def __init__(self, filename=None):
        """Create a new SyllRules instance.

        :param filename: (str) Name of the file with the rules.

        """
        self.general = dict()    # list of general rules
        self.exception = dict()  # list of exception rules
        self.gap = dict()        # list of gap rules
        self.phonclass = dict()  # list of tuple (phoneme, classe)

        if filename is not None:
            self.load(filename)
        else:
            self.reset()

    # ------------------------------------------------------------------------

    def reset(self):
        """Reset the set of rules."""
        self.general = dict()  # list of general rules
        self.general["VV"] = 0
        self.general["VXV"] = 0
        self.general["VXXV"] = 1
        self.general["VXXXV"] = 1
        self.general["VXXXXV"] = 1
        self.general["VXXXXXV"] = 2
        self.general["VXXXXXV"] = 3
        self.general["VXXXXXXV"] = 3

        self.exception = dict()  # list of exception rules
        self.gap = dict()        # list of gap rules

        self.phonclass = dict()  # list of tuple (phoneme, class)
        for phone in symbols.all:
            self.phonclass[phone] = SyllRules.BREAK_SYMBOL

    # ------------------------------------------------------------------------

    def load(self, filename):
        """Load the rules from a file.

        :param filename: (str) Name of the file with the rules.

        """
        self.reset()

        with open(filename, "r") as f:
            lines = f.readlines()
            f.close()

        for line_nb, line in enumerate(lines, 1):
            sp = sppasUnicode(line)
            line = sp.to_strip()

            wds = line.split()
            if len(wds) == 3:
                if wds[0] == "PHONCLASS":
                    self.phonclass[wds[1]] = wds[2]

                elif wds[0] == "GENRULE":
                    self.general[wds[1]] = int(wds[2])

                elif wds[0] == "EXCRULE":
                    self.exception[wds[1]] = int(wds[2])

            if len(wds) == 7:
                if wds[0] == "OTHRULE":
                    s = " ".join(wds[1:6])
                    self.gap[s] = int(wds[6])

    # ------------------------------------------------------------------------

    def get_class(self, phoneme):
        """Return the class identifier of the phoneme.

        If the phoneme is unknown, the break symbol is returned.

        :param phoneme: (str) A phoneme
        :returns: class of the phoneme or break symbol

        """
        return self.phonclass.get(phoneme, SyllRules.BREAK_SYMBOL)

    # ------------------------------------------------------------------------

    def is_exception(self, rule):
        """Return True if the rule is an exception rule.

        :param rule: (str)

        """
        return rule in self.exception

    # ------------------------------------------------------------------------

    def get_boundary(self, phonemes):
        """Get the index of the syllable boundary (EXCRULES or GENRULES).

        Phonemes are separated with the symbol defined by separators.phonemes
        variable.

        :param phonemes: (str) Sequence of phonemes to syllabify
        :returns: (int) boundary index or -1 if phonemes don't match any rule.

        """
        sp = sppasUnicode(phonemes)
        phonemes = sp.to_strip()
        phon_list = phonemes.split(separators.phonemes)
        classes = ""
        for phon in phon_list:
            classes += self.get_class(phon)

        # search into exception
        if classes in self.exception:
            return self.exception[classes]

        # search into general
        for key, val in self.general.items():
            if len(key) == len(phon_list):
                return val

        return -1

    # ------------------------------------------------------------------------

    def get_class_rules_boundary(self, classes):
        """Get the index of the syllable boundary (EXCRULES or GENRULES).

        :param classes: (str) The class sequence to syllabify
        :returns: (int) boundary index or -1 if it does not match any rule.

        """
        # search into exception
        if classes in self.exception:
            return self.exception[classes]

        # search into general
        for key, val in self.general.items():
            if len(key) == len(classes):
                return val

        return 0

    # ------------------------------------------------------------------------

    def get_gap(self, phonemes):
        """Return the shift to apply (OTHRULES).

        :param phonemes: (str) Phonemes to syllabify
        :returns: (int) boundary shift

        """
        for gp in self.gap:
            if gp == phonemes:
                return self.gap[gp]

            # Search by replacing a phoneme by "ANY"
            if gp.find("ANY") > -1:
                r = gp.split()
                phons = phonemes.split()
                new_phonemes = ""
                if len(r) == len(phons):
                    # For each phoneme, replace the ANY
                    for ph in range(len(r)):
                        if r[ph] == "ANY":
                            new_phonemes += "ANY "
                        else:
                            new_phonemes += phons[ph] + " "
                    new_phonemes = new_phonemes.strip()

                if gp == new_phonemes:
                    return self.gap[gp]

        return 0
