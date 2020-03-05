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
from sppas.src.utils import u
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

        try:
            self.SetBackgroundColour(wx.GetApp().settings.bg_color)
            self.SetForegroundColour(wx.GetApp().settings.fg_color)
            self.SetFont(wx.GetApp().settings.text_font)
        except AttributeError:
            self.InheritAttributes()

        self.__set_styles()
        self.__textctrl.SetDefaultStyle(self.text_attr)
        self.__ann = ann
        self.__refresh()
        self.__code_edit = "code_review"

    # -----------------------------------------------------------------------
    # Public methods to access data
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

    def text_labels(self):
        return self.__text_to_labels()

    # -----------------------------------------------------------------------

    def is_text_valid(self):
        try:
            serialize_labels(self.__text_to_labels())
            return True
        except:
            # The text is invalid: it means it was manually modified!
            return False

    # -----------------------------------------------------------------------

    def is_text_modified(self):
        """Return True if the text has changed compared to labels of ann."""
        ann_text_labels = serialize_labels(self.__ann.get_labels())
        try:
            textctrl_text_labels = serialize_labels(self.__text_to_labels())
        except:
            # The text is invalid: it means it was manually modified!
            return True

        return ann_text_labels == textctrl_text_labels

    # -----------------------------------------------------------------------
    # Convert Text <-> List of sppasLabel() instances
    # -----------------------------------------------------------------------

    def __text_to_labels(self):
        """Return the labels created from the text content.

        Can raise exceptions if the text can't be parsed.

        :return (list of sppasLabel)

        """
        content = self.__textctrl.GetValue()
        labels = list()

        # The text is in XML (.xra) format
        if self.__code_edit == "code_xml":
            tree = ET.fromstring(content)
            for label_root in tree.findall('Label'):
                labels.append(sppasXRA.parse_label(label_root))

        # The text is in JSON (.jra) format
        elif self.__code_edit == "code_json":
            json_obj = json.loads(content)
            for tags in json_obj:
                labels.append(sppasJRA.parse_label(tags))

        # The text is serialized
        elif self.__code_edit == "code_review":
            labels = format_labels(content)

        return labels

    # -----------------------------------------------------------------------

    def __labels_to_text(self, labels):
        """Return the text created from the given labels.

        :return (str)

        """
        if len(labels) == 0:
            return ""

        # The annotation labels are to be displayed in XML (.xra) format
        if self.__code_edit == "code_xml":
            root = ET.Element('Labels')
            for label in labels:
                label_root = ET.SubElement(root, 'Label')
                sppasXRA.format_label(label_root, label)
            sppasXRA.indent(root)
            xml_text = ET.tostring(root, encoding="utf-8", method="xml")
            return xml_text.decode('utf-8')

        # The annotation labels are to be displayed in JSON (.jra) format
        if self.__code_edit == "code_json":
            root = list()
            for label in labels:
                sppasJRA.format_label(root, label)
            json_text = json.dumps(root, indent=4, separators=(',', ': '))
            return json_text

        # The annotation labels are to be displayed in text
        if self.__code_edit == "code_review":
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
        sizer.Add(textctrl, 1, wx.EXPAND | wx.ALL, border=sppasPanel.fix_size(4))

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
        # A simple TextCtrl can't be used under MacOS because of automatic
        # quotes substitutions which can't be disabled.
        text = wx.richtext.RichTextCtrl(
            self, -1, "",
            style=wx.TE_MULTILINE | wx.TE_BESTWRAP,
            name="ann_textctrl")

        text.SetEditable(True)
        return text

    # ------------------------------------------------------------------------

    def __set_styles(self):
        """Fix a set of styles to be used in the RichTextCtrl.

        """
        fs = self.GetFont()
        bg = self.GetBackgroundColour()
        fg = self.GetForegroundColour()

        # Default style
        self.text_attr = wx.richtext.RichTextAttr()
        self.text_attr.SetTextColour(fg)
        self.text_attr.SetBackgroundColour(bg)
        self.text_attr.SetFont(fs)

        # Bold font for special chars: {}|<>[]/
        self.alt_tags = wx.richtext.RichTextAttr()
        self.alt_tags.SetTextColour(fg)
        self.alt_tags.SetBackgroundColour(bg)
        self.alt_tags.SetFont(
            wx.Font(fs.GetPointSize(),
                    fs.GetFamily(),
                    fs.GetStyle(),
                    wx.FONTWEIGHT_BOLD,
                    False,
                    fs.GetFaceName()))

    # ------------------------------------------------------------------------

    def __set_font_style(
            self, font_fg_color=None, font_bg_color=None, font_face=None,
            font_size=None, font_bold=None, font_italic=None,
            font_underline=None):

        if font_fg_color is not None:
            self.text_attr.SetTextColour(font_fg_color)

        if font_bg_color is not None:
            self.text_attr.SetBackgroundColour(font_bg_color)

        if font_face is not None:
            self.text_attr.SetFontFaceName(font_face)

        if font_size is not None:
            self.text_attr.SetFontSize(font_size)

        if font_bold is not None:
            if font_bold:
                self.text_attr.SetFontWeight(wx.FONTWEIGHT_BOLD)
            else:
                self.text_attr.SetFontWeight(wx.FONTWEIGHT_NORMAL)

        if font_italic is not None:
            if font_italic:
                self.text_attr.SetFontStyle(wx.FONTSTYLE_ITALIC)
            else:
                self.text_attr.SetFontStyle(wx.FONTSTYLE_NORMAL)

        if font_underline is not None:
            if font_underline:
                self.text_attr.SetFontUnderlined(True)
            else:
                self.text_attr.SetFontUnderlined(False)

        self.__textctrl.SetDefaultStyle(self.text_attr)

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
        self.__textctrl.Bind(wx.EVT_CHAR, self._on_char)

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
            self.__switch_code(btn_name)

        else:
            # send the button event to the parent
            event.Skip()

    # -----------------------------------------------------------------------

    def __switch_code(self, view_name):
        try:
            new_labels = self.__text_to_labels()

        except Exception as e:
            wx.LogError("The labels can't be parsed: {}. Annotation "
                        "labels are restored.".format(e))
            # enable the current view (restore).
            self.__toolbar.get_button(view_name).SetValue(False)
            self.__toolbar.get_button(self.__code_edit).SetValue(True)
            self.__refresh()

        else:
            self.__code_edit = view_name
            self.__set_text_value(self.__labels_to_text(new_labels))

    # -----------------------------------------------------------------------

    def _on_char(self, evt):
        logging.debug("On char event received. {}".format(evt.GetEventObject()))
        kc = evt.GetKeyCode()
        char = chr(kc)

        if evt.ControlDown() and kc == 83:    # Ctrl+s
            pass  # send ann to parent ???

        elif any((evt.ControlDown(), evt.AltDown())) is False:
            self.__append_styled_text(char)

        else:
            evt.Skip()

    # -----------------------------------------------------------------------

    def __refresh(self):
        """Refresh the item of the selected annotation in the textctrl."""
        self.__textctrl.SetValue("")

        if self.__ann is not None:
            labels = self.__ann.get_labels()
            if len(labels) > 0:
                self.__set_text_value(self.__labels_to_text(labels))

    # -----------------------------------------------------------------------

    def __set_text_value(self, content):
        """Set a text with the appropriate style."""
        self.__textctrl.SetValue("")
        for char in content:
            self.__append_styled_text(char)

    # -----------------------------------------------------------------------

    def __append_styled_text(self, text):
        """Append a text with the appropriate style."""
        if text in ('{', '}', '[', ']', '<', '>', '/', '|'):
            self.__textctrl.BeginStyle(self.alt_tags)
        else:
            self.__textctrl.BeginStyle(self.text_attr)

        self.__textctrl.WriteText(text)
        self.__textctrl.EndStyle()

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
