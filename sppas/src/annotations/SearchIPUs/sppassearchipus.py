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

    src.annotations.SearchIPUs.sppassearchipus.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""

import os

from sppas.src.config import symbols
from sppas.src.config import annots
from sppas.src.config import info
from sppas.src.utils import u

import sppas.src.audiodata.aio
from sppas.src.anndata import sppasTranscription
from sppas.src.anndata import sppasTier
from sppas.src.anndata import sppasMedia
from sppas.src.anndata import sppasLocation
from sppas.src.anndata import sppasInterval
from sppas.src.anndata import sppasPoint
from sppas.src.anndata import sppasLabel
from sppas.src.anndata import sppasTag
from sppas.src.anndata import sppasRW

from ..annotationsexc import AnnotationOptionError
from ..baseannot import sppasBaseAnnotation
from .searchipus import SearchIPUs

# ---------------------------------------------------------------------------

SIL_ORTHO = list(
    symbols.ortho.keys()
    )[list(symbols.ortho.values()).index("silence")]

# ---------------------------------------------------------------------------


def _info(msg_id):
    return u(info(msg_id, "annotations"))

# ---------------------------------------------------------------------------


class sppasSearchIPUs(sppasBaseAnnotation):
    """SPPAS integration of the IPUs detection.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2019  Brigitte Bigi

    """

    def __init__(self, log=None):
        """Create a new sppasSearchIPUs instance.

        Log is used for a better communication of the annotation process and its
        results. If None, logs are redirected to the default logging system.

        :param log: (sppasLog) Human-readable logs.

        """
        super(sppasSearchIPUs, self).__init__("searchipus.json", log)
        self.__searcher = SearchIPUs(channel=None)

    # -----------------------------------------------------------------------
    # Methods to fix options
    # -----------------------------------------------------------------------

    def fix_options(self, options):
        """Fix all options.

        Available options are:

            - threshold: volume threshold to decide a window is silence or not
            - win_length: length of window for a estimation or volume values
            - min_sil: minimum duration of a silence
            - min_ipu: minimum duration of an ipu
            - shift_start: start boundary shift value.
            - shift_end: end boundary shift value.

        :param options: (sppasOption)

        """
        for opt in options:

            key = opt.get_key()
            if "threshold" == key:
                self.set_threshold(opt.get_value())

            elif "win_length" == key:
                self.set_win_length(opt.get_value())

            elif "min_sil" == key:
                self.set_min_sil(opt.get_value())

            elif "min_ipu" == key:
                self.set_min_ipu(opt.get_value())

            elif "shift_start" == key:
                self.set_shift_start(opt.get_value())

            elif "shift_end" == key:
                self.set_shift_end(opt.get_value())

            elif key in ("inputpattern", "outputpattern", "inputoptpattern"):
                self._options[key] = opt.get_value()

            else:
                raise AnnotationOptionError(key)

    # -----------------------------------------------------------------------

    def get_threshold(self):
        return self._options['threshold']

    def get_win_length(self):
        return self._options['win_length']

    def get_min_sil(self):
        return self._options['min_sil']

    def get_min_ipu(self):
        return self._options['min_ipu']

    def get_shift_start(self):
        return self._options['shift_start']

    def get_shift_end(self):
        return self._options['shift_end']

    # -----------------------------------------------------------------------

    def set_threshold(self, value):
        """Fix the threshold volume.

        :param value: (int) RMS value used as volume threshold

        """
        self._options['threshold'] = value

    # -----------------------------------------------------------------------

    def set_win_length(self, value):
        """Set a new length of window for a estimation or volume values.

        TAKE CARE:
        it cancels any previous estimation of volume and silence search.

        :param value: (float) generally between 0.01 and 0.04 seconds.

        """
        self._options['win_length'] = value

    # -----------------------------------------------------------------------

    def set_min_sil(self, value):
        """Fix the default minimum duration of a silence.

        :param value: (float) Duration in seconds.

        """
        self._options['min_sil'] = value

    # -----------------------------------------------------------------------

    def set_min_ipu(self, value):
        """Fix the default minimum duration of an IPU.

        :param value: (float) Duration in seconds.

        """
        self._options['min_ipu'] = value

    # -----------------------------------------------------------------------

    def set_shift_start(self, value):
        """Fix the start boundary shift value.

        :param value: (float) Duration in seconds.

        """
        self._options['shift_start'] = value

    # -----------------------------------------------------------------------

    def set_shift_end(self, value):
        """Fix the end boundary shift value.

        :param value: (float) Duration in seconds.

        """
        self._options['shift_end'] = value

    # -----------------------------------------------------------------------
    # Annotate
    # -----------------------------------------------------------------------

    @staticmethod
    def tracks_to_tier(tracks, end_time, vagueness):
        """Create a sppasTier object from tracks.

        :param tracks: (List of tuple) with (from, to) values in seconds
        :param end_time: (float) End-time of the tier
        :param vagueness: (float) vagueness used for silence search

        """
        if len(tracks) == 0:
            raise IOError('No IPUs to write.\n')

        tier = sppasTier("IPUs")
        tier.set_meta('number_of_ipus', str(len(tracks)))
        i = 0
        to_prec = 0.

        for (from_time, to_time) in tracks:

            if from_time == 0. or to_time == end_time:
                radius = 0.
            else:
                radius = vagueness / 2.

            # From the previous track to the current track: silence
            if to_prec < from_time:
                tier.create_annotation(
                    sppasLocation(
                        sppasInterval(sppasPoint(to_prec, radius),
                                      sppasPoint(from_time, radius))),
                    sppasLabel(
                        sppasTag(SIL_ORTHO))
                )

            # New track with speech
            tier.create_annotation(
                sppasLocation(
                    sppasInterval(sppasPoint(from_time, radius),
                                  sppasPoint(to_time, radius))),
                sppasLabel(
                    sppasTag("ipu_%d" % (i+1)))
            )

            # Go to the next
            i += 1
            to_prec = to_time

        # The end is a silence? Fill...
        begin = sppasPoint(to_prec, vagueness / 2.)
        if begin < end_time:
            tier.create_annotation(
                sppasLocation(
                    sppasInterval(begin, sppasPoint(end_time))),
                sppasLabel(
                    sppasTag(SIL_ORTHO))
            )

        return tier

    # -----------------------------------------------------------------------

    def _set_meta(self, tier):
        """Set meta values to the tier."""
        tier.set_meta('required_threshold_volume',
                      str(self.__searcher.get_vol_threshold()))
        tier.set_meta('estimated_threshold_volume',
                      str(self.__searcher.get_effective_threshold()))
        tier.set_meta('minimum_silence_duration',
                      str(self.__searcher.get_min_sil_dur()))
        tier.set_meta('minimum_ipus_duration',
                      str(self.__searcher.get_min_ipu_dur()))
        tier.set_meta('shift_ipus_start',
                      str(self.__searcher.get_shift_start()))
        tier.set_meta('shift_ipus_end',
                      str(self.__searcher.get_shift_end()))

        meta = ("rms_min", "rms_max", "rms_mean", "rms_median", "rms_coefvar")
        for key, value in zip(meta, self.__searcher.get_rms_stats()):
            tier.set_meta(str(key), str(value))

        self.logfile.print_message("Information: ", indent=1)
        if self.__searcher.get_vol_threshold() == 0:
            self.logfile.print_message(
                "Automatically estimated threshold volume value: {:d}"\
                "".format(self.__searcher.get_effective_threshold()),
                indent=2)
        self.logfile.print_message(
            "Number of IPUs found: {:s}".format(tier.get_meta("number_of_ipus")),
            indent=2)

    # -----------------------------------------------------------------------
    # Apply the annotation on one or several given files
    # -----------------------------------------------------------------------

    def convert(self, channel):
        """Search for IPUs in the given channel.

        :param channel: (sppasChannel) Input channel
        :returns: (sppasTier)

        """
        # Fix options
        self.__searcher.set_vol_threshold(self._options['threshold'])
        self.__searcher.set_win_length(self._options['win_length'])
        self.__searcher.set_min_sil(self._options['min_sil'])
        self.__searcher.set_min_ipu(self._options['min_ipu'])
        self.__searcher.set_shift_start(self._options['shift_start'])
        self.__searcher.set_shift_end(self._options['shift_end'])

        # Process the data.
        self.__searcher.set_channel(channel)
        tracks = self.__searcher.get_tracks(time_domain=True)
        tier = self.tracks_to_tier(
            tracks,
            channel.get_duration(),
            self.__searcher.get_vagueness()
        )
        self._set_meta(tier)

        return tier

    # -----------------------------------------------------------------------

    def run(self, input_file, opt_input_file=None, output=None):
        """Run the automatic annotation process on an input.

        :param input_file: (list of str) audio
        :param opt_input_file: (list of str) ignored
        :param output: (str) the output file name
        :returns: (sppasTranscription)

        """
        # Get audio and the channel we'll work on
        audio_speech = sppas.src.audiodata.aio.open(input_file[0])
        framerate = audio_speech.get_framerate()
        n = audio_speech.get_nchannels()
        if n != 1:
            raise IOError("An audio file with only one channel is expected. "
                          "Got {:d} channels.".format(n))

        # Extract the channel
        idx = audio_speech.extract_channel(0)
        channel = audio_speech.get_channel(idx)
        tier = self.convert(channel)

        # Create the transcription to put the result
        trs_output = sppasTranscription(self.name)
        trs_output.set_meta("media_sample_rate", str(framerate))
        trs_output.set_meta('search_ipus_result_of', input_file[0])
        trs_output.append(tier)

        extm = os.path.splitext(input_file[0])[1].lower()[1:]
        media = sppasMedia(os.path.abspath(input_file[0]),
                           mime_type="audio/"+extm)
        tier.set_media(media)

        # Save in a file
        if output is not None:
            output_file = self.fix_out_file_ext(output)
            parser = sppasRW(output_file)
            parser.write(trs_output)
            return [output_file]

        return trs_output

    # -----------------------------------------------------------------------

    def run_for_batch_processing(self, input_file, opt_input_file):
        """Perform the annotation on a file.

        This method is called by 'batch_processing'. It fixes the name of the
        output file. If the output file is already existing, the annotation
        is cancelled (the file won't be overridden). If not, it calls the run
        method.

        :param input_file: (list of str) the required input
        :param opt_input_file: (list of str) the optional input
        :returns: output file name or None

        """
        # Fix input/output file name
        root_pattern = self.get_out_name(input_file[0])

        # Is there already an existing output file (in any format)!
        ext = []
        for e in sppas.src.anndata.aio.extensions_in:
            if e not in ('.txt', '.hz', '.PitchTier', '.IntensityTier'):
                ext.append(e)
        exist_out_name = sppasBaseAnnotation._get_filename(root_pattern, ext)

        # it's existing... but not in the expected format: convert!
        if exist_out_name is not None:
            out_name = self.fix_out_file_ext(root_pattern)
            if exist_out_name.lower() == out_name.lower():
                return list()

            else:
                try:
                    parser = sppasRW(exist_out_name)
                    t = parser.read()
                    parser.set_filename(out_name)
                    parser.write(t)
                    self.logfile.print_message(_info(1302).format(out_name), indent=2, status=annots.warning)
                    return [out_name]
                except:
                    pass

        try:
            # Execute annotation
            new_files = self.run(input_file, opt_input_file, root_pattern)
        except Exception as e:
            new_files = list()
            self.logfile.print_message("{:s}\n".format(str(e)), indent=2, status=-1)

        return new_files

    # -----------------------------------------------------------------------

    @staticmethod
    def get_input_extensions():
        """Extensions that the annotation expects for its input filename."""
        return sppas.src.audiodata.aio.extensions
