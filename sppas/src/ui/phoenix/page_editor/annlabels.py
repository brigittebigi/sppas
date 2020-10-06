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

    src.ui.phoenix.page_editor.annlabels.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Editor for the list of sppasLabel() instances of a sppasAnnotation().
    The given sppasAnnotation() instance is not modified. When a change is
    performed on a wx.Window representing the object, an event is sent to
    the parent.

"""

import os
import wx
import json
import xml.etree.cElementTree as ET
import wx.richtext

from sppas.src.config import paths
from sppas.src.utils import u
from sppas.src.anndata import sppasRW
from sppas.src.anndata.aio.xra import sppasXRA
from sppas.src.anndata.aio.xra import sppasJRA
from sppas.src.anndata.aio.aioutils import serialize_labels
from sppas.src.anndata.aio.aioutils import format_labels

from ..windows import sppasPanel

# ---------------------------------------------------------------------------


class sppasAnnLabelsCtrl(wx.richtext.RichTextCtrl):
    """Text editor of labels of an annotation of a tier.

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

    Labels of the given annotation are not modified but edited in a TextCtrl.

    """
    
    MODES = ("code_review", "code_json", "code_xml")
    
    # -----------------------------------------------------------------------

    def __init__(self, parent, ann=None, name="annlabels_textctrl"):
        """Create a sppasAnnLabelsCtrl.

        :param parent: (wx.Window)
        :param ann: (sppasAnnotation)
        :param name: (str)

        """
        super(sppasAnnLabelsCtrl, self).__init__(
            parent,
            style=wx.TE_MULTILINE | wx.TE_BESTWRAP | wx.BORDER_SIMPLE | wx.TAB_TRAVERSAL,
            name=name)

        try:
            self.SetBackgroundColour(wx.GetApp().settings.bg_color)
            self.SetForegroundColour(wx.GetApp().settings.fg_color)
            self.SetFont(wx.GetApp().settings.text_font)
        except AttributeError:
            self.InheritAttributes()

        self.__set_styles()
        self.SetDefaultStyle(self.text_attr)
        self.SetEditable(True)

        self.__ann = ann
        self.update()
        self.__code_edit = "code_review"

        self.Bind(wx.EVT_CHAR, self._on_char)

    # -----------------------------------------------------------------------
    # Public methods to access data
    # -----------------------------------------------------------------------

    def set_ann(self, ann=None):
        """Set a new annotation.

        Any changes in the text editor of labels are lost.

        :param ann: (sppasAnnotation)

        """
        self.__ann = ann
        self.update()

    # -----------------------------------------------------------------------

    def text_labels(self):
        """Return a list of labels made from the content of the text editor.

        :return: (list of sppasLabel instances)
        :raises: Raise exception if labels can't be created from the raw text.

        """
        return self.__text_to_labels()

    # -----------------------------------------------------------------------

    def text_modified(self):
        """Ask for modification in the text.

        Return 0 if the text wasn't changed.
        Return 1 if the text has changed and can create valid labels.
        Return -1 if the text has changed but can't create valid labels.

        :return: (int)

        """
        if self.__ann is None:
            return 0

        try:
            textctrl_text_labels = serialize_labels(self.__text_to_labels())
        except Exception as e:
            wx.LogError(str(e))
            return -1

        if textctrl_text_labels == serialize_labels(self.__ann.get_labels()):
            return 0

        return 1

    # -----------------------------------------------------------------------

    def update(self):
        """Reset the textctrl with the labels of the annotation.

        """
        self.SetValue("")

        if self.__ann is not None:
            labels = self.__ann.get_labels()
            if len(labels) > 0:
                self.__set_text_value(self.__labels_to_text(labels))

    # -----------------------------------------------------------------------

    def switch_view(self, view_mode):
        """Switch to the given view mode.

        :param view_mode: (str) One of the MODES.
        :return: True is the switch of mode was done

        """
        if view_mode not in sppasAnnLabelsCtrl.MODES:
            return False

        try:
            new_labels = self.__text_to_labels()
        except Exception as e:
            wx.LogError("The current labels can't be parsed: {}. Annotation "
                        "labels are restored.".format(e))
            # enable the current view (restore).
            self.update()
            return False

        self.__code_edit = view_mode
        self.__set_text_value(self.__labels_to_text(new_labels))
        return True

    # -----------------------------------------------------------------------
    # Convert Text <-> List of sppasLabel() instances
    # -----------------------------------------------------------------------

    def __text_to_labels(self):
        """Return the labels created from the text content.

        Can raise exceptions if the text can't be parsed.

        :return (list of sppasLabel)

        """
        content = self.GetValue()
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
            tag_type = "str"
            parent = self.__ann.get_parent()
            if parent is not None:
                tag_type = parent.get_labels_type()
                if tag_type == "":
                    tag_type = "str"

            labels = format_labels(content,
                                   separator="\n",
                                   empty="",
                                   tag_type=tag_type)

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
        self.tags_attr = wx.richtext.RichTextAttr()
        self.tags_attr.SetTextColour(fg)
        self.tags_attr.SetBackgroundColour(bg)
        self.tags_attr.SetFont(
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

        self.SetDefaultStyle(self.text_attr)

    # -----------------------------------------------------------------------
    # Management of events
    # -----------------------------------------------------------------------

    def _on_char(self, evt):
        """A new character is entered in the text."""
        kc = evt.GetKeyCode()
        char = chr(kc)
        
        if any((evt.ControlDown(), evt.AltDown())) is False and kc > 31 and kc != 127:
            self.__append_styled_char(char)

        else:
            evt.Skip()

    # -----------------------------------------------------------------------

    def __set_text_value(self, content):
        """Set a text with the appropriate style."""
        self.SetValue("")
        for char in content:
            self.__append_styled_char(char)

    # -----------------------------------------------------------------------

    def __append_styled_char(self, text):
        """Append a character with the appropriate style."""
        if text in ('{', '[', '<', '/', '|'):
            self.BeginStyle(self.tags_attr)
            self.WriteText(text)
            self.EndStyle()

        elif text in (u('}'), u(']'), u('>')):
            self.BeginStyle(self.tags_attr)
            self.WriteText(text)
            self.EndStyle()

        else:
            self.WriteText(text)

# ---------------------------------------------------------------------------


class TestPanel(sppasPanel):

    def __init__(self, parent):
        super(TestPanel, self).__init__(parent, name="Test AnnLabels Text Editor")

        f1 = os.path.join(paths.samples, "annotation-results",
                          "samples-fra", "F_F_B003-P8-phon.xra")

        p = sppasAnnLabelsCtrl(self, None)
        s = wx.BoxSizer()
        s.Add(p, 1, wx.EXPAND)
        self.SetSizer(s)

        parser = sppasRW(f1)
        trs1 = parser.read()
        p.set_ann(trs1[0][1])
