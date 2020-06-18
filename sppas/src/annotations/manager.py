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

    src.annotations.manager.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~

"""

import logging
import traceback
import sys
import os
from threading import Thread

from sppas.src.wkps import sppasFileUtils
from sppas.src.wkps import States
from sppas.src.anndata import sppasTranscription, sppasRW

import sppas.src.audiodata.aio
import sppas.src.anndata.aio

from sppas.src.annotations import *

from .infotier import sppasMetaInfoTier
from .log import sppasLog

# ----------------------------------------------------------------------------


class sppasAnnotationsManager(Thread):
    """Parent class for running annotation processes.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2019  Brigitte Bigi

    Run annotations on a set of files.

    """

    def __init__(self):
        """Create a new sppasAnnotationsManager instance.

        Initialize a Thread.

        """
        Thread.__init__(self)

        # fix members that are required to run annotations
        self._parameters = None
        self._progress = None
        self._logfile = sppasLog()

        # fix optional members
        self.__do_merge = False

        # start threading
        self.start()

    # -----------------------------------------------------------------------
    # Options of the manager
    # -----------------------------------------------------------------------

    def set_do_merge(self, do_merge):
        """Fix if the 'annotate' method have to create a merged file or not.

        :param do_merge: (bool) if set to True, a merged file will be created

        """
        self.__do_merge = do_merge

    # ------------------------------------------------------------------------
    # Run annotations
    # ------------------------------------------------------------------------

    def annotate(self, parameters, progress=None):
        """Run activated annotations.

        Get execution information from the 'parameters' object.
        Create a Procedure Outcome Report if a filename is set in the
        parameters.

        """
        self._parameters = parameters
        self._progress = progress

        # Print header message in the log-report file or in the logging
        report_file = self._parameters.get_report_filename()
        if report_file:
            try:
                self._logfile = sppasLog(self._parameters)
                self._logfile.create(report_file)
            except:
                self._logfile = sppasLog()
        self._logfile.print_header()
        self._logfile.print_annotations_header()

        # Run all enabled annotations
        ann_stats = [-1] * self._parameters.get_step_numbers()

        for i in range(self._parameters.get_step_numbers()):

            # ignore disabled annotations
            if self._parameters.get_step_status(i) is False:
                continue

            # ok, this annotation is enabled.
            annotation_key = self._parameters.get_step_key(i)
            self._logfile.print_step(i)
            if self._progress:
                self._progress.set_new()
                self._progress.set_header(self._parameters.get_step_name(i))

            try:

                if annotation_key == "fillipus":
                    ann_stats[i] = self._run_fillipus()

                elif annotation_key == "alignment":
                    ann_stats[i] = self._run_alignment()

                elif annotation_key == "rms":
                    ann_stats[i] = self._run_rms()

                else:
                    ann_stats[i] = self._run_annotation(annotation_key)

            except Exception as e:
                self._logfile.print_message(
                    "{:s}\n".format(str(e)), indent=1, status=-1)
                logging.info(traceback.format_exc())
                ann_stats[i] = 0

        # Log file & Merge
        self._logfile.print_separator()
        self._logfile.print_newline()
        if self.__do_merge:
            self._logfile.print_separator()
            self._merge()
        self._logfile.print_stats(ann_stats)
        self._logfile.close()

    # -----------------------------------------------------------------------
    # Private
    # ------------------------------------------------------------------------

    def _get_instance_name(self, annotation_key):
        class_name = None
        for i in range(self._parameters.get_step_numbers()):
            a = self._parameters.get_step(i)
            if a.get_key() == annotation_key:
                class_name = a.get_api()
                break
        if class_name is None:
            raise IOError('Unknown annotation key: {:s}'.format(annotation_key))

        return getattr(sys.modules[__name__], class_name)

    # ------------------------------------------------------------------------

    def _create_ann_instance(self, annotation_key):
        """Create and configure an instance of an automatic annotation.

        :param annotation_key: (str) Key of an annotation
        :returns: sppasBaseAnnotation

        """
        # Find the index of this annotation
        step_idx = self._parameters.get_step_idx(annotation_key)

        # Create the instance and fix options
        auto_annot = self._get_instance_name(annotation_key)(self._logfile)
        self._fix_ann_options(annotation_key, auto_annot)

        # Load language resources
        if self._progress:
            self._progress.set_text("Loading resources...")
        step = self._parameters.get_step(step_idx)
        auto_annot.load_resources(*step.get_langresource(), 
                                  lang=step.get_lang())

        return auto_annot

    # -----------------------------------------------------------------------

    def _fix_ann_options(self, annotation_key, auto_annot):
        """Set the options to an automatic annotation.

        :param annotation_key: (str) Key of an annotation
        :param auto_annot: (BaseAnnotation)

        """
        # Find the index of this annotation
        step_idx = self._parameters.get_step_idx(annotation_key)

        # Get options from the parameters
        options = self._parameters.get_options(step_idx)

        # Set options to the automatic annotation
        if len(options) > 0:
            auto_annot.fix_options(options)

    # -----------------------------------------------------------------------

    def _run_annotation(self, annotation_key):
        """Execute the automatic annotation.

        :param annotation_key: (str) Key of an annotation
        :returns: number of files processed successfully

        """
        a = self._create_ann_instance(annotation_key)
        files_to_process = self.get_annot_files(
            pattern=a.get_input_pattern(),
            extensions=a.get_input_extensions(),
            types=a.get_types())
        # logging.debug('{:d} files to process'.format(len(files_to_process)))
        # logging.debug(files_to_process)
        supported_out_formats = a.get_output_extensions()
        out_format = self._parameters.get_output_format()
        if out_format not in supported_out_formats:
            out_format = supported_out_formats[0]

        out_files = a.batch_processing(files_to_process, self._progress, out_format)

        self._parameters.add_to_workspace(out_files)
        return len(out_files)

    # -----------------------------------------------------------------------

    def _run_fillipus(self):
        """Execute the FillIPUs automatic annotation.

        Requires an audio file with only one channel and its transcription.

        :returns: number of files processed successfully

        """
        a = self._create_ann_instance("fillipus")

        files = list()
        audio_files = self.get_annot_files(
            pattern=a.get_input_pattern(),
            extensions=sppas.src.audiodata.aio.extensions)

        for f in audio_files:
            in_name = os.path.splitext(f)[0] + ".txt"
            files.append((f, in_name))

        out_files = a.batch_processing(
            files,
            self._progress,
            self._parameters.get_output_format())

        self._parameters.add_to_workspace(out_files)
        return len(out_files)

    # ------------------------------------------------------------------------

    def _run_rms(self):
        """Execute the RMS automatic annotation.

        Required: an audio file and an annotated file with intervals

        :returns: number of files processed successfully

        """
        a = self._create_ann_instance("rms")

        # Required input file
        annot_files = self.get_annot_files(
            pattern=a.get_input_pattern(),
            extensions=a.get_input_extensions())

        # Get optional files
        files = list()
        for f in annot_files:
            base_f = os.path.splitext(f)[0]
            base_f = base_f.replace(a.get_input_pattern(), "")

            # Get the audio input file
            audio = sppasAnnotationsManager._get_filename(
                base_f,
                sppas.src.audiodata.aio.extensions)

            # Append the 2 files
            files.append(((audio, f), []))

        out_files = a.batch_processing(
            files,
            self._progress,
            self._parameters.get_output_format())

        self._parameters.add_to_workspace(out_files)
        return len(out_files)

    # ------------------------------------------------------------------------

    def _run_alignment(self):
        """Execute the Alignment automatic annotation.

        Required: a phonetization time-aligned with the IPUs.
        Optional: an audio file (required for speech time-alignment but not
        for the alignment of a written text...).
        Optional: a text-normalization time-aligned with the IPUs.

        :returns: number of files processed successfully

        """
        a = self._create_ann_instance("alignment")

        # Required input file is a phonetization
        phon_files = self.get_annot_files(
            pattern=a.get_input_pattern(),
            extensions=a.get_input_extensions())

        # Get optional files
        files = list()
        for f in phon_files:
            base_f = os.path.splitext(f)[0]
            base_f = base_f.replace(a.get_input_pattern(), "")

            # Get the tokens input file
            extt = [a.get_opt_input_pattern() + self._parameters.get_output_format()]
            for e in sppas.src.anndata.aio.extensions_out:
                extt.append(a.get_opt_input_pattern() + e)
            tok = sppasAnnotationsManager._get_filename(base_f, extt)

            # Get the audio input file
            audio = sppasAnnotationsManager._get_filename(
                base_f,
                sppas.src.audiodata.aio.extensions)

            # Append all 3 files
            files.append(([f], (audio, tok)))

        out_files = a.batch_processing(
            files,
            self._progress,
            self._parameters.get_output_format())

        self._parameters.add_to_workspace(out_files)
        return len(out_files)

    # -----------------------------------------------------------------------
    # Manage annotations:
    # -----------------------------------------------------------------------

    def __add_trs(self, trs, trs_inputfile):

        try:
            parser = sppasRW(trs_inputfile)
            trs_input = parser.read(trs_inputfile)
        except IOError:
            return 0

        for tier in trs_input:
            already_in = False
            if trs.is_empty() is False:
                tier_name = tier.get_name()
                for t in trs:
                    if t.get_name() == tier_name:
                        already_in = True
            if already_in is False:
                trs.append(tier)
        return 1

    # ------------------------------------------------------------------------

    def _merge(self):
        """Merge all annotated files."""
        if self._progress:
            self._progress.set_header("Merge all annotations in a file")
            self._progress.update(0, "")

        # Get the list of files with the ".wav" extension
        filelist = self.get_annot_files(
            pattern="", extensions=sppas.src.audiodata.aio.extensions)
        total = len(filelist)

        output_format = self._parameters.get_output_format()

        for i, f in enumerate(filelist):

            nbfiles = 0

            # Change f, to allow "replace" to work properly
            basef = os.path.splitext(f)[0]

            self._logfile.print_message("File: " + f, indent=0)
            if self._progress:
                self._progress.set_text(os.path.basename(f)+" ("+str(i+1)+"/"+str(total)+")")

            # Add all files content in the same order than to annotate
            trs = sppasTranscription()
            nbfiles += self.__add_trs(trs, basef + output_format)
            for s in range(self._parameters.get_step_numbers()):
                ann_key = self._parameters.get_step_key(s)

                # create an instance of the annotation to get its pattern
                a = self._get_instance_name(ann_key)()
                pattern = a.get_pattern()
                if len(pattern) > 0:
                    nbfiles += self.__add_trs(trs, basef + pattern + output_format)

            if nbfiles > 1:
                try:
                    info_tier = sppasMetaInfoTier(trs)
                    tier = info_tier.create_time_tier(
                        trs.get_min_loc().get_midpoint(),
                        trs.get_max_loc().get_midpoint())
                    trs.append(tier)
                    out_file = basef + "-merge" + self._parameters.get_output_format()
                    parser = sppasRW(out_file)
                    parser.write(trs)
                    self._logfile.print_message(out_file, indent=1, status=0)
                    self._parameters.add_to_workspace([out_file])

                except Exception as e:
                    self._logfile.print_message(str(e), indent=1, status=-1)

            if self._progress:
                self._progress.set_fraction(float((i+1))/float(total))
            self._logfile.print_newline()

        if self._progress:
            self._progress.update(1, "Completed.")
            # self._progress.set_header("")

    # -----------------------------------------------------------------------
    # Manage files:
    # -----------------------------------------------------------------------

    def get_annot_files(self, pattern, extensions, types=[]):
        """Search for annotated files with pattern and extensions.

        :param pattern: (str) The pattern to search in the inputs
        :param extensions: (str) The extension to search for
        :param types: (list of str) The types to search in the references of the workspace
        :returns: List of filenames matching pattern and extensions

        """
        files = list()
        wkp = self._parameters.get_workspace()

        # create a list with the pattern followed by each possible extension
        if len(pattern) > 0:
            pat_ext = [pattern + self._parameters.get_output_format()]
            for e in extensions:
                pat_ext.append(pattern + e)
        else:
            pat_ext = extensions

        roots = wkp.get_fileroot_from_state(States().CHECKED) + \
                wkp.get_fileroot_from_state(States().AT_LEAST_ONE_CHECKED)

        for root in roots:

            new_file = sppasAnnotationsManager._get_filename(root.id, pat_ext)
            if new_file is None:
                continue

            if len(types) == 0 or "STANDALONE" in types:
                files.append(new_file)
            if "SPEAKER" in types:
                logging.error("Annotations of type SPEAKER are not supported yet.")
                pass
            if "INTERACTION" in types:
                for ref in root.get_references():
                    if ref.get_type() == "INTERACTION":
                        for fr in wkp.get_fileroot_with_ref(ref):
                            if fr != root:
                                other_file = sppasAnnotationsManager._get_filename(fr.id, pat_ext)

                                if other_file is not None:
                                    files.append((new_file, other_file))

        return files

    # ------------------------------------------------------------------------

    @staticmethod
    def _get_filename(rootname, extensions):
        """Return a filename corresponding to one of extensions.

        :param rootname: input file name
        :param extensions: the list of expected extension
        :returns: a file name of the first existing file with an expected
        extension or None

        """
        #base_name = os.path.splitext(filename)[0]
        for ext in extensions:
            ext_filename = rootname + ext
            new_filename = sppasFileUtils(ext_filename).exists()
            if new_filename is not None and os.path.isfile(new_filename):
                return new_filename

        return None
