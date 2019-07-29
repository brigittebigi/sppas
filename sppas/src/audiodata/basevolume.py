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

    src.audiodata.basevolume.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    The volume is the estimation of RMS values, sampled with a window of 10ms.

"""

import sppas.src.calculus.stats.central as central
import sppas.src.calculus.stats.variability as variability
import sppas.src.calculus.stats.moment as moment

# ---------------------------------------------------------------------------


class sppasBaseVolume(object):
    """A base class to estimate the volume.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2016  Brigitte Bigi

    """
    def __init__(self, win_len=0.01):
        """Create a sppasBaseVolume instance.

        :param win_len: (float) Size of the window (in seconds)

        """
        self._volumes = list()
        self._rms = 0
        self._winlen = float(win_len)

    # -----------------------------------------------------------------------

    def get_winlen(self):
        """Return the windows length used to estimate the volume values.
        
        :returns: (float) Duration in seconds.

        """
        return self._winlen

    # -----------------------------------------------------------------------

    def volume(self):
        """Return the global volume value (rms).
        
        :returns: (int)

        """
        return self._rms

    # -----------------------------------------------------------------------

    def volume_at(self, index):
        """Return the value of the volume at a given index.
        
        :returns: (int)

        """
        return self._volumes[index]

    # -----------------------------------------------------------------------

    def volumes(self):
        """Return the list of volume values (rms).
        
        :returns: (list)

        """
        return self._volumes

    # -----------------------------------------------------------------------

    def len(self):
        """Return the number of RMS values that were estimated.
        
        :returns: (int)

        """
        return len(self._volumes)

    # -----------------------------------------------------------------------

    def min(self):
        """Return the minimum of RMS values.
        
        :returns: (int)

        """
        return central.fmin(self._volumes)

    # -----------------------------------------------------------------------

    def max(self):
        """Return the maximum of RMS values.
        
        :returns: (int)

        """
        return central.fmax(self._volumes)

    # -----------------------------------------------------------------------

    def mean(self):
        """Return the mean of RMS values.
        
        :returns: (float)

        """
        return central.fmean(self._volumes)

    # -----------------------------------------------------------------------

    def median(self):
        """Return the median of RMS values.
        
        :returns: (float)

        """
        return central.fmedian(self._volumes)

    # -----------------------------------------------------------------------

    def variance(self):
        """Return the sample variance of RMS values.
        
        :returns: (int)

        """
        return variability.lvariance(self._volumes)

    # -----------------------------------------------------------------------

    def stdev(self):
        """Return the standard deviation of RMS values.
        
        :returns: (int)

        """
        return variability.lstdev(self._volumes)

    # -----------------------------------------------------------------------

    def coefvariation(self):
        """Return the coefficient of variation of RMS values.
         
        :returns: (float) coef variation given as a percentage.

        """
        return moment.lvariation(self._volumes)

    # -----------------------------------------------------------------------

    def zscores(self):
        """Return the z-scores of RMS values.

        The z-score determines the relative location of a data value.
        
        :returns: (list of float)

        """
        return variability.lzs(self._volumes)

    # -----------------------------------------------------------------------

    def stderr(self):
        """Calculate the standard error of the RMS values.

        :returns: (float)

        """
        return variability.lsterr(self._volumes)

    # -----------------------------------------------------------------------

    def __len__(self):
        return len(self._volumes)

    def __iter__(self):
        for x in self._volumes:
            yield x

    def __getitem__(self, i):
        return self._volumes[i]
