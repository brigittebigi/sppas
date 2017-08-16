#!/usr/bin/env python2
# -*- coding: UTF-8 -*-
# ---------------------------------------------------------------------------
#            ___   __    __    __    ___
#           /     |  \  |  \  |  \  /              Automatic
#           \__   |__/  |__/  |___| \__             Annotation
#              \  |     |     |   |    \             of
#           ___/  |     |     |   | ___/              Speech
#
#
#                           http://www.sppas.org/
#
# ---------------------------------------------------------------------------
#            Laboratoire Parole et Langage, Aix-en-Provence, France
#                   Copyright (C) 2011-2016  Brigitte Bigi
#
#                   This banner notice must not be removed
# ---------------------------------------------------------------------------
# Use of this software is governed by the GNU Public License, version 3.
#
# SPPAS is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# SPPAS is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with SPPAS. If not, see <http://www.gnu.org/licenses/>.
#
# ---------------------------------------------------------------------------

import random
import string

from ..label.label import Label
from ..ptime.interval import TimeInterval
from ..ptime.interval import TimePoint
from ..annotation import Annotation
from ..tier import Tier

# ---------------------------------------------------------------------------


def random_hexachar(y, lowercase=True):
    if lowercase:
        return ''.join(random.choice('abcdef') for x in range(y))
    return ''.join(random.choice('ABCDEF') for x in range(y))


def random_char(y, lowercase=True):
    if lowercase:
        return ''.join(random.choice(string.ascii_lowercase) for x in range(y))
    return ''.join(random.choice(string.ascii_letters) for x in range(y))


def random_int(y):
    return ''.join(str(random.randint(0,9)) for x in range(y))

# ---------------------------------------------------------------------------


def indent(elem, level=0):
    """
    pretty indent.
    http://effbot.org/zone/element-lib.htm#prettyprint
    """
    i = "\n" + level*"  "
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + "  "
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
        for elem in elem:
            indent(elem, level+1)
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = i

# -----------------------------------------------------------------


def gen_id():
    """
    Generate a unique ID, of type GUID - globally unique identifier.

    GUIDs are usually stored as 128-bit values, and are commonly
    displayed as 32 hexadecimal digits with groups separated by hyphens,
    such as {21EC2020-3AEA-4069-A2DD-08002B30309D}.

    """
    s = ''
    s += random_int(1)
    s += random_hexachar(1)
    s += random_int(3)
    s += random_hexachar(1)
    s += random_int(1)
    s += random_hexachar(1)
    s += "-"
    s += random_int(1)
    s += random_hexachar(1)
    s += random_int(2)
    s += "-"
    s += random_int(1)
    s += random_hexachar(1)
    s += random_int(2)
    s += "-"
    s += random_int(1)
    s += random_hexachar(2)
    s += random_int(1)
    s += "-"
    s += random_int(4)
    s += random_hexachar(2)
    s += random_int(1)
    s += random_hexachar(1)
    s += random_int(3)
    s += random_hexachar(1)

    return s

# -----------------------------------------------------------------


def format_float( f ):
    return round(float(f), 4)

# -----------------------------------------------------------------


def fill_gaps(tier, mintime, maxtime):
    """
    Return the tier in which the temporal gaps between annotations are filled with an un-labelled annotation.

    @param tier: (Tier)

    """
    new_tier = tier.Copy()
    prev = None

    if mintime is not None and format_float(tier.GetBeginValue()) > format_float(mintime):
        time = TimeInterval(TimePoint(mintime), TimePoint(tier.GetBeginValue()))
        annotation = Annotation(time)
        new_tier.Add(annotation)

    for a in new_tier:
        if prev is not None and prev.GetLocation().GetEnd() < a.GetLocation().GetBegin():
            time = TimeInterval(TimePoint(prev.GetLocation().GetEndMidpoint()), TimePoint(a.GetLocation().GetBeginMidpoint()))
            annotation = Annotation(time)
            new_tier.Add(annotation)
            prev = annotation
        elif prev is not None and prev.GetLocation().GetEndMidpoint() < a.GetLocation().GetBeginMidpoint():
            a.GetLocation().GetBegin().SetMidpoint( prev.GetLocation().GetEndMidpoint() )
            prev = a
        else:
            prev = a

    if maxtime is not None and format_float(tier.GetEndValue()) < format_float(maxtime):
        time = TimeInterval(TimePoint(tier.GetEndValue()), TimePoint(maxtime))
        annotation = Annotation(time)
        new_tier.Add(annotation)

    return new_tier

