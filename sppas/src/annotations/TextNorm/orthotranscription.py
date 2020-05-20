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

    src.annotations.orthotranscription.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Module managing the orthographic transcription for the multilingual text
    normalization system.

"""
import re
from unicodedata import category

from sppas.src.utils.makeunicode import u, sppasUnicode

# ---------------------------------------------------------------------------


class sppasOrthoTranscription(object):
    """Manager of an orthographic transcription.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2018  Brigitte Bigi

    This is a totally language-independent class. It supports the orthographic
    transcription defined into SPPAS software tool.

    From the manual Enriched Orthographic Transcription, two derived ortho.
    transcriptions are generated automatically by the tokenizer: the "standard"
    transcription (the list of orthographic tokens); the "faked spelling" that
    is a specific transcription from which the obtained phonetic tokens are
    used by the phonetization system.

    The following illustrates an utterance text normalization in French:

    - Transcription:
    j'ai on a j'ai p- (en)fin j'ai trouvé l(e) meilleur moyen c'était d(e) [loger,locher] chez  des amis
    (English translation is: I've we've I've - well I found the best way was to live in friends' apartment')

    - Result of the standard tokens:
    j' ai on a j' ai p- enfin j' ai trouvé le meilleur moyen c' était de loger  chez  des amis

    - Result of the faked tokens:
    j' ai on a j' ai p-   fin j' ai trouvé l  meilleur moyen c' était d  loche  chez  des amis

    """

    def __init__(self):
        pass

    # -----------------------------------------------------------------------

    @staticmethod
    def clean_toe(entry):
        """Clean Enriched Orthographic Transcription.

        The convention includes information that must be removed.

        :param entry: (str)
        :returns: (str)

        """
        # Proper names: $ name ,P\$
        entry = re.sub(u(',\s?[PTS]+\s?[\\/\\\]+\s?\\$'), r'',
                       entry, re.UNICODE)
        entry = re.sub(u('\$'), r'', entry, re.UNICODE)

        # Tags of the activity
        entry = re.sub(u('(gpd_[0-9]+)'), r" ", entry, re.UNICODE)
        entry = re.sub(u('(gpf_[0-9]+)'), r" ", entry, re.UNICODE)
        entry = re.sub(u('(ipu_[0-9]+)'), r" ", entry, re.UNICODE)

        # Remove invalid parenthesis content
        entry = re.sub(u('\s+\([\w\xaa-\xff]+\)\s+'), ' ', entry, re.UNICODE)
        entry = re.sub(u('^\([\w\xaa-\xff]+\)\s+'), ' ', entry, re.UNICODE)
        entry = re.sub(u('\s+\([\w\xaa-\xff]+\)$'), ' ', entry, re.UNICODE)

        entry = re.sub(u('\s*\[([^,]+),([^,]+)\]'),
                       sppasOrthoTranscription.__replace, entry, re.UNICODE)

        return " ".join(entry.split())

    # -----------------------------------------------------------------------

    @staticmethod
    def toe_spelling(entry, std=False):
        """Create a specific spelling from an Enriched Orthographic Transcription.

        :param entry: (str) the EOT string
        :param std: (bool) Standard spelling expected instead of the Faked one.
        :returns: (str)

        DevNote: Python’s regular expression engine supports Unicode.
        It can apply the same pattern to either 8-bit (encoded) or
        Unicode strings. To create a regular expression pattern that
        uses Unicode character classes for \w (and \s, and \b), use
        the “(?u)” flag prefix, or the re.UNICODE flag.

        """
        # Ensure all regexp will work!
        _fentry = " " + u(entry) + " "

        if std is False:
            # Stick un-regular liaisons to the previous token
            _fentry = re.sub(u(' =([\w]+)='), r'-\1', _fentry, re.UNICODE)
        else:
            # Remove liaisons
            _fentry = re.sub(u(' =([\w]+)='), u(' '), _fentry, re.UNICODE)

        # Laughing sequences
        _fentry = re.sub(u("\s?@\s?@\s?"), u(' '), _fentry, re.UNICODE)

        # Laughter
        _fentry = re.sub(u("([\w\xaa-\xff]+)@"), u(r"\1 @"), _fentry, re.UNICODE)
        _fentry = re.sub(u("@([\w\xaa-\xff]+)"), u(r"@ \1"), _fentry, re.UNICODE)

        # Noises
        _fentry = re.sub(u("([\w\xaa-\xff]+)\*"), u(r"\1 *"), _fentry, re.UNICODE)
        _fentry = re.sub(u("\*([\w\xaa-\xff]+)"), u(r"* \1"), _fentry, re.UNICODE)

        # Transcriptor comment's: {comment}
        _fentry = re.sub(u('\\{[\s\w\xaa-\xff\-:]+\\}'), '', _fentry, re.UNICODE)
        # Transcriptor comment's: [comment]
        _fentry = re.sub(u('\\[[\s\w\xaa-\xff\-:]+\\]'), '', _fentry, re.UNICODE)

        if std is False:
            # Special elisions (remove parenthesis content)
            _fentry = re.sub(u('\\([\s\w\xaa-\xff\-\']+\\)'), '', _fentry, re.UNICODE)
        else:
            # Special elisions (keep parenthesis content)
            _fentry = re.sub(u('\\(([\s\w\xaa-\xff\-]+)\\)'), u(r'\1'), _fentry, re.UNICODE)

        # Morphological variants
        _fentry = re.sub(u('\s+\\<([\-\'\s\w\xaa-\xff]+),([\-\'\s\w\xaa-\xff]+)\\>'), u(r' {\1|\2}'), _fentry, re.UNICODE)
        # the following is removed from SPPAS 1.9.6. It probably corresponded to a corpus...
        # dont remember exactly!
        # _fentry = re.sub(u('\s+\\{([\-\'\s\w\xaa-\xff]+),[\-\'\s\w\xaa-\xff]+\\}'), u(r' \1'), _fentry, re.UNICODE)

        if std is False:
            # Special pronunciations (keep right part)
            _fentry = re.sub(u('\s+\\[([\s\w\xaa-\xff/-]+),([\s\w\xaa-\xff/]+)\\]'), u(r' \2'), _fentry, re.UNICODE)
        else:
            # Special pronunciations (keep left part)
            _fentry = re.sub(u('\s+\\[([\s\w\xaa-\xff\\/-]+),[\s\w\xaa-\xff\\/]+\\]'), u(r' \1'), _fentry, re.UNICODE)

        # Proper names: $ name ,P\$
        _fentry = re.sub(u(',\s?[PTS]+\s?[\\/\\\]+\s?\\$'), '', _fentry, re.UNICODE)
        _fentry = re.sub(u('\\$'), '', _fentry, re.UNICODE)

        # specific case with numbers
        _fentry = re.sub(u("\s(?=,[0-9]+)"), '', _fentry, re.UNICODE)

        # ok, now stop regexp and work with unicode:
        _fentry = sppasUnicode(_fentry).to_strip()

        # Punctuations at the end of a token
        s = []
        entries = _fentry.split()
        for i, c in enumerate(entries):

            is_trunc = c.endswith("-")
            # Check for the SAMPA sequence to assign properly "is_sampa"
            if c.startswith("/") and c.endswith('/'):
                is_sampa = True
            else:
                is_sampa = False
                
            # if not is_sampa, add a whitespace if some punctuations are stick to a word
            if is_sampa is False:

                # if there is a serie of punctuations at the beginning
                while len(c) > 0 and category(c[0])[0] in ('P', 'S'):
                    s.append(c[0])
                    c = c[1:]

                # if there is a serie of punctuations at the end
                end_punct = []
                if is_trunc is False:
                    while len(c) > 0 and category(c[-1])[0] in ('P', 'S'):
                        end_punct.append(c[-1])
                        c = c[:-1]
                if len(end_punct) == 1 and end_punct[0] == u("."):
                    s.append(c+u("."))
                else:
                    s.append(c)
                    if len(end_punct) > 0:
                        s.extend(reversed(end_punct))
            else:
                if len(s) == 0:
                    s.append(c)
                else:
                    s[-1] += c

        return " ".join(s)

    # -----------------------------------------------------------------------

    @staticmethod
    def __replace(obj):
        """Callback for clean_toe.

        :param obj: (MatchObject)
        :returns: (str)

        """
        # Left part
        # Remove parentheses
        left = obj.group(1).replace('(', '')
        left = left.replace(')', '')
        # Replace spaces with underscores
        left = "_".join(left.split())

        # Right part
        # Remove spaces
        right = obj.group(2)
        right = "".join(right.split())
        return " [{:s},{:s}]".format(left, right)
