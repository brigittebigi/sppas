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

    src.models.acm.feature.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~

"""
import logging
import os

# ---------------------------------------------------------------------------

# audio speech file formats which can be read by the HWAVE module
SourceFormat = {
    "HTK": "The standard HTK file format",
    "TIMIT": "As used in the original prototype TIMIT CD-ROM",
    "NIST": "The standard SPHERE format used by the US NIST",
    "SCRIBE": "Subset of the European SAM standard used in the SCRIBE CD-ROM",
    "SDES1": "The Sound Designer 1 format defined by Digidesign Inc.",
    "AIFF": "Audio interchange file format",
    "SUNAU8": "Subset of 8bit .au and .snd formats used by Sun and NeXT",
    "OGI": "Format used by Oregan Graduate Institute similar to TIMIT",
    "WAVE": "Microsoft WAVE files used on PCs",
    "ESIG": "Entropic Esignal file format",
    "AUDIO": "Pseudo format to indicate direct audio input",
    "ALIEN": "Pseudo format to indicate unsupported file, the alien header "
             "size must be set via the environment variable HDSIZE",
    "NOHEAD": "As for the ALIEN format but header size is zero"
}

# basic parameter kinds supported by the HPARM module
SourceKind = {
    "WAVEFORM": "scalar samples (usually raw speech data)",
    "LPC": "linear prediction coefficients",
    "LPREFC": "linear prediction reflection coefficients",
    "LPCEPSTRA": "LP derived cepstral coefficients",
    "LPDELCEP": "LP cepstra + delta coef (obsolete)",
    "IREFC": "LPREFC stored as 16bit (short) integers",
    "MFCC": "mel-frequency cepstral coefficients",
    "FBANK": "log filter-bank parameters",
    "MELSPEC": "linear filter-bank parameters",
    "USER": "user defined parameters",
    "DISCRETE": "vector quantised codebook symbols",
    "ANON": "matches actual parameter kind"
}

# available qualifiers for parameter kinds.
# The first 6 of these are used to describe the target kind.
# The source kind may already have some of these,
# HPARM adds the rest as needed.
ParameterKind = {
    "_A": "Acceleration coefficients appended",
    "_C": "External form is compressed",
    "_D": "Delta coefficients appended",
    "_E": "Log energy appended",
    "_K": "External form has checksum appended",
    "_N": "Absolute log energy suppressed",
    "_V": "VQ index appended",
    "_Z": "Cepstral mean subtracted",
    "_0": "Cepstral C0 coefficient appended"
}

# all of the configuration parameters along with their meaning and
# default values
# See: http://www.ee.columbia.edu/ln/rosa/doc/HTKBook21/node78.html
# LINEIN     T     Select line input for audio
# MICIN     F     Select microphone input for audio
# LINEOUT     T     Select line output for audio
# SPEAKEROUT     F     Select speaker output for audio
# PHONESOUT     T     Select headphones output for audio
# SOURCEKIND     ANON     Parameter kind of source
# SOURCEFORMAT     HTK     File format of source
# SOURCERATE     0.0     Sample period of source in 100ns units
# NSAMPLES         Num samples in alien file input via a pipe
# HEADERSIZE         Size of header in an alien file
# STEREOMODE         Select channel: RIGHT or LEFT
# BYTEORDER         Define byte order VAX or other
# NATURALREADORDER     F     Enable natural read order for HTK files
# NATURALWRITEORDER     F     Enable natural write order for HTK files
# TARGETKIND     ANON     Parameter kind of target
# TARGETFORMAT     HTK     File format of target
# TARGETRATE     0.0     Sample period of target in 100ns units
# SAVECOMPRESSED     F     Save the output file in compressed form
# SAVEWITHCRC     T     Attach a checksum to output parameter file
# ADDDITHER     0.0     Level of noise added to input signal
# ZMEANSOURCE     F     Zero mean source waveform before analysis
# WINDOWSIZE     256000.0     Analysis window size in 100ns units
# USEHAMMING     T     Use a Hamming window
# PREEMCOEF     0.97     Set pre-emphasis coefficient
# LPCORDER     12     Order of LPC analysis
# NUMCHANS     20     Number of filterbank channels
# LOFREQ     -1.0     Low frequency cut-off in fbank analysis
# HIFREQ     -1.0     High frequency cut-off in fbank analysis
# USEPOWER     F     Use power not magnitude in fbank analysis
# NUMCEPS     12     Number of cepstral parameters
# CEPLIFTER     22     Cepstral liftering coefficient
# ENORMALISE     T     Normalise log energy
# ESCALE     0.1     Scale log energy
# SILFLOOR     50.0     Energy silence floor (dB)
# DELTAWINDOW     2     Delta window size
# ACCWINDOW     2     Acceleration window size
# VQTABLE     NULL     Name of VQ table
# SAVEASVQ     F     Save only the VQ indices
# AUDIOSIG     0     Audio signal number for remote control
# USESILDET     F     Enable speech/silence detector
# MEASURESIL     T     Measure background noise level prior to sampling
# OUTSILWARN     T     Print a warning message to stdout before measuring audio levels
# SPEECHTHRESH     9.0     Threshold for speech above silence level (dB)
# SILENERGY     0.0     Average background noise level (dB)
# SPCSEQCOUNT     10     Window over which speech/silence decision reached
# SPCGLCHCOUNT     0     Maximum number of frames marked as silence in window which is classified as speech whilst expecting start of speech
# SILSEQCOUNT     100     Number of frames classified as silence needed to mark end of utterance
# SILGLCHCOUNT     2     Maximum number of frames marked as silence in window which is classified as speech whilst expecting silence
# SILMARGIN     40     Number of extra frames included before and after start and end of speech marks from the speech/silence detector
# V1COMPAT     F     Set Version 1.5 compatibility mode
# TRACE     0     Trace setting

# ---------------------------------------------------------------------------


class sppasAcFeatures(object):
    """Acoustic model features.

    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2018  Brigitte Bigi
    :author:       Brigitte Bigi
    :contact:      develop@sppas.org

    """

    def __init__(self):
        """Create a sppasAcFeatures instance."""
        self.sourcekind = "MFC"   # either WAV or anything else!
        self.win_length_ms = 25   # The window length of the cepstral analysis in milliseconds
        self.win_shift_ms = 10    # The window shift of the cepstral analysis in milliseconds
        self.num_chans = 26       # Number of filterbank channels
        self.num_lift_ceps = 22   # Length of cepstral liftering
        self.num_ceps = 12        # The number of cepstral coefficients
        self.pre_em_coef = 0.97   # The coefficient used for the pre-emphasis
        self.targetkindw = "MFCC_0_D"     # "MFCC_0_E"
        self.targetkind = "MFCC_0_D_N_Z"  # "MFCC_E_D_A_Z"
        self.nbmv = 25            # The number of means and variances. It's commonly either 25 or 39.

        self.configfile = ""      # the file for HVite
        self.mfcconfigfile = ""   # the file for HCopy

        self.framerate = 16000  # Hz
        self.sampwidth = 2      # 16 bits

    # -----------------------------------------------------------------------

    def write_all(self, dirname):
        """Write all files at once.

        Write files with their default name, in the given directory.

        :param dirname: (str) a directory name (existing or to be created).

        """
        if os.path.exists(dirname) is False:
            os.mkdir(dirname)

        self.write_mfcconfig(os.path.join(dirname, "mfc_config"))
        self.write_config(os.path.join(dirname, "config"))

    # -----------------------------------------------------------------------

    def write_config(self, filename):
        """Write the wav config into a file.

        :param filename: (str) Name of the file to save the features.

        """
        logging.info('Write wav config file: %s ' % filename)
        with open(filename, "w") as fp:
            if self.sourcekind == "WAV":
                fp.write("SOURCEFORMAT = WAV\n")
                fp.write("SOURCEKIND = WAVEFORM\n")
                fp.write("SOURCERATE = %d\n" % ((1000./float(self.framerate))*10000))
            fp.write("TARGETFORMAT = HTK\n")
            fp.write("TARGETKIND = %s\n" % self.targetkind)
            fp.write("TARGETRATE = %.1f\n" % (self.win_shift_ms*10000))
            fp.write("SAVECOMPRESSED = T\n")
            fp.write("SAVEWITHCRC = T\n")
            fp.write("WINDOWSIZE = %.1f\n" % (self.win_length_ms*10000))
            fp.write("USEHAMMING = T\n")
            fp.write("PREEMCOEF = %f\n" % self.pre_em_coef)
            fp.write("NUMCHANS = %d\n" % self.num_chans)
            fp.write("CEPLIFTER = %d\n" % self.num_lift_ceps)
            fp.write("NUMCEPS = %d\n" % self.num_ceps)
            fp.write("ENORMALISE = F\n")
        self.configfile = filename

    # -----------------------------------------------------------------------

    def write_mfcconfig(self, filename):
        """Write the wav config into a file. For HCopy only.

        :param filename: (str) Name of the file to save the features.

        """
        logging.info('Write wav config file: %s ' % filename)
        with open(filename, "w") as fp:
            fp.write("SOURCEFORMAT = WAV\n")
            fp.write("SOURCEKIND = WAVEFORM\n")
            fp.write("SOURCERATE = %d\n" % ((1000./float(self.framerate))*10000))
            fp.write("TARGETFORMAT = HTK\n")
            fp.write("TARGETKIND = %s\n" % self.targetkindw)
            fp.write("TARGETRATE = %.1f\n" % (self.win_shift_ms*10000))
            fp.write("SAVECOMPRESSED = T\n")
            fp.write("SAVEWITHCRC = T\n")
            fp.write("WINDOWSIZE = %.1f\n" % (self.win_length_ms*10000))
            fp.write("USEHAMMING = T\n")
            fp.write("PREEMCOEF = %f\n" % self.pre_em_coef)
            fp.write("NUMCHANS = %d\n" % self.num_chans)
            fp.write("CEPLIFTER = %d\n" % self.num_lift_ceps)
            fp.write("NUMCEPS = %d\n" % self.num_ceps)
            fp.write("ENORMALISE = F\n")
        self.mfcconfigfile = filename
