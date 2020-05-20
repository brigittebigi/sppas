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

    src.annotations.SeachIPUs.silences.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""

import logging
from sppas.src.audiodata.channel import sppasChannel
from sppas.src.audiodata.channelvolume import sppasChannelVolume

# ---------------------------------------------------------------------------


class sppasSilences(object):
    """Silence search on a channel of an audio file.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2018  Brigitte Bigi

    Silences are stored in a list of (from_pos,to_pos) values, indicating
    the frame from which the silences are beginning and ending respectively.

    """

    def __init__(self, channel, win_len=0.020, vagueness=0.005):
        """Create a sppasSilences instance.

        :param channel: (sppasChannel) the input channel
        :param win_len: (float) duration of a window
        :param vagueness: (float) WindowsInstaller length to estimate the boundaries.

        Maximum value of vagueness is win_len.
        The duration of a window (win_len) is relevant for the estimation
        of the rms values.

        Radius (see sppasPoint) is the 2*vagueness of the boundaries.

        """
        self._win_len = win_len
        self._vagueness = vagueness

        self._channel = None
        self.__volume_stats = None
        self.__silences = list()
        if channel is not None:
            self.set_channel(channel)

    # -----------------------------------------------------------------------
    # Getters and setters
    # -----------------------------------------------------------------------

    def set_vagueness(self, vagueness):
        """WindowsInstaller length to estimate the boundaries.

        :param vagueness: (float) Maximum value of radius is win_len.

        """
        self._vagueness = min(vagueness, self._win_len)

    # -----------------------------------------------------------------------

    def get_vagueness(self):
        """Get the vagueness value (=2*radius)."""
        return self._vagueness

    # -----------------------------------------------------------------------

    def set_channel(self, channel):
        """Set a channel, then reset all previous results.

        :param channel: (sppasChannel)

        """
        if isinstance(channel, sppasChannel) is False:
            raise TypeError('Expected a sppasChannel, got {:s} instead'
                            ''.format(str(type(channel))))

        self._channel = channel
        self.__volume_stats = sppasChannelVolume(channel, self._win_len)
        self.__silences = list()

    # -----------------------------------------------------------------------

    def get_volstats(self):
        """Return the sppasChannelVolume() estimated on the channel."""
        return self.__volume_stats

    # -----------------------------------------------------------------------

    def set_silences(self, silences):
        """Fix manually silences.

        To be use carefully!

        :param silences: (list of tuples (start_pos, end_pos))

        """
        # check if it's really a list of tuples
        if isinstance(silences, list) is False:
            raise TypeError('Expected a list, got {:s}'
                            ''.format(type(silences)))
        for v in silences:
            v[0] = int(v[0])
            v[1] = int(v[1])

        # ok, assign value
        self.__silences = silences

    # -----------------------------------------------------------------------

    def reset_silences(self):
        """Reset silences to an empty list."""
        self.__silences = list()

    # -----------------------------------------------------------------------
    # Utility methods for tracks
    # -----------------------------------------------------------------------

    def track_data(self, tracks):
        """Yield the track data: a set of frames for each track.

        :param tracks: (list of tuples) List of (from_pos,to_pos)

        """
        if self._channel is None:
            return

        nframes = self._channel.get_nframes()
        for from_pos, to_pos in tracks:
            if nframes < from_pos:
                # Accept a "DELTA" of 10 frames, in case of corrupted data.
                if nframes < from_pos-10:
                    raise ValueError("Position {:d} not in range({:d})"
                                     "".format(from_pos, nframes))
                else:
                    from_pos = nframes

            # Go to the provided position
            self._channel.seek(from_pos)
            # Keep in mind the related frames
            yield self._channel.get_frames(to_pos - from_pos)

    # -----------------------------------------------------------------------

    def extract_tracks(self, min_track_dur, shift_dur_start, shift_dur_end):
        """Return the tracks, deduced from the silences and track constrains.

        :param min_track_dur: (float) The minimum duration for a track
        :param shift_dur_start: (float) The time to remove to the start bound
        :param shift_dur_end: (float) The time to add to the end boundary
        :returns: list of tuples (from_pos,to_pos)

        Duration is in seconds.

        """
        if self._channel is None:
            return []

        tracks = list()

        # No silence: Only one track!
        if len(self.__silences) == 0:
            tracks.append((0, self._channel.get_nframes()))
            return tracks

        # Convert values from time to frames
        delta = int(min_track_dur * self._channel.get_framerate())
        shift_start = int(shift_dur_start * self._channel.get_framerate())
        shift_end = int(shift_dur_end * self._channel.get_framerate())
        from_pos = 0

        for to_pos, next_from in self.__silences:

            if (to_pos-from_pos) >= delta:
                # Track is long enough to be considered an IPU.
                # Apply the shift values
                shift_from_pos = max(from_pos - shift_start, 0)
                shift_to_pos = min(to_pos + shift_end,
                                   self._channel.get_nframes())
                # Store as it
                tracks.append((int(shift_from_pos), int(shift_to_pos)))

            from_pos = next_from

        # Last track after the last silence
        # (if the silence does not end at the end of the channel)
        to_pos = self._channel.get_nframes()
        if (to_pos - from_pos) >= delta:
            tracks.append((int(from_pos), int(to_pos)))

        return tracks

    # -----------------------------------------------------------------------
    # Silence detection
    # -----------------------------------------------------------------------

    def fix_threshold_vol(self):
        """Fix the threshold for tracks/silences segmentation.

        This is an observation of the distribution of rms values.

        :returns: (int) volume value

        """
        volumes = sorted(self.__volume_stats.volumes())
        vmin = max(self.__volume_stats.min(), 0)  # provide negative values
        logging.info("RMS min={:d}".format(vmin))
        vmean = self.__volume_stats.mean()
        logging.info("RMS mean={:.2f}".format(vmean))
        vmedian = self.__volume_stats.median()
        logging.info("RMS median={:2f}".format(vmedian))
        vvar = self.__volume_stats.coefvariation()
        logging.info("RMS coef. var={:2f}".format(vvar))

        # Remove very high volume values (outliers)
        # only for distributions with a too high variability
        if vmedian > vmean:
            logging.debug('The RMS distribution need to be normalized.')

            rms_threshold = volumes[int(0.85 * len(volumes))]
            nb = 0
            for i, v in enumerate(self.__volume_stats):
                if v > rms_threshold:
                    self.__volume_stats.set_volume_value(i, rms_threshold)
                    nb += 1

            vmean = self.__volume_stats.mean()
            vmedian = self.__volume_stats.median()
            vvar = self.__volume_stats.coefvariation()

        # Normal situation... (more than 75% of the files!!!)
        vcvar = 1.5 * vvar
        threshold = int(vmin) + int((vmean - vcvar))

        # Alternative, in case the audio is not as good as expected!
        # (too low volume, or outliers which make the coeff var very high)
        if vmedian > vmean:
            # often means a lot of low volume values and some very high
            median_index = 0.55 * len(volumes)
            threshold = volumes[int(median_index)]
            logging.debug(' ... threshold: estimator exception 1 - median > mean')
        elif vcvar > vmean:
            if vmedian < (vmean * 0.2):
                # for distributions with a too low variability
                threshold = int(vmin) + int((vmean - vmedian))
                logging.debug(' ... threshold: estimator exception 2 - median < 0.2*mean')
            else:
                # often means some crazy values (very rare)
                threshold = int(vmin) + int(0.2 * float(vmean))
                logging.debug(' ... threshold: estimator exception 3 - vcvar > mean')
        else:
            logging.debug(' ... threshold: normal estimator')

        logging.info('Threshold value for the search of silences: {:d}'
                     ''.format(threshold))

        return threshold

    # -----------------------------------------------------------------------

    def search_silences(self, threshold=0):
        """Search windows with a volume lesser than a given threshold.

        This is then a search for silences. All windows with a volume
        higher than the threshold are considered as tracks and not included
        in the result. Block of silences lesser than min_sil_dur are
        also considered tracks.

        :param threshold: (int) Expected minimum volume (rms value)
        If threshold is set to 0, search_minvol() will assign a value.
        :returns: threshold

        """
        if self._channel is None:
            return 0

        if threshold == 0:
            threshold = self.fix_threshold_vol()

        # This scans the volumes whether it is lower than threshold,
        # and if true, it is written to silence.
        self.__silences = list()
        inside = False  # inside a silence or not
        idx_begin = 0
        nframes = self.__volume_stats.get_winlen() * self._channel.get_framerate()

        i = 0
        for v in self.__volume_stats:
            if v < threshold:
                # It's a small enough volume to consider the window a silence
                if inside is False:
                    # We consider it like the beginning of a block of silences
                    idx_begin = i
                    inside = True
                # else: it's the continuation of a silence

            else:
                # It's a big enough volume to consider the window an IPU
                if inside is True:
                    # It's the first window of an IPU
                    # so the previous window was the end of a silence
                    from_pos = int(idx_begin * nframes)
                    to_pos = int((i - 1) * nframes)
                    self.__silences.append((from_pos, to_pos))
                    inside = False

                # else: it's the continuation of an IPU

            i += 1

        # Last interval
        if inside is True:
            start_pos = int(idx_begin *
                            self.__volume_stats.get_winlen() *
                            self._channel.get_framerate())
            end_pos = self._channel.get_nframes()
            self.__silences.append((start_pos, end_pos))

        # Filter the current very small windows
        self.__filter_silences(2. * self._win_len)

        return threshold

    # -----------------------------------------------------------------------

    def filter_silences(self, threshold, min_sil_dur=0.200):
        """Filter the current silences.

        :param threshold: (int) Expected minimum volume (rms value)
        If threshold is set to 0, search_minvol() will assign a value.
        :param min_sil_dur: (float) Minimum silence duration in seconds
        :returns: Number of silences with the expected minimum duration

        """
        if len(self.__silences) == 0:
            return 0

        if threshold == 0:
            threshold = self.fix_threshold_vol()

        # Adjust boundaries of the silences
        adjusted = list()
        for (from_pos, to_pos) in self.__silences:
            adjusted.append((
                self.__adjust_bound(from_pos, threshold, direction=-1),
                to_pos))
        self.__silences = adjusted

        # Re-filter
        self.__filter_silences(min_sil_dur)

        return len(self.__silences)

    # -----------------------------------------------------------------------

    def filter_silences_from_tracks(self, min_track_dur=0.60):
        """Filter the given silences to remove very small tracks.

        :param min_track_dur: (float) Minimum duration of a track
        :returns: filtered silences

        """
        if len(self.__silences) < 3:
            return
        tracks = self.extract_tracks(min_track_dur, 0., 0.)

        # Remove too short tracks
        keep_tracks = list()
        for (from_track, to_track) in tracks:
            delta = float((to_track - from_track)) / float(self._channel.get_framerate())
            if delta > min_track_dur:
                keep_tracks.append((from_track, to_track))

        # Re-create silences from the selected tracks
        filtered_sil = list()
        # first silence
        if self.__silences[0][0] < keep_tracks[0][0]:
            filtered_sil.append((self.__silences[0][0], self.__silences[0][1]))
        # silences between tracks
        prev_track_end = -1
        for (from_track, to_track) in keep_tracks:
            if prev_track_end > -1:
                filtered_sil.append((int(prev_track_end), int(from_track)))
            prev_track_end = to_track
        # last silence
        to_pos = self._channel.get_nframes()
        to_track = tracks[-1][1]
        if (to_pos - to_track) > 0:
            filtered_sil.append((int(to_track), int(to_pos)))

        self.__silences = filtered_sil

    # -----------------------------------------------------------------------

    def __filter_silences(self, min_sil_dur=0.200):
        """Filter the given silences.

        :param min_sil_dur: (float) Minimum silence duration in seconds
        :returns: filtered silences

        """
        filtered_sil = list()
        for (start_pos, end_pos) in self.__silences:
            sil_dur = float(end_pos-start_pos) / \
                      float(self._channel.get_framerate())
            if sil_dur > min_sil_dur:
                filtered_sil.append((start_pos, end_pos))

        self.__silences = filtered_sil

    # -----------------------------------------------------------------------

    def __adjust_bound(self, pos, threshold, direction=0):
        """Adjust the position of a silence around a given position.

        Here "around" the position means in a range of 18 windows,
        i.e. 6 before + 12 after the position.

        :param pos: (int) Initial position of the silence
        :param threshold: (int) RMS threshold value for a silence
        :param direction: (int)

        :returns: new position

        """
        if self._vagueness == self._win_len:
            return pos
        if direction not in (-1, 1):
            return pos

        # Extract the frames of the windows around the pos
        delta = int(1.5 * self.__volume_stats.get_winlen() * self._channel.get_framerate())
        start_pos = int(max(pos - delta, 0))
        self._channel.seek(start_pos)
        frames = self._channel.get_frames(int(delta * 3))

        # Create a channel and estimate volume values with a window
        # of vagueness (i.e. 4 times more precise than the original)
        c = sppasChannel(self._channel.get_framerate(),
                         self._channel.get_sampwidth(),
                         frames)
        vol_stats = sppasChannelVolume(c, self._vagueness)

        # we'll see if we can reduce the silence

        if direction == 1:  # silence | ipu
            for idx, v in enumerate(vol_stats):
                shift = idx * (int(self._vagueness * self._channel.get_framerate()))
                if v > threshold:
                    return start_pos + int(shift)

        elif direction == -1:  # ipu | silence
            idx = len(vol_stats)  # = 12 (3 windows of 4 vagueness)
            for v in reversed(vol_stats):
                if v > threshold:
                    shift = idx * (int(self._vagueness * self._channel.get_framerate()))
                    return start_pos + int(shift)
                idx -= 1

        return pos

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
