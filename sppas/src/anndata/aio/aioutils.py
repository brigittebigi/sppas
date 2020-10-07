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

    anndata.aio.aioutils.py: Utilities for readers and writers.
    ~~~~~~~~~~~~~~~~~~~~~~~

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2020  Brigitte Bigi

    BNF to represent tags of a label:

        ALTERNATE :== "{" TEXT ALT+ "}"
        ALT :== "|" TEXT
        TEXT :== string | string=SCORE
        SCORE :== float

"""
import codecs

from sppas.src.config import sg
from sppas.src.config import symbols
from sppas.src.utils import sppasUnicode, u

from ..tier import sppasTier
from ..ann.annotation import sppasAnnotation
from ..ann.annlocation import sppasLocation
from ..ann.annlocation import sppasInterval
from ..ann.annlocation import sppasPoint
from ..ann.annlabel import sppasLabel
from ..ann.annlabel import sppasTag
from ..anndataexc import AioError
from ..anndataexc import AioEncodingError

# ---------------------------------------------------------------------------

SIL_ORTHO = list(symbols.ortho.keys())[list(symbols.ortho.values()).index("silence")]
SIL_PHONO = list(symbols.phone.keys())[list(symbols.phone.values()).index("silence")]

# ---------------------------------------------------------------------------


def format_point_to_float(p):
    f = p.get_midpoint()
    return round(float(f), 4)

# ---------------------------------------------------------------------------


def load(filename, file_encoding=sg.__encoding__):
    """Load a file into lines.

    :param filename: (str)
    :param file_encoding: (str)
    :returns: list of lines (str)

    """
    try:
        with codecs.open(filename, 'r', file_encoding) as fp:
            lines = fp.readlines()
            fp.close()
    except IOError:
        raise AioError(filename)
    except UnicodeDecodeError:
        raise AioEncodingError(filename, "", file_encoding)

    return lines

# ---------------------------------------------------------------------------


def is_ortho_tier(tier_name):
    """Return true is the tier_name matches an ortho trans.

    i.e. is containing either "ipu", "trans", "trs", "toe" or "ortho" in its name.

    :param tier_name: (str)
    :returns: (bool)

    """
    tier_name = tier_name.lower()
    if "trans" in tier_name:
        return True
    if "trs" in tier_name:
        return True
    if "toe" in tier_name:
        return True
    if "ortho" in tier_name:
        return True
    if "ipu" in tier_name:
        return True

    return False

# --------------------------------------------------------------------------


def serialize_labels(labels, separator="\n", empty="", alt=True):
    """Create a text from a list of labels.

    Use the separator to split the text into labels.
    Use the "{ | }" system to parse the alternative tags and = for scores.

    :param labels: (list of sppasLabel)
    :param separator: (str) String separating labels
    :param empty: (str) The text representing an empty tag
    :param alt: (bool) Include alternative tags. If False, only the best tag is serialized.

    :returns: list of sppasLabel

    """
    if len(labels) == 0:
        return empty

    if len(labels) == 1:
        label = labels[0]
        return serialize_label(label, empty, alt)

    c = list()
    for label in labels:
        c.append(serialize_label(label, empty, alt))

    return separator.join(c)

# ---------------------------------------------------------------------------


def serialize_label(label, empty="", alt=True):
    """Convert the label into a string, include or not alternative tags.

    Use the "{ | }" system to serialize the alternative tags.
    Scores of the tags are not returned.

    :param label: (sppasLabel)
    :param empty: (str) The text to return if a tag is empty or not set.
    :param alt: (bool) Include alternative tags
    :returns: (str)

    """
    if label.is_tagged() is False:
        return empty
    if label.get_best() is None:
        return empty

    if alt is False or len(label) == 1:
        best = label.get_best()
        if best.is_empty():
            return empty
        content = best.get_content()
        score = label.get_score(best)
        if score is None:
            return content
        else:
            return content+"="+str(score)

    # we store the alternative tags into a list.
    # empty tags are replaced by the empty item.
    tag_contents = list()
    for tag, score in label:
        content = tag.get_content()
        if len(content) > 0:
            if score is None:
                tag_contents.append(content)
            else:
                tag_contents.append(content+"="+str(score))
        else:
            tag_contents.append(empty)

    # we return the alternative tags
    return "{" + "|".join(tag_contents) + "}"

# ---------------------------------------------------------------------------


def format_labels(text, separator="\n", empty="", tag_type="str"):
    """Create a set of labels from a text.

    Use the separator to split the text into labels.
    Use the "{ | }" system to parse the alternative tags.

    :examples:
        text = "{le|les} {chat|chats}" is 2 labels with 2 tags each
        text = "{le=0.6|les=0.4}" is a label with 2 tags and their score

    :param text: (str)
    :param separator: (str) String to separate labels.
    :param empty: (str) The text representing an empty tag.
    :param tag_type: (str): One of: ('str', 'int', 'float', 'bool').

    :returns: list of sppasLabel

    """
    if text is None:
        return []
    
    su = sppasUnicode(text.strip())
    text = su.unicode()
    if len(text) == 0:
        return []

    labels = list()
    for line in text.split(sppasUnicode(separator).unicode()):
        label = format_label(line, empty, tag_type)
        labels.append(label)

    return labels

# ---------------------------------------------------------------------------


def format_label(text, empty="", tag_type="str"):
    """Create a label from a text.

    Use the "{ | }" system to parse the alternative tags and = for scores.

    :param text: (str)
    :param empty: (str) The text representing an empty tag.
    :param tag_type: (str): One of: ('str', 'int', 'float', 'bool').

    :returns: sppasLabel

    """
    su = sppasUnicode(text.strip())
    text = su.unicode()
    if len(text) == 0:
        return sppasLabel(sppasTag(""))

    # Alternative tags
    if text.startswith(u('{')) and text.endswith(u('}')) and u('|') in text:
        text = text[1:-1]
        tag = list()
        score = list()
        for content in text.split(u('|')):
            tag.append(format_tag(content, empty, tag_type))
            score.append(format_score(content))

    else:
        tag = format_tag(text, empty, tag_type)
        score = format_score(text)

    return sppasLabel(tag, score)

# ---------------------------------------------------------------------------


def format_score(text):
    """Return a score from a text.

    :param text: (str) Unicode text
    :returns: float or None

    """
    if len(text) == 0:
        return None

    score = None
    if "=" in text:
        tab = text.split("=")
        try:
            score = float(tab[1])
        except:
            pass

    return score


# ---------------------------------------------------------------------------


def format_tag(text, empty="", tag_type="str"):
    """Return a tag from a text.

    :param text: (str) Unicode text
    :param empty: (str) The text representing an empty tag.
    :param tag_type: (str): The type of this content.\
        One of: ('str', 'int', 'float', 'bool').

    :returns: sppasTag

    """
    if len(text) == 0:
        return sppasTag(empty, tag_type)

    if "=" in text:
        tab = text.split("=")
        try:
            float(tab[1])
        except:
            # the given text is in the format: text=text
            pass
        else:
            # the given text is in the format: text=score
            text = tab[0]

    return sppasTag(text, tag_type)

# ---------------------------------------------------------------------------


def check_gaps(tier, min_loc=None, max_loc=None):
    """Check if there are holes between annotations.

    :param tier: (sppasTier)
    :param min_loc: (sppasPoint)
    :param max_loc: (sppasPoint)
    :returns: (bool)

    """
    if tier.is_empty():
        return True

    if min_loc is not None and format_point_to_float(tier.get_first_point()) > format_point_to_float(min_loc):
        return True
    if max_loc is not None and format_point_to_float(tier.get_last_point()) < format_point_to_float(max_loc):
        return True

    prev = None
    for ann in tier:
        if prev is not None:
            prev_end = prev.get_highest_localization()
            ann_begin = ann.get_lowest_localization()
            if prev_end < ann_begin:
                return True
        prev = ann

    return False

# ---------------------------------------------------------------------------


def fill_gaps(tier, min_loc=None, max_loc=None):
    """Temporal gaps/holes between annotations are filled.

    :param tier: (sppasTier) A tier with intervals.
    :param min_loc: (sppasPoint)
    :param max_loc: (sppasPoint)
    :returns: (sppasTier) a tier with un-labelled annotations instead of gaps.

    """
    if tier.is_empty() and min_loc is not None and max_loc is not None:
        new_tier = tier.copy()
        new_tier.gen_id()
        interval = sppasInterval(min_loc, max_loc)
        new_tier.add(sppasAnnotation(sppasLocation(interval)))
        return new_tier

    if tier.is_empty():
        return tier

    # find gaps only if the tier is an IntervalTier
    if tier.is_interval() is False:
        return tier

    # There's no reason to do anything if the tier is already without gaps!
    if check_gaps(tier, min_loc, max_loc) is False:
        return tier

    # Right, we have things to do...
    new_tier = tier.copy()
    new_tier.gen_id()

    # Check firstly the begin/end
    if min_loc is not None and format_point_to_float(tier.get_first_point()) > format_point_to_float(min_loc):
        interval = sppasInterval(min_loc, tier.get_first_point())
        new_tier.add(sppasAnnotation(sppasLocation(interval)))

    if max_loc is not None and format_point_to_float(tier.get_last_point()) < format_point_to_float(max_loc):
        interval = sppasInterval(tier.get_last_point(), max_loc)
        new_tier.add(sppasAnnotation(sppasLocation(interval)))

    # There's no reason to go further if the tier is already without gaps!
    if check_gaps(new_tier, min_loc, max_loc) is False:
        return new_tier

    # Right, we have to check all annotations
    prev = None
    for a in new_tier:

        if prev is not None and prev.get_highest_localization() < a.get_lowest_localization():
            interval = sppasInterval(prev.get_highest_localization(), a.get_lowest_localization())
            annotation = sppasAnnotation(sppasLocation(interval))
            new_tier.add(annotation)
            prev = annotation
        elif prev is not None and prev.get_highest_localization() < a.get_lowest_localization():
            a.get_lowest_localization().set(prev.get_highest_localization())
            prev = a
        else:
            prev = a

    return new_tier

# ---------------------------------------------------------------------------


def unfill_gaps(tier):
    """Return the tier in which un-labelled annotations are removed.

    An un_labelled annotation means that:

        - the annotation has no labels,
        - or the tags of each label are an empty string.

    The hierarchy is not copied to the new tier.

    :param tier: (Tier)
    :returns: (sppasTier)

    """
    new_tier = sppasTier(tier.get_name()+"-unfill")
    new_tier.set_ctrl_vocab(tier.get_ctrl_vocab())
    new_tier.set_media(tier.get_media())
    for key in tier.get_meta_keys():
        new_tier.set_meta(key, tier.get_meta(key))

    for i, ann in enumerate(tier):
        if ann.label_is_filled() is True:
            content = serialize_labels(ann.get_labels())
            if len(content) > 0:
                new_tier.append(ann.copy())

    return new_tier

# ---------------------------------------------------------------------------


def check_overlaps(tier):
    """Check whether some annotations are overlapping or not.

    :param tier: (sppasTier)
    :returns: (bool)

    """
    if tier.is_empty():
        return False
    prev = None
    for ann in tier:
        if prev is not None:
            prev_end = prev.get_highest_localization()
            ann_begin = ann.get_lowest_localization()
            if ann_begin < prev_end:
                return True
        prev = ann

    return False

# ---------------------------------------------------------------------------


def merge_overlapping_annotations(tier):
    """Merge overlapping annotations.

    The labels of 2 overlapping annotations are appended.

    :param tier: (Tier)
    :returns: (sppasTier)

    """
    if tier.is_interval() is False:
        return tier
    if tier.is_empty():
        return tier
    if len(tier) == 1:
        return tier

    if check_overlaps(tier) is False:
        return tier

    new_tier = sppasTier(tier.get_name())
    for key in tier.get_meta_keys():
        new_tier.set_meta(key, tier.get_meta(key))
    new_tier.set_parent(tier.get_parent())
    new_tier.set_ctrl_vocab(tier.get_ctrl_vocab())
    new_tier.set_media(tier.get_media())

    prev = None

    # At a first stage, we create the annotations without labels
    for a in tier:

        # first interval
        if prev is None:
            a2 = sppasAnnotation(
                    sppasLocation(sppasInterval(a.get_lowest_localization(),
                                                a.get_highest_localization())))
            new_tier.append(a2)
            prev = a2
            continue

        if a.get_lowest_localization() < prev.get_lowest_localization():
            # normally it can't happen:
            # annotations are sorted by "append" and "add" methods.
            continue

        # a is after prev
        if a.get_lowest_localization() >= prev.get_highest_localization():
            # either:   |   prev   |  a   |
            # or:       |   prev   |   |  a  |

            a2 = sppasAnnotation(
                    sppasLocation(sppasInterval(a.get_lowest_localization(),
                                                a.get_highest_localization())))
            new_tier.append(a2)
            prev = a2

        # prev and a, both start at the same time
        elif a.get_lowest_localization() == prev.get_lowest_localization():

            # we must disable CtrlVocab because new entries are created...
            new_tier.set_ctrl_vocab(None)

            if a.get_highest_localization() > prev.get_highest_localization():
                #   |   prev  |
                #   |   a        |

                a2 = sppasAnnotation(
                    sppasLocation(sppasInterval(prev.get_highest_localization(),
                                                a.get_highest_localization())))
                new_tier.append(a2)
                prev = a2

            elif a.get_highest_localization() < prev.get_highest_localization():
                #   |   prev    |
                #   |   a    |

                a2 = sppasAnnotation(
                        sppasLocation(sppasInterval(a.get_highest_localization(),
                                                    prev.get_highest_localization())))
                prev_loc = prev.get_location().get_best()
                prev_loc.set_end(a.get_highest_localization())
                prev.set_best_localization(prev_loc)
                new_tier.append(a2)
                prev = a2

            else:
                #   |   prev   |
                #   |   a      |
                continue

        # a starts inside prev
        elif a.get_lowest_localization() < prev.get_highest_localization():

            # we must disable CtrlVocab because new entries are created...
            new_tier.set_ctrl_vocab(None)

            if a.get_highest_localization() < prev.get_highest_localization():
                #  |      prev       |
                #      |   a      |

                a2 = sppasAnnotation(
                            sppasLocation(sppasInterval(a.get_highest_localization(),
                                                        prev.get_highest_localization())))
                prev_loc = prev.get_location().get_best()
                prev_loc.set_end(a.get_lowest_localization())
                prev.set_best_localization(prev_loc)
                new_tier.append(a)
                new_tier.append(a2)
                prev = a2

            elif a.get_highest_localization() > prev.get_highest_localization():
                #  |  prev   |
                #       |   a    |

                a2 = sppasAnnotation(
                            sppasLocation(sppasInterval(a.get_lowest_localization(),
                                                        prev.get_highest_localization())))
                prev_loc = prev.get_location().get_best()
                prev_loc.set_end(a2.get_lowest_localization())
                prev.set_best_localization(prev_loc)
                new_tier.append(a2)

                a3 = sppasAnnotation(
                       sppasLocation(sppasInterval(a2.get_highest_localization(),
                                                   a.get_highest_localization())))
                new_tier.append(a3)
                prev = a3

            else:
                # |    prev   |
                #    |   a    |

                prev_loc = prev.get_location().get_best()
                prev_loc.set_end(a.get_lowest_localization())
                prev.set_best_localization(prev_loc)
                a2 = sppasAnnotation(
                            sppasLocation(sppasInterval(a.get_lowest_localization(),
                                                        a.get_highest_localization())))
                new_tier.append(a2)
                prev = a2

    # At a second stage, we assign the labels to the new tier
    for new_ann in new_tier:

        begin = new_ann.get_lowest_localization()
        end = new_ann.get_highest_localization()
        anns = tier.find(begin, end, overlaps=True)

        new_labels = list()
        for ann in anns:
            new_labels.extend(ann.get_labels())
        new_ann.set_labels(new_labels)

    return new_tier

# ------------------------------------------------------------------------


def point2interval(tier, radius=0.001):
    """Convert a PointTier into an IntervalTier.

    - Ensure the radius to be always >= 1 millisecond and the newly created
    tier won't contain overlapped intervals.
    - Do not convert alternatives localizations.
    - Do not share the hierarchy.
    - New tier share the original tier's metadata, except that its 'id' is different.
    - New annotations share the original annotation's metadata, except that
    their 'id' is different.

    :param tier: (Tier)
    :param radius: (float) the radius to use for all intervals
    :returns: (sppasTier) or None if tier was not converted.

    """
    # check the type of the tier!
    if tier.is_point() is False:
        return None

    # create the new tier and share information (except 'id' and hierarchy)
    new_tier = sppasTier(tier.get_name())
    for key in tier.get_meta_keys():
        if key != 'id':
            new_tier.set_meta(key, tier.get_meta(key))
    new_tier.set_media(tier.get_media())
    new_tier.set_ctrl_vocab(tier.get_ctrl_vocab())

    # create the annotations with intervals
    end_midpoint = 0.
    for ann in tier:

        # get the point with the best score for this annotation
        point = ann.get_location().get_best()
        m = point.get_midpoint()
        r = max(radius, point.get_radius())

        # fix begin/end new points. Provide overlaps.
        begin_midpoint = max(m - r, end_midpoint)
        begin = sppasPoint(begin_midpoint, r)
        end_midpoint = m + r
        end = sppasPoint(end_midpoint, r)

        # create the new annotation with an interval
        new_ann = sppasAnnotation(sppasLocation(sppasInterval(begin, end)),
                                  [label.copy() for label in ann.get_labels()])
        # new annotation shares original annotation's metadata, except the 'id'
        for key in new_ann.get_meta_keys():
            if key != 'id':
                new_ann.set_meta(key, ann.get_meta(key))
        new_tier.append(new_ann)

    return new_tier

# ------------------------------------------------------------------------


def unalign(aligned_tier, ipus_separators=(SIL_ORTHO, SIL_PHONO, 'dummy')):
    """Convert a time-aligned tier into a non-aligned tier.

    :param aligned_tier: (sppasTier)
    :param ipus_separators: (list)
    :returns: (Tier)

    """
    new_tier = sppasTier("Un-aligned")
    b = aligned_tier.get_first_point()
    e = b
    l = ""
    for a in aligned_tier:
        label = serialize_labels(a.get_labels())
        if label in ipus_separators or len(label) == 0:
            if e > b:
                loc = sppasLocation(sppasInterval(b, e))
                new_tier.create_annotation(loc, sppasLabel(sppasTag(l)))
            new_tier.add(a)
            b = a.get_location().get_best().get_end()
            e = b
            l = ""
        else:
            e = a.get_location().get_best().get_end()
            label = label.replace('.', ' ')
            l += " " + label

    if e > b:
        a = aligned_tier[-1]
        e = a.get_location().get_best().get_end()
        loc = sppasLocation(sppasInterval(b, e))
        new_tier.create_annotation(loc, sppasLabel(sppasTag(l)))

    return new_tier
