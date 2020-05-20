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

    src.models.acm.htktrain.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~
    
"""
import logging
import os
import subprocess
import shutil
import copy
import collections
import codecs

from sppas.src.config import sg
from sppas.src.config import symbols
from sppas.src.config import separators

from sppas.src.wkps import sppasFileUtils
from sppas.src.wkps import sppasDirUtils

from sppas.src.annotations import sppasFindTier
from sppas.src.annotations import sppasPhon
from sppas.src.annotations import sppasTextNorm
from sppas.src.annotations import sppasAlign
from sppas.src.annotations.annotationsexc import NoInputError

import sppas.src.anndata as anndata
from sppas.src.anndata import sppasTranscription, sppasRW, sppasLabel, sppasTag
import sppas.src.anndata.aio.aioutils as tierutils
import sppas.src.audiodata.aio as audiodataio

from sppas.src.audiodata import sppasAudioPCM
from sppas.src.audiodata.channelformatter import sppasChannelFormatter
from sppas.src.audiodata.channelmfcc import sppasChannelMFCC

from sppas.src.resources import sppasDictPron
from sppas.src.resources import sppasVocabulary
from sppas.src.presenters import sppasMappingTier

from .hmm import sppasHMM
from .htkscripts import sppasHtkScripts
from .acmodel import sppasAcModel
from .acmodelhtkio import sppasHtkIO
from .features import sppasAcFeatures
from .phoneset import sppasPhoneSet


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

DEFAULT_HMMDEFS_FILENAME = "hmmdefs"
DEFAULT_MACROS_FILENAME = "macros"
DEFAULT_PROTO_FILENAME = "proto.hmm"
DEFAULT_MONOPHONES_FILENAME = "monophones"
DEFAULT_MAPPING_MONOPHONES_FILENAME = "monophones.repl"

DEFAULT_PROTO_DIR = "protos"
DEFAULT_SCRIPTS_DIR = "scripts"
DEFAULT_FEATURES_DIR = "features"
DEFAULT_LOG_DIR = "log"

SIL_PHON = list(symbols.phone.keys())[list(symbols.phone.values()).index("silence")]
SP_PHON = list(symbols.phone.keys())[list(symbols.phone.values()).index("pause")]
SIL_ORTHO = list(symbols.ortho.keys())[list(symbols.ortho.values()).index("silence")]
SP_ORTHO = list(symbols.ortho.keys())[list(symbols.ortho.values()).index("pause")]

# ---------------------------------------------------------------------------


def test_command(command):
    """Test if a command is available.

    :param command: (str) The command to execute as a sub-process.

    """
    try:
        os_null = open(os.devnull, "w")
        subprocess.call([command], stdout=os_null, stderr=subprocess.STDOUT)
    except OSError:
        return False

    return True

# ---------------------------------------------------------------------------


class sppasDataTrainer(object):
    """Acoustic model trainer for HTK-ASCII models.

    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2018  Brigitte Bigi
    :author:       Brigitte Bigi
    :contact:      develop@sppas.org

    This class is a manager for the data created at each step of the
    acoustic training model procedure, following the HTK Handbook.
    It includes:

        - HTK scripts
        - phoneme prototypes
        - log files
        - features

    """
    def __init__(self):
        """Create a sppasDataTrainer instance.
        
        Initialize all members to None or empty lists.

        """
        # The working directory.
        self.workdir = None
        self.featsdir = None
        self.scriptsdir = None
        self.logdir = None

        self.htkscripts = sppasHtkScripts()
        self.features = sppasAcFeatures()

        # The data storage directories, for transcribed speech and audio files.
        self.storetrs = []
        self.storewav = []
        self.storemfc = []
        self.storeidx = -1

        # The directory with all HMM prototypes, and the default proto file.
        self.protodir = None
        self.protofile = None
        self.macrofile = None
        self.proto = sppasHMM()
        self.proto.create_proto(self.features.nbmv)

    # -----------------------------------------------------------------------

    def reset(self):
        """Fix all members to their initial value."""
        # The working directory.
        self.workdir = None
        self.featsdir = None
        self.scriptsdir = None
        self.logdir = None
        self.htkscripts = sppasHtkScripts()
        self.features = sppasAcFeatures()

        # The data storage directories, for transcribed speech and audio files.
        self.storetrs = []
        self.storewav = []
        self.storemfc = []
        self.storeidx = -1

        # The directory with all HMM prototypes, and the default proto file.
        self.protodir = None
        self.protofile = None
        self.macrofile = None
        self.proto = sppasHMM()
        self.proto.create_proto(self.features.nbmv)

    # -----------------------------------------------------------------------

    def create(self, 
               workdir=None, 
               scriptsdir=DEFAULT_SCRIPTS_DIR, 
               featsdir=DEFAULT_FEATURES_DIR, 
               logdir=DEFAULT_LOG_DIR, 
               protodir=None, 
               protofilename=DEFAULT_PROTO_FILENAME):
        """Create all folders and their content (if possible) with their
        default names.

        :param workdir: (str) Name of the working directory
        :param scriptsdir: (str) The folder for HTK scripts
        :param featsdir: (str) The folder for features
        :param logdir: (str) Directory to store log files
        :param protodir: (str) Name of the prototypes directory
        :param protofilename: (str) Name of the file for the HMM prototype.

        :raises: IOError

        """
        self.fix_working_dir(workdir, scriptsdir, featsdir, logdir)
        self.fix_proto(protodir, protofilename)
        self.check()

    # -----------------------------------------------------------------------

    def delete(self):
        """Delete all folders and their content, then reset members."""
        if self.workdir is not None:
            shutil.rmtree(self.workdir)
        self.reset()

    # -----------------------------------------------------------------------

    def fix_working_dir(self, 
                        workdir=None, 
                        scriptsdir=DEFAULT_SCRIPTS_DIR, 
                        featsdir=DEFAULT_FEATURES_DIR, 
                        logdir=DEFAULT_LOG_DIR):
        """Set the working directory and its folders.

        Create all of them if necessary.

        :param workdir: (str) The working main directory
        :param scriptsdir: (str) The folder for HTK scripts
        :param featsdir: (str) The folder for features
        :param logdir: (str) The folder to write output logs

        """
        # The working directory will be located in the system temp dir
        if workdir is None:
            sf = sppasFileUtils()
            workdir = sf.set_random()
        if os.path.exists(workdir) is False:
            os.mkdir(workdir)
        self.workdir = workdir

        if os.path.exists(scriptsdir) is False:
            scriptsdir = os.path.join(self.workdir, scriptsdir)
        self.htkscripts.write_all(scriptsdir)

        if os.path.exists(featsdir) is False:
            featsdir = os.path.join(self.workdir, featsdir)
        self.features.write_all(featsdir)

        if os.path.exists(logdir) is False:
            logdir = os.path.join(self.workdir, logdir)
            if os.path.exists(logdir) is False:
                os.mkdir(logdir)

        self.scriptsdir = scriptsdir
        self.featsdir = featsdir
        self.logdir = logdir

        logging.info('Working directory is {:s}'.format(self.workdir))

    # -----------------------------------------------------------------------

    def fix_storage_dirs(self, basename):
        """Fix the folders to store annotated speech and audio files.

        The given basename can be something like: align, phon, trans, ...

        :param basename: (str) a name to identify storage folders
        :raises: IOError

        """
        if basename is None:
            self.storeidx = -1
            return

        if self.workdir is None:
            raise IOError("A working directory must be fixed before "
                          "defining its folders.")

        store_trs = os.path.join(self.workdir, "trs-"+basename)
        store_wav = os.path.join(self.workdir, "wav-"+basename)
        store_mfc = os.path.join(self.workdir, "mfc-"+basename)

        if os.path.exists(store_trs) is False:
            os.mkdir(store_trs)
            os.mkdir(store_wav)
            os.mkdir(store_mfc)

        if store_trs not in self.storetrs:
            self.storetrs.append(store_trs)
            self.storewav.append(store_wav)
            self.storemfc.append(store_mfc)

        self.storeidx = self.storetrs.index(store_trs)

    # -----------------------------------------------------------------------

    def get_storetrs(self):
        """Get the current folder name to store transcribed data files.

        :returns: folder name or None.

        """
        if self.storeidx == -1: 
            return None
        return self.storetrs[self.storeidx]

    # -----------------------------------------------------------------------

    def get_storewav(self):
        """Get the current folder name to store audio data files.

        :returns: folder name or None.

        """
        if self.storeidx == -1: 
            return None
        return self.storewav[self.storeidx]

    # -----------------------------------------------------------------------

    def get_storemfc(self):
        """Get the current folder name to store MFCC data files.

        :returns: folder name or None.

        """
        if self.storeidx == -1: 
            return None
        return self.storemfc[self.storeidx]

    # -----------------------------------------------------------------------

    def fix_proto(self, 
                  proto_dir=DEFAULT_PROTO_DIR, 
                  proto_filename=DEFAULT_PROTO_FILENAME):
        """(Re-)Create the proto.

        If relevant, create a `protos` directory
        and add the proto file. Create the macro if any.

        :param proto_dir: (str) Directory in which prototypes will be stored
        :param proto_filename: (str) File name of the default prototype

        """
        self.proto.create_proto(self.features.nbmv)
        if proto_dir is not None and os.path.exists(proto_dir) is True:
            self.protodir = proto_dir

        if self.workdir is not None:
            if proto_dir is None or os.path.exists(proto_dir) is False:
                proto_dir = os.path.join(self.workdir, DEFAULT_PROTO_DIR)
                if os.path.exists(proto_dir) is False:
                    os.mkdir(proto_dir)

        if proto_dir is not None and os.path.exists(proto_dir):
            self.protodir = proto_dir

        if self.protodir is not None:
            self.protofile = os.path.join(self.protodir,
                                          proto_filename)
            self.macrofile = os.path.join(self.protodir,
                                          DEFAULT_MACROS_FILENAME)

            if os.path.exists(self.protofile) is False:
                logging.info('Write proto file: {:s}'.format(self.protofile))
                sppasHtkIO.write_hmm(self.proto, self.protofile)
            else:
                logging.info('Read proto file: {!s:s}'.format(self.protofile))
                self.proto = sppasHtkIO.read_hmm(self.protofile)
                self.features.nbmv = self.proto.get_vecsize()
                logging.info(' ... [OK] Vector size: {:d}'
                             ''.format(self.features.nbmv))

            if os.path.exists(self.macrofile) is False:
                logging.info('Write macros file: {:s}'
                             ''.format(DEFAULT_MACROS_FILENAME))
                vectorsize = self.features.nbmv
                targetkind = self.features.targetkind
                paramkind = sppasAcModel.create_parameter_kind("mfcc",
                                                               targetkind[4:])

                opt = sppasAcModel.create_options(vector_size=vectorsize,
                                                  parameter_kind=paramkind,
                                                  stream_info=[vectorsize])

                self.macrofile = os.path.join(self.protodir,
                                              DEFAULT_MACROS_FILENAME)
                macromodel = sppasHtkIO()
                macromodel.set_macros([opt])
                macromodel.write(self.protodir, DEFAULT_MACROS_FILENAME)

    # -----------------------------------------------------------------------

    def check(self):
        """Check if all members are initialized with appropriate values.

        :returns: None if success.
        :raises: IOError

        """
        if self.protodir is None:
            raise IOError("No proto directory defined.")
        if os.path.isdir(self.protodir) is False:
            raise IOError("Bad proto directory: {:s}."
                          "".format(self.protodir))

        if self.protofile is None:
            raise IOError("No proto file defined.")
        if os.path.isfile(self.protofile) is False:
            raise IOError("Bad proto file name: {:s}."
                          "".format(self.protofile))

        if self.workdir is None:
            raise IOError("No working directory defined.")
        if os.path.isdir(self.workdir) is False:
            raise IOError("Bad working directory: {:s}."
                          "".format(self.workdir))

        if self.scriptsdir is None:
            raise IOError("No scripts directory defined.")
        if os.path.isdir(self.scriptsdir) is False:
            raise IOError("Bad scripts directory: {:s}."
                          "".format(self.scriptsdir))

        if self.featsdir is None:
            raise IOError("No features directory defined.")
        if os.path.isdir(self.featsdir) is False:
            raise IOError("Bad features directory: {:s}."
                          "".format(self.featsdir))

        if self.logdir is None:
            raise IOError("No log directory defined.")
        if os.path.isdir(self.logdir) is False:
            raise IOError("Bad log directory: {:s}."
                          "".format(self.logdir))

# ---------------------------------------------------------------------------


class sppasTrainingCorpus(object):
    """Manager of a training corpus, to prepare a set of data.

    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2018  Brigitte Bigi
    :author:       Brigitte Bigi
    :contact:      develop@sppas.org

    Data preparation is the step 1 of the acoustic model training procedure.

    It establishes the list of phonemes.
    It converts the input data into the HTK-specific data format.
    It codes the audio data, also called "parameterizing the raw speech
    waveforms into sequences of feature vectors" (i.e. convert from wav
    to MFCC format).

    Accepted input:

        - annotated files: one of anndata.aio.extensions_in
        - audio files: one of audiodata.extensions

    """
    def __init__(self, datatrainer=None, lang="und"):
        """Create a sppasTrainingCorpus instance.

        :param datatrainer: (sppasDataTrainer)
        :param lang: (str) iso-8859-3 of the language

        """
        self.datatrainer = datatrainer
        self.lang = lang
        self.transfiles = {}  # Time-aligned at the ipus level, orthograph
        self.phonfiles = {}   # Time-aligned at the ipus level, phonetization
        self.alignfiles = {}  # Time-aligned at the phone level
        self.audiofiles = {}  #
        self.mfcfiles = {}    #
        self.vocabfile = None
        self.dictfile = None
        self.phonesfile = None
        self.monophones = sppasPhoneSet()
        self.phonemap = sppasMappingTier()

        if datatrainer is None:
            self.datatrainer = sppasDataTrainer()

        self.create()

    # -----------------------------------------------------------------------

    def reset(self):
        """Fix all members to None or to their default values."""
        if self.datatrainer is not None:
            self.datatrainer.reset()

        # Selection of the input data files.
        #   - Key   = original file
        #   - Value = working file
        self.transfiles = {}  # Time-aligned at the ipus level, orthography
        self.phonfiles = {}   # Time-aligned at the ipus level, phonetization
        self.alignfiles = {}  # Time-aligned at the phone level
        self.audiofiles = {}  #
        self.mfcfiles = {}    #

        # The lexicon, the pronunciation dictionary and the phoneset
        self.vocabfile = None
        self.dictfile = None
        self.phonesfile = None
        self.monophones = sppasPhoneSet()
        self.phonemap = sppasMappingTier()

    # -----------------------------------------------------------------------

    def create(self):
        """Create files and directories."""
        if self.datatrainer.workdir is None:
            logging.info('Create a temporary working directory: ')
            self.datatrainer.create()

    # -----------------------------------------------------------------------

    def fix_resources(self, vocab_file=None, dict_file=None, mapping_file=None):
        """Fix resources using default values.

        Ideally, resources are fixed *after* the datatrainer.

        :param vocab_file: (str) The lexicon, used during tokenization of the corpus.
        :param dict_file: (str) The pronunciation dictionary, used both to
        generate the list of phones and to perform phonetization of the corpus.
        :param mapping_file: (str) file that contains the mapping table for the phone set.

        """
        logging.info('Fix resources: ')

        # The mapping table (required to convert the dictionary)
        if self.datatrainer.workdir is not None and mapping_file is not None:
            logging.info(' - mapping table {!s:s}'.format(mapping_file))
            self._create_phonemap(mapping_file)
        else:
            logging.info(' - no mapping table is defined.')

        # The pronunciation dictionary
        # (also used to construct the vocab if required)
        if dict_file is not None and os.path.exists(dict_file) is True:
            logging.info(' - pronunciation dictionary {!s:s}'
                         ''.format(dict_file))

            # Map the phoneme strings of the dictionary.
            # Save the mapped version.
            pdict = sppasDictPron(dict_file)
            if self.datatrainer.workdir is not None:
                map_dict = pdict.map_phones(self.phonemap)
                dict_file = os.path.join(self.datatrainer.workdir,
                                         self.lang + ".dict")
                map_dict.save_as_ascii(dict_file)
            # Create the vocabulary from the dictionary.
            if vocab_file is None:
                vocab_file = os.path.join(self.datatrainer.workdir,
                                          self.lang + ".vocab")
                w = sppasVocabulary()
                for token in pdict:
                    if '(' not in token and ')' not in token:
                        w.add(token)
                w.save(vocab_file)
            self.dictfile = dict_file
            self.monophones.add_from_dict(self.dictfile)
        else:
            logging.info(' - no pronunciation dictionary is defined.')

        # Either the given vocab or the constructed one
        if vocab_file is not None:
            logging.info(' - vocabulary: {!s:s}'.format(vocab_file))
            self.vocabfile = vocab_file
        else:
            logging.info(' - no vocabulary is defined.')

        # The list of monophones included in the dict
        if self.datatrainer.workdir is not None:
            self.phonesfile = os.path.join(self.datatrainer.workdir, "monophones")
            self.monophones.save(self.phonesfile)

    # -----------------------------------------------------------------------

    def add_corpus(self, directory):
        """Add a new corpus to deal with.

        Find matching pairs of files (audio / transcription) of the
        given directory and its folders.

        :param directory: (str) The directory to find data files of a corpus.
        :returns: the number of pairs appended.

        """
        # Get the list of audio files from the input directory
        audio_files = []
        sd = sppasDirUtils(directory)
        for extension in audiodataio.extensions:
            files = sd.get_files(extension)
            audio_files.extend(files)

        # Get the list of annotated files from the input directory
        trs_files = list()
        for extension in anndata.aio.extensions_in:
            if extension.lower() in [".hz", ".pitchtier", ".txt"]:
                continue
            files = sd.get_files(extension)
            if len(files) > 0:
                trs_files.extend(files)

        count = 0
        # Find matching files (audio / transcription files).
        for trs_filename in trs_files:
            trs_basename = os.path.splitext(trs_filename)[0]

            if trs_basename.endswith("-palign"):  # already aligned
                trs_basename = trs_basename[:-7]
            if trs_basename.endswith("-phon"):    # already phonetized
                trs_basename = trs_basename[:-5]
            if trs_basename.endswith("-token"):   # already tokenized
                trs_basename = trs_basename[:-6]
            if trs_basename.endswith("-merge"):   # several of them
                trs_basename = trs_basename[:-6]

            for audio_filename in audio_files:
                audio_basename = os.path.splitext(audio_filename)[0]

                if audio_basename == trs_basename:
                    ret = self.add_file(trs_filename, audio_filename)
                    if ret is True:
                        count += 1

        return count

    # -----------------------------------------------------------------------

    def add_file(self, trs_filename, audio_filename):
        """Add a new set of files to deal with.

        If such files are already in the data, they will be added again.

        :param trs_filename: (str) The annotated file.
        :param audio_filename: (str) The audio file.
        :returns: (bool)

        """
        if self.datatrainer.workdir is None:
            self.create()

        try:
            parser = sppasRW(trs_filename)
            trs = parser.read(trs_filename)
        except Exception as e:
            logging.error("Error with file: {!s:s}: {:s}"
                          "".format(trs_filename, str(e)))
            return False

        appended = False
        # Already time-aligned phonemes
        try:
            tier = sppasFindTier.aligned_phones(trs)
            appended = self._append_phonalign(tier,
                                              trs_filename,
                                              audio_filename)
        except NoInputError:
            pass

        # Already phonetized
        try:
            tier = sppasFindTier.phonetization(trs)
            appended = self._append_phonetization(tier,
                                                  trs_filename,
                                                  audio_filename)
        except NoInputError:
            pass

        # Already tokenized (appended as an ortho transc.)
        try:
            tier = sppasFindTier.tokenization(trs)
            appended = self._append_transcription(tier,
                                                  trs_filename,
                                                  audio_filename)
        except NoInputError:
            # Orthographic transcription
            try:
                tier = sppasFindTier.transcription(trs)
                appended = self._append_transcription(tier,
                                                      trs_filename,
                                                      audio_filename)
            except NoInputError:
                pass

        if appended is False:
            logging.warning("No tier was found and/or appended from "
                            "file {!s:s}.".format(trs_filename))
        return appended

    # -----------------------------------------------------------------------

    def get_scp(self, aligned=True, phonetized=False, transcribed=False):
        """Fix the train.scp file content.

        :param aligned: (bool) Add time-aligned data in the scp file
        :param phonetized: (bool) Add phonetized data in the scp file
        :param transcribed: (bool) Add transcribed data in the scp file

        :returns: filename or None if no data is available.

        """
        files = False
        scp_file = os.path.join(self.datatrainer.workdir, "train.scp")

        with open(scp_file, "w") as fp:

            if transcribed is True:
                for trs_file, work_file in self.transfiles.items():
                    if work_file.endswith(".lab"):
                        mfc_file = self.mfcfiles[trs_file]
                        fp.write("{:s}\n".format(mfc_file))
                        files = True

            if phonetized is True:
                for trs_file in self.phonfiles:
                    mfc_file = self.mfcfiles[trs_file]
                    fp.write("{:s}\n".format(mfc_file))
                    files = True

            if aligned is True:
                for trs_file in self.alignfiles:
                    mfc_file = self.mfcfiles[trs_file]
                    fp.write("{:s}\n".format(mfc_file))
                    files = True

        if files is True:
            return scp_file

        return None

    # -----------------------------------------------------------------------

    def get_mlf(self):
        """Fix the mlf file by defining the directories to add.

        Example of a line of the MLF file is:
        "*/mfc-align/*" => "workdir/trs-align"

        """
        files = False
        mlf_file = os.path.join(self.datatrainer.workdir, "train.mlf")

        with open(mlf_file, "w") as fp:
            fp.write('#!MLF!#\n')
            for i, trs_dir in enumerate(self.datatrainer.storetrs):
                mfc_dir = self.datatrainer.storemfc[i]
                mfc = os.path.basename(mfc_dir)
                fp.write('"*/{:s}/*" => "{:s}"\n'.format(mfc, trs_dir))
                files = True

        if files is True:
            return mlf_file

        return None

    # -----------------------------------------------------------------------

    def _append_phonalign(self, tier, trs_filename, audio_filename):
        """Append a PhonAlign tier in the set of known data.

        :returns: (bool)

        """
        tier = self.phonemap.map_tier(tier)

        # Fix current storage dir.
        self.datatrainer.fix_storage_dirs("align")
        sf = sppasFileUtils()
        outfile = os.path.basename(sf.set_random(root="track_aligned",
                                                 add_today=False,
                                                 add_pid=False))

        # Add the tier
        res = self._append_tier(tier, outfile, trs_filename, audio_filename)
        if res is True:
            self.alignfiles[trs_filename] = os.path.join(
                self.datatrainer.get_storetrs(),
                outfile+".lab")

        return res

    # -----------------------------------------------------------------------

    def _append_phonetization(self, tier, trs_filename, audio_filename):
        """Append a Phonetization tier in the set of known data.

        :returns: (bool)

        """
        # Map phonemes.
        d = self.phonemap.get_delimiters()
        self.phonemap.set_delimiters([" ", "\n",  # separate labels of an ann
                                      separators.phonemes,
                                      separators.variants])
        tier = self.phonemap.map_tier(tier)
        self.phonemap.set_delimiters(d)

        for ann in tier:
            label = tierutils.serialize_labels(
                ann.get_labels(), separator=" ", empty="", alt=False)
            new_content = sppasTrainingCorpus._format_phonetization(label)
            ann.set_labels(sppasLabel(sppasTag(new_content)))

        # Fix current storage dir.
        self.datatrainer.fix_storage_dirs("phon")
        sf = sppasFileUtils()
        outfile = os.path.basename(sf.set_random(root="track_phonetized", add_today=False, add_pid=False))

        # Add the tier
        res = self._append_tier(tier, outfile, trs_filename, audio_filename)
        if res is True:
            self.phonfiles[trs_filename] = os.path.join(self.datatrainer.get_storetrs(), outfile+".lab")

        return res

    # -----------------------------------------------------------------------

    def _append_transcription(self, tier, trs_filename, audio_filename):
        """Append a Transcription tier in the set of known data."""

        # Fix current storage dir.
        self.datatrainer.fix_storage_dirs("trans")
        sf = sppasFileUtils()
        outfile = os.path.basename(sf.set_random(root="track_transcribed", add_today=False, add_pid=False))

        # Add the tier
        res = self._append_tier(tier, outfile, trs_filename, audio_filename, ext=".xra")
        if res is True:
            # no lab file created (it needs sppas... a vocab, a dict and an acoustic model).
            self.transfiles[trs_filename] = os.path.join(self.datatrainer.get_storetrs(), outfile+".xra")
        return res

    # -----------------------------------------------------------------------

    def _append_tier(self, tier, outfile, trs_filename, audio_filename, ext=".lab"):
        """Append a Transcription (orthography) tier in the set of known data."""

        ret = self._add_tier(tier, outfile, ext)
        if ret is True:

            ret = self._add_audio(audio_filename, outfile)
            if ret is True:

                logging.info('Files {:s} / {:s} appended as {:s}.'
                             ''.format(trs_filename, audio_filename, outfile))
                self.audiofiles[trs_filename] = \
                    os.path.join(self.datatrainer.get_storewav(),
                                 outfile + ".wav")
                self.mfcfiles[trs_filename] = \
                    os.path.join(self.datatrainer.get_storemfc(),
                                 outfile + ".mfc")
                return True

            else:
                self._pop_tier(outfile)

        logging.info('Files {:s} / {:s} rejected.'
                     ''.format(trs_filename, audio_filename))
        return False

    # -----------------------------------------------------------------------

    def _add_tier(self, tier, outfile, ext):
        try:
            trs = sppasTranscription()
            trs.append(tier)

            out_filename = os.path.join(self.datatrainer.get_storetrs(),
                                        outfile+ext)
            parser = sppasRW(out_filename)
            parser.write(trs)
        except:
            return False
        return True

    # -----------------------------------------------------------------------

    def _pop_tier(self, outfile):
        try:
            filename = os.path.join(self.datatrainer.get_storetrs(),
                                    outfile + ".lab")
            os.remove(filename)
        except IOError:
            pass

    # -----------------------------------------------------------------------

    def _add_audio(self, audio_filename, outfile):
        # Get the first channel
        try:
            audio = audiodataio.open(audio_filename)
            audio.extract_channel(0)
            formatter = sppasChannelFormatter(audio.get_channel(0))
        except:
            return False

        # Check/Convert
        formatter.set_framerate(self.datatrainer.features.framerate)
        formatter.set_sampwidth(self.datatrainer.features.sampwidth)
        formatter.convert()
        audio.close()

        # Save the converted channel
        audio_out = sppasAudioPCM()
        audio_out.append_channel(formatter.get_channel())
        audiodataio.save(os.path.join(self.datatrainer.get_storewav(), outfile + ".wav"), audio_out)

        # Generate MFCC
        wav = os.path.join(self.datatrainer.get_storewav(), outfile + ".wav")
        mfc = os.path.join(self.datatrainer.get_storemfc(), outfile + ".mfc")
        sf = sppasFileUtils()
        tmpfile = sf.set_random(root="scp", add_today=False, add_pid=False)
        with open(tmpfile, "w") as fp:
            fp.write('%s %s\n' % (wav, mfc))

        cmfc = sppasChannelMFCC(formatter.get_channel())
        cmfc.hcopy(self.datatrainer.features.mfcconfigfile, tmpfile)
        os.remove(tmpfile)

        return True

    # -----------------------------------------------------------------------

    def _pop_audio(self, outfile):
        try:
            os.remove(os.path.join(self.datatrainer.get_storewav(), outfile + ".wav"))
        except IOError:
            pass

    # -----------------------------------------------------------------------

    def _append_mlf(self, filename, outfile):
        """Append a transcription in a mlf file from a prepared corpus."""

        lab_filename = os.path.join(self.datatrainer.get_storetrs(), outfile+".lab")

        try:
            with codecs.open(lab_filename, "r", sg.__encoding__) as fp:
                lab = "".join(fp.readlines()).strip()
            if len(lab) == 0:
                return False
        except:
            return False

        with codecs.open(filename, "a+", sg.__encoding__) as fp:
            fp.write('"*/%s/%s.lab"\n' % (os.path.basename(self.datatrainer.get_storetrs()),
                                          os.path.basename(outfile)))
            fp.write('%s\n' % lab)
            fp.close()

        return True

    # -----------------------------------------------------------------------

    def _create_phonemap(self, mapfile):
        """Create the default mapping table, and/or get from a file.

        :param mapfile:

        """
        self.phonemap = sppasMappingTier(mapfile)
        self.phonemap.set_reverse(True)
        self.phonemap.set_map_symbols(True)

        self.phonemap.add(SIL_PHON, SIL_ORTHO)
        self.phonemap.add(SIL_PHON, SP_ORTHO)

        # Update the list of monophones from the phonemap table.
        for phoneme in self.phonemap:
            if phoneme != SP_PHON:
                self.monophones.add(phoneme)

        self.phonemap.add("dummy", symbols.unk)

    # -----------------------------------------------------------------------

    @staticmethod
    def _format_phonetization(ipu):
        """Remove variants of a phonetized ipu, replace dots by whitespace.

        :returns: the ipu without pronunciation variants.

        """
        select_list = []
        for pron in ipu.split(" "):
            tab = pron.split("|")
            i = 0
            m = len(tab[0])
            for n, p in enumerate(tab):
                if len(p) < m:
                    i = n
                    m = len(p)
            select_list.append(tab[i].replace(separators.phonemes, " "))

        return " ".join(select_list)

# ---------------------------------------------------------------------------


class sppasHTKModelInitializer(object):
    """Acoustic model initializer.

    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2018  Brigitte Bigi
    :author:       Brigitte Bigi
    :contact:      develop@sppas.org

    Monophones initialization is the step 2 of the acoustic model training
    procedure.

    In order to create a HMM definition, it is first necessary to produce a
    prototype definition. The function of a prototype definition is to describe
    the form and topology of the HMM, the actual numbers used in the definition
    are not important.

    Having set up an appropriate prototype, an HMM can be initialized by both
    methods:
    1. create a flat start monophones model, a prototype trained from
       phonetized data, and copied for each phoneme (using `HCompV` command).
       It reads in a prototype HMM definition and some training data and outputs
       a new definition in which every mean and covariance is equal to the
       global speech mean and covariance.
    2. create a prototype for each phoneme using time-aligned data (using
       `Hinit` command). Firstly, the Viterbi algorithm is used to find the most
       likely state sequence corresponding to each training example, then the
       HMM parameters are estimated. As a side-effect of finding the Viterbi
       state alignment, the log likelihood of the training data can be computed.
        Hence, the whole estimation process can be repeated until no further
       increase in likelihood is obtained.

    This program trains the flat start model and fall back on this model
    for each phoneme that fails to be trained with `Hinit` (if there are not
    enough occurrences).

    """
    def __init__(self, trainingcorpus, directory):
        """Create an instance of sppasHTKModelInitializer.

        :param trainingcorpus: (sppasTrainingCorpus) The data prepared during step 1.
        :param directory: (str) The current directory to write the result of this step.
        :raises: IOError

        """
        self.trainingcorpus = trainingcorpus
        self.directory = directory
        if os.path.exists(directory) is False:
            raise IOError('A valid directory must be defined in order to '
                          'initialize the model.')

    # -----------------------------------------------------------------------

    def create_model(self):
        """Main method to create the initial acoustic model.

        :raises: IOError

        """
        if self.trainingcorpus.monophones is None:
            raise IOError('A list of monophones must be defined in order '
                          'to initialize the model.')

        self.create_models()
        self.create_macros()
        self.create_hmmdefs()

    # -----------------------------------------------------------------------

    def _create_flat_start_model(self):
        """Create a new version of proto in the directory with `HCompV`.

        Read the current proto and the data, then, creates two new files
        in the directory:
            - proto (with variances and means updated);
            - vFloors (variance floor macros).

        """
        if test_command("HCompV") is False:
            logging.error("HCompV is not installed.")
            return

        scp_file = self.trainingcorpus.get_scp(aligned=True,
                                               phonetized=True,
                                               transcribed=False)
        if scp_file is None:
            logging.error("The scp file is not defined.")
            return

        log_file = os.path.join(self.trainingcorpus.datatrainer.logdir,
                                "log-step00.txt")
        error_file = os.path.join(self.trainingcorpus.datatrainer.logdir,
                                  "err-step00.txt")

        try:
            subprocess.check_call([
               "HCompV",
               "-T", "2",
               "-m",
               "-I", self.trainingcorpus.get_mlf(),
               "-f", str(0.01),
               "-C", self.trainingcorpus.datatrainer.features.configfile,
               "-S", scp_file,
               "-H", self.trainingcorpus.datatrainer.macrofile,
               "-M", self.directory,
               self.trainingcorpus.datatrainer.protofile],
               stdout=open(log_file, 'ab+'),
               stderr=open(error_file, 'ab+'))
        except subprocess.CalledProcessError as e:
            logging.error("HCompV failed with error:\n"
                          "{:s}".format(str(e)))
            return

    # -----------------------------------------------------------------------

    def _create_start_model(self, phone, outfile):
        """Create a proto for a specific phone, using `HInit`.

        :param phone:
        :param outfile:

        """
        if test_command("HInit") is False:
            logging.error("HInit is not installed.")
            return

        scp_file = self.trainingcorpus.get_scp(aligned=True,
                                               phonetized=False,
                                               transcribed=False)
        if scp_file is None:
            logging.error("The scp file is not defined.")
            return

        log_file = os.path.join(self.trainingcorpus.datatrainer.logdir,
                                "log-step00.txt")
        error_file = os.path.join(self.trainingcorpus.datatrainer.logdir,
                                  "err-step00.txt")

        try:
            subprocess.check_call([
                "HInit",
                "-T", "2",
                "-i", "20",
                "-m", "1",
                "-v", "0.0001",
                "-I", self.trainingcorpus.get_mlf(),
                "-l", phone,
                "-o", outfile,
                "-C", self.trainingcorpus.datatrainer.features.configfile,
                "-S", scp_file,
                "-H", self.trainingcorpus.datatrainer.macrofile,
                "-M", self.directory,
                self.trainingcorpus.datatrainer.protofile],
                stdout=open(log_file, 'ab+'),
                stderr=open(error_file, 'ab+'))
        except subprocess.CalledProcessError as e:
            logging.warning("HInit failed with message:\n"
                            "{:s}".format(str(e)))
            return

    # -----------------------------------------------------------------------

    def create_models(self):
        """Create an initial model for each phoneme.

        Create a start model for each phoneme:

            - either from time-aligned data [TRAIN],
            - or use the prototype trained by HCompV (i.e. a flat-start-model) [FLAT],
            - or use the existing saved prototype [PROTO],
            - or use the default prototype.

        """
        scp_file = self.trainingcorpus.get_scp(aligned=True,
                                               phonetized=False,
                                               transcribed=False)

        # Adapt the proto file from the corpus (if any)
        if scp_file is not None:
            if self.trainingcorpus.datatrainer.protofile is not None:
                logging.info(' ... Train proto model:')
                self._create_flat_start_model()
                hcompv_proto_file = os.path.join(self.directory, "proto")
                if os.path.exists(hcompv_proto_file) is True:
                    self.trainingcorpus.datatrainer.protofile = hcompv_proto_file
                    self.trainingcorpus.datatrainer.proto = sppasHtkIO.read_hmm(hcompv_proto_file)
                    self.trainingcorpus.datatrainer.features.nbmv = self.trainingcorpus.datatrainer.proto.get_vecsize()
                    logging.info(' ... ... [ OK ] ')
                else:
                    logging.info(' ... ... [FAIL] ')

        logging.info(" ... [INFO] Vector size: {:d}"
                     "".format(self.trainingcorpus.datatrainer.features.nbmv))

        # Create a start model for each phoneme
        logging.info(" ... Train initial model for phones: {:s}"
                     "".format(" ".join(self.trainingcorpus.monophones.get_list())))

        for phone in self.trainingcorpus.monophones.get_list():

            logging.info(" ... Initial model of {:s}: ".format(phone))
            outfile = os.path.join(self.directory, phone + ".hmm")

            # If a proto is existing, just keep it.
            if self.trainingcorpus.datatrainer.protodir is not None:
                proto_phone = os.path.join(self.trainingcorpus.datatrainer.protodir, phone + ".hmm")
                if os.path.exists(proto_phone):
                    h = sppasHtkIO.read_hmm(proto_phone)
                    if h.get_vecsize() != self.trainingcorpus.datatrainer.features.nbmv:
                        logging.info(" ... ... [FAIL] Bad HMM vector size. Got {:d}."
                                     "".format(h.get_vecsize()))
                    else:
                        h.set_name(phone)
                        sppasHtkIO.write_hmm(h, os.path.join(self.directory, phone + ".hmm"))
                        logging.info(" ... ... [PROTO]: {:s}".format(proto_phone))
                        continue

            # Train an initial model
            if scp_file is not None:
                if os.path.exists(scp_file):
                    self._create_start_model(phone, outfile)

            # the start model was not created.
            if os.path.exists(outfile) is False:
                h = self.trainingcorpus.datatrainer.proto
                h.set_name(phone)
                sppasHtkIO.write_hmm(h, outfile)
                logging.info(" ... ... [FLAT]")
                h.set_name("proto")
            else:
                # HInit assigned a bad name (it's the filename, including path!!)!
                h = sppasHtkIO.read_hmm(outfile)
                h.set_name(phone)
                sppasHtkIO.write_hmm(h, outfile)
                logging.info(" ... ... [TRAIN]")

    # -----------------------------------------------------------------------

    def create_hmmdefs(self):
        """Create an hmmdefs file from a set of separated hmm files."""
        logging.info(" ... ... Create hmmdefs file with files: ")
        parser = sppasHtkIO()

        # Read the set of HMMs of the directory, and if any, read the macros.
        parser.read(self.directory)

        # Create a default macro if a macros is not already existing.
        if parser.get_macros() is None:
            vector_size = self.trainingcorpus.datatrainer.features.nbmv
            target_kind = self.trainingcorpus.datatrainer.features.targetkind
            param_kind = sppasAcModel.create_parameter_kind("mfcc", target_kind[4:])
            opt = sppasAcModel.create_options(vector_size=vector_size,
                                              parameter_kind=param_kind,
                                              stream_info=[vector_size])
            parser.set_macros([opt])

        # Write all-in-one in an hmmdefs file
        parser.write(self.directory, DEFAULT_HMMDEFS_FILENAME)

    # -----------------------------------------------------------------------

    def create_macros(self):
        """Create macros file from vfloors."""
        ac_model = sppasHtkIO()

        # Create a default macro
        vector_size = self.trainingcorpus.datatrainer.features.nbmv
        target_kind = self.trainingcorpus.datatrainer.features.targetkind
        param_kind = sppasAcModel.create_parameter_kind("mfcc", target_kind[4:])
        opt = sppasAcModel.create_options(vector_size=vector_size,
                                          parameter_kind=param_kind,
                                          stream_info=[vector_size])
        ac_model.set_macros([opt])

        # Get the given vFloors (if it was created by HCompv)
        vfloors = os.path.join(self.directory, "vFloors")
        if os.path.exists(vfloors):
            parser = sppasHtkIO()
            parser.read(self.directory, filename="vFloors")
            m = parser.get_macros()
            ac_model.get_macros().append(m[0])

        # Write the macros
        ac_model.write(self.directory, filename=DEFAULT_MACROS_FILENAME)

# ---------------------------------------------------------------------------


class sppasHTKModelTrainer(object):
    """Acoustic model trainer.

    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2018  Brigitte Bigi
    :author:       Brigitte Bigi
    :contact:      develop@sppas.org

    This class allows to train an acoustic model from audio data and their
    transcriptions (either phonetic or orthographic or both).

    Acoustic models are trained with HTK toolbox using a training corpus of
    speech, previously segmented in utterances and transcribed.
    The trained models are Hidden Markov models (HMMs).
    Typically, the HMM states are modeled by Gaussian mixture densities
    whose parameters are estimated using an expectation maximization procedure.
    The outcome of this training procedure is dependent on the availability
    of accurately annotated data and on good initialization.

    Acoustic models are trained from 16 bits, 16000 hz wav files.
    The Mel-frequency cepstrum coefficients (MFCC) along with their first
    and second derivatives are extracted from the speech.

    Step 1 is the data preparation.

    Step 2 is the monophones initialization.

    Step 3 is the monophones generation.
    This first model is re-estimated using the MFCC files
    to create a new model, using ``HERest''. Then, it fixes the ``sp''
    model from the ``sil'' model by extracting only 3 states of the initial
    5-states model. Finally, this monophone model is re-estimated using the
    MFCC files and the training data.

    Step 4 creates tied-state triphones from monophones and from some language
    specificity defined by means of a configuration file.

    """
    def __init__(self, corpus=None):
        """Create a sppasHTKModelTrainer instance.

        :param corpus: (sppasTrainingCorpus)

        """
        self.corpus = corpus

        # Epoch folders: the content of one round of the training procedure
        self.__epoch = 0
        self.__previous_dir = None  # Folder of the previous epoch
        self.__current_dir = None   # Folder we're currently working in

    # -----------------------------------------------------------------------

    def init_epoch_dir(self):
        """Create a new epoch folder and fill it with the macros."""
        # Create the new epoch folder
        next_dir = os.path.join(self.corpus.datatrainer.workdir,
                                "hmm" + str(self.__epoch).zfill(2))
        if os.path.exists(next_dir) is False:
            os.mkdir(next_dir)

        # Copy the current macros into the new folder
        if self.__current_dir is not None:
            if os.path.exists(os.path.join(self.__current_dir,
                                           DEFAULT_MACROS_FILENAME)):
                shutil.copy(os.path.join(self.__current_dir,
                                         DEFAULT_MACROS_FILENAME), next_dir)

        # Set data
        self.__previous_dir = self.__current_dir
        self.__current_dir = next_dir
        self.__epoch += 1

    # -----------------------------------------------------------------------

    def small_pause(self):
        """Create and save the "sp" model for short pauses.

         - create a "silst" macro, using state 3 of the "sil" HMM,
         - adapt state 3 of the "sil" HMM definition, to use "silst",
         - create a "sp" HMM,
         - save the "sp" HMM into the directory of monophones.

        """
        # Load current acoustic model and prepare the new working directory
        model = sppasHtkIO()
        model.read(self.__current_dir, DEFAULT_HMMDEFS_FILENAME)
        self.init_epoch_dir()

        # Manage sil (to extract the "silst" state).
        sil = model.get_hmm(SIL_PHON)
        silst = copy.deepcopy(sil.get_state(3))
        states = sil.definition['states']
        for item in states:
            if int(item['index']) == 3:
                item['state'] = "silst"

        macro = collections.defaultdict(lambda: None)
        option = collections.defaultdict(lambda: None)
        option['name'] = "silst"
        option['definition'] = silst
        macro['state'] = option
        if model.get_macros() is not None:
            model.get_macros().append(macro)
        else:
            model.set_macros(macro)

        # Create an "sp" HMM and append it in the model.
        # It supposes that a "silst" state is already existing in the model.
        sp = sppasHMM()
        sp.create_sp()
        model.append_hmm(sp)

        # Finally, save the model with the new sp HMM.
        model.write(self.__current_dir, DEFAULT_HMMDEFS_FILENAME)
        self.corpus.monophones.add("sp")
        self.corpus.monophones.save(self.corpus.phonesfile)

    # -----------------------------------------------------------------------

    def align_trs(self):
        """Alignment of the transcribed speech using the current model.

        """
        # Nothing to do!
        if len(self.corpus.transfiles) == 0:
            logging.info("... ... No transcribed files. Nothing to do!")
            return True

        # Create Tokenizer, Phonetizer, Aligner
        try:
            tokenizer = sppasTextNorm(log=None)
            tokenizer.load_resources(vocab_filename=self.corpus.vocabfile,
                                     lang=self.corpus.lang)
            tokenizer.set_std(False)
            tokenizer.set_custom(False)

            phonetizer = sppasPhon()
            phonetizer.load_resources(dict_filename=self.corpus.dictfile)
            phonetizer.set_unk(True)
            phonetizer.set_usestdtokens(False)

            aligner = sppasAlign()
            aligner.load_resources(self.__current_dir)
            if test_command("julius") is False:
                if test_command("HVite") is True:
                    aligner.set_aligner("hvite")
                    logging.info("Aligner is set to HVite.")
                else:
                    logging.error('None of Julius nor HVite command '
                                  'is available.')
                    return False
            else:
                logging.info("Aligner is set to Julius.")
            # aligner.set_clean(False)
            # aligner.set_activity_tier(False)
            # aligner.set_activity_duration_tier(False)
            aligner.set_basic(False)

            alignerdir = os.path.join(self.corpus.datatrainer.workdir,
                                      "alignerio")
            if os.path.exists(alignerdir) is False:
                os.mkdir(alignerdir)

        except Exception as e:
            logging.info('Error while creating automatic annotations: {:s}'
                         ''.format(str(e)))
            return False

        # Annotate
        success = 0
        for trs_filename, trs_workfile in self.corpus.transfiles.items():
            audio_work_file = self.corpus.audiofiles[trs_filename]

            # we are re-aligning...
            if trs_workfile.endswith(".lab"):
                trs_workfile = trs_workfile.replace('.lab', '.xra')

            # Read input file, get tier with orthography
            parser = sppasRW(trs_workfile)
            trs_input = parser.read()
            try:
                tier_input = sppasFindTier.transcription(trs_input)
            except NoInputError:
                try:
                    tier_input = sppasFindTier.tokenization(trs_input)
                except NoInputError:
                    logging.info(" ... [ERROR] "
                                 "No transcription tier for file: {:s}"
                                 "".format(trs_workfile))
                    continue

            # Annotate the tier: tokenization, phonetization, time-alignment
            try:
                tokens_faked, tokens_std, tokens_custom = \
                    tokenizer.convert(tier_input)
            except Exception as e:
                logging.info(" ... [ERROR] "
                             "Text normalization failed for file {:s}. {:s}"
                             "".format(trs_workfile, str(e)))
                return False

            try:
                phones_tier = phonetizer.convert(tokens_faked)
            except Exception as e:
                logging.info(" ... [ERROR] "
                             "Phonetization failed for file {:s}. {:s}"
                             "".format(trs_workfile, str(e)))
                return False

            try:
                tier_phn, tier_tok, tier_pron = \
                    aligner.convert(phones_tier, None, audio_work_file, alignerdir)
            except Exception as e:
                logging.info(" ... [ERROR] "
                             "Alignment error failed file {:s}. {:s}"
                             "".format(trs_workfile, str(e)))
                return False

            # Get only the phonetization from the time-alignment
            if len(tier_phn) == 0:
                logging.info(" ... [ERROR] "
                             "Empty result for file {:s}. "
                             "".format(trs_workfile))
                return False
            if len(tier_phn) == 1 and tier_phn[0].is_labelled() is False:
                logging.info(" ... [ERROR] "
                             "Empty result for file {:s}. "
                             "".format(trs_workfile))
                return False

            tier = self.corpus.phonemap.map_tier(tier_phn)
            tier = tierutils.unalign(tier)
            trs = sppasTranscription()
            trs.append(tier)

            # Save file.
            outfile = trs_workfile.replace('.xra', '.lab')
            parser = sppasRW(outfile)
            parser.write(trs)
            self.corpus.transfiles[trs_filename] = outfile
            logging.info(" ... [SUCCESS] Created file: {:s}".format(outfile))
            success += 1

        if success > 0:
            return True
        return False

    # -----------------------------------------------------------------------

    def make_triphones(self):
        """Extract triphones from monophones data (mlf).

        A new mlf file is created with triphones instead of monophones, and
        a file with the list of triphones is created. This latter is sorted
        in order of arrival (this is very important).

        Command:
        HLEd -T 2 -n output/triphones -l '*' -i output/wintri.mlf scripts/mktri.led corpus.mlf

        """
        if test_command("HLEd") is False:
            logging.info("Error. HLEd is not installed.")
            return False

        # Created files
        triphones = os.path.join(self.__current_dir, "triphones")
        new_mlf = os.path.join(self.__current_dir, "wintri.mlf")

        try:
            subprocess.check_call([
                    "HLEd", "-T", "2",
                    "-l", "'*'",
                    "-n", triphones,
                    "-i", new_mlf,
                    self.corpus.datatrainer.htkscripts.mktrifile,
                    self.corpus.get_mlf(),
                    ],
                    stdout=open(os.devnull, 'ab+'),
                    stderr=open(os.devnull, 'ab+'))
        except subprocess.CalledProcessError as e:
            logging.info('HLEd failed with error:\n'
                         '{:s}'.format(str(e)))
            return False

        return True

    # -----------------------------------------------------------------------

    def train_step(self, scpfile, rounds=3, dopruning=True):
        """Perform some rounds of HERest estimation.

        It expects the input HMM definition to have been initialised and
        it uses the embedded Baum-Welch re-estimation. This involves finding
        the probability of being in each state at each time frame using the
        Forward-Backward algorithm.

        :param scpfile: (str) Description file with the list of data files
        :param rounds: (int) Number of times HERest is called.
        :param dopruning: (bool) Do the pruning
        :returns: bool

        """
        if test_command("HERest") is False:
            logging.error("HERest is not installed.")
            return False

        # Is there files?
        if scpfile is None or len(scpfile) == 0:
            logging.error("The scp file is not defined.")
            return True

        macro = []
        # if self.__previous_dir is not None and \
        #    os.path.exists(os.path.join(self.__previous_dir, DEFAULT_MACROS_FILENAME)) is True:
        #     macro.append('-H')
        #     macro.append(os.path.join(self.__previous_dir, DEFAULT_MACROS_FILENAME))

        stat_file = os.path.join(self.corpus.datatrainer.logdir,
                                 "stats-step"+str(self.__epoch).zfill(2)+".txt")
        log_file = os.path.join(self.corpus.datatrainer.logdir,
                                "log-step"+str(self.__epoch).zfill(2)+".txt")
        error_file = os.path.join(self.corpus.datatrainer.logdir,
                                  "err-step"+str(self.__epoch).zfill(2)+".txt")

        pruning = []
        if dopruning is True:
            pruning.append("-t")
            pruning.append("250.0")
            pruning.append("150.0")
            pruning.append("1000.0")

        for _ in range(rounds):
            logging.info("Training iteration {:d}.".format(self.__epoch))
            self.init_epoch_dir()

            try:
                subprocess.check_call([
                        "HERest", "-T", "2",
                        "-I", self.corpus.get_mlf(),
                        "-C", self.corpus.datatrainer.features.configfile,
                        "-S", scpfile,
                        "-s", stat_file,
                        "-M", self.__current_dir,
                        "-H", os.path.join(self.__previous_dir, DEFAULT_HMMDEFS_FILENAME)]
                        + macro
                        + pruning
                        + [self.corpus.phonesfile],
                        stdout=open(log_file, 'wb+'),
                        stderr=open(error_file, 'wb+'))
            except subprocess.CalledProcessError as e:
                logging.error('HERest failed with error:\n'
                              '{:s}'.format(str(e)))
                return False

        return True

    # -----------------------------------------------------------------------

    def training_step1(self):
        """Step 1 of the training procedure.

        Data preparation.

        """
        logging.info("Step 1. Data preparation.")

        # Create a working directory if needed
        if self.corpus.datatrainer.workdir is None:
            sf = sppasFileUtils()
            work_dir = sf.set_random()
            os.mkdir(work_dir)
            self.corpus.datatrainer.workdir = work_dir

        # Fix resources if needed
        if self.corpus.phonesfile is None:
            self.corpus.fix_resources()

    # -----------------------------------------------------------------------

    def training_step2(self):
        """Step 2 of the training procedure.

        Monophones initialization.

        """
        logging.info("Step 2. Monophones initialization.")

        if self.corpus.datatrainer.workdir is None:
            raise IOError('No working directory was previously fixed. '
                          'Step 2 aborted.')
        if os.path.exists(self.corpus.datatrainer.workdir) is False:
            raise IOError('The working directory was not previously created. '
                          'Step 2 aborted.')

        self.init_epoch_dir()
        initial = sppasHTKModelInitializer(self.corpus, self.__current_dir)
        initial.create_model()

        if os.path.exists(os.path.join(self.__current_dir,
                                       DEFAULT_HMMDEFS_FILENAME)) is False:
            raise IOError('Monophones initialization failed.')

        if len(self.corpus.audiofiles) == 0:
            logging.error('No audio file: '
                          'the model was created only from prototypes.')
            return False

        return True

    # -----------------------------------------------------------------------

    def training_step3(self):
        """Step 3 of the training procedure.

        Monophones training.

            1. Train phonemes from manually time-aligned data.
            2. Create sp model.
            3. Train from phonetized data.
            4. Align transcribed data.
            5. Train from all data.

        """
        logging.info("Step 3. Monophones training.")

        # Step 3.1 Train from time-aligned data.
        # --------------------------------------

        logging.info(" ... Initial training.")
        scp_file = self.corpus.get_scp(aligned=True,
                                       phonetized=False,
                                       transcribed=False)
        ret = self.train_step(scp_file, dopruning=True)
        if ret is False:
            logging.info('Initial training failed.')
            return False

        # Step 3.2 Modeling silence.
        # --------------------------

        logging.info(" ... Modeling silence.")
        self.small_pause()

        # Step 3.3 Train from utterance-aligned data with phonetization.
        # --------------------------------------------------------------

        logging.info(" ... Additional training.")
        scp_file = self.corpus.get_scp(aligned=True,
                                       phonetized=True,
                                       transcribed=False)
        ret = self.train_step(scp_file, dopruning=True)
        if ret is False:
            logging.error('Additional training failed.')
            return False

        # Step 3.4 Train from utterance-aligned data with orthography.
        # ------------------------------------------------------------

        logging.info(" ... Aligning transcribed files.")
        self.align_trs()

        logging.info(" ... Intermediate training.")
        ret = self.train_step(self.corpus.get_scp(aligned=True,
                                                  phonetized=True,
                                                  transcribed=True))
        if ret is False:
            logging.error('Intermediate training failed.')
            return False

        logging.info(" ... Re-Aligning transcribed files.")
        self.align_trs()  # here we should infer 'sp'

        logging.info(" ... Final training.")
        ret = self.train_step(self.corpus.get_scp(aligned=True,
                                                  phonetized=True,
                                                  transcribed=True))
        if ret is False:
            logging.error('Final training failed.')
            return False

        return True

    # -----------------------------------------------------------------------

    def training_step4(self, header_tree):
        """Step 4 of the training procedure. Not implemented yet.

        Triphones training.

        :param header_tree: (str) Name of the script file to train a
        triphone (commonly header-tree.hed).

        """
        logging.info("Step 4. Tied-State Triphones training.")

        # Making Triphones from Monophones
        if self.make_triphones() is False:
            logging.error('Failed to make triphones from the mlf data.')
            return False

        return True
        # TODO: Triphones training.

        # The following code in TCSH has to be translated in PYTHON:

        # cat ./htk/triphones | grep - v "-" | grep - v "+" > monophones
        # cat ./htk/monophones1 monophones | sort | uniq - u >> ./htk/triphones
        # rm monophones

        # This will create the transcription file wintri.mlf (words in triphones),
        # and the file triphones1 which contains the list of the corpus' triphones.
        # Create a list of triphones from monophones:
        # cat ./htk/monophones1 | awk 'BEGIN{print "CL htk/triphones"} {printf "TI T_%s {(*-%s+*,%s+*,*-%s).transP}\n",$0,$0,$0,$0}' >./ htk / mktri.hed
        #
        # cp  hmm11/macros hmm12
        # CAUTION: this will use the file htk/triphones
        # HHEd -A -D -T 1 -H ./hmm11/hmmdefs -M  hmm12 ./htk/mktri.hed ./htk/monophones1

        # logging.info(" ... Intermediate training.")
        # ret = self.train_step(self.corpus.get_scp(aligned=True,
        #                                           phonetized=True,
        #                                           transcribed=True))
        #  if ret is False:
        #      logging.info('ERROR: Intermediate training failed.')
        #      return False

        # ** Making Tied - State Triphones
        #
        # Execute the HDMan command against the entire lexicon file,
        # not just the training dictionnary we have used thus far.
        #  HDMan -A -D -T 1 -b sp -n ./htk/fulllist -g ./htk/global.ded -l ./log/flog ./etc/dict-tri $DICT
        # This creates 2 files:
        #  * dict-tri: the entire dictionary.
        #  * fulllist: the complete list of monophones.

        # Now, add triphones to the full monophones list.
        #  cat ./htk/monophones1 ./htk/triphones | sort | uniq > ./htk/fulllist

        # touch ./htk/tree.hed
        # echo "RO 100 ./log/stats"  >> ./htk/tree.hed
        # echo ""                    >> ./htk/tree.hed
        # echo "TR 0"                >> ./htk/tree.hed
        # echo ""                    >> ./htk/tree.hed
        # cat $TREE                  >> ./htk/tree.hed
        # echo ""                    >> ./htk/tree.hed
        # echo "TR 2"                >> ./htk/tree.hed
        # echo ""                    >> ./htk/tree.hed
        # perl ./scripts/mkclscript.pl TB 350 ./htk/monophones1 >> ./htk/tree.hed
        # echo ""                    >> ./htk/tree.hed
        # echo "TR 1"                >> ./htk/tree.hed
        # echo ""                    >> ./htk/tree.hed
        # echo 'AU "./htk/fulllist"' >> ./htk/tree.hed
        # echo 'CO "./htk/tiedlist"' >> ./htk/tree.hed
        # echo ""                    >> ./htk/tree.hed
        # echo 'ST "./htk/trees"'    >> ./htk/tree.hed
        # echo ""                    >> ./htk/tree.hed

        #  HHEd -A -D -T 1 -H ./hmm14/hmmdefs -M  hmm15 ./htk/mktri.hed ./htk/monophones1
        #  logging.info(" ... Final training.")
        #  ret = self.train_step(self.corpus.get_scp(aligned=True,
        #                                           phonetized=True,
        #                                           transcribed=True))
        #  if ret is False:
        #      logging.info('ERROR: Final training failed.')
        #      return False

        # cp ./htk/tiedlist ./hmm17

    # -----------------------------------------------------------------------

    def get_current_model(self):
        """Return the model of the current epoch, or None."""
        if os.path.exists(os.path.join(self.__current_dir,
                                       DEFAULT_HMMDEFS_FILENAME)) is False:
            return None

        model = sppasHtkIO()
        try:
            model.read(self.__current_dir, DEFAULT_HMMDEFS_FILENAME)
        except:
            return None
        return model

    # -----------------------------------------------------------------------

    def get_current_macro(self):
        """Return the macros of the current epoch, or None."""
        if os.path.exists(os.path.join(self.__current_dir,
                                       DEFAULT_MACROS_FILENAME)) is False:
            return None

        model = sppasHtkIO()
        try:
            model.read(self.__current_dir, DEFAULT_MACROS_FILENAME)
        except:
            return None
        return model

    # -----------------------------------------------------------------------

    def training_recipe(self, outdir=None, delete=False, header_tree=None):
        """Create an acoustic model and return it.

        A corpus (sppasTrainingCorpus) must be previously defined.

        :param outdir: (str) Directory to save the final model and related files
        :param delete: (bool) Delete the working directory.
        :param header_tree: (str) Name of the script file to train a triphone (commonly header-tree.hed).

        :returns: sppasAcModel

        """
        if self.corpus is None: 
            return sppasAcModel()

        # Step 1: Data preparation
        self.training_step1()

        # Step 2: Monophones initialization
        if self.training_step2() is True:

            # Step 3: Monophones training
            if self.training_step3() is True:

                # Step 4: Triphones training
                if header_tree is not None:
                    self.training_step4(header_tree)

        model = self.get_current_model()
        macro = self.get_current_macro()
        self.corpus.datatrainer.features.sourcekind = "WAV"

        if outdir is not None and model is not None:
            to_continue = True
            if os.path.exists(outdir) is False:
                try:
                    os.mkdir(outdir)
                except:
                    logging.error('Error while creating directory {:s}'.format(outdir))
                    to_continue = False
            if to_continue:
                model.write(outdir, DEFAULT_HMMDEFS_FILENAME)
                if macro is not None:
                    macro.write(outdir, DEFAULT_MACROS_FILENAME)
                self.corpus.monophones.save(os.path.join(outdir, DEFAULT_MONOPHONES_FILENAME))
                self.corpus.phonemap.save_as_ascii(os.path.join(outdir, DEFAULT_MAPPING_MONOPHONES_FILENAME))
                self.corpus.datatrainer.features.write_config(os.path.join(outdir, "config"))
        elif model is None:
            model = sppasAcModel()

        if delete is True:
            self.corpus.datatrainer.delete()

        return model
