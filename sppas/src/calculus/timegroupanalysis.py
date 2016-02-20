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
# File: timegroupanalysis.py
# ----------------------------------------------------------------------------

from descriptivesstats import DescriptiveStatistics
import stats.linregress
import stats.variability

# ----------------------------------------------------------------------------

class TimeGroupAnalysis( DescriptiveStatistics ):
    """
    @authors: Brigitte Bigi
    @contact: brigitte.bigi@gmail.com
    @license: GPL, v3
    @summary: TGA estimator class.

    This class estimates TGA on a set of data values, stored in a dictionary:
    - key is the name of the time group;
    - value is the list of durations of each segments in the time group.

    >>> d = { 'tg1':[1.0,1.2,3.2,4.1] , 'tg2':[2.9,3.3,3.6,5.8] }
    >>> tga = TimeGroupAnalyses(d)
    >>> total = tga.total()
    >>> slope = tga.slope()
    >>> print slope['tg_1']
    >>>
    >>> print slope['tg_2']
    >>>

    """

    def __init__(self, dictitems):
        """
        TGA.

        @param dictitems (dict): a dict of a list of durations.
        """
        DescriptiveStatistics.__init__(self, dictitems)

    # -----------------------------------------------------------------------
    # Specific estimators for rythm analysis
    # -----------------------------------------------------------------------

    def rPVI(self):
        """
        Estimates the Raw Pairwise Variability Index of data values.
        @return (dict): a dictionary of (key, nPVI) of float values
        """
        return dict( (key, stats.variability.rPVI(values)) for key,values in self.items.iteritems() )

    def nPVI(self):
        """
        Estimates the Normalized Pairwise Variability Index of data values.
        @return (dict): a dictionary of (key, nPVI) of float values
        """
        return dict( (key, stats.variability.nPVI(values)) for key,values in self.items.iteritems() )

    def intercept_slope_original(self):
        """
        Estimates the intercept like the original TGA of data values.
        @return (dict): a dictionary of (key, (intercept,slope)) of float values
        """
        # Create the list of points (x,y) of each TG where:
        # x is the position
        # y is the duration
        linreg = []
        for key,values in self.items.iteritems():
            points = [ (position,duration) for position,duration in enumerate(values) ]
            linreg.append( (key, (stats.linregress.tga_linear_regression(points))) )
        return dict(linreg)

    def intercept_slope(self):
        """
        Estimates the intercept like AnnotationPro of data values.
        @return (dict): a dictionary of (key, (intercept,slope)) of float values
        """
        # Create the list of points (x,y) of each TG where:
        # x is the timestamps
        # y is the duration
        linreg = []
        for key,values in self.items.iteritems():
            points = []
            timestamp = 0.
            for duration in values:
                points.append( (timestamp,duration) )
                timestamp += duration
            linreg.append( (key, (stats.linregress.tga_linear_regression(points))) )
        return dict(linreg)

    # -----------------------------------------------------------------------
