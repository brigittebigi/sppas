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

    src.annotations.baseannot.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""

import logging
import os
import json

from sppas.src.config import annots
from sppas.src.config import paths
from sppas.src.config import info
from sppas.src.exceptions import sppasError
from sppas.src.exceptions import sppasExtensionWriteError
from sppas.src.structs import sppasOption
from sppas.src.wkps import sppasFileUtils
from sppas.src.anndata import sppasRW
from sppas.src.imgdata import image_extensions
from sppas.src.audiodata import audio_extensions
from sppas.src.videodata import video_extensions

from .annotationsexc import AnnotationOptionError
from .diagnosis import sppasDiagnosis
from .log import sppasLog

# ---------------------------------------------------------------------------


class sppasBaseAnnotation(object):
    """Base class for any automatic annotation integrated into SPPAS.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2020  Brigitte Bigi

    """

    def __init__(self, config, log=None):
        """Base class for any SPPAS automatic annotation.

        Load default options/member values from a configuration file.
        This file must be in paths.etc

        Log is used for a better communication of the annotation process and its
        results. If None, logs are redirected to the default logging system.

        :param config: (str) Name of the JSON configuration file, without path.
        :param log: (sppasLog) Human-readable logs.

        """
        # Log messages for the user
        if log is None:
            self.logfile = sppasLog()
        else:
            self.logfile = log

        # The annotation types (standalone, speaker...)
        self.__types = list()
        # The options the annotation can support
        self._options = dict()
        # The name of the annotation
        self.name = self.__class__.__name__

        # New in SPPAS 3.3
        self._out_extensions = dict()
        self.set_default_out_extensions()

        # Then, fill in the values from a configuration file
        self.__load(config)

    # -----------------------------------------------------------------------
    # Input and output file name and/or file extension
    # -----------------------------------------------------------------------

    def set_default_out_extensions(self):
        """Return the default output extension of each format.

        The default extension of each format is defined in the config.

        """
        self._out_extensions["ANNOT"] = annots.annot_extension
        self._out_extensions["IMAGE"] = annots.image_extension
        self._out_extensions["VIDEO"] = annots.video_extension
        self._out_extensions["AUDIO"] = annots.audio_extension

    # -----------------------------------------------------------------------

    def set_out_extension(self, extension, out_format="ANNOT"):
        """Set the extension for a specific out format.

        :param extension: (str) File extension for created files
        :param out_format: (str) One of ANNOT, IMAGE, VIDEO, AUDIO

        """
        if out_format == "ANNOT":
            all_ext = ["."+e for e in sppasRW.extensions_out()]
        elif out_format == "AUDIO":
            all_ext = audio_extensions
        elif out_format == "VIDEO":
            all_ext = video_extensions
        elif out_format == "IMAGE":
            all_ext = image_extensions
        else:
            raise sppasError("Unknown {} out format".format(out_format))

        if extension.startswith(".") is False:
            extension = "." + extension

        if extension not in all_ext and out_format not in ("VIDEO", "IMAGE"):
            logging.error("Extension {} is not in the {} list."
                          "".format(extension, out_format))
            raise sppasExtensionWriteError(extension)

        self._out_extensions[out_format] = extension

    # -----------------------------------------------------------------------

    def fix_out_file_ext(self, output, out_format="ANNOT"):
        """Return the output with an appropriate file extension.

        If the output has already an extension, it is not changed.

        :param output: (str) Base name or filename
        :param out_format: (str) One of ANNOT, IMAGE, VIDEO, AUDIO
        :return: (str) filename

        """
        _, fe = os.path.splitext(output)
        if len(fe) == 0:
            # No extension in the output.
            output = output + self._out_extensions[out_format]

        # If output exists, it is overridden
        if os.path.exists(output) and self.logfile is not None:
            self.logfile.print_message(
                (info(1300, "annotations")).format(output) + " " +
                info(1304, "annotations"), indent=2, status=annots.warning)

        return output

    # -----------------------------------------------------------------------

    def get_pattern(self):
        """Pattern that the annotation uses for its output filename."""
        return self._options.get("outputpattern", "")

    def get_input_pattern(self):
        """Pattern that the annotation expects for its input filename."""
        return self._options.get("inputpattern", "")

    def get_opt_input_pattern(self):
        """Pattern that the annotation can optionally use as input."""
        return self._options.get("inputoptpattern", "")

    # -----------------------------------------------------------------------

    @staticmethod
    def get_input_extensions():
        """Extensions that the annotation expects for its input filename."""
        ext = ["."+e for e in sppasRW.extensions_in()]
        if ".pitchtier" in ext:
            ext.remove(".pitchtier")
        if ".hz" in ext:
            ext.remove(".hz")

        return ext

    # -----------------------------------------------------------------------

    def get_out_name(self, filename, output_format=""):
        """Return the output filename from the input one.

        Output filename is created from the given filename, the annotation
        output pattern and the given output format (if any).

        :param filename: (str) Name of the input file
        :param output_format: (str) Extension of the output file
        :returns: (str)

        """
        # remove the extension
        fn, _ = os.path.splitext(filename)

        # remove the existing pattern
        r = self.get_input_pattern()
        if len(r) > 0 and fn.endswith(r):
            fn = fn[:-len(r)]

        # add the annotation pattern and the extension
        return fn + self.get_pattern() + output_format

    # -----------------------------------------------------------------------
    # Shared methods to fix options and to annotate
    # -----------------------------------------------------------------------

    def __load(self, filename):
        """Fix members from a configuration file.

        :param filename: (str) Name of the configuration file (json)
        The filename must NOT contain the path. This file must be in
        paths.etc

        """
        config = os.path.join(paths.etc, filename)
        if os.path.exists(config) is False:
            raise IOError('Installation error: the file {:s} to configure '
                          'the automatic annotations does not exist.'
                          ''.format(config))

        # Read the whole file content
        with open(config) as cfg:
            dict_cfg = json.load(cfg)

        # Extract options
        for new_option in dict_cfg['options']:
            # Create a sppasOption() instance to convert into the right type
            opt = sppasOption(new_option['id'])
            opt.set_type(new_option['type'])
            opt.set_value(str(new_option['value']))
            # Add key and typed value to the dict of options
            self._options[opt.get_key()] = opt.get_value()

        # Extract other members
        self.name = dict_cfg.get('name', self.__class__.__name__)
        self.__types = dict_cfg.get('anntype', [annots.types[0]])

    # -----------------------------------------------------------------------

    def get_option(self, key):
        """Return the option value of a given key or raise KeyError.

        :param key: (str) Return the value of an option, or None.
        :raises: KeyError

        """
        if key in self._options:
            return self._options[key]
        raise KeyError('{:s} is not a valid option for the automatic '
                       'annotation.'.format(key))

    # -----------------------------------------------------------------------

    def fix_options(self, options):
        """Fix all options of the annotation from a list of sppasOption().

        :param options: (list of sppasOption)

        """
        for opt in options:

            key = opt.get_key()
            if key in ("inputpattern", "outputpattern", "inputoptpattern"):
                self._options[key] = opt.get_value()

            else:
                raise AnnotationOptionError(key)

    # -----------------------------------------------------------------------

    def get_types(self):
        """Return the list of types this annotation can perform.

        If this annotation is expecting another file, the type allow to
        find it by using the references of the workspace (if any).

        """
        return self.__types

    # -----------------------------------------------------------------------
    # Load the linguistic resources
    # -----------------------------------------------------------------------

    def load_resources(self, *args, **kwargs):
        """Load the linguistic resources."""
        pass

    # -----------------------------------------------------------------------
    # Perform automatic annotation:
    # -----------------------------------------------------------------------

    def run(self, input_file, opt_input_file=None, output_file=None):
        """Run the automatic annotation process on an input.

        Both the required and the optional inputs are a list of files
        the annotation needs (audio, transcription, pitch, etc).
        There's no constraint on the filenames, neither for the inputs nor
        for the outputs.

        :param input_file: (list of str) the required input(s)
        :param opt_input_file: (list of str) the optional input(s)
        :param output_file: (str) the output name with or without extension
        :returns: (sppasTranscription)

        """
        raise NotImplementedError

    # -----------------------------------------------------------------------

    def run_for_batch_processing(self,
                                 input_file,
                                 opt_input_file):
        """Perform the annotation on a file.

        This method is called by 'batch_processing'. It fixes the name of the
        output file, and call the run method.
        Can be overridden.

        :param input_file: (list of str) the required input(s)
        :param opt_input_file: (list of str) the optional input(s)
        :returns: output file name or None

        """
        # Save a copy of the options ('run' could modify the current ones)
        opt = self._options.copy()

        # Fix the output base name with the appropriate pattern
        out_name = self.get_out_name(input_file[0])

        # Execute annotation
        try:
            self.run(input_file, opt_input_file, out_name)
        except Exception as e:
            out_name = None
            self.logfile.print_message("{:s}\n".format(str(e)), indent=2, status=annots.error)

        # Restore the options before returning the result
        self._options = opt
        return out_name

    # -----------------------------------------------------------------------

    def batch_processing(self,
                         file_names,
                         progress=None):
        """Perform the annotation on a bunch of files.

        The given list of inputs can be either:
            - a list of the files to be used as a single input:
              [file1, file2, ...]
            - a list of the files to be used as several-required-inputs:
              [(file1_a, file1_b), (file2_a, file2_b), ...]
            - a list of the files to be used as inputs and optional-inputs:
              [((file_1_a), (file_1_x)), ((file_2_a), (file_2_x)), ... ]
            - a list of the files to be used as several-required-inputs and
              optional-inputs:
              [((file1_a, file1_b), (file_1_x, file_1_y)), ...]

        :param file_names: (list) List of inputs
        :param progress: ProcessProgressTerminal() or ProcessProgressDialog()
        :returns: (list of str) List of created files

        """
        if len(self._options) > 0:
            self.print_options()

        total = len(file_names)
        if total == 0:
            return list()
        files_processed_success = list()
        if progress:
            progress.update(0, "")

        # Execute the annotation for each file in the list
        for i, input_files in enumerate(file_names):

            required_inputs, optional_inputs = self._split_inputs(input_files)
            self.print_diagnosis(*required_inputs)
            self.print_diagnosis(*optional_inputs)
            if progress:
                progress.set_fraction(round(float(i)/float(total), 2))
                progress.set_text("{!s:s}".format(*required_inputs))

            out_name = self.run_for_batch_processing(required_inputs, optional_inputs)
            if out_name is None:
                self.logfile.print_message(
                    info(1306, "annotations"), indent=1, status=annots.info)
            else:
                files_processed_success.append(out_name)
                self.logfile.print_message(out_name, indent=1, status=annots.ok)
            self.logfile.print_newline()

        # Indicate completed!
        if progress:
            progress.update(1, (info(9000, "ui").format(len(files_processed_success),
                                                        total)))

        return files_processed_success

    # -----------------------------------------------------------------------

    @staticmethod
    def transfer_metadata(from_trs, to_trs):
        """Transfer the metadata from a sppasTranscription to another one.

        The identifier is not copied and any already existing metadata is
        not copied.

        """
        for key in from_trs.get_meta_keys():
            if to_trs.get_meta(key, default=None) is None:
                to_trs.set_meta(key, from_trs.get_meta(key))

    # -----------------------------------------------------------------------

    def _split_inputs(self, input_files):
        """Return required and optional inputs from the input files.

        The given input files can be:

            - a single input:
              file1
            - several-required-inputs:
              (file1_a, file1_b)
            - a single required-input and an optional-input:
              ((file_1_a), file_1_x)
            - several required-inputs and an optional-input:
              ((file1_a, file1_b), file_1_x))
            - several required-inputs and several optional-inputs:
              ((file1_a, file1_b), (file_1_x, file_1_y)))

        :param input_files: (str, list of str, list of tuple, list of tuple of tuple)
        :returns: a list of required files; a list of optional files

        """
        if len(input_files) == 0:
            raise IOError

        optional_inputs = tuple()

        if isinstance(input_files, (list, tuple)) is False:
            # a single file to be used as a single required input
            required_inputs = [input_files]

        else:
            # input_files is either a list of required + optional files
            # or a list of required files
            if isinstance(input_files[0], (list, tuple)) is False:
                # input_files is a list of required files
                required_inputs = input_files
            else:

                # input_files is a list with (required inputs, optional inputs)
                required_inputs = input_files[0]
                # optional inputs can be either a single file or a list
                if len(input_files) == 2:
                    if isinstance(input_files[1], (list, tuple)) is False:
                        optional_inputs = [input_files[1]]
                    else:
                        optional_inputs = input_files[1]

        for fn in required_inputs:
            if os.path.exists(fn) is False:
                msg = info(1308, "annotations") + " " + (info(1310, "annotations")).format(fn)
                self.print_filename(input_files[0])
                self.logfile.print_message(msg, indent=1, status=annots.error)
                self.logfile.print_message(info(1312, "annotations"),
                                           indent=1, status=annots.ignore)
                raise IOError(msg)

        return required_inputs, optional_inputs

    # -----------------------------------------------------------------------
    # To communicate with the interface:
    # -----------------------------------------------------------------------

    def print_filename(self, filename):
        """Print the annotation name applied on a filename in the user log.

        :param filename: (str) Name of the file to annotate.

        """
        if self.logfile:
            fn = os.path.basename(filename)
            self.logfile.print_message(
                (info(1056, "annotations")).format(fn), indent=0, status=None)
        else:
            logging.info((info(1056, "annotations")).format(filename))

    # -----------------------------------------------------------------------

    def print_options(self):
        """Print the list of options in the user log.

        """
        self.logfile.print_message(info(1050, "annotations") + ": ",
                                   indent=0, status=None)

        for k, v in self._options.items():
            msg = " ... {!s:s}: {!s:s}".format(k, v)
            self.logfile.print_message(msg, indent=0, status=None)

        self.logfile.print_newline()

    # -----------------------------------------------------------------------

    def print_diagnosis(self, *filenames):
        """Print the diagnosis of a list of files in the user report.

        :param filenames: (list) List of files.

        """
        for filename in filenames:
            if filename is not None and os.path.exists(filename):
                fn = os.path.basename(filename)
                (s, m) = sppasDiagnosis.check_file(filename)
                msg = (info(1056, "annotations")).format(fn) + ": {!s:s}".format(m)
                self.logfile.print_message(msg, indent=0, status=None)

    # ------------------------------------------------------------------------
    # Utility methods:
    # ------------------------------------------------------------------------

    @staticmethod
    def _get_filename(filename, extensions):
        """Return a filename corresponding to one of the extensions.

        :param filename: input file name
        :param extensions: the list of expected extension
        :returns: a file name of the first existing file with an expected extension or None

        """
        base_name = os.path.splitext(filename)[0]
        for ext in extensions:
            ext_filename = base_name + ext
            new_filename = sppasFileUtils(ext_filename).exists()
            if new_filename is not None and os.path.isfile(new_filename):
                return new_filename

        return None
