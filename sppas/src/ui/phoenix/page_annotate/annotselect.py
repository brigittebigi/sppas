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

    ui.phoenix.page_annotate.annselect.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""

import logging
import wx

from sppas import msg
from sppas import u
from sppas import annots

from ..panels import sppasOptionsPanel
from ..windows import sppasDialog
from ..windows import sppasPanel
from ..windows import sppasScrolledPanel
from ..windows import sppasStaticLine
from ..windows import sppasStaticText
from ..windows import sppasTextCtrl
from ..windows import BitmapTextButton, sppasTextButton

from .annotevent import PageChangeEvent

# ---------------------------------------------------------------------------

LANG_NONE = "---"


def _(message):
    return u(msg(message, "ui"))


ANN_TYPE = _("Annotations of type {:s}")
MSG_CONFIG = _("Configure")

# ---------------------------------------------------------------------------


class sppasAnnotationsPanel(sppasPanel):
    """Create a panel to fix properties of all the annotations.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2019  Brigitte Bigi

    """

    def __init__(self, parent, param, anntype=annots.types[0]):
        super(sppasAnnotationsPanel, self).__init__(
            parent=parent,
            name="page_annot_"+anntype,
            style=wx.BORDER_NONE
        )
        # The type of annotations this page is supporting
        self.__anntype = anntype

        # The parameters to set the properties
        self.__param = param

        # Construct the panel
        self._create_content()
        self._setup_events()
        self.Layout()

    # -----------------------------------------------------------------------
    # Public methods to manage the data
    # -----------------------------------------------------------------------

    def get_param(self):
        for i in range(self.__param.get_step_numbers()):
            a = self.__param.get_step(i)
            if a.get_activate() is True:
                logging.info("Annotation {:s} is activated. "
                             "Language is set to '{!s:s}'"
                             "".format(a.get_name(), a.get_lang()))
        return self.__param

    # -----------------------------------------------------------------------

    def set_param(self, param):
        for i in range(param.get_step_numbers()):
            a = param.get_step(i)
            if self.__anntype in a.get_types():
                w = self.FindWindow("panel_annot_" + a.get_key())
                if w is not None:
                    w.set_annparam(a)
                else:
                    logging.error("In annotation type '{:s}', panel not "
                                  "found for annotation '{:s}'"
                                  "".format(self.__anntype, a.get_key()))
        self.__param = param

    # -----------------------------------------------------------------------
    # Private methods to construct the panel.
    # -----------------------------------------------------------------------

    def _create_content(self):
        """Create the main content."""
        sizer = wx.BoxSizer(wx.VERTICAL)
        btn_size = sppasPanel.fix_size(64)

        btn_back_top = BitmapTextButton(self, name="arrow_up")
        btn_back_top.FocusWidth = 0
        btn_back_top.BorderWidth = 0
        btn_back_top.BitmapColour = self.GetForegroundColour()
        btn_back_top.SetMinSize(wx.Size(btn_size, btn_size))

        title = sppasStaticText(
            self, label=ANN_TYPE.format(self.__anntype),
            name="title_text")

        sizer_top = wx.BoxSizer(wx.HORIZONTAL)
        sizer_top.Add(btn_back_top, 0, wx.RIGHT, btn_size // 4)
        sizer_top.Add(title, 1, wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_CENTER_HORIZONTAL)

        scrolled = sppasScrolledPanel(self, name="anns_list", style=wx.BORDER_NONE)
        sizer_anns = wx.BoxSizer(wx.VERTICAL)
        for i in range(self.__param.get_step_numbers()):
            a = self.__param.get_step(i)
            if self.__anntype in a.get_types():
                pa = sppasEnableAnnotation(scrolled, a)
                sizer_anns.Add(self.HorizLine(scrolled), 0, wx.EXPAND | wx.TOP | wx.RIGHT, btn_size // 8)
                sizer_anns.Add(pa, 1, wx.EXPAND | wx.RIGHT, btn_size // 8)
                sizer_anns.Add(self.HorizLine(scrolled), 0, wx.EXPAND | wx.BOTTOM | wx.RIGHT, btn_size // 8)
        scrolled.SetSizer(sizer_anns)
        scrolled.SetupScrolling(scroll_x=True, scroll_y=True)

        sizer.Add(sizer_top, 0, wx.EXPAND)
        sizer.Add(scrolled, 1, wx.EXPAND | wx.LEFT, btn_size // 4)

        self.SetSizer(sizer)

    # -----------------------------------------------------------------------

    def HorizLine(self, parent, depth=1):
        """Return an horizontal static line."""
        line = sppasStaticLine(parent, orient=wx.LI_HORIZONTAL)
        line.SetMinSize(wx.Size(-1, depth))
        line.SetSize(wx.Size(-1, depth))
        line.SetPenStyle(wx.PENSTYLE_SOLID)
        line.SetDepth(depth)
        line.SetForegroundColour(self.GetForegroundColour())
        return line

    # -----------------------------------------------------------------------
    # Events management
    # -----------------------------------------------------------------------

    def notify(self):
        """Send the EVT_PAGE_CHANGE to the parent."""
        if self.GetParent() is not None:
            evt = PageChangeEvent(from_page=self.GetName(),
                                  to_page="page_annot_actions",
                                  fct="")
            evt.SetEventObject(self)
            wx.PostEvent(self.GetParent(), evt)

    # -----------------------------------------------------------------------

    def _setup_events(self):
        """Associate a handler function with the events.

        It means that when an event occurs then the process handler function
        will be called.

        """
        # Bind all events from our buttons (including 'exit')
        self.Bind(wx.EVT_BUTTON, self._process_event)

    # -----------------------------------------------------------------------

    def _process_event(self, event):
        """Process any kind of events.

        :param event: (wx.Event)

        """
        event_obj = event.GetEventObject()
        event_name = event_obj.GetName()

        if event_name == "arrow_up":
            self.notify()

    # -----------------------------------------------------------------------

    def SetFont(self, font):
        wx.Window.SetFont(self, font)
        for child in self.GetChildren():
            if child.GetName() != "title_text":
                child.SetFont(font)
            else:
                try:
                    settings = wx.GetApp().settings
                    child.SetFont(settings.header_text_font)
                except:
                    pass

    # -----------------------------------------------------------------------

    def SetForegroundColour(self, colour):
        wx.Window.SetForegroundColour(self, colour)
        for child in self.GetChildren():
            if child.GetName() != "title_text":
                child.SetForegroundColour(colour)
            else:
                try:
                    settings = wx.GetApp().settings
                    child.SetForegroundColour(settings.header_fg_color)
                except:
                    child.SetForegroundColour(colour)

# ---------------------------------------------------------------------------
# Annotation panel to enable and select language.
# ---------------------------------------------------------------------------


class sppasEnableAnnotation(sppasPanel):
    """Create a panel to enable and select language of an annotation.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2019  Brigitte Bigi

    """

    def __init__(self, parent, annparam):
        super(sppasEnableAnnotation, self).__init__(
            parent=parent,
            name="panel_annot_" + annparam.get_key(),
            style=wx.BORDER_NONE
        )
        self.__annparam = annparam

        self._create_content()
        self._setup_events()
        self.SetMaxSize(wx.Size(-1, sppasPanel.fix_size(128)))

        self.Layout()

    # -----------------------------------------------------------------------

    def set_annparam(self, p):
        """Set a new AnnotationParam()."""
        self.__annparam = p
        self.UpdateLangChoice()

    # -----------------------------------------------------------------------
    # Private methods to construct the panel.
    # -----------------------------------------------------------------------

    def _create_content(self):
        """Create the main content."""
        es = self.__create_enable_sizer()
        ls = self.__create_lang_sizer()
        ds = self.__create_description_sizer()
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(es, 0, wx.ALIGN_CENTRE)
        sizer.Add(ls, 0, wx.ALIGN_CENTRE | wx.RIGHT | wx.LEFT, 8)
        sizer.Add(ds, 1, wx.ALIGN_CENTRE)

        self.SetSizer(sizer)

    # -----------------------------------------------------------------------

    def __create_enable_sizer(self):
        sizer = wx.BoxSizer(wx.VERTICAL)
        w = sppasPanel.fix_size(128)
        h = sppasPanel.fix_size(32)

        btn_enable = BitmapTextButton(
            self, label=self.__annparam.get_name(), name="on-off-off")
        btn_enable.LabelPosition = wx.RIGHT
        btn_enable.Spacing = 12
        btn_enable.FocusWidth = 0
        btn_enable.BorderWidth = 0
        btn_enable.BitmapColour = self.GetForegroundColour()
        btn_enable.SetMinSize(wx.Size(w, h))

        btn_configure = sppasTextButton(
            self, label=MSG_CONFIG + "...", name="configure")
        btn_configure.SetForegroundColour(wx.Colour(80, 100, 220))
        btn_configure.SetMinSize(wx.Size(w, h))

        sizer.Add(btn_enable, 1, wx.EXPAND)
        sizer.Add(btn_configure, 1, wx.ALIGN_CENTRE | wx.EXPAND)
        return sizer

    # -----------------------------------------------------------------------

    def __create_lang_sizer(self):
        choice_list = self.__annparam.get_langlist()

        # choice of the language
        choice = sppasPanel(self, name="lang_panel")

        # if there are different languages available, add a choice to the panel
        if len(choice_list) > 0:
            choice_list.append(LANG_NONE)
            lang = self.__annparam.get_lang()
            if lang is None or len(lang) == 0:
                lang = LANG_NONE
            choice = wx.ComboBox(
                self, -1, choices=sorted(choice_list), name="lang_choice")
            choice.SetSelection(choice.GetItems().index(lang))
            choice.Bind(wx.EVT_COMBOBOX, self._on_lang_changed)

        choice.SetMinSize(wx.Size(sppasPanel.fix_size(80), -1))

        return choice

    # -----------------------------------------------------------------------

    def __create_description_sizer(self):
        text_style = wx.TAB_TRAVERSAL | \
                     wx.TE_MULTILINE | \
                     wx.TE_READONLY | \
                     wx.TE_BESTWRAP | \
                     wx.TE_AUTO_URL | \
                     wx.NO_BORDER | \
                     wx.TE_RICH
        td = sppasTextCtrl(
            self, value=self.__annparam.get_descr(), style=text_style)
        #td.SetMinSize(wx.Size(sppasPanel.fix_size(512), -1))

        return td

    # -----------------------------------------------------------------------
    # Events management
    # -----------------------------------------------------------------------

    def _setup_events(self):
        """Associate a handler function with the events.

        It means that when an event occurs then the process handler function
        will be called.

        """
        # Bind all events from our buttons (including 'exit')
        self.Bind(wx.EVT_BUTTON, self._process_event)

    # -----------------------------------------------------------------------

    def _process_event(self, event):
        """Process any kind of events.

        :param event: (wx.Event)

        """
        event_obj = event.GetEventObject()
        event_name = event_obj.GetName()

        if event_name == "on-off-off":
            event_obj.SetName("on-off-on")
            event_obj.SetImage("on-off-on")
            self.__annparam.set_activate(True)

        elif event_name == "on-off-on":
            event_obj.SetName("on-off-off")
            event_obj.SetImage("on-off-off")
            self.__annparam.set_activate(False)

        elif event_name == "configure":
            dlg = sppasAnnotationConfigureDialog(self, self.__annparam)
            if dlg.ShowModal() == wx.ID_OK:
                self.__annparam = dlg.annparam
            dlg.Destroy()

    # -----------------------------------------------------------------------

    def _on_lang_changed(self, event):
        choice = event.GetEventObject()
        lang = choice.GetValue()
        if lang == LANG_NONE:
            lang = None

        self.__annparam.set_lang(lang)

    # -----------------------------------------------------------------------

    def SetForegroundColour(self, colour):
        wx.Window.SetForegroundColour(self, colour)
        for c in self.GetChildren():
            if c.GetName() != "configure":
                c.SetForegroundColour(colour)

    # -----------------------------------------------------------------------

    def SetBackgroundColour(self, colour):
        r, g, b = colour.Red(), colour.Green(), colour.Blue()
        delta = 10
        if (r + g + b) > 384:
            colour = wx.Colour(r, g, b, 50).ChangeLightness(100 - delta)
        else:
            colour = wx.Colour(r, g, b, 50).ChangeLightness(100 + delta)

        wx.Window.SetBackgroundColour(self, colour)
        for c in self.GetChildren():
            c.SetBackgroundColour(colour)

    # -----------------------------------------------------------------------

    def UpdateLangChoice(self):
        """Update the language choice buttons depending on the parameters."""
        if len(self.__annparam.get_langlist()) > 0:
            lang = self.__annparam.get_lang()
            if lang is None or len(lang) == 0:
                lang = LANG_NONE
            choice = self.FindWindow("lang_choice")
            choice.SetSelection(choice.GetItems().index(lang))
            choice.Refresh()

# ---------------------------------------------------------------------------


class sppasAnnotationConfigureDialog(sppasDialog):
    """Dialog to configure the given annotation.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2019  Brigitte Bigi

    Returns either wx.ID_CANCEL or wx.ID_OK if ShowModal().

    """
    def __init__(self, parent, annparam):
        """Create a dialog to fix an annotation config.

        :param parent: (wx.Window)

        """
        super(sppasAnnotationConfigureDialog, self).__init__(
            parent=parent,
            title="annot_configure",
            style=wx.DEFAULT_FRAME_STYLE | wx.DIALOG_NO_PARENT)

        self.annparam = annparam

        self.CreateHeader(MSG_CONFIG + " {:s}".format(annparam.get_name()),
                          "wizard-config")
        self._create_content()
        self._create_buttons()

        # Bind events
        self.Bind(wx.EVT_BUTTON, self._process_event)

        self.LayoutComponents()
        self.GetSizer().Fit(self)
        self.CenterOnParent()
        self.FadeIn(deltaN=-8)

    # -----------------------------------------------------------------------

    def _create_content(self):
        """Create the content of the dialog."""
        options_panel = sppasOptionsPanel(self, self.annparam.get_options())
        options_panel.SetAutoLayout(True)
        self.items = options_panel.GetItems()
        self.SetContent(options_panel)

    # -----------------------------------------------------------------------

    def _create_buttons(self):
        self.CreateActions([wx.ID_CANCEL, wx.ID_OK])
        self.Bind(wx.EVT_BUTTON, self._process_event)
        self.SetAffirmativeId(wx.ID_OK)

    # -----------------------------------------------------------------------

    def _process_event(self, event):
        """Process any kind of events.

        :param event: (wx.Event)

        """
        event_obj = event.GetEventObject()
        event_id = event_obj.GetId()

        if event_id == wx.ID_CANCEL:
            self.SetReturnCode(wx.ID_CANCEL)
            self.Close()

        elif event_id == wx.ID_OK:
            # Save options
            for i, item in enumerate(self.items):
                self.annparam.get_option(i).set_value(item.GetValue())
            self.EndModal(wx.ID_OK)
