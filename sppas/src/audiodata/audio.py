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

    src.audiodata.audio.py
    ~~~~~~~~~~~~~~~~~~~~~~~

    Pulse-code modulation (PCM) is a method used to digitally represent sampled
    analog signals. A PCM signal is a sequence of digital audio samples
    containing the data providing the necessary information to reconstruct the
    original analog signal. Each sample represents the amplitude of the signal
    at a specific point in time, and the samples are uniformly spaced in time.
    The amplitude is the only information explicitly stored in the sample

    A PCM stream has two basic properties that determine the stream's fidelity
    to the original analog signal: the sampling rate, which is the number of
    times per second that samples are taken; and the bit depth, which
    determines the number of possible digital values that can be used to
    represent each sample.

    For speech analysis, recommended sampling rate are 16000 (for automatic
    analysis) or 48000 (for manual analysis); and recommended sample depths
    are 16 (for automatic analysis) or 32 bits (for both automatic and manual
    analysis) per sample.

"""

from .audioframes import sppasAudioFrames
from .audioconvert import sppasAudioConverter
from .audiodataexc import AudioError
from .audiodataexc import AudioDataError
from .audiodataexc import ChannelIndexError
from .audiodataexc import MixChannelError
from .channel import sppasChannel
from .channelsmixer import sppasChannelMixer

# ---------------------------------------------------------------------------


class sppasAudioPCM(object):
    """An audio manager.

    :author:       Nicolas Chazeau, Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2018  Brigitte Bigi

    These variables are user gettable through appropriate methods:
        - nchannels -- the number of audio channels
        - framerate -- the sampling frequency
        - sampwidth -- the number of bytes per audio sample (1, 2 or 4)
        - nframes   -- the number of frames
        - params    -- parameters of the wave file
        - filename  -- the name of the wave file

    The audiofp member is assigned by the IO classes (WaveIO, AifIO, SunauIO).
    It is expected that it can access the following methods:
        - readframes()
        - writeframes()
        - getsampwidth()
        - getframerate()
        - getnframes()
        - getnchannels()
        - setpos()
        - tell()
        - rewind()

    """

    def __init__(self):
        """Create a new sppasAudioPCM instance."""
        super(sppasAudioPCM, self).__init__()

        # The audio file pointer
        self._audio_fp = None

        # The list of loaded channels of this audio
        self._channels = list()

    # ----------------------------------------------------------------------

    def set(self, other):
        """Set a new sppasAudioPCM() instance.

        It can be set either with an audio file pointer, or a list of
        channels or both.

        :param other: (sppasAudioPCM) the other sppasAudioPCM to set

        """
        self._audio_fp = other.get_audiofp()
        self._channels = other.get_channels()

    # ----------------------------------------------------------------------

    def get_channels(self):
        """Return the list of uploaded channels.

        :returns: (list) channels

        """
        return self._channels

    # ----------------------------------------------------------------------

    def get_audiofp(self):
        """Return the audio file pointer.

        :returns: audio file pointer

        """
        return self._audio_fp

    # ----------------------------------------------------------------------
    # Uploaded channels
    # ----------------------------------------------------------------------

    def remove_channel(self, channel):
        """Remove a channel from the list of uploaded channels.

        :param channel: (sppasChannel) the channel to remove

        """
        self._channels.remove(channel)

    # ----------------------------------------------------------------------

    def pop_channel(self, idx):
        """Pop a channel at the position given from the list of uploaded channels.

        :param idx: (int) the index of the channel to remove

        """
        idx = int(idx)
        self._channels.pop(idx)

    # ----------------------------------------------------------------------

    def insert_channel(self, idx, channel):
        """Insert a channel at the position given in the list of uploaded channels.

        :param idx: (int) the index where the channel has to be inserted
        :param channel: (sppasChannel) the channel to insert

        """
        idx = int(idx)
        self._channels.insert(idx, channel)

    # ----------------------------------------------------------------------

    def get_channel(self, idx):
        """Get an uploaded channel.

        :param idx: (int) the index of the channel to return
        :returns: (sppasChannel)

        """
        idx = int(idx)
        return self._channels[idx]

    # ----------------------------------------------------------------------

    def append_channel(self, channel):
        """Append a channel to the list of uploaded channels.

        :param channel: (sppasChannel) the channel to append
        :returns: index of the channel

        """
        self._channels.append(channel)
        return len(self._channels) - 1

    # ----------------------------------------------------------------------

    def extract_channel(self, index=0):
        """Extract a channel from the Audio File Pointer.

        Append the channel into the list of channels.

        Frames are stored into a sppasChannel() instance.
        Index of the channel in the audio file:
        0 = 1st channel (left); 1 = 2nd channel (right); 2 = 3rd channel...

        :param index: (int) The index of the channel to extract
        :returns: the index of the sppasChannel() in the list

        """
        if self._audio_fp is None:
            raise AudioError

        index = int(index)
        if index < 0:
            raise ChannelIndexError(index)

        nc = self.get_nchannels()
        self.seek(0)
        data = self.read_frames(self.get_nframes())

        if nc == 0:
            raise AudioDataError

        if index+1 > nc:
            raise ChannelIndexError(index)

        if nc == 1:
            channel = sppasChannel(self.get_framerate(),
                                   self.get_sampwidth(),
                                   data)
            return self.append_channel(channel)

        frames = b""
        sw = self.get_sampwidth()
        for i in range(index*sw, len(data), nc*sw):
            frames += data[i:i+sw]
        channel = sppasChannel(self.get_framerate(),
                               self.get_sampwidth(),
                               frames)

        return self.append_channel(channel)

    # ----------------------------------------------------------------------

    def extract_channels(self):
        """Extract all channels from the Audio File Pointer.

        Append the extracted channels to the list of channels.

        """
        if self._audio_fp is None:
            raise AudioError

        nc = self.get_nchannels()
        sw = self.get_sampwidth()
        self.seek(0)
        data = self.read_frames(self.get_nframes())

        if nc == 0:
            raise AudioDataError

        for index in range(nc):
            frames = b""
            for i in range(index*sw, len(data), nc*sw):
                frames = frames + data[i:i+sw]
            channel = sppasChannel(self.get_framerate(),
                                   self.get_sampwidth(),
                                   frames)
            self.append_channel(channel)

    # ----------------------------------------------------------------------
    # Read content, for audiofp
    # ----------------------------------------------------------------------

    def read(self):
        """Read all frames of the audio file.

        :returns: (str) frames

        """
        return self.read_frames(self.get_nframes())

    # ----------------------------------------------------------------------

    def read_frames(self, nframes):
        """Read n frames from the audio file.

        :param nframes: (int) the number of frames to read
        :returns: (str) frames

        """
        if self._audio_fp is None:
            raise AudioError

        return self._audio_fp.readframes(nframes)

    # ----------------------------------------------------------------------

    def read_samples(self, nframes):
        """Read the samples from the audio file.

        :param nframes: (int) the number of frames to read
        :returns: (list of list) list of samples of each channel

        """
        if self._audio_fp is None:
            raise AudioError

        return sppasAudioConverter().unpack_data(self.read_frames(nframes),
                                                 self.get_sampwidth(),
                                                 self.get_nchannels())

    # ----------------------------------------------------------------------
    # Getters, for audiofp
    # ----------------------------------------------------------------------

    def get_sampwidth(self):
        """Return the sample width of the Audio File Pointer.

        :returns: (int) sample width of the audio file

        """
        if self._audio_fp is None:
            if len(self._channels) > 0:
                return self._channels[0].get_sampwidth()
            else:
                raise AudioDataError

        return self._audio_fp.getsampwidth()

    # ----------------------------------------------------------------------

    def get_framerate(self):
        """Return the frame rate of the Audio File Pointer.

        :returns: (int) frame rate of the audio file

        """
        if self._audio_fp is None:
            if len(self._channels) > 0:
                return self._channels[0].get_framerate()
            else:
                raise AudioDataError

        return self._audio_fp.getframerate()

    # ----------------------------------------------------------------------

    def get_nframes(self):
        """Return the number of frames of the Audio File Pointer.

        :returns: (int) number of frames of the audio file

        """
        if self._audio_fp is None:
            if len(self._channels) > 0:
                return self._channels[0].get_nframes()
            else:
                raise AudioDataError

        return self._audio_fp.getnframes()

    # ----------------------------------------------------------------------

    def get_nchannels(self):
        """Return the number of channels of the Audio File Pointer.

        :returns: (int) number of channels of the audio file

        """
        if self._audio_fp is None:
            if len(self._channels) > 0:
                return len(self._channels)
            else:
                raise AudioDataError

        return self._audio_fp.getnchannels()

    # ----------------------------------------------------------------------

    def get_duration(self):
        """Return the duration of the Audio File Pointer.

        :returns: (float) duration of the audio file (in seconds)

        """
        if self._audio_fp is None:
            if len(self._channels) > 0:
                return self._channels[0].get_duration()
            else:
                raise AudioDataError

        return float(self.get_nframes())/float(self.get_framerate())

    # ----------------------------------------------------------------------

    def rms(self):
        """Return the root mean square of the whole file.

        :returns: (int) rms of the audio file

        """
        pos = self.tell()
        self.seek(0)
        a = sppasAudioFrames(self.read_frames(self.get_nframes()),
                             self.get_sampwidth(),
                             self.get_nchannels())
        self.seek(pos)

        return a.rms()

    # ----------------------------------------------------------------------

    def clipping_rate(self, factor):
        """Return the clipping rate of the frames.

        :param factor: (float) An interval to be more precise on clipping rate.
        It will consider that all frames outside the interval are clipped.
        Factor has to be between 0 and 1.
        :returns: (float)

        """
        pos = self.tell()
        self.seek(0)
        a = sppasAudioFrames(self.read_frames(self.get_nframes()),
                             self.get_sampwidth())
        self.seek(pos)

        return a.clipping_rate(factor)

    # ----------------------------------------------------------------------
    # Navigate into the audiofp
    # ----------------------------------------------------------------------

    def seek(self, pos):
        """Fix the reader pointer position.

        :param pos: (int) the position to set.

        """
        if self._audio_fp is None:
            raise AudioError

        self._audio_fp.setpos(pos)

    # ----------------------------------------------------------------------

    def tell(self):
        """Get the reader pointer position.

        :returns: (int) the current position

        """
        if self._audio_fp is None:
            raise AudioError

        return self._audio_fp.tell()

    # ----------------------------------------------------------------------

    def rewind(self):
        """Set reader position at the beginning of the file."""
        if self._audio_fp is None:
            raise AudioError

        return self._audio_fp.rewind()

    # ----------------------------------------------------------------------
    # Verify the compatibility between the channels
    # ----------------------------------------------------------------------

    def verify_channels(self):
        """Check that the uploaded channels have the same parameters.

        Check the frame rate, sample width and number of frames.

        :returns: (bool)

        """
        mixer = sppasChannelMixer()
        f = 1./len(self._channels)
        for c in self._channels:
            mixer.append_channel(c, f)
        try:
            mixer.check_channels()
        except MixChannelError:
            return False

        return True

    # ------------------------------------------------------------------------
    # Input/Output
    # ------------------------------------------------------------------------

    def open(self, filename):
        """Open an audio file."""
        name = self.__class__.__name__
        raise NotImplementedError("{:s} does not support open()."
                                  "".format(name))

    # ------------------------------------------------------------------------

    def save(self, filename):
        """Save an audio file."""
        name = self.__class__.__name__
        raise NotImplementedError("{:s} does not support save()."
                                  "".format(name))

    # ------------------------------------------------------------------------

    def save_fragments(self, filename):
        """Save a fragment of an audio file."""
        name = self.__class__.__name__
        raise NotImplementedError("{:s} does not support save_fragments()."
                                  "".format(name))

    # ------------------------------------------------------------------------

    def close(self):
        """Close the audio file."""
        if self._audio_fp is None:
            raise AudioError

        self._audio_fp.close()
        self._audio_fp = None

    # ----------------------------------------------------------------------
    # Overloads
    # ----------------------------------------------------------------------

    def __len__(self):
        return len(self._channels)

    def __iter__(self):
        for x in self._channels:
            yield x

    def __getitem__(self, i):
        return self._channels[i]
