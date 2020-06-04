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

    src.annotations.OtherRepet.keyrules.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    The set of rules to accept or reject a self-repetition.

"""
from ..SelfRepet.rules import SelfRules

# ----------------------------------------------------------------------------


class OtherRules(SelfRules):
    """Rules to select other-repetitions.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2018  Brigitte Bigi

    Proposed rules deal with the number of words, the word frequencies and
    distinguishes if the repetition is strict or not. The following rules are
    proposed for other-repetitions:

        - Rule 1: A source is accepted if it contains one or more relevant
        token. Relevance depends on the speaker producing the echo;
        - Rule 2: A source which contains at least K tokens is accepted
        if the repetition is strict.

    Rule number 1 need to fix a clear definition of the relevance of a
    token. Un-relevant tokens are then stored in a stop-list.
    The stop-list also should contain very frequent tokens in the given
    language like adjectives, pronouns, etc.

    """

    def __init__(self, stop_list=None):
        """Create an OtherRules instance.

        :param stop_list: (sppasVocabulary or list) Un-relevant tokens.

        """
        super(OtherRules, self).__init__(stop_list)

    # -----------------------------------------------------------------------

    def rule_strict(self, start, end, speaker1, speaker2):
        """Apply rule 2 to decide if selection is a repetition or not.

        Rule 2: The selection is a repetition if it respects at least one of
        the following criteria:

            - selection contains at least 3 tokens;
            - the repetition is strict (the source is strictly included
            into the echo).

        :param start: (int) Index to start the selection
        :param end: (int) Index to stop the selection
        :param speaker1: (DataSpeaker) All the data
        :param speaker2: (DataSpeaker) All the data
        :returns: (bool)

        """
        # At least 3 tokens are acceptable
        if (end-start) < 2:
            return False

        # Test if the echo is strict

        # create a string with the tokens of the source speaker
        #source = ""
        #for i in range(start, end+1):
        #    source = source + " " + speaker1.get_entry(i)
        source = " ".join(speaker1[i] for i in range(start, end+1))

        # create a string with the tokens of the echoing spk
        #echo = ""
        #for i in range(len(speaker2)):
        #    echo = echo + " " + speaker2.get_entry(i)
        echo = " ".join(speaker2[i] for i in range(len(speaker2)))

        return source in echo
