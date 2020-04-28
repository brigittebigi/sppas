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

    src.annotations.param.py
    ~~~~~~~~~~~~~~~~~~~~~~~~

"""

import logging
import json
import os

from sppas import paths
from sppas import annots
from sppas import sppasTypeError

from sppas.src.config import msg
from sppas.src.structs import sppasOption
from sppas.src.structs import sppasLangResource
from sppas.src.anndata.aio import extensions_out as annots_ext

from sppas.src.wkps import sppasWorkspace, States

# ----------------------------------------------------------------------------


class annotationParam(object):
    """Annotation parameters data manager.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2018  Brigitte Bigi

    Class to store data of an automatic annotation like its name, description,
    supported languages, etc.

    """

    def __init__(self, filename=None):
        """Create a new annotationParam instance.

        :param filename: (str) Annotation configuration file

        """
        # An identifier to represent this annotation
        self.__key = None
        # The name of the annotation
        self.__name = ""
        # The description of the annotation
        self.__descr = ""
        # Name of the instance class of this annotation
        self.__api = None
        # The types this annotation can support
        self.__types = []
        # The status of the annotation
        self.__enabled = False
        self.__invalid = False
        # The language resource: sppasLangResource()
        self.__resources = list()
        # The list of options
        self.__options = list()

        # Fix all members from a given config file
        if filename is not None:
            self.parse(filename)

    # ------------------------------------------------------------------------

    def parse(self, filename):
        """Parse a configuration file to fill members.

        :param filename: (str) Annotation configuration file (.ini)

        """
        if filename.endswith('.json'):

            config = os.path.join(paths.etc, filename)
            if os.path.exists(config) is False:
                raise IOError('Installation error: the file to configure the '
                              'automatic annotations does not exist.')

            # Read the whole file content
            with open(config) as cfg:
                conf = json.load(cfg)

            self.__key = conf['id']
            self.__name = msg(conf.get('name', ''), "annotations)")  # translate the name
            self.__descr = conf.get('descr', "")
            self.__types = conf.get('anntype', ["STANDALONE"])
            self.__api = conf.get('api', None)
            if self.__api is None:
                self.__enabled = False
                self.__invalid = True

            for new_option in conf['options']:
                opt = sppasOption(new_option['id'])
                opt.set_type(new_option['type'])
                opt.set_value(str(new_option['value']))  # dangerous cast
                opt.set_text(msg(new_option.get('text', ''), "annotations"))   # translated
                self.__options.append(opt)

            for new_resource in conf['resources']:
                lr = sppasLangResource()
                lr.set(new_resource['type'],
                       new_resource['path'],
                       new_resource.get('name', ''),
                       new_resource['ext'])
                self.__resources.append(lr)

        else:
            raise IOError('Unknown extension for filename {:s}'.format(filename))

    # -----------------------------------------------------------------------
    # Setters
    # -----------------------------------------------------------------------

    def set_activate(self, activate):
        """Enable the annotation but only if this annotation is valid.

        :param activate: (bool) Enable or disable the annotation
        :returns: (bool) enabled or disabled

        """
        self.__enabled = activate
        if activate is True and self.__invalid is True:
            self.__enabled = False
        return self.__enabled

    # -----------------------------------------------------------------------

    def set_lang(self, lang):
        """Set the language of the annotation, if this latter is accepted.

        :param lang: (str) Language to fix for the annotation
        :returns: (bool) Language is set or not

        """
        if len(self.__resources) > 0:
            try:
                self.__resources[0].set_lang(lang)
                return True
            except:
                self.__invalid = True
                self.__enabled = False
                return False
        return True

    # -----------------------------------------------------------------------
    # Getters
    # -----------------------------------------------------------------------

    def get_key(self):
        """Return the identifier of the annotation (str)."""
        return self.__key

    # -----------------------------------------------------------------------

    def get_name(self):
        """Return the name of the annotation (str)."""
        return self.__name

    # -----------------------------------------------------------------------

    def get_types(self):
        """Return the list of types the annotation can support (list of str)."""
        return self.__types

    # -----------------------------------------------------------------------

    def get_descr(self):
        """Return the description of the annotation (str)."""
        return self.__descr

    # -----------------------------------------------------------------------

    def get_activate(self):
        """Return the activation status of the annotation (bool)."""
        return self.__enabled

    # -----------------------------------------------------------------------

    def get_api(self):
        """Return the name of the class to instantiate to perform this annotation."""
        return self.__api

    # -----------------------------------------------------------------------

    def get_lang(self):
        """Return the language or an empty string or None."""
        if len(self.__resources) > 0:
            return self.__resources[0].get_lang()

        # this annotation does not require a lang to be defined
        return None

    # -----------------------------------------------------------------------

    def get_langlist(self):
        """Return the list of available languages (list of str)."""
        if len(self.__resources) > 0:
            return self.__resources[0].get_langlist()
        return []

    # -----------------------------------------------------------------------

    def get_langresource(self):
        """Return the list of language resources."""
        return [r.get_langresource() for r in self.__resources]

    # -----------------------------------------------------------------------

    def get_options(self):
        """Return the list of options of the annotation."""
        return self.__options

    # -----------------------------------------------------------------------

    def get_option(self, step):
        """Return the step-th option."""
        return self.__options[step]

    # -----------------------------------------------------------------------

    def get_option_by_key(self, key):
        """Return an option from its key."""
        for opt in self.__options:
            if key == opt.get_key():
                return opt

    # -----------------------------------------------------------------------

    def set_option_value(self, key, value):
        """Change value of an option.

        :param key: (str) Identifier of the option
        :param value: (any) New value for the option
        :raises: KeyError

        """
        # the option is already in the list, change its value
        for opt in self.__options:
            if key == opt.get_key():
                opt.set_value(value)
                return

        # the option was not found in the list
        raise KeyError("Unknown option {:s} in annotation parameters."
                       "".format(key))

# ---------------------------------------------------------------------------


class sppasParam(object):
    """Annotation parameters manager.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2018  Brigitte Bigi

    Parameters of a set of annotations.

    """

    def __init__(self, annotation_keys=None):
        """Create a new sppasParam instance with default values.

        :param annotation_keys: (list) List of annotations to load. None=ALL.

        """
        # A log file to communicate to the user
        self._report = None

        # The format of the annotated files
        self._output_ext = annots.extension

        # Input files to annotate
        self._workspace = sppasWorkspace()

        # The parameters of all the annotations
        self.annotations = []
        self.load_annotations(annotation_keys)

    # ------------------------------------------------------------------------

    def load_annotations(self, annotation_files=None):
        """Load the annotation configuration files.

        Load from a list of given file names (without path) or from the
        default sppas ui configuration file.

        :param annotation_files: (list) List of annotations to load. None=ALL.

        """
        if not annotation_files or len(annotation_files) == 0:
            self.parse_config_file()

        else:
            for cfg_file in annotation_files:
                self.__load(os.path.join(paths.etc, cfg_file))

    # ------------------------------------------------------------------------

    def parse_config_file(self):
        """Parse the sppasui.json file.

        Parse the file to get the list of annotations and parse the
        corresponding "ini" file.

        """
        config = os.path.join(paths.etc, "sppasui.json")
        if os.path.exists(config) is False:
            raise IOError('Installation error: the file to configure the '
                          'automatic annotations does not exist.')

        # Read the whole file content
        with open(config) as cfg:
            dict_cfg = json.load(cfg)

        # Load annotation configurations
        for ann in dict_cfg["annotate"]:
            self.__load(os.path.join(paths.etc, ann["config"]))

    # -----------------------------------------------------------------------

    def __load(self, cfg_file):
        """Load parameters of an annotation from its configuration file."""
        try:
            a = annotationParam(cfg_file)
            self.annotations.append(a)
        except:
            a = None
            logging.error('Configuration file {:s} not loaded.'
                          ''.format(cfg_file))
        return a

    # -----------------------------------------------------------------------
    # Input entries to annotate
    # -----------------------------------------------------------------------

    def get_workspace(self):
        """Return the workspace."""
        return self._workspace

    # -----------------------------------------------------------------------

    def set_workspace(self, wkp):
        if isinstance(wkp, FileData) is False:
            raise sppasTypeError("sppasWorkspace", type(wkp))
        logging.debug('New data to set in sppasParam. '
                      'Id={:s}'.format(wkp.id))
        self._workspace = wkp

    # -----------------------------------------------------------------------

    def add_to_workspace(self, files):
        """Add a list of files or directories into the workspace.

        The state of all the added files is set to CHECKED.

        :param files: (str or list of str)

        """
        if isinstance(files, list) is False:
            try:
                if os.path.isfile(files):
                    objs = self._workspace.add_file(files)
                    if objs is not None:
                        for obj in objs:
                            self._workspace.set_object_state(States().CHECKED, obj)

                elif os.path.isdir(files):
                    for f in os.listdir(files):
                        self.add_to_workspace(os.path.join(files, f))

            except Exception as e:
                logging.error('File {!s:s} not added into the workspace: {:s}'
                              ''.format(files, str(e)))
        else:
            for f in files:
                self.add_to_workspace(f)

    # -----------------------------------------------------------------------
    # deprecated:
    # -----------------------------------------------------------------------

    def get_checked_roots(self):
        """Return the list of entries to annotate."""
        roots = self._workspace.get_fileroot_from_state(States().CHECKED) + self._workspace.get_fileroot_from_state(States().AT_LEAST_ONE_CHECKED)
        return [r.id for r in roots]

    # -----------------------------------------------------------------------
    # Procedure Outcome Report file name
    # -----------------------------------------------------------------------

    def set_report_filename(self, filename):
        """Fix the name of the file to save the report of the annotations.

        :param filename: (str) Filename for the Procedure Outcome Report

        """
        self._report = filename

    # -----------------------------------------------------------------------

    def get_report_filename(self):
        """Return the name of the file for the Procedure Outcome Report."""
        return self._report

    # -----------------------------------------------------------------------
    # selected language
    # -----------------------------------------------------------------------

    def set_lang(self, language, step=None):
        if step is not None:
            self.annotations[step].set_lang(language)
        else:
            for a in self.annotations:
                a.set_lang(language)

    def get_lang(self, step=None):
        if step is None:
            for a in self.annotations:
                lang = a.get_lang()
                if lang is not None and lang != annots.UNDETERMINED:
                    return a.get_lang()
            return annots.UNDETERMINED
        return self.annotations[step].get_lang()

    def get_langresource(self, step):
        return self.annotations[step].get_langresource()

    # ------------------------------------------------------------------------
    # annotations
    # ------------------------------------------------------------------------

    def activate_annotation(self, stepname):
        for i, a in enumerate(self.annotations):
            if a.get_key() == stepname:
                a.set_activate(True)
                return i
        return -1

    def activate_step(self, step):
        step = self.__check_step(step)
        self.annotations[step].set_activate(True)

    def disable_step(self, step):
        step = self.__check_step(step)
        self.annotations[step].set_activate(False)

    def get_step_status(self, step):
        step = self.__check_step(step)
        return self.annotations[step].get_activate()

    def get_step_name(self, step):
        step = self.__check_step(step)
        return self.annotations[step].get_name()

    def get_step_types(self, step):
        step = self.__check_step(step)
        return self.annotations[step].get_types()

    def get_step_descr(self, step):
        step = self.__check_step(step)
        return self.annotations[step].get_descr()

    # ------------------------------------------------------------------------

    def get_step_idx(self, annotation_key):
        """Get the annotation step index from an annotation key.

        :param annotation_key: (str)
        :raises: KeyError

        """
        for i, a in enumerate(self.annotations):
            if a.get_key() == annotation_key:
                return i

        raise KeyError('No configuration file is available for an annotation'
                       'with key {:s}'.format(annotation_key))

    # ------------------------------------------------------------------------

    @staticmethod
    def __check_step(step):
        try:
            step = int(step)
        except TypeError:
            raise sppasTypeError(step, "int")
        return step

    # ------------------------------------------------------------------------

    def get_step_key(self, step):
        step = self.__check_step(step)
        return self.annotations[step].get_key()

    def get_step_numbers(self):
        return len(self.annotations)

    def get_steplist(self):
        steps = []
        for i in range(len(self.annotations)):
            steps.append(self.annotations[i].get_name())
        return steps

    def get_langlist(self, step=2):
        step = self.__check_step(step)
        return self.annotations[step].get_langlist()

    def get_step(self, step):
        """Return the 'sppasParam' instance of the annotation."""
        step = self.__check_step(step)
        return self.annotations[step]

    def get_options(self, step):
        step = self.__check_step(step)
        return self.annotations[step].get_options()

    def set_option_value(self, step, key, value):
        step = self.__check_step(step)
        self.annotations[step].set_option_value(key, value)

    # -----------------------------------------------------------------------
    # Annotation file output format
    # -----------------------------------------------------------------------

    def get_output_format(self):
        """Return the output format of the annotations (extension)."""
        return self._output_ext

    # -----------------------------------------------------------------------

    def set_output_format(self, output_format):
        """Fix the output format of the annotations.

        :param output_format: (str) File extension (with or without a dot)
        :returns: the extension really set.

        """

        # Force to contain the dot
        if not output_format.startswith("."):
            output_format = "." + output_format

        # Force to use the appropriate upper-lower cases
        for e in annots_ext:
            if output_format.lower() == e.lower():
                output_format = e

        # Check if this extension is know. If not, set to the default.
        if output_format not in annots_ext:
            # Instead we could raise an exception...
            logging.warning(
                "Unknown extension: {:s}. Output format is set to the "
                "default: {:s}.".format(output_format, annots.extension))
            output_format = annots.extension

        self._output_ext = output_format
