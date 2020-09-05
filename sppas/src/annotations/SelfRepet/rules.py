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

    src.annotations.SelfRepet.keyrules.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    The set of rules to accept or reject a self-repetition.

"""
from sppas.src.resources.vocab import sppasVocabulary

# ----------------------------------------------------------------------------


class SelfRules(object):
    """Rules to select self-repetitions.

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
        """Create a SelfRules instance.

        :param stop_list: (sppasVocabulary or list) Un-relevant tokens.

        """
        self.__stoplist = sppasVocabulary()
        if stop_list is not None:
            if isinstance(stop_list, sppasVocabulary):
                self.__stoplist = stop_list
            else:
                for token in stop_list:
                    self.__stoplist.add(token)

    # -----------------------------------------------------------------------

    def is_relevant(self, idx, speaker):
        """Ask for the entry of a speaker to be relevant or not.

        An entry is considered relevant if:

            1. It is not a silence, a pause, a laugh, dummy or a noise;
            2. It is not in the stop-list.

        :param idx: (str) Index of the data to be checked
        :param speaker: (DataSpeaker) All the data
        :returns: (bool)

        """
        word = speaker.is_word(idx)
        not_stop_word = self.__stoplist.is_unk(speaker[idx])

        return word and not_stop_word

    # -----------------------------------------------------------------------

    def count_relevant_tokens(self, start, end, speaker):
        """Count the number of relevant words from start to end (included).

        :param start: (int) Index to start to count
        :param end: (int) Index to stop to count
        :param speaker: (DataSpeaker) All the data
        :returns: (int)

        """
        return len([True for i in range(start, end + 1)
                    if self.is_relevant(i, speaker)])

    # -----------------------------------------------------------------------

    def rule_one_token(self, current, speaker):
        """Check whether one token is a self-repetition or not.

        Rules are:

            - the token must be a word, and not in the stop-list;
            - the token must be repeated.

        :param current: (int) Index of the token to check
        :param speaker: (DataSpeaker) All the data
        :returns: (bool)

        """
        # is it a relevant token?
        is_relevant = self.is_relevant(current, speaker)
        if is_relevant is False:
            return False

        # is it a repeated word?
        next_word = speaker.get_next_word(current)
        is_repeated = speaker.is_word_repeated(current, next_word, speaker)
        if is_repeated == -1:
            return False

        return True

    # -----------------------------------------------------------------------

    def rule_syntagme(self, start, end, speaker):
        """Apply rule 1 to decide if selection is a repetition or not.

        Rule 1: The selection of tokens of speaker 1 must contain at least
        one relevant token for speaker 2.

        :param start: (int) Index to start the selection
        :param end: (int) Index to stop the selection
        :param speaker: (DataSpeaker) All the data
        :returns: (bool)

        """
        return self.count_relevant_tokens(start, end, speaker) > 0