# ------------------------------------------------------------------------


def unfill_gaps(tier):
    """
    Return the tier in which un-labelled annotations are removed.

    @param tier (Tier - IN)
    @return tier

    """
    new_tier = tier.Copy()
    topop = []
    for i,ann in enumerate(new_tier):
        if ann.GetLabel().IsEmpty():
            topop.append(i)

    for i in reversed(topop):
        new_tier.Pop(i)

    return new_tier

# ------------------------------------------------------------------------


def merge_overlapping_annotations(tier, separator=' '):
    """
    Merge overlapping annotations.
    The values of the labels are concatenated.

    Do not pay attention to alternatives.

    @param tier: (Tier)
    @return Tier

    """
    if tier.IsInterval() is False:
        return tier

    new_tier = Tier(tier.GetName())
    new_tier.metadata = tier.metadata
    new_tier.SetMedia( tier.GetMedia() )
    new_tier.SetDataType( tier.GetDataType() )
    new_tier.SetTranscription( tier.GetTranscription() )
    new_tier.SetCtrlVocab( tier.GetCtrlVocab() )
    prev = None

    for a in tier:

        if prev is None:
            new_tier.Append(a)
            prev = a
            continue

        #TW:
        # test whether prev overlaps with a
        #if prev and prev.Begin < a.End and a.Begin < prev.End:
            # Interval containing both prev and a
            #prev.TextValue += separator + a.TextValue
            #prev.EndValue = max((prev.EndValue, a.EndValue))

        if a.GetLocation().GetBegin() < prev.GetLocation().GetBegin():
            # TODO
            # it happens if more than 2 annotations are starting at the same time
            #print "IGNORED: ",a
            continue

        # a is after prev: normal.
        if a.GetLocation().GetBegin() >= prev.GetLocation().GetEnd():
            new_tier.Append(a)
            prev = a

        # prev and a start at the same time
        elif a.GetLocation().GetBegin() == prev.GetLocation().GetBegin():
            new_tier.SetCtrlVocab( None )
            # must disable CtrlVocab or, eventually, add new labels in its entries...

            # a ends after prev => join a's label to prev
            #                      and reduce a to the remaining part [prev.end, a.end]
            if a.GetLocation().GetEnd() > prev.GetLocation().GetEnd():
                a.GetLocation().SetBegin( prev.GetLocation().GetEnd() )
                prev.GetLabel().SetValue( prev.GetLabel().GetValue() + separator + a.GetLabel().GetValue())
                new_tier.Append(a)
                prev = a

            # a ends before prev => join a's label to prev, reduced to [prev.begin, a.end]
            #                       and create a2 for the remaining part [a.end, prev.end]
            elif a.GetLocation().GetEnd() < prev.GetLocation().GetEnd():
                a2 = Annotation(TimeInterval(a.GetLocation().GetEnd(), prev.GetLocation().GetEnd()), Label(prev.GetLabel().GetValue()))
                #TODO? a2.metadata = a.metadata # a2 shares a's metadata
                if prev.GetLocation().GetBegin() < a.GetLocation().GetEnd():
                    prev.GetLocation().SetEnd( a.GetLocation().GetEnd() )
                prev.GetLabel().SetValue( prev.GetLabel().GetValue() + separator + a.GetLabel().GetValue())
                try:
                    new_tier.Append(a2)
                except Exception:
                    pass
                prev = a2

            # a ends with prev => join the label
            else:
                prev.GetLabel().SetValue( prev.GetLabel().GetValue() + separator + a.GetLabel().GetValue())

        # a starts inside prev
        elif a.GetLocation().GetBegin() < prev.GetLocation().GetEnd():
            new_tier.SetCtrlVocab( None )
            # must disable CtrlVocab or, eventually, add new labels in its entries...

            # a ends before prev => reduce prev to [prev.begin, a.begin]
            #                       join the prev's label to a
            #                       and create a2 for [a.end, prev.end]
            if a.GetLocation().GetEnd() < prev.GetLocation().GetEnd():
                a2 = Annotation(TimeInterval(a.GetLocation().GetEnd(),prev.GetLocation().GetEnd()),Label(prev.GetLabel().GetValue()))
                a.GetLabel().SetValue( a.GetLabel().GetValue() + separator + prev.GetLabel().GetValue() )
                prev.GetLocation().SetEnd( a.GetLocation().GetBegin() )
                new_tier.Append(a)
                new_tier.Append(a2)
                prev = a2

            # a ends after prev => reduce prev to [prev.begin, a.begin]
            #                      create a2 for [a.begin, prev.end], with the 2 labels
            #                      reduce a to [prev.end, a.end]
            elif a.GetLocation().GetEnd() > prev.GetLocation().GetEnd():
                a2 = Annotation(TimeInterval(a.GetLocation().GetBegin(),prev.GetLocation().GetEnd()),Label(prev.GetLabel().GetValue() + separator + a.GetLabel().GetValue()))
                prev.GetLocation().SetEnd( a2.GetLocation().GetBegin() )
                a.GetLocation().SetBegin(  a2.GetLocation().GetEnd() )
                new_tier.Append(a2)
                new_tier.Append(a)
                prev = a

            # a ends with prev => reduce prev to [prev.begin, a.begin]
            #                     join prev's label to a
            else:
                a.GetLabel().SetValue( a.GetLabel().GetValue() + separator + prev.GetLabel().GetValue() )
                prev.GetLocation().SetEnd( a.GetLocation().GetBegin() )
                new_tier.Append(a)
                prev = a

    return new_tier

