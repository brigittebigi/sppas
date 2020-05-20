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

    src.audiodata.channelsilence.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""

from .channel import sppasChannel
from .channelvolume import sppasChannelVolume

# ----------------------------------------------------------------------------


class sppasChannelSilence(object):
    """
    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2017  Brigitte Bigi
    :summary:      This class implements the silence finding on a channel.

    """
    def __init__(self, channel, win_len=0.01):
        """Create a sppasChannelSilence instance.

        :param channel (sppasChannel) the input channel object
        :param win_len (float) duration of a window for the estimation of the volume

        """
        self._channel = channel
        self._volume_stats = sppasChannelVolume(channel, win_len)
        self.__silences = []

    # -----------------------------------------------------------------------

    def get_channel(self):
        """Return the sppasChannel."""

        return self._channel

    # -----------------------------------------------------------------------

    def get_volstats(self):
        """Return the sppasChannelVolume of the sppasChannel."""

        return self._volume_stats

    # -----------------------------------------------------------------------
    # Utility method
    # -----------------------------------------------------------------------

    def track_data(self, tracks):
        """Get the track data: a set of frames for each track.

        :param tracks: (list of tuples) List of (from_pos,to_pos)

        """
        nframes = self._channel.get_nframes()
        for from_pos, to_pos in tracks:
            if nframes < from_pos:
                # Accept a "DELTA" of 10 frames, in case of corrupted data.
                if nframes < from_pos-10:
                    raise ValueError("Position %d not in range(%d)" % (from_pos, nframes))
                else:
                    from_pos = nframes
            # Go to the provided position
            self._channel.seek(from_pos)
            # Keep in mind the related frames
            yield self._channel.get_frames(to_pos - from_pos)

    # -----------------------------------------------------------------------

    def refine(self, pos, threshold, win_length=0.005, direction=1):
        """Refine the position of a silence around a given position.

        :param pos: (int) Initial position of the silence
        :param threshold: (int) RMS threshold value for a silence
        :param win_length: (float) WindowsInstaller duration to estimate the RMS
        :param direction: (int)
        :returns: new position

        """
        delta = int(self._volume_stats.get_winlen() * self._channel.get_framerate())
        from_pos = max(pos-delta, 0)
        self._channel.seek(from_pos)
        frames = self._channel.get_frames(delta*2)
        c = sppasChannel(self._channel.get_framerate(), self._channel.get_sampwidth(), frames)
        vol_stats = sppasChannelVolume(c, win_length)

        if direction == 1:
            for i, v in enumerate(vol_stats):
                if v > threshold:
                    return from_pos + i*(int(win_length*self._channel.get_framerate()))
        if direction == -1:
            i = len(vol_stats)
            for v in reversed(vol_stats):
                if v > threshold:
                    return from_pos + (i*(int(win_length*self._channel.get_framerate())))
                i -= 1

        return pos

    # -----------------------------------------------------------------------

    def extract_tracks(self, mintrackdur=0.300, shiftdurstart=0.010, shiftdurend=0.010):
        """Return a list of tuples (from_pos,to_pos) of the tracks.

        :param mintrackdur: (float) The minimum duration for a track (in seconds)
        :param shiftdurstart: (float) The time to remove to the start boundary (in seconds)
        :param shiftdurend: (float) The time to add to the end boundary (in seconds)

        """
        tracks = []

        # No silence: Only one track!
        if len(self.__silences) == 0:
            tracks.append((0, self._channel.get_nframes()))
            return tracks

        # Convert values: time into frame
        delta = int(mintrackdur * self._channel.get_framerate())
        shiftstart = int(shiftdurstart * self._channel.get_framerate())
        shiftend = int(shiftdurend * self._channel.get_framerate())
        from_pos = 0

        for to_pos, next_from in self.__silences:

            shift_from_pos = max(from_pos - shiftstart, 0)
            shift_to_pos = min(to_pos + shiftend, self._channel.get_nframes())

            if (shift_to_pos-shift_from_pos) >= delta:
                # Track is long enough to be considered a track.
                tracks.append((int(shift_from_pos), int(shift_to_pos)))

            from_pos = next_from

        # Last track after the last silence
        # (if the silence does not end at the end of the channel)
        to_pos = self._channel.get_nframes()
        if (to_pos - from_pos) >= delta:
            tracks.append((int(from_pos), int(to_pos)))

        return tracks

    # -----------------------------------------------------------------------
    # New silence detection
    # -----------------------------------------------------------------------

    def search_threshold_vol(self):
        """Try to fix optimally the threshold for speech/silence segmentation.
        This is a simple observation of the distribution of rms values.

        :returns: (int) volume value

        """
        vmin = max(self._volume_stats.min(), 0)  # provide negative values
        vmean = self._volume_stats.mean()
        vcvar = 1.5 * self._volume_stats.coefvariation()

        # alternative, in case the audio is not as good as expected!
        # (too low volume, or outliers which make the coeff variation very high)
        alt = (vmean-vmin) / 5.
        if alt > vcvar or vcvar > vmean:
            vcvar = alt

        return vmin + int((vmean - vcvar))

    # -----------------------------------------------------------------------

    def search_silences(self, threshold=0, mintrackdur=0.08):
        """Search windows with a volume lesser than a given threshold.

        :param threshold: (int) Expected minimum volume (rms value)
        If threshold is set to 0, search_minvol() will assign a value.
        :param mintrackdur: (float) The very very minimum duration for
        a track (in seconds).

        """
        if threshold == 0:
            threshold = self.search_threshold_vol()

        # This scans the volumes whether it is lower than threshold,
        # if it is it is written to silence.
        self.__silences = []
        inside = False
        idxbegin = 0
        ignored = 0
        delta = int(mintrackdur / self._volume_stats.get_winlen())

        for i, v in enumerate(self._volume_stats):
            if v < threshold:
                if inside is False:
                    # It's the beginning of a block of zero volumes
                    idxbegin = i
                    inside = True
            else:
                if inside is True:
                    # It's the end of a block of non-zero volumes...
                    # or not if the track is very short!
                    if (i-idxbegin) > delta:
                        inside = False
                        idxend = i - ignored  # we not use -1 because we want the end of the frame
                        from_pos = int(idxbegin * self._volume_stats.get_winlen() * self._channel.get_framerate())
                        to_pos = int(idxend * self._volume_stats.get_winlen() * self._channel.get_framerate())

                        # Find the boundaries with a better precision
                        w = self._volume_stats.get_winlen() / 4.
                        from_pos = self.refine(from_pos, threshold, w, direction=-1)
                        to_pos = self.refine(to_pos, threshold, w, direction=1)

                        self.__silences.append((from_pos, to_pos))
                        ignored = 0
                    else:
                        ignored += 1

        # Last interval
        if inside is True:
            start_pos = int(idxbegin * self._volume_stats.get_winlen() * self._channel.get_framerate())
            end_pos = self._channel.get_nframes()
            self.__silences.append((start_pos, end_pos))

        return threshold

    # -----------------------------------------------------------------------

    def filter_silences(self, minsildur=0.200):
        """Filtered the current silences.

        :param minsildur: (float) Minimum silence duration in seconds

        """
        if len(self.__silences) == 0:
            return 0

        filteredsil = []
        for (start_pos, end_pos) in self.__silences:
            sildur = float(end_pos-start_pos) / float(self._channel.get_framerate())
            if sildur > minsildur:
                filteredsil.append((start_pos, end_pos))

        self.__silences = filteredsil

        return len(self.__silences)

    # -----------------------------------------------------------------------

    def set_silences(self, silences):
        """Fix manually silences!

        :param silences: (list of tuples (start_pos,end_pos))

        """
        self.__silences = silences

    # -----------------------------------------------------------------------

    def reset_silences(self):
        """Reset silences."""

        self.__silences = []

    # -----------------------------------------------------------------------
    # overloads
    # -----------------------------------------------------------------------

    def __len__(self):
        return len(self.__silences)

    def __iter__(self):
        for x in self.__silences:
            yield x

    def __getitem__(self, i):
        return self.__silences[i]
