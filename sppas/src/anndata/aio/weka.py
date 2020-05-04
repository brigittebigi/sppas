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

    src.anndata.aio.weka.py
    ~~~~~~~~~~~~~~~~~~~~~~~

Weka is a collection of machine learning algorithms for data mining tasks.
https://www.cs.waikato.ac.nz/ml/weka/

WEKA is supporting 2 file formats:

    1. ARFF: a simple ASCII file,
    2. XRFF: an XML file which can be compressed with gzip.

ONLY writers are implemented.

"""
import codecs
from datetime import datetime

from sppas.src.config import sg
from .basetrsio import sppasBaseIO
from ..anndataexc import AioNoTiersError
from ..anndataexc import TagValueError
from ..anndataexc import AioEmptyTierError
from ..ann.annlabel import sppasLabel
from ..ann.annlabel import sppasTag
from ..ann.annlocation import sppasPoint

from sppas.src.utils.makeunicode import sppasUnicode, b

# ----------------------------------------------------------------------------

# Maximum number of class to predict
MAX_CLASS_TAGS = 100

# Maximum of attributes to list explicitly. Others are mentioned with "STRING".
MAX_ATTRIBUTES_TAGS = 200

# ----------------------------------------------------------------------------


class sppasWEKA(sppasBaseIO):
    """SPPAS Base writer for ARFF and XRFF formats.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2018  Brigitte Bigi

    The following metadata of the Transcription object can be defined:

        - weka_instance_step: time step for the data instances. Do not
        define if "weka_instance_anchor" is set to a tier.
        - weka_max_class_tags
        - weka_max_attributes_tags
        - weka_empty_annotation_tag
        - weka_empty_annotation_class_tag
        - weka_uncertain_annotation_tag

    The following metadata can be defined in a tier:

        - `weka_attribute` is fixed if the tier will be used as attribute
        (i.e. its data will be part of the instances). The value can
        be "numeric" to use distributions of probabilities or
        "label" to use the annotation labels in the vector of parameters.
        - `weka_class` is fixed to the tier with the annotation labels to
         be inferred by the classification system. No matter of the value.
        - `weka_instance_anchor` is fixed if the tier has to be used to
        define the time intervals of the instances.
        - `weka_epsilon` probability of an unobserved tag.

    """

    def __init__(self, name=None):
        """Initialize a new sppasWEKA instance.

        :param name: (str) This transcription name.

        """
        if name is None:
            name = self.__class__.__name__
        super(sppasWEKA, self).__init__(name)

        self._max_class_tags = int(MAX_CLASS_TAGS/10)
        self._max_attributes_tags = int(MAX_ATTRIBUTES_TAGS/10)
        self._empty_annotation_tag = "none"
        self._empty_annotation_class_tag = None
        self._uncertain_annotation_tag = "?"
        self._epsilon_proba = 0.001

        self._accept_multi_tiers = True
        self._accept_no_tiers = False
        self._accept_metadata = True
        self._accept_ctrl_vocab = True
        self._accept_media = False
        self._accept_hierarchy = False
        self._accept_point = True
        self._accept_interval = True
        self._accept_disjoint = True
        self._accept_alt_localization = False
        self._accept_alt_tag = True
        self._accept_radius = False
        self._accept_gaps = True    # is True only for the reference tier
        self._accept_overlaps = True

        self.software = "weka"

    # -----------------------------------------------------------------------
    # Getters and setters
    # -----------------------------------------------------------------------

    def get_max_class_tags(self):
        """Return the maximum number of tags for the class."""
        return self._max_class_tags

    # -----------------------------------------------------------------------

    def set_max_class_tags(self, nb_tags):
        """Set the maximum number of tags for a class.

        :param nb_tags: (int) Size of the controlled vocabulary of the
        class tier

        """
        sppasWEKA.check_max_class_tags(nb_tags)
        self._max_class_tags = int(nb_tags)

    # -----------------------------------------------------------------------

    @staticmethod
    def check_max_class_tags(nb_tags):
        """Check the maximum number of tags for the class.

        :param nb_tags: (int) Size of the controlled vocabulary of the
        class tier

        """
        nb_tags = int(nb_tags)
        if nb_tags < 2:
            raise IOError("The class must have at least 2 different tags.")
        if nb_tags > MAX_CLASS_TAGS:
            raise IOError("The class must have at max {:d} different tags."
                          "".format(MAX_CLASS_TAGS))

    # -----------------------------------------------------------------------

    def set_max_attributes_tags(self, nb_tags):
        """Set the maximum number of tags for an attribute.

        Instead, the program won't list the attribute and will use 'STRING'.

        :param nb_tags: (int) Size of the controlled vocabulary of the
        class tier

        """
        sppasWEKA.check_max_attributes_tags(nb_tags)
        self._max_attributes_tags = int(nb_tags)

    # -----------------------------------------------------------------------

    @staticmethod
    def check_max_attributes_tags(nb_tags):
        """Check the maximum number of tags for an attribute.

        :param nb_tags: (int) Size of the controlled vocabulary of the
        attribute tier

        """
        nb_tags = int(nb_tags)
        if nb_tags < 1:
            raise ValueError("The attributes must have at least one tag.")
        if nb_tags > MAX_ATTRIBUTES_TAGS:
            raise ValueError("The attributes must have at max {:d} "
                             "different tags.".format(MAX_ATTRIBUTES_TAGS))

    # -----------------------------------------------------------------------

    def set_empty_annotation_tag(self, tag_str):
        """Fix the annotation string to be used to replace...

         empty annotations.

        :param tag_str: (str)

        """
        tag_str_formatted = sppasUnicode(tag_str).clear_whitespace()
        if len(tag_str_formatted) > 0:
            self._empty_annotation_tag = tag_str_formatted
        else:
            raise TagValueError(tag_str)

    # -----------------------------------------------------------------------

    def set_empty_annotation_class_tag(self, tag_str=None):
        """Fix the annotation string to be used to replace...

        empty annotations in the class tier.

        :param tag_str: (str or None) None is used to NOT fill
        unlabelled annotations, so to ignore them in the data.

        """
        if tag_str is None:
            self._empty_annotation_class_tag = None
        else:
            tag_str_formatted = sppasUnicode(tag_str).clear_whitespace()
            if len(tag_str_formatted) > 0:
                self._empty_annotation_class_tag = tag_str_formatted
            else:
                raise TagValueError(tag_str)

    # -----------------------------------------------------------------------

    def set_uncertain_annotation_tag(self, tag_str):
        """Fix the annotation string that is used in the annotations to...

        mention an uncertain label.

        :param tag_str: (str)

        """
        tag_str_formatted = sppasUnicode(tag_str).clear_whitespace()
        if len(tag_str_formatted) > 0:
            self._uncertain_annotation_tag = tag_str_formatted
        else:
            raise TagValueError(tag_str)

    # -----------------------------------------------------------------------
    # Validation methods
    # -----------------------------------------------------------------------

    def check_metadata(self):
        """Check the metadata and fix the variable members."""
        if self.is_meta_key("weka_max_class_tags") is True:
            self.set_max_class_tags(
                self.get_meta("weka_max_class_tags"))

        if self.is_meta_key("weka_max_attributes_tags") is True:
            self.set_max_attributes_tags(
                self.get_meta("weka_max_attributes_tags"))

        if self.is_meta_key("weka_empty_annotation_tag") is True:
            self.set_empty_annotation_tag(
                self.get_meta("weka_empty_annotation_tag"))

        if self.is_meta_key("weka_empty_annotation_class_tag") is True:
            self.set_empty_annotation_class_tag(
                self.get_meta("weka_empty_annotation_class_tag"))

        if self.is_meta_key("weka_uncertain_annotation_tag") is True:
            self.set_uncertain_annotation_tag(
                self.get_meta("weka_uncertain_annotation_tag"))

    # -----------------------------------------------------------------------

    def validate_annotations(self):
        """Prepare data to be compatible with the expected format.

        - Convert tier names
        - Delete the existing controlled vocabularies
        - Convert tags: fill empty tags, replace whitespace by underscores

        """
        if self.is_empty():
            raise AioNoTiersError("WEKA")

        min_time_point = self.get_min_loc()
        max_time_point = self.get_max_loc()
        if min_time_point is None or max_time_point is None:
            # it means there are only empty tiers in the transcription
            raise AioNoTiersError("WEKA")

        for tier in self:

            # only change the tiers to be used (no matter of the other ones!)
            if tier.is_meta_key("weka_attribute") is False and\
               tier.is_meta_key("weka_class") is False:
                continue

            # Name of the tier: no whitespace
            name = tier.get_name()
            tier.set_name(sppasUnicode(name).clear_whitespace())

            # Delete current controlled vocabulary.
            #  if tier.is_meta_key("weka_attribute") or
            #  tier.is_meta_key("weka_class"):
            if tier.get_ctrl_vocab() is not None:
                tier.set_ctrl_vocab(None)

            # Convert annotation tags.
            for ann in tier:
                if ann.is_labelled():
                    for label in ann.get_labels():
                        #if len(label) > 0:
                        for tag, score in label:
                            if tag.get_type() == "str":
                                # Replace whitespace by underscore and check for an empty tag.
                                tag_text = sppasUnicode(tag.get_content()).clear_whitespace()
                                if len(tag_text) == 0:
                                    # The tag is empty. We have to fill it (or not).
                                    if tier.is_meta_key("weka_class") is False:
                                        tag_text = self._empty_annotation_tag
                                    else:
                                        if self._empty_annotation_class_tag is not None:
                                            tag_text = self._empty_annotation_class_tag

                                new_tag = sppasTag(tag_text)
                                # Set the new version of the tag to the label
                                if new_tag != tag:
                                    ann.remove_tag(tag)
                                    label.append(new_tag, score)
                        else:
                            if tier.is_meta_key("weka_class") is False:
                                # The annotation was not labelled.
                                # We have to do it.
                                ann.set_label(
                                    sppasTag(
                                        self._empty_annotation_tag))
                            else:
                                if self._empty_annotation_class_tag is not None:
                                    ann.set_label(
                                        sppasTag(
                                            self._empty_annotation_class_tag))
                else:
                    if tier.is_meta_key("weka_class") is False:
                        # The annotation was not labelled. We have to do it.
                        ann.set_label(sppasTag(self._empty_annotation_tag))
                    else:
                        if self._empty_annotation_class_tag is not None:
                            ann.set_label(
                                sppasTag(self._empty_annotation_class_tag))

        # Set the controlled vocabularies
        self._create_ctrl_vocab()

    # -----------------------------------------------------------------------

    def validate(self):
        """Check the tiers.

         Verify if everything is ok:

            1. A class is defined: "weka_class" in the metadata of a tier
            2. Attributes are fixed: "weka_attribute" in the metadata of
               at least one tier

        Raises IOError or ValueError if something is wrong.

        """
        if self.is_empty() is True:
            raise AioNoTiersError("WEKA")
        if len(self) == 1:
            raise IOError("The transcription must contain at least 2 tiers.")

        class_tier = self._get_class_tier()
        if class_tier is None:
            raise IOError("The transcription must contain a class.")
        if class_tier.is_empty():
            raise AioEmptyTierError("WEKA", class_tier.get_name())
        sppasWEKA.check_max_class_tags(len(class_tier.get_ctrl_vocab()))

        has_attribute = list()
        for tier in self:
            if tier.is_meta_key("weka_attribute"):
                has_attribute.append(tier)
                if tier is class_tier:
                    raise IOError("A tier can be either an attribute or "
                                  "the class. It can't be both.")
        if len(has_attribute) == 0:
            raise IOError("The transcription must contain attributes.")
        for tier in has_attribute:
            if tier.is_empty():
                raise AioEmptyTierError("WEKA", tier.get_name())

        has_time_slice = False
        if self.is_meta_key("weka_instance_step") is False:
            for tier in self:
                if tier.is_meta_key("weka_instance_anchor"):
                    has_time_slice = True
        else:
            try:
                time = float(self.get_meta("weka_instance_step"))
            except ValueError:
                raise ValueError(
                    "The instance step must be a numerical value. "
                    "Got {:s}".format(self.get_meta("weka_instance_step")))
            has_time_slice = True
        if has_time_slice is False:
            raise IOError("An instance time step or an anchor tier "
                          "must be defined.")

    # -----------------------------------------------------------------------
    # Private
    # -----------------------------------------------------------------------

    def _create_ctrl_vocab(self):
        """Fix the controlled vocabularies of attribute tiers."""
        for tier in self:
            if tier.is_meta_key("weka_attribute") or \
                    tier.is_meta_key("weka_class"):
                tier.create_ctrl_vocab()

    # -----------------------------------------------------------------------

    @staticmethod
    def _tier_is_attribute(tier):
        """Check if a tier is an attribute for the classification.

        :param tier: (sppasTier)
        :returns: (is attribute, is numeric)

        """
        if tier.is_meta_key("weka_class"):
            return False, False

        is_att = False
        is_numeric = False
        if tier.is_meta_key("weka_attribute"):
            is_att = True
            is_numeric = "numeric" in tier.get_meta("weka_attribute").lower()

        return is_att, is_numeric

    # -----------------------------------------------------------------------

    def _get_class_tier(self):
        """Return the tier which is the class or None."""

        for tier in self:
            if tier.is_meta_key("weka_class"):
                return tier

        return None

    # -----------------------------------------------------------------------

    def _get_anchor_tier(self):
        """Return the tier which will be used to create the instances...

         or None.

         """
        for tier in self:
            if tier.is_meta_key("weka_instance_anchor"):
                return tier

        return None

    # -----------------------------------------------------------------------

    def _get_labels(self, localization, tier):
        """Return the list of sppasLabel() at the given time in the given tier.
        Return the empty label if no label was assigned at the given time.

        :param localization: (sppasPoint)
        :param tier: (sppasTier)

        :returns: sppasLabel()

        """
        # Find the annotation at the given time.
        # Return the first one in case of overlapping annotations.
        if tier.is_point() is True:
            mindex = tier.index(localization)
        else:
            mindex = tier.mindex(localization, bound=10)
            # TODO: return all sppasLabel() during the localization
            # (i.e. during the period including the vagueness) and
            # not only at the midpoint of the localization.
            # And in the same idea, we have to deal with overlapping
            # annotations.

        labels = list()
        # Fix the label to be returned: the observed one or an empty one
        if mindex != -1:
            ann = tier[mindex]
            if ann.is_labelled():
                for label in ann.get_labels():
                    # if len(label) > 0:
                    for tag, score in label:
                        if tag.get_content() == "":
                            labels.append(
                                sppasLabel(
                                    sppasTag(self._empty_annotation_tag),
                                    score))
                        else:
                            labels.append(label)

        if len(labels) == 0:
            return [sppasLabel(sppasTag(self._empty_annotation_tag))]

        return labels

    # -----------------------------------------------------------------------

    @staticmethod
    def _fix_all_possible_instance_steps(start_time,
                                         end_time,
                                         time_step=None,
                                         anchor_tier=None):
        """Fix all the possible time-points of the instances.

        If an anchor tier is given, only labelled annotations are used
        to create the instances.

        :param start_time: (float)
        :param end_time: (float)
        :param time_step: (float)
        :param anchor_tier: (sppasTier)

        :returns: list of sppasPoint()

        """
        # Create the list of all possible points for the instances
        all_points = list()

        # A timer is used to fix the steps
        if time_step is not None:
            time_value = start_time

            while (time_value + (time_step/2.)) < end_time:
                # Fix the anchor point of the instance
                midpoint = time_value + (time_step/2.)
                radius = time_step/2.
                all_points.append(sppasPoint(midpoint, radius))
                # next...
                time_value += time_step

        # An anchor class is used to fix the steps
        # Only labelled annotations are selected
        elif anchor_tier is not None:
            for ann in anchor_tier:
                localization = ann.get_location().get_best()
                if ann.label_is_filled() is True:
                    if localization.is_point():
                        all_points.append(localization)
                    else:
                        # Fix the anchor point of the instance
                        duration = localization.duration()
                        midpoint = \
                            localization.get_begin().get_midpoint() + \
                            (duration.get_value() / 2.)
                        radius = (duration.get_value() +
                                  duration.get_margin()) / 2.

                        all_points.append(sppasPoint(midpoint, radius))

        return all_points

    # -----------------------------------------------------------------------

    def _fix_instance_steps(self):
        """Fix the time-points to create the instances and the
        tag of the class to predict by the classification system.

        The instances are created only for the labelled annotations of
        the class tier.
        If several classes were assigned, the instance is also ignored.
        (we also could choose to predict the one with the better score)

        :returns: List of (sppasPoint, tag content)

        """
        class_tier = self._get_class_tier()
        # The localization point to start the instances
        begin = class_tier.get_first_point().get_midpoint()
        # The localization point to finish the instances
        end = class_tier.get_last_point().get_midpoint()

        # Fix the list of candidates for the instance points
        time_step = None
        if self.is_meta_key("weka_instance_step") is True:
            time_step = float(self.get_meta("weka_instance_step"))
        anchor_tier = self._get_anchor_tier()
        all_points = self._fix_all_possible_instance_steps(begin,
                                                           end,
                                                           time_step,
                                                           anchor_tier)

        # Create the list of points for the instances
        instance_points = list()
        for point in all_points:

            # Fix the tag to predict
            labels = self._get_labels(point, class_tier)
            tags = list()
            for label in labels:
                if label is not None and label.is_tagged():
                    tag = label.get_best()
                    if tag.get_content() != self._empty_annotation_tag:
                        tags.append(tag.get_content())

            # Append only if the class was labelled
            # * * * WITH ONLY ONE LABEL * * *
            if len(tags) == 1:
                instance_points.append((point, tags[0]))

        return instance_points

    # -----------------------------------------------------------------------

    @staticmethod
    def _scores_to_probas(tags):
        """Convert scores of a set of tags to probas."""

        if len(tags) == 0:
            return False

        # Convert "None" scores into a numerical value
        # then convert numerical values into probabilities.
        if len(tags) == 1:
            for tag in tags:
                tags[tag] = 1.

        else:
            # Search for the minimum score
            min_score = None
            for tag in tags:
                score = tags[tag]
                if score is not None:
                    if min_score is None or min_score > score:
                        min_score = score
            if min_score is None:
                # None of the tags had a score.
                min_score = 2.

            # Assign a score to the tags if needed
            for tag in tags:
                score = tags[tag]
                if score is None:
                    tags[tag] = min_score / 2.

            # Convert scores to probabilities
            total = float(sum(tags[tag] for tag in tags))
            for tag in tags:
                score = tags[tag]
                tags[tag] = float(score) / total

    # -----------------------------------------------------------------------

    def _fix_data_instance(self, point):
        """Fix the data content of an instance.

        Create the instance at the given point with annotations of all
        attribute tiers, followed by the class.

        To be fixed:

            - tiers with points
            - tiers with boolean tags
            - tiers with int/float tags: should be converted to labels

        :param point: (sppasPoint) The moment to be used
        :returns: list of attributes (str)

        """
        instances_data = list()
        for tier in self:

            is_att, is_numeric = sppasWEKA._tier_is_attribute(tier)
            if is_att is False:
                continue

            # Get all labels of the annotation
            labels = self._get_labels(point, tier)

            if is_numeric is True:

                # Create a list of tags
                tags = dict()
                for label in labels:
                    if label is None:
                        continue
                    if len(label) == 0:
                        continue
                    for tag, score in label:
                        if tag in tags:
                            tags[tag] += score
                        else:
                            tags[tag] = score

                # Scores of observed tags are converted to probabilities
                self._scores_to_probas(tags)

                # Score of un-observed tags are all set to an
                # epsilon probability
                nb_eps_tags = len(tier.get_ctrl_vocab()) - len(tags)
                epsilon = self._epsilon_proba
                if tier.is_meta_key('weka_epsilon'):
                    epsilon = float(tier.get_meta('weka_epsilon'))
                # ... if an uncertain tag is observed
                uncertain_tag = sppasTag(self._uncertain_annotation_tag)
                if uncertain_tag in tags:
                    score = tags[uncertain_tag]
                    nb_eps_tags += 1
                    epsilon = score / float(nb_eps_tags)
                    del tags[uncertain_tag]

                # All possible tags are written
                for tag in tier.get_ctrl_vocab():
                    proba = epsilon
                    if tag in tags:
                        proba = tags[tag] - (nb_eps_tags * epsilon)
                    instances_data.append(str(proba))

            else:

                content = ""
                for label in labels:
                    if label is None:
                        continue
                    if len(label) == 0:
                        continue
                    content += label.get_best().get_content() + " "
                content = content.strip()
                if len(content) == 0:
                    content = self._empty_annotation_tag
                instances_data.append(content)

        return instances_data

# ---------------------------------------------------------------------------


class sppasARFF(sppasWEKA):
    """SPPAS ARFF writer.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2018  Brigitte Bigi

    ARFF format description is at the following URL:
    http://weka.wikispaces.com/ARFF+(book+version)
    An ARFF file for WEKA has the following structure:

        1. Several lines starting by '%' with any kind of comment,
        2. The name of the relation,
        3. The set of attributes,
        4. The set of instances.

    """
    @staticmethod
    def detect(filename):
        try:
            with codecs.open(filename, 'r', sg.__encoding__) as fp:
                for i in range(200):
                    line = fp.readline()
                    if "@relation" in line.lower():
                        return True
            return False
        except IOError:
            return False
        except UnicodeDecodeError:
            return False

    # -----------------------------------------------------------------------

    def __init__(self, name=None):
        """Initialize a new sppasARFF instance.

        :param name: (str) This transcription name.

        """
        if name is None:
            name = self.__class__.__name__
        super(sppasARFF, self).__init__(name)

        self.default_extension = "arff"

    # -----------------------------------------------------------------------
    # Write data
    # -----------------------------------------------------------------------

    def write(self, filename):
        """Write a RawText file.

        :param filename: (str)

        """
        if self.is_empty() is True:
            raise AioNoTiersError(self.default_extension)

        with codecs.open(filename, 'w', sg.__encoding__, buffering=8096) as fp:

            # Check metadata
            self.check_metadata()

            # Check the annotation tags.
            self.validate_annotations()

            # Check if the metadata are properly fixed.
            self.validate()

            # OK, we are ready to write
            fp.write(sppasARFF._serialize_header())
            fp.write(self._serialize_metadata())
            fp.write(self._serialize_relation())
            fp.write(self._serialize_attributes())
            self._write_data(fp)

            fp.close()

    # -----------------------------------------------------------------------
    # Private
    # -----------------------------------------------------------------------

    @staticmethod
    def _serialize_header():
        """Return a standard header in comments."""

        content = "% creator: {:s}\n".format(sg.__name__)
        content += "% version: {:s}\n".format(sg.__version__)
        content += "% date: {:s}\n".format(datetime.now().strftime("%Y-%m-%d"))
        content += "% author: {:s}\n".format(sg.__author__)
        content += "% license: {:s}\n".format(sg.__copyright__)
        content += "% \n"
        return content

    # -----------------------------------------------------------------------

    def _serialize_metadata(self):
        """Serialize metadata in comments."""

        content = ""
        for key in self.get_meta_keys():
            # todo: we should ignore metadata already in the header.
            value = self.get_meta(key)
            content += "% {:s}: {:s}\n".format(key, value)
        content += "\n\n"
        return content

    # -----------------------------------------------------------------------

    def _serialize_relation(self):
        """Serialize the relation of the ARFF file."""

        content = "@RELATION {:s}\n".format(self.get_name())
        content += "\n"
        return content

    # -----------------------------------------------------------------------

    @staticmethod
    def _serialize_attributes_ctrl_vocab(tier, is_class=False):
        """Serialize the controlled vocabulary in an attribute set.

        :param tier: (sppasTier)

        """
        # Prepare the list of strings to write
        tags = list()
        for tag in tier.get_ctrl_vocab():
            tags.append(tag.get_content())

        # Write the name of the attribute serie
        content = "@ATTRIBUTES "
        if is_class is True:
            content += "class "
        else:
            content += "{:s} ".format(tier.get_name())

        # Write the attributes
        content += "{"
        content += "{:s}".format(",".join(tags))
        content += "}\n"
        return content

    # -----------------------------------------------------------------------

    def _serialize_attributes(self):
        """Write the attributes of the ARFF file.
        Attributes are corresponding to the controlled vocabulary.
        They are the list of possible tags of the annotations, except
        for the numerical ones.

        It is supposed that the transcription has been already validated.

        """
        content = ""
        for tier in self:

            is_att, is_numeric = sppasWEKA._tier_is_attribute(tier)
            if is_att is False:
                continue

            if is_numeric is True:
                # Tags will be converted to probabilities
                for tag in tier.get_ctrl_vocab():
                    # Do not write an uncertain label in that situation.
                    if tag.get_content() != self._uncertain_annotation_tag:
                        attribute_name = tier.get_name() + "-" + tag.get_content()
                        content += "@ATTRIBUTES {:s} NUMERIC\n" \
                                   "".format(attribute_name)
            else:
                # Either a generic "string" or we can explicitly fix the list
                if len(tier.get_ctrl_vocab()) > self._max_attributes_tags:
                    content += "@ATTRIBUTES {:s} STRING\n" \
                               "".format(tier.get_name())
                else:
                    content += sppasARFF._serialize_attributes_ctrl_vocab(tier)

        tier = self._get_class_tier()
        content += sppasARFF._serialize_attributes_ctrl_vocab(
                        tier,
                        is_class=True)
        content += "\n"
        return content

    # -----------------------------------------------------------------------

    def _write_data(self, fp):
        """Write the data content of the ARFF file.
        Data are the tags of the annotations or distributions of
        probabilities.

        * Each instance is represented on a single line, with carriage
        returns denoting the end of the instance.
        * Attribute values for each instance are delimited by commas.
        They must appear in the order that they were declared in the header.
        * Missing values are represented by a single question mark
        * Values of string and nominal attributes are case sensitive,
        and any that contain space must be quoted

        :param fp: FileDescriptor

        """
        fp.write(b("@DATA\n"))

        for point, class_str in self._fix_instance_steps():
            line = ""
            data_instances = self._fix_data_instance(point)
            for attribute in data_instances:
                line += attribute
                line += ","
            line += str(class_str)
            line += "\n"
            fp.write(b(line))

# ----------------------------------------------------------------------------


class sppasXRFF(sppasWEKA):
    """SPPAS XRFF writer.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2017  Brigitte Bigi

    XML-based format of WEKA software tool.
    XRFF format description is at the following URL:
    http://weka.wikispaces.com/XRFF

    This class is limited to:
        1. Only the writers are implemented. No readers.
        2. Sparse option is not supported by both writers.
        3. XRFF output file is not gzipped.
        4. XRFF format supports the followings that are not currently \
        implemented into this class:

            - attribute weights;
            - instance weights.

    -- !!!!!!!! No guarantee !!!!!! --

    This class has never been tested.

    -- !!!!!!!! No guarantee !!!!!! --

    """
    @staticmethod
    def detect(filename):
        try:
            with codecs.open(filename, 'r', 'utf-8') as fp:
                for i in range(200):
                    line = fp.readline()
                    if "<dataset " in line.lower():
                        return True
        except Exception:
            return False

        return False

    # -----------------------------------------------------------------------

    def __init__(self, name=None):
        """Initialize a new sppasXRFF instance.

        :param name: (str) This transcription name.

        """
        if name is None:
            name = self.__class__.__name__
        super(sppasXRFF, self).__init__(name)

        self.default_extension = "xrff"

    # -----------------------------------------------------------------------
    # Write data
    # -----------------------------------------------------------------------

    def write(self, filename):
        """Write a XRFF file.

        :param filename: (str)

        """
        if self.is_empty() is True:
            raise AioNoTiersError(self.default_extension)

        with codecs.open(filename, 'w', sg.__encoding__, buffering=8096) as fp:

            # Check metadata
            self.check_metadata()

            # Check the annotation tags.
            self.validate_annotations()

            # Check if the metadata are properly fixed.
            self.validate()

            # OK, we are ready to write
            fp.write(b('<?xml version="1.0" encoding="utf-8"?>\n'))
            fp.write(b("\n"))
            fp.write(b('<dataset name="{:s}" />\n'.format(self.get_name())))
            fp.write(b("\n"))
            fp.write(b('<header>\n'))
            self._write_attributes(fp)
            fp.write(b('</header>\n'))
            fp.write(b('\n'))
            fp.write(b('<body>\n'))
            self._write_instances(fp)
            fp.write(b('</body>\n'))

            fp.close()

    # -----------------------------------------------------------------------
    # Private
    # -----------------------------------------------------------------------

    @staticmethod
    def _write_attribute_ctrl_vocab(tier, fp, is_class=False):
        """Write the controlled vocabulary in an attribute set.

        :param tier: (sppasTier)
        :param fp: FileDescription
        :param is_class: (boolean)

        """
        fp.write(b('        <attribute '))
        if is_class is True:
            fp.write(b('class="yes" '))
        fp.write(b('name="{:s}" type="nominal">\n'.format(tier.get_name())))
        fp.write(b('            <labels>\n'))
        for tag in tier.get_ctrl_vocab():
            fp.write(b("            <label>{:s}</label>\n"
                       "".format(tag.get_content())))
        fp.write(b('            </labels>\n'))
        fp.write(b('        </attribute>\n'))

    # -----------------------------------------------------------------------

    def _write_attributes(self, fp):
        """Write the attributes of the ARFF file.
        Attributes are corresponding to the controlled vocabulary.
        They are the list of possible tags of the annotations, except
        for the numerical ones.

        It is supposed that the transcription has been already validated.

        """
        fp.write(b('    <attributes>\n'))
        for tier in self:

            is_att, is_numeric = sppasWEKA._tier_is_attribute(tier)
            if is_att is False:
                continue

            if is_numeric is True:
                # Tags will be converted to probabilities
                for tag in tier.get_ctrl_vocab():
                    # Do not write an uncertain label in that situation.
                    if tag.get_content() != self._uncertain_annotation_tag:
                        attribute_name = \
                            tier.get_name() + "-" + tag.get_content()
                        fp.write(b('        <attribute name="{:s}" '
                                   'type="numeric" />\n'
                                   ''.format(attribute_name)))
            else:
                # Either a generic "string" or we can explicitly fix the list
                if len(tier.get_ctrl_vocab()) > self._max_attributes_tags:
                    fp.write(b('        <attribute name="{:s}" '
                               'type="nominal" />\n'
                               ''.format(tier.get_name())))
                else:
                    # The controlled vocabulary
                    fp.write(b('        <attribute name="{:s}" '
                               'type="nominal">'.format(tier.get_name())))
                    fp.write('            <labels>\n')
                    for tag in tier.get_ctrl_vocab():
                        fp.write(b("            <label>{:s}"
                                   "</label>\n"
                                   "".format(tag.get_content())))
                    fp.write(b('            </labels>\n'))
                    fp.write(b('        </attribute>\n'))

        tier = self._get_class_tier()
        self._write_attribute_ctrl_vocab(tier, fp, is_class=True)

        fp.write(b('    </attributes>\n'))

    # -----------------------------------------------------------------------

    def _write_instances(self, fp):
        """Write the data content of the XRFF file.
        Data are the tags of the annotations or distributions of
        probabilities.

        :param fp: FileDescriptor

        """
        fp.write(b("    <instances>\n"))
        for point, class_str in self._fix_instance_steps():
            data_instances = self._fix_data_instance(point)
            fp.write(b("        <instance>\n"))

            for attribute in data_instances:

                fp.write(b("            <value>{!s:s}</value>\n"
                           "".format(attribute)))

            fp.write(b("            <value>{!s:s}</value>\n"
                       "".format(class_str)))

            fp.write(b("        </instance>\n"))

        fp.write(b("    </instances>\n"))
