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

"""

from sppas import sppasTier, sppasLocation
from sppas import sppasInterval, sppasPoint
from sppas import sppasLabel, sppasTag

# ---------------------------------------------------------------------------


class ReOccurences(object):
    """Manager for a set of re-occurrences annotations.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2019  Brigitte Bigi

    """

    def __init__(self):
        super(ReOccurences, self).__init__()

    # -----------------------------------------------------------------------

    @staticmethod
    def compare_labels(label1, label2):
        """Compare two labels.

        :param label1: (sppasLabel)
        :param label2: (sppasLabel)
        :returns: (bool) Number of tags they have in common

        """
        tags1 = [tag.get_typed_content() for tag, score in label1]
        tags2 = [tag.get_typed_content() for tag, score in label2]
        union = tags1 + tags2
        diff = set(union)

        return len(union) - len(diff)

    # -----------------------------------------------------------------------

    @staticmethod
    def eval(ann1, anns2):
        """Return the list of re-occurrences.

        An annotation in anns2 is matching ann1 if all labels of ann1 are
        in ann2. It is not one-to-one: some labels of ann2 could not match
        those of ann1.

        :param ann1: (sppasAnnotation)
        :param anns2: (list of sppasAnnotation)
        :returns: (list of sppasAnnotation)

        """
        reocc = list()
        for ann2 in anns2:

            # Evaluate if all labels of ann1 are also in ann2
            match = False
            for label1 in ann1.get_labels():
                match = False
                for label2 in ann2.get_labels():
                    equals = ReOccurences.compare_labels(label1, label2)
                    # we've found that a label of ann2 is matching label1
                    # we can stop to search it anymore. label1 == label2
                    if equals > 0:
                        match = True
                        break

                # As soon as a label1 is missing in ann2, we can stop:
                # ann2 is not a re-occurrence of ann1
                if match is False:
                    break

            if match is True:
                reocc.append(ann2)

        return list(set(reocc))
