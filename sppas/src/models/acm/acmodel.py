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

    src.models.acm.acmodel.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~

"""
import collections
import json
import copy
import uuid

from sppas.src.resources.mapping import sppasMapping
from sppas.src.utils.makeunicode import sppasUnicode

from ..modelsexc import ModelsDataTypeError
from .hmm import sppasHMM
from .tiedlist import sppasTiedList

# ---------------------------------------------------------------------------


class sppasAcModel(object):
    """Acoustic model representation.

    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2018  Brigitte Bigi
    :author:       Brigitte Bigi
    :contact:      develop@sppas.org

    An acoustic model is made of:
       - 'macros' is an OrderedDict of options, transitions, states, ...
       - 'hmms' models (one per phone/biphone/triphone): list of HMM instances
       - a tiedlist (if any)
       - a mapping table to replace phone names.

    """

    def __init__(self, name=None):
        """Create an sppasAcModel instance."""
        self._name = None
        self._macros = None
        self._hmms = list()
        self._tiedlist = sppasTiedList()
        self._repllist = sppasMapping()

        self.set_name(name)

    # -----------------------------------------------------------------------
    # Name
    # -----------------------------------------------------------------------

    def get_name(self):
        """Return the identifier name of the acoustic model."""
        return self._name

    # -----------------------------------------------------------------------

    def set_name(self, name=None):
        """Set the name of the acoustic model.

        :param name: (str or None) The identifier name or None.
        :returns: the name

        """
        if name is None:
            name = str(uuid.uuid4())
        su = sppasUnicode(name)
        self._name = su.to_strip()

        return self._name

    # -----------------------------------------------------------------------
    # Getters
    # -----------------------------------------------------------------------

    def get_macros(self):
        return self._macros

    def get_hmms(self):
        return self._hmms

    def get_tiedlist(self):
        return self._tiedlist

    def get_repllist(self):
        return self._repllist

    # -----------------------------------------------------------------------
    # Setters
    # -----------------------------------------------------------------------

    def set_repllist(self, repllist):
        """Set the placement list of the model.

        :param repllist: (sppasMapping)

        """
        if not isinstance(repllist, sppasMapping):
            raise ModelsDataTypeError("tiedlist",
                                      "sppasMapping()",
                                      type(repllist))

        self._repllist = repllist

    # -----------------------------------------------------------------------

    def set_macros(self, macros):
        """Set the macros of the model.

        :param macros: (OrderedDict)

        """
        self._macros = macros

    # -----------------------------------------------------------------------

    def set_hmms(self, hmms):
        """Set the list of HMMs the model.

        :param hmms: (list) List of HMM instances

        """
        if not (isinstance(hmms, list) and
                all([isinstance(h, sppasHMM) for h in hmms])):
            raise ModelsDataTypeError("hmms", "list of sppasHMM()", type(hmms))

        self._hmms = hmms

    # -----------------------------------------------------------------------
    # HMM
    # -----------------------------------------------------------------------

    def get_hmm(self, phone):
        """Return the hmm corresponding to the given phoneme.

        :param phone: (str) the phoneme name to get hmm
        :raises: ValueError if phoneme is not in the model

        """
        hmms = [h for h in self._hmms if h.get_name() == phone]
        if len(hmms) == 1:
            return hmms[0]
        raise ValueError('{:s} not in the model'.format(phone))

    # -----------------------------------------------------------------------

    def append_hmm(self, hmm):
        """Append an HMM to the model.

        :param hmm: (OrderedDict)
        :raises: TypeError, ValueError

        """
        if isinstance(hmm, sppasHMM) is False:
            raise TypeError('Expected an HMM instance. Got {:s}.'
                            ''.format(type(hmm)))

        for h in self._hmms:
            if h.get_name() == hmm.get_name():
                raise ValueError('Duplicate HMM is forbidden. '
                                 '{:s} is already in the model.'
                                 ''.format(hmm.get_name()))

        if hmm.definition is None:
            raise TypeError('Expected an hmm with a definition as key. '
                            'No definition was given.')

        if hmm.definition.get('states', None) is None or\
                hmm.definition.get('transition', None) is None:
            raise TypeError('Expected an hmm with a definition '
                            'including states and transitions.')

        self._hmms.append(hmm)

    # -----------------------------------------------------------------------

    def pop_hmm(self, phone):
        """Remove an HMM of the model.

        :param phone: (str) the phoneme name to get hmm
        :raises: ValueError if phoneme is not in the model

        """
        hmm = self.get_hmm(phone)
        idx = self._hmms.index(hmm)
        self._hmms.pop(idx)

    # -----------------------------------------------------------------------
    # Manage the model
    # -----------------------------------------------------------------------

    def replace_phones(self, reverse=False):
        """Replace the phones by using a mapping table.

        This is mainly useful due to restrictions in some acoustic model tks:
        X-SAMPA can't be fully used and a "mapping" is required.
        As for example, the /2/ or /9/ can't be represented directly in an
        HTK-ASCII acoustic model. We can replace respectively by /eu/ and
        /oe/.

        Notice that '+' and '-' can't be used as a phone name.

        :param reverse: (bool) reverse the replacement direction.

        """
        if self._repllist.is_empty() is True:
            return
        delimiters = ["-", "+"]

        oldreverse = self._repllist.get_reverse()
        self._repllist.set_reverse(reverse)

        # Replace in the tiedlist
        newtied = sppasTiedList()

        for observed in self._tiedlist.observed:
            mapped = self._repllist.map(observed, delimiters)
            newtied.add_observed(mapped)
        for tied, observed in self._tiedlist.tied.items():
            mappedtied = self._repllist.map(tied, delimiters)
            mappedobserved = self._repllist.map(observed, delimiters)
            newtied.add_tied(mappedtied, mappedobserved)
        self._tiedlist = newtied

        # Replace in HMMs
        for hmm in self._hmms:
            hmm.set_name(self._repllist.map(hmm.get_name(), delimiters))

            states = hmm.definition['states']
            if all(isinstance(state['state'], (collections.OrderedDict, collections.defaultdict)) for state in states) is False:
                for state in states:
                    if isinstance(state['state'], (collections.OrderedDict, collections.defaultdict)) is False:
                        tab = state['state'].split('_')
                        tab[1] = self._repllist.map_entry(tab[1])
                        state['state'] = "_".join(tab)

            transition = hmm.definition['transition']
            if isinstance(transition, (collections.OrderedDict, collections.defaultdict)) is False:
                tab = transition.split('_')
                tab[1] = self._repllist.map_entry(tab[1])
                # transition = "_".join(tab)

        self._repllist.set_reverse(oldreverse)

    # -----------------------------------------------------------------------

    def fill_hmms(self):
        """Fill HMM states and transitions.

        - replace all the "ST_..." by the corresponding macro, for states.
        - replace all the "T_..." by the corresponding macro, for transitions.

        """
        for hmm in self._hmms:

            states = hmm.definition['states']
            transition = hmm.definition['transition']

            if all(isinstance(state['state'], (collections.OrderedDict, collections.defaultdict)) for state in states) is False:
                new_states = self._fill_states(states)
                if all(s is not None for s in new_states):
                    hmm.definition['states'] = new_states
                else:
                    raise ValueError('No corresponding macro for states: '
                                     '{:s}'.format(states))

            if isinstance(transition, (collections.OrderedDict, collections.defaultdict)) is False:
                new_trs = self._fill_transition(transition)
                if new_trs is not None:
                    hmm.definition['transition'] = new_trs
                else:
                    raise ValueError('No corresponding macro for transition:'
                                     ' {:s}'.format(transition))

        # No more need of states and transitions in macros
        new_macros = list()
        if self._macros is not None:
            for m in self._macros:
                if m.get('transition', None) is None and m.get('state', None) is None:
                    new_macros.append(m)
        self._macros = new_macros

    # -----------------------------------------------------------------------

    @staticmethod
    def create_model(macros, hmms):
        """Create an empty sppasAcModel and return it.

        :param macros: OrderedDict of options, transitions, states, ...
        :param hmms: models (one per phone/biphone/triphone) is a list
        of HMM instances

        """
        model = sppasAcModel()
        model.set_macros(macros)
        model.set_hmms(hmms)

        return model

    # -----------------------------------------------------------------------

    def extract_monophones(self):
        """Return an Acoustic Model that includes only monophones.

            - hmms and macros are selected,
            - repllist is copied,
            - tiedlist is ignored.

        :returns: sppasAcModel

        """
        ac = sppasAcModel()

        # The macros
        if self._macros is not None:
            ac.set_macros(copy.deepcopy(self._macros))

        # The HMMs
        for h in self._hmms:
            if "+" not in h.get_name() and "-" not in h.get_name():
                ac.append_hmm(copy.deepcopy(h))
        ac.fill_hmms()

        # The phonemes mapping table
        ac.set_repllist(copy.deepcopy(self._repllist))

        return ac

    # -----------------------------------------------------------------------

    def get_mfcc_parameter_kind(self):
        """Return the MFCC parameter kind, as a string, or an empty string."""
        if self._macros is None:
            return ""

        for m in self._macros:
            option = m.get('options', None)
            if option is not None:
                definition = option.get('definition', None)
                if definition is not None:
                    for defn in definition:
                        parameter_kind = defn.get('parameter_kind', None)
                        if parameter_kind is not None:
                            # Check if of MFCC type...
                            if parameter_kind['base'].lower() == "mfcc":
                                return "mfcc_" + "".join(parameter_kind['options'])

        return ""

    # -----------------------------------------------------------------------

    def compare_mfcc(self, other):
        """Compare MFCC parameter kind with another one.

        :param other: (sppasAcModel)
        :returns: bool

        """
        my_param = self.get_mfcc_parameter_kind().lower()
        other_param = other.get_mfcc_parameter_kind().lower()

        my_params = sorted(my_param.split('_'))
        other_params = sorted(other_param.split('_'))
        return my_params == other_params

    # -----------------------------------------------------------------------

    def merge_model(self, other, gamma=1.):
        """Merge another model with self.

        All new phones/biphones/triphones are added and the shared ones are
        combined using a static linear interpolation.

        :param other: (sppasAcModel) the sppasAcModel to be merged with.
        :param gamma: (float) coefficient to apply to the model: between 0.
        and 1. This means that a coefficient value of 1. indicates to keep
        the current version of each shared hmm.

        :raises: TypeError, ValueError
        :returns: a tuple indicating the number of hmms that was
        appended, interpolated, kept, changed.

        """
        # Check the given input data
        if gamma < 0. or gamma > 1.:
            raise ValueError('Gamma coefficient must be between 0. and 1. '
                             'Got {:s}'.format(gamma))
        if isinstance(other, sppasAcModel) is False:
            raise TypeError('Expected an sppasAcModel instance.')

        # Check the MFCC parameter kind:
        # we can only interpolate identical models.
        if self.compare_mfcc(other) is False:
            raise TypeError('Can only merge models of identical MFCC '
                            'parameter kind.')

        # Fill HMM states and transitions, i.e.:
        #   - replace all the "ST_..." by the corresponding macro, for states.
        #   - replace all the "T_..." by the corresponding macro, for transitions.
        self.fill_hmms()
        other_copy = copy.deepcopy(other)
        other_copy.fill_hmms()

        # Merge the list of HMMs
        appended = 0
        interpolated = 0
        kept = len(self._hmms)
        changed = 0
        for hmm in other_copy.get_hmms():
            got = False
            for h in self._hmms:
                if h.get_name() == hmm.get_name():
                    got = True
                    if gamma == 1.0:
                        pass
                    elif gamma == 0.:
                        self.pop_hmm(hmm.get_name())
                        self.append_hmm(hmm)
                        changed = changed + 1
                        kept = kept - 1
                    else:
                        self_hmm = self.get_hmm(hmm.get_name())
                        res = self_hmm.static_linear_interpolation(hmm, gamma)
                        if res is True:
                            interpolated = interpolated + 1
                            kept = kept - 1
                    break
            if got is False:
                self.append_hmm(hmm)
                appended = appended + 1

        # Merge the tiedlists
        self._tiedlist.merge(other.get_tiedlist())

        for k in other.get_repllist():
            v = other.get_repllist().get(k)
            if k not in self._repllist and self._repllist.is_value(v) is False:
                self._repllist.add(k, v)

        return appended, interpolated, kept, changed

    # -----------------------------------------------------------------------
    # Create methods
    # -----------------------------------------------------------------------

    @staticmethod
    def _create_default():
        return collections.OrderedDict()

    # ----------------------------------

    @staticmethod
    def create_parameter_kind(base=None, options=list()):
        result = sppasAcModel._create_default()
        result['base'] = base
        result['options'] = options
        return result

    # ----------------------------------

    @staticmethod
    def create_options(vector_size,
                       parameter_kind=None,
                       stream_info=None,
                       duration_kind="nulld",
                       covariance_kind="diagc"):
        macro = sppasAcModel._create_default()
        options = []

        if stream_info:
            option = sppasAcModel._create_default()
            option['stream_info'] = sppasAcModel._create_default()
            option['stream_info']['count'] = len(stream_info)
            option['stream_info']['sizes'] = stream_info
            options.append(option)

        option = sppasAcModel._create_default()
        option['vector_size'] = vector_size
        options.append(option)

        option = sppasAcModel._create_default()
        option['duration_kind'] = duration_kind
        options.append(option)

        if parameter_kind:
            option = sppasAcModel._create_default()
            option['parameter_kind'] = parameter_kind
            options.append(option)

        option = sppasAcModel._create_default()
        option['covariance_kind'] = covariance_kind
        options.append(option)

        macro['options'] = {'definition': options}

        return macro

    # -----------------------------------------------------------------------
    # Private
    # -----------------------------------------------------------------------

    def _fill_states(self, states):
        new_states = list()
        for state in states:
            if isinstance(state['state'], (collections.OrderedDict,
                                           collections.defaultdict)) is True:
                new_states.append(state)
                continue
            news = copy.deepcopy(state)
            news['state'] = self._fill_state(state['state'])
            new_states.append(news)
        return new_states

    # ----------------------------------

    def _fill_state(self, state):
        new_state = None
        if self._macros is not None:
            for macro in self._macros:
                if macro.get('state', None):
                    if macro['state']['name'] == state:
                        new_state = copy.deepcopy(macro['state']['definition'])
        return new_state

    # ----------------------------------

    def _fill_transition(self, transition):
        new_transition = None
        if self._macros is not None:
            for macro in self._macros:
                if macro.get('transition', None):
                    if macro['transition']['name'] == transition:
                        new_transition = copy.deepcopy(macro['transition']['definition'])
        return new_transition

    # -----------------------------------------------------------------------
    # Overloads
    # -----------------------------------------------------------------------

    def __str__(self):
        str_macros = json.dumps(self._macros, indent=2)
        str_hmms = "\n".join([str(h) for h in self._hmms])
        return "Model: " + self._name + "\nMACROS:\n" + str_macros + "\nHMMS:\n" + str_hmms

    def __len__(self):
        return len(self._hmms)
