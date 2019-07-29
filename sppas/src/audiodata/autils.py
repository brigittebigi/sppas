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

    src.audiodata.autils.py
    ~~~~~~~~~~~~~~~~~~~~~~~~

"""

from .aio import open as audio_open
from .aio import save as audio_save

from .audio import sppasAudioPCM
from .channel import sppasChannel
from .channelframes import sppasChannelFrames
from .channelformatter import sppasChannelFormatter
from .channelsilence import sppasChannelSilence

# ------------------------------------------------------------------------


def frames2times(frames, framerate):
    """Convert a list of frame' into a list of time' values.

    :param frames: (list) tuples (from_pos,to_pos)
    :returns: a list of tuples (from_time,to_time)

    """
    list_times = []
    fm = float(framerate)

    for (s, e) in frames:
        fs = float(s) / fm
        fe = float(e) / fm
        list_times.append((fs, fe))

    return list_times

# ------------------------------------------------------------------


def times2frames(times, framerate):
    """Convert a list of time' into a list of frame' values.

    :param listframes: (list) tuples (from_time,to_time)
    :returns: a list of tuples (from_pos,to_pos)

    """
    list_frames = []
    fm = float(framerate)
    for (s, e) in times:
        fs = int(s*fm)
        fe = int(e*fm)
        list_frames.append((fs, fe))

    return list_frames

# ------------------------------------------------------------------


def extract_audio_channel(input_audio, idx):
    """Return the channel of a specific index from an audio file name.

    :param inputaudio: (str) Audio file name.
    :param idx: (int) Channel index

    """
    idx = int(idx)
    audio = audio_open(input_audio)
    i = audio.extract_channel(idx)
    channel = audio.get_channel(i)
    audio.close()

    return channel

# ------------------------------------------------------------------------


def extract_channel_fragment(channel, fromtime, totime, silence=0.):
    """Extract a fragment of a channel in the interval [fromtime,totime].
    Eventually, surround it by silences.

    :param channel:  (sppasChannel)
    :param fromtime: (float) From time value in seconds.
    :param totime:   (float) To time value in seconds.
    :param silence:  (float) Duration value in seconds.

    """
    framerate = channel.get_framerate()

    # Extract the fragment of the channel
    startframe = int(fromtime*framerate)
    toframe = int(totime*framerate)
    fragmentchannel = channel.extract_fragment(begin=startframe, end=toframe)

    # Get all the frames of this fragment
    nbframes = fragmentchannel.get_nframes()
    cf = sppasChannelFrames(fragmentchannel.get_frames(nbframes))

    # surround by silences
    if silence > 0.:
        cf.prepend_silence(silence*framerate)
        cf.append_silence(silence*framerate)

    return sppasChannel(16000, 2, cf.get_frames())

# ------------------------------------------------------------------------


def search_channel_speech(channel, winlenght=0.010, minsildur=0.200, mintrackdur=0.300, shiftdurstart=0.010, shiftdurend=0.010):
    """Return a list of tracks (i.e. speech intervals where energy is high enough).
    Use only default parameters.

    :param channel: (sppasChannel) The channel we'll try to find tracks
    :returns: A list of tuples (fromtime,totime)

    """
    chansil = sppasChannelSilence(channel, winlenght)
    chansil.search_silences(threshold=0, mintrackdur=0.08)
    chansil.filter_silences(minsildur)
    tracks = chansil.extract_tracks(mintrackdur, shiftdurstart, shiftdurend)
    tracks.append((channel.get_nframes(), channel.get_nframes()))
    trackstimes = frames2times(tracks, channel.get_framerate())

    return trackstimes

# ------------------------------------------------------------------------


def format_channel(channel, framerate, sampwith):
    """Return a channel with the requested framerate and sampwidth.

    :param channel: (sppasChannel)

    """
    fm = channel.get_framerate()
    sp = channel.get_sampwidth()
    if fm != framerate or sp != sampwith:
        formatter = sppasChannelFormatter(channel)
        formatter.set_framerate(framerate)
        formatter.set_sampwidth(sampwith)
        formatter.convert()
        return formatter.get_channel()

    return channel

# ------------------------------------------------------------------------


def write_channel(audioname, channel):
    """Write a channel as an audio file.

    :param audioname: (str) Audio file name to write
    :param channel: (sppasChannel) Channel to be saved

    """
    audio_out = sppasAudioPCM()
    audio_out.append_channel(channel)
    audio_save(audioname, audio_out)