# ------------------------------------------------------------------------


def point2interval(tier, fixradius=None, minradius=0.001):
    """
    Convert localization.
    Ensure the radius to be always >= minradius (1 millisecond).

    Do not convert alternatives.

    (!) Result interval annotations share the metadata of the original point annotation

    @param tier: (Tier)
    @param fixradius: the radius to use for all interval (if not None, else the point radius)
    @param minradius: a minimal radius
    @return Tier

    """
    if tier.IsInterval():
        return tier.Copy()

    new_tier = Tier(tier.GetName())
    new_tier.metadata = tier.metadata
    new_tier.SetMedia( tier.GetMedia() )
    new_tier.SetCtrlVocab( tier.GetCtrlVocab() )
    new_tier.SetDataType( tier.GetDataType() )
    #new_tier.SetTranscription( tier.GetTranscription() ) # no need
    new_tier.metadata['TIER_TYPE']="TimePoint"

    for a in tier:
        # get point with the best score for this annotation
        point = a.GetLocation().GetPoint()
        midpoint = point.GetMidpoint()
        radius = fixradius if fixradius is not None else point.GetRadius()
        if radius < minradius:
            radius = minradius

        begin = TimePoint(midpoint-radius,radius)
        end   = TimePoint(midpoint+radius,radius)

        new_a=Annotation(TimeInterval(begin,end),Label(a.GetLabel().GetValue()))
        new_a.metadata = a.metadata # new annotation shares original annotation's metadata
        new_tier.Append( new_a )

    return new_tier

# ------------------------------------------------------------------------
