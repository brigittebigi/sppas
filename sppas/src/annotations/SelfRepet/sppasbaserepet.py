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

    src.annotations.SelfRepet.sppasbaserepet.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""
import os

from sppas import IndexRangeException
from sppas import symbols
from sppas import sppasTier
from sppas import sppasLabel
from sppas import sppasTag
from sppas import sppasVocabulary
from sppas import sppasWordStrain
from sppas import sppasUnigram

from ..baseannot import sppasBaseAnnotation
from ..annotationsexc import AnnotationOptionError

# ---------------------------------------------------------------------------

SIL_ORTHO = list(symbols.ortho.keys())[list(symbols.ortho.values()).index("silence")]

# ---------------------------------------------------------------------------


class sppasBaseRepet(sppasBaseAnnotation):
    """SPPAS Automatic Any-Repetition Detection.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2018  Brigitte Bigi

    """

    def __init__(self, config, log=None):
        """Create a new sppasRepetition instance.

        Log is used for a better communication of the annotation process and its
        results. If None, logs are redirected to the default logging system.

        :param config: (str) Name of the JSON configuration file, without path.
        :param log: (sppasLog) Human-readable logs.

        """
        super(sppasBaseRepet, self).__init__(config, log)

        self.max_span = 8
        self.max_alpha = 4.

        # List of options to configure this automatic annotation
        self._options = dict()
        self._options['span'] = 3
        self._options['stopwords'] = True
        self._options['alpha'] = 0.5

        self._word_strain = sppasWordStrain()
        self._stop_words = sppasVocabulary()

    # -----------------------------------------------------------------------

    def fix_options(self, options):
        """Fix all options.

        :param options: list of sppasOption instances

        """
        for opt in options:

            key = opt.get_key()

            if "stopwords" == key:
                self.set_use_stopwords(opt.get_value())

            elif "span" == key:
                self.set_span(opt.get_value())

            elif "alpha" == key:
                self.set_alpha(opt.get_value())

            elif key in ("inputpattern", "outputpattern", "inputoptpattern"):
                self._options[key] = opt.get_value()

            else:
                raise AnnotationOptionError(key)

    # -----------------------------------------------------------------------

    def load_resources(self, lang_resources, lang=None):
        """Load a list of stop-words and replacements.

        Override the existing loaded lists...

        :param lang_resources: (str) File with extension '.stp' or '.lem' or nothing
        :param lang: (str)

        """
        self._stop_words = sppasVocabulary()
        self._word_strain = sppasWordStrain()
        fn, fe = os.path.splitext(lang_resources)

        try:
            stp = fn + '.stp'
            self._stop_words.load_from_ascii(stp)
            self.logfile.print_message(
                "The initial list contains {:d} stop-words"
                "".format(len(self._stop_words)), indent=0)

        except Exception as e:
            self._stop_words = sppasVocabulary()
            self.logfile.print_message(
                "No stop-words loaded: {:s}".format(str(e)), indent=1)

        try:
            repl = fn + ".lem"
            if os.path.exists(repl):
                self._word_strain.load(repl)
            self.logfile.print_message(
                "The replacement list contains {:d} tokens"
                "".format(len(self._word_strain)), indent=0)

        except Exception as e:
            self._word_strain = sppasWordStrain()
            self.logfile.print_message(
                "No replacement list loaded: {:s}"
                "".format(str(e)), indent=1)

    # -----------------------------------------------------------------------
    # Getters and Setters
    # -----------------------------------------------------------------------

    def set_use_stopwords(self, use_stopwords):
        """Fix the use_stopwords option.

        If use_stopwords is set to True, sppasRepetition() will add specific
        stopwords to the stopwords list (deducted from the input text).

        :param use_stopwords: (bool)

        """
        self._options['stopwords'] = bool(use_stopwords)

    # -----------------------------------------------------------------------

    def set_span(self, span):
        """Fix the span option.

        Span is the maximum number of IPUs to search for repetitions.
        A value of 1 means to search only in the current IPU.

        :param span: (int)

        """
        span = int(span)
        if 0 < span <= self.max_span:
            self._options['span'] = span
        else:
            raise IndexRangeException(span, 0, self.max_span)

    # -----------------------------------------------------------------------

    def set_alpha(self, alpha):
        """Fix the alpha option.

        Alpha is a coefficient to add specific stop-words in the list.

        :param alpha: (float)

        """
        alpha = float(alpha)
        if 0. < alpha < self.max_alpha:
            self._options['alpha'] = alpha
        else:
            raise IndexRangeException(alpha, 0, self.max_alpha)

    # -----------------------------------------------------------------------

    def fix_stop_list(self, tier=None):
        """Return the expected list of stop-words.

        It is either:

            - the current stop-list or,
            - this list + un-relevant tokens, estimated on the given tier.

        A token 'w' is relevant for the speaker if its probability is
        less than a threshold:

            | P(w) <= 1 / (alpha * V)

        where 'alpha' is an empirical coefficient and 'V' is the vocabulary
        size of the speaker.

        :param tier: (sppasTier) A tier with entries to be analyzed.
        :returns: (sppasVocabulary) List of stop-words

        """
        if self._options['stopwords'] is False:
            return sppasVocabulary()

        if tier is None or len(tier) < 5:
            return self._stop_words.copy()

        # Create the sppasUnigram and put data
        u = sppasUnigram()
        for a in tier:
            content = a.serialize_labels()
            if content not in symbols.all:
                u.add(content)

        # Estimate values for relevance
        _v = float(len(u))
        threshold = 1. / (self._options["alpha"] * _v)

        # Estimate if a token is relevant; if not: put it in the stop-list
        stop_list = self._stop_words.copy()
        for token in u.get_tokens():
            p_w = float(u.get_count(token)) / float(u.get_sum())
            if p_w > threshold:
                stop_list.add(token)
                self.logfile.print_message(
                    'Add in the stop-list: {:s}'.format(token), indent=2)

        return stop_list

    # -----------------------------------------------------------------------
    # Make tiers for the result
    # -----------------------------------------------------------------------

    def make_word_strain(self, tier):
        """Return a tier with modified tokens.

        :param tier: (sppasTier) Time-aligned tokens.

        """
        if len(self._word_strain) == 0:
            return tier

        self.logfile.print_message("Words strain enabled.", indent=1, status=2)
        lems_tier = sppasTier('TokenStrain')
        for ann in tier:
            token = ann.serialize_labels()
            lem = self._word_strain.get(token, token)
            lems_tier.create_annotation(
                ann.get_location().copy(),
                sppasLabel(sppasTag(lem))
            )
        return lems_tier

    # -----------------------------------------------------------------------

    def make_stop_words(self, tier):
        """Return a tier indicating if entries are stop-words.

        :param tier: (sppasTier) Time-aligned tokens.

        """
        stp_tier = sppasTier('StopWord')
        for ann in tier:
            token = ann.serialize_labels()
            if token not in symbols.all:
                stp = self._stop_words.is_in(token)
                stp_tier.create_annotation(
                    ann.get_location().copy(),
                    sppasLabel(sppasTag(stp, tag_type="bool"))
                )
        return stp_tier
