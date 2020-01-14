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

    src.annotations.Repet.detectrepet.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""
from .datastructs import DataRepetition
from .rules import SelfRules

# ----------------------------------------------------------------------------


class SelfRepetition(DataRepetition):
    """Self-Repetition automatic detection.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2018  Brigitte Bigi

    Search for the sources, then find where are the echos.

    """

    def __init__(self, stop_list=None):
        """Create a new SelfRepetitions instance.

        :param stop_list: (StopWords) List of un-relevant tokens.

        """
        super(SelfRepetition, self).__init__()
        self.__rules = SelfRules(stop_list)

    # -----------------------------------------------------------------------
    # Detect sources
    # -----------------------------------------------------------------------

    def detect(self, speaker, limit=10):
        """Search for the first self-repetition in tokens.

        :param speaker: (DataSpeaker) All the data of speaker
        :param limit: (int) Go no longer than 'limit' entries in speaker data

        """
        self.reset()

        current_spk = 0
        next_spk = self.get_longest(current_spk, speaker)

        # Stop for searching if end of the data or self-repet found
        while current_spk < len(speaker) and current_spk < limit and \
                self.get_source() is None:

            if next_spk == -1:
                current_spk += 1
            else:
                current_spk = self.select(current_spk, next_spk, speaker)

            next_spk = SelfRepetition.get_longest(current_spk, speaker)

    # -----------------------------------------------------------------------

    @staticmethod
    def get_longest(current, speaker):
        """Return the index of the last token of the longest repeated string.

        :param current: (int) Current index in entries of speaker data
        :param speaker: (DataSpeaker) All the data of speaker
        :returns: (int) Index or -1

        """
        last_token = -1
        # Get the longest string
        for current_token in range(current, len(speaker)):

            next_word = speaker.get_next_word(current_token)
            repet_idx = speaker.is_word_repeated(current_token,
                                                 next_word, speaker)
            if repet_idx > -1:
                if repet_idx == current_token:
                    return current_token
                last_token = current_token
            else:
                break

        return last_token

    # -----------------------------------------------------------------------

    def select(self, start, end, speaker):
        """Append (or not) a self-repetition.

        :param start: (int) start index of the entry of the source (speaker)
        :param end: (int) end index of the entry of the source (speaker)
        :param speaker: (DataSpeaker) Entries of speaker

        """
        source_len = end - start

        if source_len == 0:
            keep_me = self.__rules.rule_one_token(start, speaker)
            if keep_me is True:
                self.set_source(start, start)
                self.find_echos(start, start, speaker)
            current = start + 1

        else:
            keep_me = self.__rules.rule_syntagme(start, end, speaker)
            if keep_me is True:
                self.set_source(start, end)
                self.find_echos(start, end, speaker)
            current = end + 1

        return current

    # -----------------------------------------------------------------------
    # Search for echos (for a given source)
    # -----------------------------------------------------------------------

    def find_echos(self, start, end, speaker):
        """Find all echos of a source.

        :param start: (int) start index of the entry of the source (speaker)
        :param end: (int) end index of the entry of the source (speaker)
        :param speaker: (DataSpeaker) All data of speaker
        :returns: DataRepetition()

        """
        # Find all repeated tokens of each token of the source
        repeats = list()

        ridx = 0
        i = start
        while i <= end:
            repeats.append(list())
            idx2 = speaker.is_word_repeated(i, end+1, speaker)

            while idx2 != -1:
                repeats[ridx].append(idx2)
                idx2 = speaker.is_word_repeated(i, idx2+1, speaker)
            i += 1
            ridx += 1

        # Filter the repetitions (try to get the longest sequence)
        if len(repeats) == 1:
            self.add_echo(repeats[0][0], repeats[0][0])
        else:
            i = 0
            while i < len(repeats):
                repeated = SelfRepetition.__get_longest_repeated(i, repeats)
                self.add_echo(repeated[0], repeated[-1])
                i += len(repeated)

    # -----------------------------------------------------------------------

    @staticmethod
    def __get_longest_repeated(start, repeats):
        """Select the longest echo from start position in repeats."""
        path_repeats = []
        for i in range(len(repeats[start])):
            path_repeats.append([])
            path_repeats[i].append(repeats[start][i])

            for j in range(start+1, len(repeats)):
                prec_value = path_repeats[-1][-1]
                v = 0
                if prec_value not in repeats[j]:
                    if (prec_value+1) not in repeats[j]:
                        if (prec_value+2) not in repeats[j]:
                            if (prec_value-1) not in repeats[j]:
                                break
                            else:
                                v = repeats[j].index(prec_value-1)
                        else:
                            v = repeats[j].index(prec_value+2)
                    else:
                        v = repeats[j].index(prec_value+1)
                else:
                    v = repeats[j].index(prec_value)
                path_repeats[i].append(repeats[j][v])

        # return the (first of the) longest path:
        return sorted(max(path_repeats, key=lambda x: len(x)))
