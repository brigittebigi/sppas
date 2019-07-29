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

    src.annotations.searchtier.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""

from .annotationsexc import NoInputError

# ---------------------------------------------------------------------------


class sppasFindTier:
    """Search for tiers in a sppasTranscription.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2019  Brigitte Bigi

    """

    @staticmethod
    def transcription(trs):
        """Return the tier with orthographic transcription.

        :param trs: (sppasTranscription)
        :returns: (sppasTier)

        """
        # Search for a tier with exact name "transcription"
        tier = trs.find('transcription', case_sensitive=False)
        if tier is not None:
            return tier

        # Search for a tier containing "transcription" in its name
        for tier in trs:
            tier_name = tier.get_name().lower()
            if "transcription" in tier_name:
                return tier

        # Search for a tier containing either
        # "trans", "trs", "toe" or "ortho" in its name
        for tier in trs:
            tier_name = tier.get_name().lower()
            if "trans" in tier_name:
                return tier
            elif "trs" in tier_name:
                return tier
            elif "toe" in tier_name:
                return tier
            elif "ortho" in tier_name:
                return tier

        # Search for a tier containing "ipu" in its name
        for tier in trs:
            tier_name = tier.get_name().lower()
            if "ipu" in tier_name:
                return tier

        raise NoInputError

    # -----------------------------------------------------------------------

    @staticmethod
    def tokenization(trs, pattern=""):
        """Return the tier with tokenization.

        In case of EOT, several tiers with tokens are available.
        Priority is given to faked (i.e. without pattern).

        :param trs: (sppasTranscription)
        :param pattern: (str) Priority pattern
        :returns: (sppasTier)

        """
        # Search with the pattern
        if len(pattern) > 0:
            pattern = pattern.lower()
            for tier in trs:
                tier_name = tier.get_name().lower()
                if pattern in tier_name and "token" in tier_name:
                    return tier

        # Search with known patterns
        if len(trs) == 1:
            if "token" in trs[0].get_name().lower():
                return trs[0]

        else:
            tok_tier = None  # generic tier with tokens
            std_tier = None  # tier with standard tokens

            for tier in trs:
                tier_name = tier.get_name().lower()
                if "align" in tier_name:
                    continue
                if tier_name == "tokens":
                    return tier
                elif "std" in tier_name and "token" in tier_name:
                    std_tier = tier
                elif "token" in tier_name:
                    tok_tier = tier

            if std_tier is not None:
                return std_tier

            if tok_tier is not None:
                return tok_tier

        raise NoInputError

    # -----------------------------------------------------------------------

    @staticmethod
    def phonetization(trs):
        """Return the tier with phonetization.

        :param trs: (sppasTranscription)
        :returns: (sppasTier)

        """
        # Search for a tier with exact name "phones"
        tier = trs.find('phones', case_sensitive=False)
        if tier is not None:
            return tier

        # Search for a tier starting with "phon"
        for tier in trs:
            tier_name = tier.get_name().lower()
            if "align" in tier_name:
                continue
            if tier_name.startswith("phon") is True:
                return tier

        # Search for a tier containing "phon"
        for tier in trs:
            tier_name = tier.get_name().lower()
            if "align" in tier_name:
                continue
            if "phon" in tier_name:
                return tier

        raise NoInputError

    # -----------------------------------------------------------------------

    @staticmethod
    def aligned_phones(trs):
        """Return the tier with time-aligned phonemes.

        :param trs: (sppasTranscription)

        """
        for tier in trs:
            if "align" in tier.get_name().lower() and \
                    "phon" in tier.get_name().lower():
                return tier

        raise NoInputError

    # -----------------------------------------------------------------------

    @staticmethod
    def aligned_tokens(trs):
        """Return the tier with time-aligned tokens.

        :param trs: (sppasTranscription)

        """
        for tier in trs:
            if "align" in tier.get_name().lower() and \
                    "token" in tier.get_name().lower():
                return tier

        raise NoInputError

    # -----------------------------------------------------------------------

    @staticmethod
    def aligned_syllables(trs):
        """Return the tier with time-aligned syllables.

        :param trs: (sppasTranscription)

        """
        for tier in trs:
            if "align" in tier.get_name().lower() and \
                    "syll" in tier.get_name().lower():
                return tier

        # for backward compatibility:
        for tier in trs:
            if tier.get_name() == "Syllables":
                return tier

        raise NoInputError

    # -----------------------------------------------------------------------

    @staticmethod
    def aligned_lemmas(trs):
        """Return the tier with time-aligned lemmas.

        :param trs: (sppasTranscription)

        """
        for tier in trs:
            if "lemma" in tier.get_name().lower():
                return tier

        raise NoInputError

    # -----------------------------------------------------------------------

    @staticmethod
    def pitch_anchors(trs):
        """Return the tier with pitch anchors, like momel.

        :param trs: (sppasTranscription)
        :returns: (sppasTier)

        """
        for tier in trs:
            if "momel" in tier.get_name().lower():
                return tier

        for tier in trs:
            if "anchors" in tier.get_name().lower():
                return tier

        raise NoInputError
