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

    src.ui.phoenix.panels.ann.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Editor for a sppasAnnotation().
    Allows to modify its labels and metadata.

"""

import os
import wx
import logging
import json
import xml.etree.cElementTree as ET
import wx.richtext

from sppas import paths
from sppas.src.anndata import sppasRW
from sppas.src.anndata.aio.xra import sppasXRA
from sppas.src.anndata.aio.xra import sppasJRA
from sppas.src.anndata.aio.aioutils import serialize_labels
from sppas.src.anndata.aio.aioutils import format_labels

from ..windows import sppasPanel
from ..windows import sppasToolbar

# ---------------------------------------------------------------------------


class sppasAnnEditPanel(sppasPanel):
    """Edit an annotation of a tier.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2020  Brigitte Bigi

    Existing shortcuts in a richtextctrl:
        - ctrl+a - select all
        - ctrl+c - copy
        - ctrl+y - del the character after the cursor
        - ctrl+v - paste
        - ctrl+x - cut
        - ctrl+z - undo

    """

    def __init__(self, parent, ann=None):
        """Create a sppasAnnEditPanel.

        :param parent: (wx.Window)
        :param ann: (sppasAnnotation)

        """
        super(sppasAnnEditPanel, self).__init__(
            parent,
            style=wx.BORDER_SIMPLE | wx.TAB_TRAVERSAL,
            name="annedit_panel")
        self._create_content()
        self._setup_events()
        self.__ann = ann
        self.__refresh()
        self._code_edit = "code_review"

    # -----------------------------------------------------------------------
    # Get/Set of the sppasAnnotation()
    # -----------------------------------------------------------------------

    def set_ann(self, ann):
        self.__ann = ann
        self.__refresh()

    # -----------------------------------------------------------------------

    def ann_labels(self):
        if self.__ann is None:
            return list()
        return self.__ann.get_labels()

    # -----------------------------------------------------------------------

    def is_text_modified(self):
        """Return True if the text has changed compared to labels of ann."""
        ann_text_labels = serialize_labels(self.__ann.get_labels())
        try:
            textctrl_text_labels = serialize_labels(self.text_to_labels())
        except:
            # The text is invalid: it means it was manually modified!
            return True

        return ann_text_labels == textctrl_text_labels

    # -----------------------------------------------------------------------
    # Convert Text <-> List of sppasLabel() instances
    # -----------------------------------------------------------------------

    def text_to_labels(self):
        """Return the labels created from the text content.

        Can raise exceptions if the text can't be parsed.

        :return (list of sppasLabel)

        """
        content = self.__textctrl.GetValue()
        labels = list()

        # The text is in XML (.xra) format
        if self._code_edit == "code_xml":
            tree = ET.fromstring(content)
            for label_root in tree.findall('Label'):
                labels.append(sppasXRA.parse_label(label_root))

        # The text is in JSON (.jra) format
        elif self._code_edit == "code_json":
            json_obj = json.loads(content)
            for tags in json_obj:
                labels.append(sppasJRA.parse_label(tags))

        # The text is serialized
        elif self._code_edit == "code_review":
            labels = format_labels(content)

        return labels

    # -----------------------------------------------------------------------

    def labels_to_text(self, labels):
        """Return the text created from the given labels.

        :return (str)

        """
        if len(labels) == 0:
            return ""

        # The annotation labels are to be displayed in XML (.xra) format
        if self._code_edit == "code_xml":
            root = ET.Element('Labels')
            for label in labels:
                label_root = ET.SubElement(root, 'Label')
                sppasXRA.format_label(label_root, label)
            sppasXRA.indent(root)
            xml_text = ET.tostring(root, encoding="utf-8", method="xml")
            return xml_text

        # The annotation labels are to be displayed in JSON (.jra) format
        if self._code_edit == "code_json":
            root = list()
            for label in labels:
                sppasJRA.format_label(root, label)
            json_text = json.dumps(root, indent=4, separators=(',', ': '))
            return json_text

        # The annotation labels are to be displayed in text
        if self._code_edit == "code_review":
            return serialize_labels(labels)

        return ""

    # -----------------------------------------------------------------------
    # Construct the GUI
    # -----------------------------------------------------------------------

    def _create_content(self):
        """Create the main panel to edit an annotation.

        """
        toolbar = self.__create_toolbar()
        textctrl = self.__create_textctrl()

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(toolbar, 0, wx.EXPAND)
        sizer.Add(textctrl, 1, wx.EXPAND)

        self.SetSizer(sizer)

    # -----------------------------------------------------------------------

    def __create_toolbar(self):
        toolbar = sppasToolbar(self, name="ann_toolbar")
        toolbar.set_height(24)
        toolbar.AddButton("way_up_down")
        toolbar.AddSpacer(1)

        toolbar.AddButton("restore")
        toolbar.AddToggleButton("code_review", value=True, group_name="view_mode")
        toolbar.AddToggleButton("code_xml", group_name="view_mode")
        toolbar.AddToggleButton("code_json", group_name="view_mode")
        toolbar.AddSpacer(1)

        meta = toolbar.AddButton("tags")
        meta.Enable(False)
        toolbar.AddSpacer(1)

        return toolbar

    # -----------------------------------------------------------------------

    def __create_textctrl(self):
        # A simple TextCtrl can't be used under MacOS because of automatic quotes substitutions.
        text = wx.richtext.RichTextCtrl(
            self, -1, "",
            style=wx.TE_MULTILINE | wx.TE_BESTWRAP,
            name="ann_textctrl")
        try:
            text.SetBackgroundColour(wx.GetApp().settings.bg_color)
            text.SetForegroundColour(wx.GetApp().settings.fg_color)
            text.SetFont(wx.GetApp().settings.text_font)
        except AttributeError:
            text.InheritAttributes()
        # text.Bind(wx.EVT_CHAR, self._on_char, text)
        return text

    # -----------------------------------------------------------------------

    @property
    def __toolbar(self):
        return self.FindWindow("ann_toolbar")

    @property
    def __textctrl(self):
        return self.FindWindow("ann_textctrl")

    # -----------------------------------------------------------------------
    # Management of events
    # -----------------------------------------------------------------------

    def _setup_events(self):
        """Capture some of the events our controls are emitting.

        """
        self.Bind(wx.EVT_BUTTON, self._process_toolbar_event)
        self.Bind(wx.EVT_TOGGLEBUTTON, self._process_toolbar_event)

    # -----------------------------------------------------------------------

    def _process_toolbar_event(self, event):
        """Process a button of the toolbar event.

        :param event: (wx.Event)

        """
        wx.LogDebug("Toolbar Event received by {:s}".format(self.GetName()))
        btn = event.GetEventObject()
        btn_name = btn.GetName()

        if btn_name == "restore":
            self.__refresh()

        elif btn_name in ("code_review", "code_xml", "code_json"):
            try:
                new_labels = self.text_to_labels()
            except Exception as e:
                wx.LogError("The labels can't be parsed: {}. Annotation "
                            "labels are restored.".format(e))
                # enable the current view.
                self.__toolbar.get_button(btn_name).SetValue(False)
                self.__toolbar.get_button(self._code_edit).SetValue(True)
                self.__refresh()
            else:
                self._code_edit = btn_name
                self.__textctrl.SetValue(self.labels_to_text(new_labels))

        else:
            # send the button event to the parent
            event.Skip()

    # -----------------------------------------------------------------------

    def _on_char(self, evt):
        logging.debug("On char event received. {}".format(evt.GetEventObject()))
        kc = evt.GetKeyCode()
        text = evt.GetEventObject()
        if evt.ControlDown() and kc == 83:    # Ctrl+s
            pass  # send ann to parent ???
        else:
            evt.Skip()

    # -----------------------------------------------------------------------

    def __refresh(self):
        """Refresh the item of the selected annotation in the textctrl."""
        if self.__ann is not None:
            labels = self.__ann.get_labels()
            if len(labels) == 0:
                self.__textctrl.SetValue("")
            else:
                self.__textctrl.SetValue(self.labels_to_text(labels))

        else:
            self.__textctrl.SetValue("<<no annotation selected>>")

# ---------------------------------------------------------------------------


class TestPanel(sppasPanel):

    def __init__(self, parent):
        super(TestPanel, self).__init__(parent)

        f1 = os.path.join(paths.samples, "annotation-results",
                          "samples-fra", "F_F_B003-P8-phon.xra")

        p = sppasAnnEditPanel(self, None)
        s = wx.BoxSizer()
        s.Add(p, 1, wx.EXPAND)
        self.SetSizer(s)

        parser = sppasRW(f1)
        trs1 = parser.read()
        p.set_ann(trs1[0][1])
