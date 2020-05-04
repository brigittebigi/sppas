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

    src.anndata.aio.transcriber.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Transcriber is a tool for assisting the manual annotation of speech signals.
It provides a graphical user interface for segmenting long duration speech
recordings, transcribing them, and labeling speech turns, topic changes and
acoustic conditions.
It is more specifically designed for the annotation of broadcast news
recordings.

http://trans.sourceforge.net

"""
import codecs
import xml.etree.cElementTree as ET

from .basetrsio import sppasBaseIO
from ..anndataexc import AnnDataTypeError
from ..media import sppasMedia
from ..ctrlvocab import sppasCtrlVocab
from ..ann.annotation import sppasAnnotation
from ..ann.annlocation import sppasLocation
from ..ann.annlocation import sppasPoint
from ..ann.annlocation import sppasInterval
from ..ann.annlabel import sppasLabel
from ..ann.annlabel import sppasTag
from .aioutils import format_labels

# ---------------------------------------------------------------------------

NO_SPK_TIER = "Trans-NoSpeaker"

# list of Transcriber noise events with their conversion into SPPAS convention.
NOISE_EVENTS = {
    "r": "* {respiration}",
    "i": "* {inspiration}",
    "e": "* {exhalation}",
    "n": "* {sniffing}",
    "pf": "* {breath}",
    "bb": "* {mouth noise}",
    "bg": "* {throaty noise}",
    "tx": "* {coughing, sneeze}",
    "sif": "{whistling}",
    "b": "* {undetermined}",
    "conv": "* {background conversations}",
    "pap": "* {wrinkling of papers}",
    "shh": "* {electric blast}",
    "mic": "* {micro}",
    "toux en fond": "* {background cough}",
    "indicatif": "* {indicative signal}",
    "jingle": "* {jingle}",
    "top": "* {top}",
    "musique": "* {music}",
    "applaude": "* {applaude}",
    "rire": "@",
    "rire-": "@@",       # begin/end of a laughing sequence
    "rire_begin": "@@",
    "rire_end": "@@",
    "-rire": "@@",
    "rire en fond": "@ {background laughter}",
    "nontrans": "dummy"
}

# ---------------------------------------------------------------------------


class sppasTRS(sppasBaseIO):
    """SPPAS reader for TRS format.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      contact@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2018  Brigitte Bigi

    """

    @staticmethod
    def detect(filename):
        """Check whether a file is of TRS format or not.

        :param filename: (str) Name of the file to check.
        :returns: (bool)

        """
        try:
            with codecs.open(filename, 'r', "ISO-8859-1") as it:
                it.next()
                doctype_line = it.next().strip()
                it.close()
        except IOError:
            return False
        except UnicodeDecodeError:
            return False

        return '<!DOCTYPE Trans SYSTEM "trans' in doctype_line

    # -----------------------------------------------------------------------

    @staticmethod
    def make_point(midpoint):
        """The localization is a time value, so a float."""
        try:
            midpoint = float(midpoint)
        except ValueError:
            raise AnnDataTypeError(midpoint, "float")
        return sppasPoint(midpoint, radius=0.005)

    # -----------------------------------------------------------------------

    def __init__(self, name=None):
        """Initialize a new sppasTRS instance.

        :param name: (str) This transcription name.

        """
        if name is None:
            name = self.__class__.__name__
        super(sppasTRS, self).__init__(name)

        self.default_extension = "trs"
        self.software = "Transcriber"

        self._accept_multi_tiers = True
        self._accept_no_tiers = False
        self._accept_metadata = True
        self._accept_ctrl_vocab = False
        self._accept_media = True
        self._accept_hierarchy = True
        self._accept_point = False
        self._accept_interval = True
        self._accept_disjoint = False
        self._accept_alt_localization = False
        self._accept_alt_tag = False
        self._accept_radius = False
        self._accept_gaps = False
        self._accept_overlaps = False

    # -----------------------------------------------------------------------

    def read(self, filename):
        """Read a TRS file and fill the Transcription.

        <!ELEMENT Trans ((Speakers|Topics)*,Episode)>

        :param filename: (str)

        """
        try:
            tree = ET.parse(filename)
        except ET.ParseError:
            xmlp = ET.XMLParser(encoding="ISO-8859-1")
            tree = ET.parse(filename, parser=xmlp)
        root = tree.getroot()

        # Get metadata for self
        self._parse_metadata(root)

        # Speakers. One tier by speaker is created.
        self._parse_speakers(root.find('Speakers'))
        self.create_tier(NO_SPK_TIER)

        # Topics. Set the controlled vocabulary.
        topics = self.create_tier("Topics")
        sppasTRS._parse_topics(root.find('Topics'), topics)

        # Episodes. Fill the tier.
        episodes_tier = self.create_tier("Episodes")
        for episode_root in root.iter('Episode'):
            sppasTRS._parse_episode_attributes(episode_root, episodes_tier)

        # Episodes. Examine sections.
        section_tier = self.create_tier("Sections")
        for section_root in root.iter('Section'):
            self._parse_section_attributes(section_root, section_tier)

        # Episodes. Examine each "Turn" (content of tiers)
        self.create_tier("Turns")
        for turn_root in root.iter('Turn'):
            self._parse_turn(turn_root)

        # Reformat the tags (problems of the transcription convention).
        for tier in self:
            if "Trans" in tier.get_name():
                for ann in tier:
                    if ann.is_labelled():
                        for label in ann.get_labels():
                            tag = label.get_best()
                            new_content = sppasTRS.__format_tag(tag)
                            label.get_best().set_content(new_content)

        # Create the hierarchy
        self.add_hierarchy_link("TimeAlignment",
                                self.find('Turns'),
                                self.find('Sections'))
        self.add_hierarchy_link("TimeAlignment",
                                self.find('Sections'),
                                self.find('Episodes'))
        self.add_hierarchy_link("TimeAlignment",
                                self.find('Sections'),
                                self.find('Topics'))
        # TurnRecordingQuality, TurnElocutionMode and TurnChannel should be
        # "TimeAssociation" of Turns but... if sparse data (?) !

        # Remove empty tiers.
        for i in reversed(range(len(self))):
            if len(self[i]) == 0:
                self.pop(i)

    # -----------------------------------------------------------------------

    @staticmethod
    def __format_tag(tag):
        """Reformat tokens in tags.

        Remove specific markers of the transcription convention of
        Transcriber.

        """
        content = tag.get_content()
        tokens = content.split(" ")
        new_tokens = list()
        for token in tokens:
            if token.startswith("^^"):
                token = token[2:]
            if len(token) > 1 and \
                    (token.startswith("*") or
                     token.startswith('?')):
                token = token[1:]
            if "()" in token:
                token = token.replace("()", "")
            if len(token) > 0:
                new_tokens.append(token)

        return " ".join(new_tokens)

    # -----------------------------------------------------------------------

    def _parse_metadata(self, root):
        """Get metadata from attributes of the main root.

        <!ATTLIST Trans
        audio_filename  CDATA           #IMPLIED
        scribe          CDATA           #IMPLIED
        xml:lang        NMTOKEN         #IMPLIED
        version         NMTOKEN         #IMPLIED
        version_date    CDATA           #IMPLIED
        elapsed_time    CDATA           "0"
        >

        :param root: (ET) Main XML Element tree root of a TRS file.

        """
        # The media linked to this file.
        if "audio_filename" in root.attrib:
            media_url = root.attrib['audio_filename']
            media = sppasMedia(media_url)
            media.set_meta('media_source', 'primary')
            self.set_media_list([media])

        # Name of the annotator.
        if "scribe" in root.attrib:
            scribe = root.attrib['scribe']
            self.set_meta("annotator_name", scribe)

        # Version of the annotation.
        if "version" in root.attrib:
            version = root.attrib['version']
            self.set_meta("annotator_version", version)

        # Date of the annotation.
        if "version_date" in root.attrib:
            version_date = root.attrib['version_date']
            self.set_meta("annotator_version_date", version_date)

        # Language of the annotation. saved as a language name because
        # it's iso639-1 and SPPAS is expecting iso639-3.
        if "xml:lang" in root.attrib:
            lang = root.attrib['xml:lang']
            self.set_meta("language_name_0", lang)

    # -----------------------------------------------------------------------

    def _parse_speakers(self, spk_root):
        """Read the <Speakers> element and create tiers.

        <!ELEMENT Speakers (Speaker*)>
        <!ATTLIST Speakers>

        <!ELEMENT Speaker EMPTY>
        <!ATTLIST Speaker
            id		    ID		#REQUIRED
            name		CDATA		#REQUIRED
            check		(yes|no)	#IMPLIED
            type 		(male|female|child|unknown)	#IMPLIED
            dialect		(native|nonnative)		#IMPLIED
            accent		CDATA		#IMPLIED
            scope		(local|global)	#IMPLIED
        >

        :param spk_root: (ET) XML Element tree root.

        """
        if spk_root is not None:
            for spk_node in spk_root.findall('Speaker'):
                # Speaker identifier -> new tier
                if "id" in spk_node.attrib:
                    value = spk_node.attrib['id']
                    tier = self.create_tier("Trans-" + value)
                    tier.set_meta("speaker_id", value)

                # Speaker name: CDATA
                if "name" in spk_node.attrib:
                    tier.set_meta("speaker_name",
                                  spk_node.attrib['name'])

                # Speaker type: male/female/child/unknown
                if "type" in spk_node.attrib:
                    tier.set_meta("speaker_type",
                                  spk_node.attrib['type'])

                # "spelling checked" for speakers whose name
                # has been checked: yes/no
                if "check" in spk_node.attrib:
                    tier.set_meta("speaker_check",
                                  spk_node.attrib['check'])

                # Speaker dialect: native/nonnative
                if "dialect" in spk_node.attrib:
                    tier.set_meta("speaker_dialect",
                                  spk_node.attrib['dialect'])

                # Speaker accent: CDATA
                if "accent" in spk_node.attrib:
                    tier.set_meta("speaker_accent",
                                  spk_node.attrib['accent'])

                # Speaker scope: local/global
                if "scope" in spk_node.attrib:
                    tier.set_meta("speaker_scope",
                                  spk_node.attrib['scope'])

    # -----------------------------------------------------------------------

    @staticmethod
    def _parse_topics(topic_root, topic_tier):
        """Read the <Topics> element and create a tier.

        The topics and their description are stored in a controlled
        vocabulary.

        <!ELEMENT Topics (Topic*)>
        <!ATTLIST Topics>

        <!ELEMENT Topic EMPTY>
        <!ATTLIST Topic
            id		ID		#REQUIRED
            desc	CDATA	#REQUIRED
        >

        :param topic_root: (ET) XML Element tree root.
        :param topic_tier: (sppasTier) Tier to store topic segmentation

        """
        if topic_root is None:
            return

        # assign the vocabulary.
        ctrl_vocab = sppasCtrlVocab('topics')
        for topic_node in topic_root.findall('Topic'):
            # Topic identifier
            try:
                topic_id = topic_node.attrib['id']
            except KeyError:
                continue
            # Topic description: CDATA
            try:
                topic_desc = topic_node.attrib['desc']
            except KeyError:
                topic_desc = ""
            # Add an entry in the controlled vocabulary
            ctrl_vocab.add(sppasTag(topic_id), topic_desc)

        topic_tier.set_ctrl_vocab(ctrl_vocab)

    # -----------------------------------------------------------------------

    @staticmethod
    def _parse_episode_attributes(episode_root, episodes_tier):
        """Read the episode attributes.

        <!ELEMENT Episode (Section*)>
        <!ATTLIST Episode
        program		CDATA		#IMPLIED
        air_date	CDATA		#IMPLIED
        >

        :param episode_root: (ET) XML Element tree root.
        :param episodes_tier: (sppasTier) The tier to store the episodes.

        """
        if episode_root is None:
            return
        if len(episode_root) == 0:
            # no sections in this episode.
            return

        # Get this episode information
        begin = episode_root[0].attrib['startTime']
        end = episode_root[-1].attrib['endTime']
        try:
            program = episode_root.attrib['program']
        except KeyError:
            program = "episode"

        # Add the episode in the tier
        episodes_tier.create_annotation(
            sppasLocation(
                sppasInterval(
                    sppasTRS.make_point(begin),
                    sppasTRS.make_point(end))),
            sppasLabel(sppasTag(program)))

    # -----------------------------------------------------------------------

    def _parse_section_attributes(self, section_root, section_tier):
        """Read the section attributes.

        Sections are mainly used to segment the topics and to mention
        un-transcribed segments.

        <!ELEMENT Section (Turn*)>
        <!ATTLIST Section
        type		(report | nontrans | filler)	#REQUIRED
        topic		IDREF		#IMPLIED
        startTime	CDATA		#REQUIRED
        endTime		CDATA		#REQUIRED
        >

        :param section_root: (ET) XML Element tree root.
        :param section_tier: (sppasTier) The tier to store the sections.

        """
        if section_root is None:
            return

        # Get the location of the section
        begin = section_root.attrib['startTime']
        end = section_root.attrib['endTime']
        location = sppasLocation(sppasInterval(sppasTRS.make_point(begin),
                                               sppasTRS.make_point(end)))

        # Check if it's a non-transcribed section
        section_type = sppasTRS.__parse_type_in_section(section_root)

        # Check the topic
        self.__parse_topic_in_section(section_root, location)

        # Add the section in the tier
        section_tier.create_annotation(location,
                                       sppasLabel(sppasTag(section_type)))

    # -----------------------------------------------------------------------

    def _parse_turn_attributes(self, turn_root):
        """Read the turn attributes and fill the tiers.

        <!ATTLIST Turn
        speaker		IDREFS		#IMPLIED
        startTime	CDATA		#REQUIRED
        endTime		CDATA		#REQUIRED
        mode		(spontaneous|planned)	#IMPLIED
        fidelity	(high|medium|low)		#IMPLIED
        channel		(telephone|studio)		#IMPLIED
        >

        :param turn_root: (ET) XML Element tree root.
        :returns: (list) the tiers of the turn (i.e. speakers...)

        """
        if turn_root is None:
            return

        # Get the location of the turn
        begin = sppasTRS.make_point(turn_root.attrib['startTime'])
        end = sppasTRS.make_point(turn_root.attrib['endTime'])
        location = sppasLocation(sppasInterval(begin, end))

        self.__parse_mode_in_turn(turn_root, location)
        self.__parse_fidelity_in_turn(turn_root, location)
        self.__parse_channel_in_turn(turn_root, location)

        tiers = list()
        speakers = "dummy"
        if "speaker" in turn_root.attrib:
            speakers = turn_root.attrib['speaker']
            for speaker in speakers.split():
                tier = self.find("Trans-" + speaker)
                tiers.append(tier)

        if len(tiers) == 0:
            tier = self.find(NO_SPK_TIER)
            tiers.append(tier)

        turn_tier = self.find("Turns")
        turn_tier.create_annotation(
            sppasLocation(sppasInterval(begin, end)),
            sppasLabel(sppasTag(speakers)))

        return tiers, begin, end

    # -----------------------------------------------------------------------

    def _parse_turn(self, turn_root):
        """Fill a tier with the content of a turn.

        <!ELEMENT Turn (#PCDATA|Sync|Background|Comment|Who|Vocal|Event)*>

        :param turn_root: (ET) XML Element tree root.

        """
        # the turn attributes
        # -------------------
        tiers, turn_begin, turn_end = self._parse_turn_attributes(turn_root)
        tier = None
        if len(tiers) == 1:
            tier = tiers[0]

        # the content of the turn
        # -----------------------
        # PCDATA: handle text directly inside the Turn
        if turn_root.text.strip() != '':
            text = turn_root.text
            # create new annotation covering the whole turn.
            # will eventually be reduced by the rest of the turn content.
            prev_ann = sppasTRS.__create_annotation(turn_begin, turn_end, text)
            if tier is not None:
                tier.add(prev_ann)
        else:
            prev_ann = None

        begin = turn_begin
        for node in turn_root:
            # A node contains a tag and/or a text content

            if node.tag == 'Sync':
                # Update the begin value
                begin = sppasTRS.make_point(node.attrib['time'])

                # Update the end of the previous annotation
                # to the current value
                if prev_ann is not None:
                    prev_ann.get_location().get_best().set_end(begin)

                # create new annotation covering the rest of the turn.
                # will eventually be reduced by the rest of the turn content.
                if len(tiers) == 1:
                    prev_ann = sppasTRS.__create_annotation(
                        begin,
                        turn_end,
                        "")
                    tier.add(prev_ann)

            elif node.tag == 'Background':
                if prev_ann is None:
                    prev_ann = sppasTRS.__create_annotation(
                        begin,
                        turn_end,
                        node.tail)
                    tier.add(prev_ann)
                sppasTRS.__append_background_in_label(node, prev_ann)

            elif node.tag == 'Comment':
                if prev_ann is None:
                    prev_ann = sppasTRS.__create_annotation(
                        begin,
                        turn_end,
                        node.tail)
                    tier.add(prev_ann)
                sppasTRS.__append_comment_in_label(node, prev_ann)

            elif node.tag == 'Who':
                # Update the tier to be annotated
                tier_index = int(node.attrib['nb']) - 1
                tier = tiers[tier_index]
                if len(tiers) > 1:
                    prev_ann = sppasTRS.__create_annotation(
                        begin,
                        turn_end,
                        "")
                    tier.add(prev_ann)

            elif node.tag == 'Vocal':
                # never found it in a large amount of transcribed files.
                pass

            elif node.tag == 'Event':
                if prev_ann is None:
                    prev_ann = sppasTRS.__create_annotation(
                        begin,
                        turn_end,
                        node.tail)
                    tier.add(prev_ann)
                sppasTRS.__append_event_in_label(node, prev_ann)

            # ----------
            # PCDATA: handle text directly inside the Turn
            if node.tail.strip() != "":
                if prev_ann is None:
                    prev_ann = sppasTRS.__create_annotation(
                        begin,
                        turn_end,
                        node.tail)
                    tier.add(prev_ann)

                sppasTRS.__append_text_in_label(prev_ann, node.tail)

        return

    # -----------------------------------------------------------------------
    # Private - parse attributes
    # -----------------------------------------------------------------------

    @staticmethod
    def __append_background_in_label(node_event, annotation):
        """Background is appended like a comment in the transcription.

        <!ELEMENT Background EMPTY>
        <!ATTLIST Background
        time		CDATA		#REQUIRED
        type        NMTOKENS	#REQUIRED
        level       NMTOKENS	#IMPLIED
        >

        """
        # convert the Background node into a comment of SPPAS.
        txt = "{background_type=" + node_event.attrib['type']
        if "level" in node_event.attrib:
            txt += " ; background_level=" + \
                   node_event.attrib['level'].replace(',', '_')
        txt += '}'
        # append to the label of the transcription.
        sppasTRS.__append_text_in_label(annotation, txt)

    # -----------------------------------------------------------------------

    @staticmethod
    def __append_comment_in_label(node_event, annotation):
        """Append a comment to the label.

        <!ELEMENT Comment EMPTY>
        <!ATTLIST Comment
        desc		CDATA		#REQUIRED
        >

        """
        # Convert the Comment node into a comment of SPPAS
        txt = '{' + node_event.attrib['desc'].replace(',', '_') + '}'
        # append to the label of the transcription.
        sppasTRS.__append_text_in_label(annotation, txt)

    # -----------------------------------------------------------------------

    @staticmethod
    def __append_event_in_label(node_event, annotation):
        """Append an event to the label.

        <!ATTLIST Event
        type		(noise|lexical|pronounce|language)	"noise"
        extent		(begin|end|previous|next|instantaneous)	"instantaneous"
        desc		CDATA		#REQUIRED
        >

        """
        description = node_event.attrib['desc']
        extent = (node_event.attrib['extent']
                  if 'extent' in node_event.attrib
                  else '')

        if description+"_"+extent in NOISE_EVENTS:
            sppasTRS.__append_text_in_label(
                annotation,
                NOISE_EVENTS[description+"_"+extent])

        elif description in NOISE_EVENTS:
            sppasTRS.__append_text_in_label(
                annotation,
                NOISE_EVENTS[description])

        else:
            sppasTRS.__append_text_in_label(
                annotation,
                '{%s}' % description.replace(' ', '_'))

    # -----------------------------------------------------------------------

    @staticmethod
    def __append_text_in_label(annotation, text):
        labels = annotation.get_labels()
        if len(labels) == 0:
            labels.append(sppasLabel(sppasTag(text)))
        else:
            old_tag = labels[0].get_best()
            old_text = old_tag.get_content()
            old_tag.set_content(old_text + " " + text)

    # -----------------------------------------------------------------------

    @staticmethod
    def __create_annotation(begin, end, text):
        loc = sppasLocation(sppasInterval(begin, end))
        lab = format_labels(text)
        return sppasAnnotation(loc, lab)

    # -----------------------------------------------------------------------

    @staticmethod
    def __parse_type_in_section(section_root):
        """Extract the type of a section."""
        if "type" in section_root.attrib:
            return section_root.attrib['type']
        return "undefined"

    # -----------------------------------------------------------------------

    def __parse_topic_in_section(self, section_root, location):
        """Extract the topic of a section."""
        try:
            section_topic = section_root.attrib['topic']
        except KeyError:
            return

        # Append this section in the Topics tier
        topics = self.find('Topics')
        topics.create_annotation(location,
                                 sppasLabel(sppasTag(section_topic)))

    # -----------------------------------------------------------------------

    def __parse_mode_in_turn(self, turn_root, location):
        """Extract the mode of a turn."""
        try:
            mode = turn_root.attrib['mode']
        except KeyError:
            return

        mode_tier = self.find('TurnElocutionMode')
        if mode_tier is None:
            mode_tier = self.create_tier('TurnElocutionMode')
            ctrl = sppasCtrlVocab('mode', description="Elocution mode")
            ctrl.add(sppasTag('spontaneous'))
            ctrl.add(sppasTag('planned'))
            mode_tier.set_ctrl_vocab(ctrl)

        mode_tier.create_annotation(location,
                                    sppasLabel(sppasTag(mode)))

    # -----------------------------------------------------------------------

    def __parse_fidelity_in_turn(self, turn_root, location):
        """Extract the fidelity of a turn."""
        try:
            fidelity = turn_root.attrib['fidelity']
        except KeyError:
            return

        fidelity_tier = self.find('TurnRecordingQuality')
        if fidelity_tier is None:
            fidelity_tier = self.create_tier('TurnRecordingQuality')
            ctrl = sppasCtrlVocab('fidelity', description="Recording quality")
            ctrl.add(sppasTag('high'))
            ctrl.add(sppasTag('medium'))
            ctrl.add(sppasTag('low'))
            fidelity_tier.set_ctrl_vocab(ctrl)

        fidelity_tier.create_annotation(location,
                                        sppasLabel(sppasTag(fidelity)))

    # -----------------------------------------------------------------------

    def __parse_channel_in_turn(self, turn_root, location):
        """Extract the channel of a turn."""
        try:
            channel = turn_root.attrib['channel']
        except KeyError:
            return

        channel_tier = self.find('TurnChannel')
        if channel_tier is None:
            channel_tier = self.create_tier('TurnChannel')
            ctrl = sppasCtrlVocab('channel', description="Recording quality")
            ctrl.add(sppasTag('studio'))
            ctrl.add(sppasTag('telephone'))
            channel_tier.set_ctrl_vocab(ctrl)

        channel_tier.create_annotation(location, sppasLabel(sppasTag(channel)))
