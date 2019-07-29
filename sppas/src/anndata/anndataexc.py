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

    src.anndata.anndataexc.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~

    Exceptions for anndata package.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      contact@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2018  Brigitte Bigi

"""

from sppas.src.config import sg
from sppas.src.config import error

# -----------------------------------------------------------------------


class AnnDataError(Exception):
    """:ERROR 1000:.

    No annotated data file is defined.

    """

    def __init__(self):
        self.parameter = error(1000) + (error(1000, "anndata"))

    def __str__(self):
        return repr(self.parameter)

# -----------------------------------------------------------------------


class AnnDataEqError(Exception):
    """:ERROR 1010:.

    Values are expected to be equals but are {:s!s} and {:s!s}.

    """

    def __init__(self, v1, v2):
        self.parameter = error(1010) + \
                         (error(1010, "anndata")).format(v1, v2)

    def __str__(self):
        return repr(self.parameter)

# -----------------------------------------------------------------------


class AnnDataTypeError(TypeError):
    """:ERROR 1100:.

    {!s:s} is not of the expected type '{:s}'.

    """

    def __init__(self, rtype, expected):
        self.parameter = error(1100) + \
                         (error(1100, "anndata")).format(rtype, expected)

    def __str__(self):
        return repr(self.parameter)

# -----------------------------------------------------------------------


class AnnUnkTypeError(TypeError):
    """:ERROR 1050:.

    {!s:s} is not a valid type.

    """

    def __init__(self, rtype):
        self.parameter = error(1050) + \
                         (error(1050, "anndata")).format(rtype)

    def __str__(self):
        return repr(self.parameter)

# -----------------------------------------------------------------------


class AnnDataIndexError(IndexError):
    """:ERROR 1200:.

    Invalid index value {:d}.

    """

    def __init__(self, index):
        self.parameter = error(1200) + \
                         (error(1200, "anndata")).format(index)

    def __str__(self):
        return repr(self.parameter)

# -----------------------------------------------------------------------


class AnnDataEqTypeError(TypeError):
    """:ERROR 1105:.

    {!s:s} is not of the same type as {!s:s}.

    """

    def __init__(self, obj, obj_ref):
        self.parameter = error(1105) + \
                         (error(1105, "anndata")).format(obj, obj_ref)

    def __str__(self):
        return repr(self.parameter)

# -----------------------------------------------------------------------


class AnnDataValueError(ValueError):
    """:ERROR 1300:.

    Invalid value '{!s:s}' for '{!s:s}'.

    """

    def __init__(self, data_name, value):
        self.parameter = error(1300) + \
                         (error(1300, "anndata")).format(value, data_name)

    def __str__(self):
        return repr(self.parameter)

# -----------------------------------------------------------------------


class AnnDataNegValueError(ValueError):
    """:ERROR 1310:.

    Expected a positive value. Got '{:f}'.

    """

    def __init__(self, value):
        self.parameter = error(1310) + \
                         (error(1310, "anndata")).format(value)

    def __str__(self):
        return repr(self.parameter)

# -----------------------------------------------------------------------


class AnnDataKeyError(KeyError):
    """:ERROR 1250:.

    Invalid key '{!s:s}' for data '{!s:s}'.

    """

    def __init__(self, data_name, value):
        self.parameter = error(1250) + \
                         (error(1250, "anndata")).format(value, data_name)

    def __str__(self):
        return repr(self.parameter)


# -----------------------------------------------------------------------


class IntervalBoundsError(ValueError):
    """:ERROR 1120:.

    The begin must be strictly lesser than the end in an interval.
    Got: [{:s};{:s}].

    """

    def __init__(self, begin, end):
        self.parameter = error(1120) + \
                         (error(1120, "anndata")).format(begin, end)

    def __str__(self):
        return repr(self.parameter)

# -----------------------------------------------------------------------


class CtrlVocabContainsError(ValueError):
    """:ERROR 1130:.

    {:s} is not part of the controlled vocabulary.

    """

    def __init__(self, tag):
        self.parameter = error(1130) + \
                         (error(1130, "anndata")).format(tag)

    def __str__(self):
        return repr(self.parameter)

# -----------------------------------------------------------------------


class CtrlVocabSetTierError(ValueError):
    """:ERROR 1132:.

    The controlled vocabulary {:s} can't be associated to the tier {:s}.

    """

    def __init__(self, vocab_name, tier_name):
        self.parameter = error(1132) + \
                         (error(1132, "anndata")).format(vocab_name, tier_name)

    def __str__(self):
        return repr(self.parameter)

# -----------------------------------------------------------------------


class TierAppendError(ValueError):
    """:ERROR 1140:.

    Can't append annotation. Current end {!s:s} is highest than the given
    one {!s:s}.

    """

    def __init__(self, cur_end, ann_end):
        self.parameter = error(1140) + \
                         (error(1140, "anndata")).format(cur_end, ann_end)

    def __str__(self):
        return repr(self.parameter)

# -----------------------------------------------------------------------


class TierAddError(ValueError):
    """:ERROR 1142:.

    Can't add annotation. An annotation with the same location is already
    in the tier at index {:d}.

    """

    def __init__(self, index):
        self.parameter = error(1142) + \
                         (error(1142, "anndata")).format(index)

    def __str__(self):
        return repr(self.parameter)

# -----------------------------------------------------------------------


class TierHierarchyError(ValueError):
    """:ERROR 1144:.

    Attempt a modification in tier '{:s}' that invalidates its hierarchy.

    """

    def __init__(self, name):
        self.parameter = error(1144) + \
                         (error(1144, "anndata")).format(name)

    def __str__(self):
        return repr(self.parameter)

# -----------------------------------------------------------------------


class TrsAddError(ValueError):
    """:ERROR 1150:.

    Can't add: '{:s}' is already in '{:s}'.

    """

    def __init__(self, tier_name, transcription_name):
        self.parameter = error(1150) + \
                         (error(1150, "anndata")).format(
                             tier_name,
                             transcription_name)

    def __str__(self):
        return repr(self.parameter)

# -----------------------------------------------------------------------


class TrsRemoveError(ValueError):
    """:ERROR 1152:.

    Can't remove: '{:s}' is not in '{:s}'.

    """

    def __init__(self, tier_name, transcription_name):
        self.parameter = error(1152) + \
                         (error(1152, "anndata")).format(tier_name,
                                                         transcription_name)

    def __str__(self):
        return repr(self.parameter)

# -----------------------------------------------------------------------


class TrsInvalidTierError(ValueError):
    """:ERROR 1160:.

    {:s} is not a tier of {:s}. It can't be included in its hierarchy.

    """

    def __init__(self, tier_name, transcription_name):
        self.parameter = error(1160) + \
                         (error(1160, "anndata")).format(tier_name,
                                                         transcription_name)

    def __str__(self):
        return repr(self.parameter)

# -----------------------------------------------------------------------


class HierarchyAlignmentError(ValueError):
    """:ERROR 1170:.

    Can't create a time alignment between tiers: '{:s}' is not a superset
    of '{:s}'."

    """

    def __init__(self, parent_tier_name, child_tier_name):
        self.parameter = error(1170) + \
                         (error(1170, "anndata")).format(parent_tier_name,
                                                         child_tier_name)

    def __str__(self):
        return repr(self.parameter)

# -----------------------------------------------------------------------


class HierarchyAssociationError(ValueError):
    """:ERROR 1172:.

    Can't create a time association between tiers: '{:s}' and '{:s}' are not
    supersets of each other.

    """

    def __init__(self, parent_tier_name, child_tier_name):
        self.parameter = error(1172) + \
                         (error(1172, "anndata")).format(parent_tier_name,
                                                         child_tier_name)

    def __str__(self):
        return repr(self.parameter)

# -----------------------------------------------------------------------


class HierarchyParentTierError(ValueError):
    """:ERROR 1174:.

    The tier can't be added into the hierarchy: '{:s}' has already a link of
    type {:s} with its parent tier '{:s}'.

    """

    def __init__(self, child_tier_name, parent_tier_name, link_type):
        self.parameter = error(1174) + \
                         (error(1174, "anndata")).format(child_tier_name,
                                                         parent_tier_name,
                                                         link_type)

    def __str__(self):
        return repr(self.parameter)

# -----------------------------------------------------------------------


class HierarchyChildTierError(ValueError):
    """:ERROR 1176:.

    The tier '{:s}' can't be added into the hierarchy: a tier can't be its
    own child.

    """

    def __init__(self, tier_name):
        self.parameter = error(1176) + \
                         (error(1176, "anndata")).format(tier_name)

    def __str__(self):
        return repr(self.parameter)


# -----------------------------------------------------------------------


class HierarchyAncestorTierError(ValueError):
    """:ERROR 1178:.

    The tier can't be added into the hierarchy: '{:s}' is an ancestor
    of '{:s}'.

    """

    def __init__(self, child_tier_name, parent_tier_name):
        self.parameter = error(1178) + \
                         (error(1178, "anndata")).format(child_tier_name,
                                                         parent_tier_name)

    def __str__(self):
        return repr(self.parameter)

# -----------------------------------------------------------------------
# AIO
# -----------------------------------------------------------------------


class AioError(IOError):
    """:ERROR 1400:.

    No such file: '{!s:s}'.

    """

    def __init__(self, filename):
        self.parameter = error(1400) + \
                         (error(1400, "anndata")).format(filename)

    def __str__(self):
        return repr(self.parameter)

# -----------------------------------------------------------------------


class AioEncodingError(UnicodeDecodeError):
    """:ERROR 1500:.

    The file {filename} contains non {encoding} characters: {error}.

    """

    def __init__(self, filename, error_msg, encoding=sg.__encoding__):
        self.parameter = error(1500) + \
                         (error(1500, "anndata")).format(filename=filename,
                                                         error=error_msg,
                                                         encoding=encoding)

    def __str__(self):
        return repr(self.parameter)

# -----------------------------------------------------------------------


class AioFileExtensionError(IOError):
    """:ERROR 1505:.

    Fail formats: unrecognized extension for file {:s}.

    """

    def __init__(self, filename):
        self.parameter = error(1505) + \
                         (error(1505, "anndata")).format(filename)

    def __str__(self):
        return repr(self.parameter)

# -----------------------------------------------------------------------


class AioMultiTiersError(IOError):
    """:ERROR 1510:.

    The file format {!s:s} does not support multi-tiers.

    """

    def __init__(self, file_format):
        self.parameter = error(1510) + \
                         (error(1510, "anndata")).format(file_format)

    def __str__(self):
        return repr(self.parameter)

# -----------------------------------------------------------------------


class AioNoTiersError(IOError):
    """:ERROR 1515:.

    The file format {!s:s} does not support to save no tiers.

    """

    def __init__(self, file_format):
        self.parameter = error(1515) + \
                         (error(1515, "anndata")).format(file_format)

    def __str__(self):
        return repr(self.parameter)

# -----------------------------------------------------------------------


class AioLineFormatError(IOError):
    """:ERROR 1520:.

    Unexpected format string at line {:d}: '{!s:s}'.

    """

    def __init__(self, number, line):
        self.parameter = error(1520) + \
                         (error(1520, "anndata")).format(number, line)

    def __str__(self):
        return repr(self.parameter)

# -----------------------------------------------------------------------


class AioFormatError(IOError):
    """:ERROR 1521:.

    Unexpected format about '{!s:s}'.

    """

    def __init__(self, line):
        self.parameter = error(1521) + \
                         (error(1521, "anndata")).format(line)

    def __str__(self):
        return repr(self.parameter)


# -----------------------------------------------------------------------


class AioEmptyTierError(IOError):
    """:ERROR 1525:.

    The file format {!s:s} does not support to save empty tiers: {:s}.

    """

    def __init__(self, file_format, tier_name):
        self.parameter = error(1525) + \
                         (error(1525, "anndata")).format(file_format,
                                                         tier_name)

    def __str__(self):
        return repr(self.parameter)

# -----------------------------------------------------------------------


class AioLocationTypeError(TypeError):
    """:ERROR 1530:.

    The file format {!s:s} does not support tiers with {:s}.

    """

    def __init__(self, file_format, location_type):
        self.parameter = error(1530) + \
                         (error(1530, "anndata")).format(file_format,
                                                         location_type)

    def __str__(self):
        return repr(self.parameter)

# -----------------------------------------------------------------------


class TagValueError(ValueError):
    """:ERROR 1190:.

    {!s:s} is not a valid tag.

    """

    def __init__(self, tag_str):
        self.parameter = error(1190) + \
                         (error(1190, "anndata")).format(tag_str)

    def __str__(self):
        return repr(self.parameter)
