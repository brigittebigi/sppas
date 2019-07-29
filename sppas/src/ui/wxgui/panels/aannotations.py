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

    src.wxgui.panels.aannotations.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""
import logging
import wx
import wx.lib.newevent
import wx.lib.scrolledpanel

from sppas import msg
from sppas import u

from sppas.src.annotations.param import sppasParam
from sppas.src.ui.logs import sppasLogFile

from sppas.src.ui.wxgui.cutils.imageutils import spBitmap
from sppas.src.ui.wxgui.cutils.ctrlutils import CreateGenButton

from sppas.src.ui.wxgui.views.annotationoptions import spAnnotationConfig
from sppas.src.ui.wxgui.process.annotateprocess import AnnotateProcess

from sppas.src.ui.wxgui.sp_consts import MIN_PANEL_W
from sppas.src.ui.wxgui.sp_consts import MIN_PANEL_H

from sppas.src.ui.wxgui.sp_icons import LINK_ICON
from sppas.src.ui.wxgui.sp_icons import UNLINK_ICON
from sppas.src.ui.wxgui.sp_icons import ANNOTATE_ICON
import sppas.src.ui.wxgui.ui.CustomCheckBox as CCB
from sppas.src.ui.wxgui.dialogs.msgdialogs import ShowInformation

# -----------------------------------------------------------------------


def _(message):
    return u(msg(message, "ui"))

# ----------------------------------------------------------------------------
# Constants
# ----------------------------------------------------------------------------


LANG_NONE = "---"

RUN_ID = wx.NewId()
LINK_ID = wx.NewId()

# ----------------------------------------------------------------------------
# Events
# ----------------------------------------------------------------------------

# event launched when a step is checked or unchecked
stepEvent, EVT_STEP_EVENT = wx.lib.newevent.NewEvent()

# event launched when a language is chosen
langEvent, EVT_LANG_EVENT = wx.lib.newevent.NewEvent()

# ----------------------------------------------------------------------------


class sppasStepPanel(wx.Panel):
    """Panel with an annotation and the language choice.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2017  Brigitte Bigi

    Panel containing a checkbox and eventually a choice of languages for a
    given annotation.

    """
    def __init__(self, parent, parameters, preferences, index):

        wx.Panel.__init__(self, parent, size=wx.DefaultSize, style=wx.NO_BORDER)
        self.SetBackgroundColour(preferences.GetValue('M_BGD_COLOUR'))

        # Members
        self.parameters = parameters
        self.step_idx = index
        self._prefsIO = preferences
        choicelist = self.parameters.get_langlist(index)
        self.choice = None
        self.opened_frames = {}
        self.ID_FRAME_ANNOTATION_CFG = wx.NewId()

        # create the checkbox allowing to select or deselect the annotation
        annotation_name = self.parameters.get_step_name(index)
        self.checkbox = CCB.CustomCheckBox(self, -1, annotation_name, CCB_TYPE="activecheck")
        self.__apply_preferences(self.checkbox)
        self.checkbox.SetSpacing(self._prefsIO.GetValue('F_SPACING'))
        self.checkbox.Bind(wx.EVT_CHECKBOX, self.on_check_changed)

        # choice of the language
        self.choice = None
        # if there are different languages available, add a choice to the panel
        if len(choicelist) > 0:
            choicelist.append(LANG_NONE)
            self.choice = wx.ComboBox(self, -1, choices=sorted(choicelist))
            self.__apply_preferences(self.choice)
            self.choice.SetSelection(self.choice.GetItems().index(LANG_NONE))
            self.choice.SetMinSize((80, -1))
            self.choice.Bind(wx.EVT_COMBOBOX, self.on_lang_changed)

        # description of the annotation
        d = self.parameters.get_step_descr(index)
        self.text = wx.StaticText(self, wx.ID_ANY, d)
        self.__apply_preferences(self.text)
        self.text.Wrap(300)

        # link to configure the annotation
        self.link = wx.StaticText(self, -1, _("Configure") + "...")
        self.__apply_preferences(self.link)
        self.link.SetForegroundColour(wx.Colour(80, 100, 220))
        self.link.Bind(wx.EVT_LEFT_UP, self.on_click)

        # organize all tools

        csizer = wx.BoxSizer(wx.VERTICAL)
        csizer.Add(self.checkbox, proportion=0, flag=wx.LEFT | wx.RIGHT | wx.BOTTOM, border=4)
        csizer.Add(self.link, proportion=0, flag=wx.LEFT, border=4)

        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(csizer, proportion=2, flag=wx.ALIGN_CENTER_VERTICAL, border=0)
        sizer.Add(self.text, proportion=4, flag=wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, border=4)
        if self.choice is not None:
            sizer.Add(self.choice, proportion=0, flag=wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, border=4)

        self.SetSizerAndFit(sizer)
        self.SetAutoLayout(True)

        self.parameters.set_lang(None, self.step_idx)

    # -----------------------------------------------------------------------

    def on_check_changed(self, evt):
        if hasattr(evt, 'IsChecked'):
            checked = evt.IsChecked()
        else:
            checked = True
        event = stepEvent(step_idx=self.step_idx, checked=checked)
        wx.PostEvent(self, event)

    # -----------------------------------------------------------------------

    def on_click(self, event):
        self.on_check_changed(event)
        self.checkbox.SetValue(True)
        annotId = self.step_idx
        frameId = self.ID_FRAME_ANNOTATION_CFG + annotId
        if frameId not in self.opened_frames.keys():
            dlg = spAnnotationConfig(self, self._prefsIO, self.parameters.annotations[annotId], annotId)
            dlg.Show()
            self.opened_frames[frameId] = dlg
        else:
            self.opened_frames[frameId].SetFocus()
            self.opened_frames[frameId].Raise()

    # -----------------------------------------------------------------------

    def on_lang_changed(self, event):
        event = langEvent(step_idx=self.step_idx, lang=self.choice.GetValue())
        wx.PostEvent(self, event)

    # -----------------------------------------------------------------------

    def set_lang(self, lang):
        logging.debug('set lang for annotation {:s}'.format(
            self.parameters.get_step_name(self.step_idx)))
        if self.choice is not None:
            if lang in self.choice.GetItems():
                logging.debug(' - choice fixed lang={:s}'.format(lang))
                self.choice.SetSelection(self.choice.GetItems().index(lang))
                self.parameters.set_lang(lang, self.step_idx)

            else:
                # empty the selection
                self.choice.SetSelection(self.choice.GetItems().index(LANG_NONE))
                self.parameters.set_lang(None, self.step_idx)
                logging.debug(' - choice fixed lang to None')

        else:
            logging.debug(' - no choice available. lang is None')
            self.parameters.set_lang(None, self.step_idx)

    # -----------------------------------------------------------------------

    def SetPrefs(self, prefs):
        """Fix new preferences."""
        self._prefsIO = prefs

        self.__apply_preferences(self)
        self.__apply_preferences(self.checkbox)
        self.__apply_preferences(self.text)
        if self.choice:
            self.__apply_preferences(self.choice)
            self.choice.Refresh()

        self.Layout()
        self.Refresh()

    # -----------------------------------------------------------------------

    def __apply_preferences(self, wx_object):
        """Set font, background color and foreground color to an object."""

        wx_object.SetFont(self._prefsIO.GetValue('M_FONT'))
        wx_object.SetForegroundColour(self._prefsIO.GetValue('M_FG_COLOUR'))
        wx_object.SetBackgroundColour(self._prefsIO.GetValue('M_BGD_COLOUR'))

# ----------------------------------------------------------------------------


class AnnotationsPanel(wx.lib.scrolledpanel.ScrolledPanel):
    """
    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2017  Brigitte Bigi
    :summary:      Panel allowing to select annotations and languages.

    """
    def __init__(self, parent, preferences):
        """Constructor.

        :param parent:
        :param preferences:

        """
        wx.lib.scrolledpanel.ScrolledPanel.__init__(self, parent, -1, size=wx.DefaultSize, style=wx.NO_BORDER)
        self.SetBackgroundColour(preferences.GetValue('M_BG_COLOUR'))

        # Members
        self.activated = []
        self.step_panels = []
        self.linked = False
        self.parameters = sppasParam()
        self._prefsIO = preferences
        self.parameters.set_output_format(self._prefsIO.GetValue('M_OUTPUT_EXT'))

        _contentbox = self.__create_content()

        # Button to annotate
        runBmp = spBitmap(ANNOTATE_ICON,
                          self._prefsIO.GetValue('M_BUTTON_ICONSIZE'),
                          self._prefsIO.GetValue('M_ICON_THEME'))
        self._brun = CreateGenButton(self, RUN_ID, runBmp,
                                     text="  "+_("Perform annotations") + "  ",
                                     tooltip=_("Automatically annotate selected files"),
                                     colour=wx.Colour(220, 100, 80),
                                     font=self._prefsIO.GetValue('M_FONT'))

        _vbox = wx.BoxSizer(wx.VERTICAL)
        _vbox.Add(_contentbox, proportion=1, flag=wx.EXPAND | wx.ALL, border=0)
        _vbox.Add(self._brun,
                  proportion=0,
                  flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_CENTER_HORIZONTAL,
                  border=20)
        self.Bind(wx.EVT_BUTTON, self.on_sppas_run, self._brun, RUN_ID)
        self.SetSizer(_vbox)
        self.SetupScrolling(scroll_x=True, scroll_y=True)
        self.SetMinSize(wx.Size(MIN_PANEL_W, MIN_PANEL_H))

        self.log_report = sppasLogFile()

    # -----------------------------------------------------------------------

    def __create_content(self):
        """Annotation and language choices."""

        self.steplist_panel = wx.Panel(self)
        self.steplist_panel.SetBackgroundColour(self._prefsIO.GetValue('M_BG_COLOUR'))
        sbox = wx.BoxSizer(wx.VERTICAL)
        for i in range(self.parameters.get_step_numbers()):
            a = self.parameters.get_step(i)
            if "STANDALONE" in a.get_types():
                p = sppasStepPanel(self.steplist_panel, self.parameters, self._prefsIO, i)
                p.Bind(EVT_STEP_EVENT, self.on_check_changed)
                p.Bind(EVT_LANG_EVENT, self.on_lang_changed)
                self.step_panels.append(p)
                self.activated.append(False)
                sbox.Add(p, 1, wx.EXPAND | wx.ALL, border=4)
        self.steplist_panel.SetSizer(sbox)

        lnk_bmp = spBitmap(LINK_ICON, theme=self._prefsIO.GetValue('M_ICON_THEME'))
        self.link_btn = CreateGenButton(self, LINK_ID, lnk_bmp,
                                        tooltip="Link/Unlink language selection.",
                                        colour=self._prefsIO.GetValue('M_BG_COLOUR'),
                                        font=self._prefsIO.GetValue('M_FONT'))
        self.Bind(wx.EVT_BUTTON, self.on_link, self.link_btn, LINK_ID)
        self.on_link(None)

        _box = wx.BoxSizer(wx.HORIZONTAL)
        _box.Add(self.steplist_panel, 1, wx.EXPAND | wx.TOP, 4)
        _box.Add(self.link_btn, 0, wx.RIGHT | wx.EXPAND, 4)
        return _box

    def on_link(self, evt):
        self.linked = not self.linked
        if self.linked:
            b = spBitmap(LINK_ICON, size=24, theme=self._prefsIO.GetValue('M_ICON_THEME'))
        else:
            b = spBitmap(UNLINK_ICON, size=24, theme=self._prefsIO.GetValue('M_ICON_THEME'))
        self.link_btn.SetBitmapLabel(b)

    def on_check_changed(self, evt):
        index = evt.step_idx
        self.activated[index] = evt.checked

    def on_lang_changed(self, evt):
        if evt.lang == LANG_NONE:
            l = None
        else:
            l = evt.lang

        if self.linked:
            for sp in self.step_panels:
                sp.set_lang(l)
        else:
            self.parameters.set_lang(l, evt.step_idx)

    # -----------------------------------------------------------------------

    def on_sppas_run(self, evt):
        """ Execute the automatic annotations. """
        # The procedure outcome report file.
        self.parameters.set_report_filename(self.log_report.get_filename())
        self.log_report.increment()

        # The list of files and folders selected by the user
        file_list = self.GetTopLevelParent().GetAudioSelection()
        file_list.extend(self.GetTopLevelParent().GetTrsSelection())

        # The annotation
        annprocess = AnnotateProcess(self._prefsIO)
        message = annprocess.Run(self.GetParent(), file_list, self.activated, self.parameters)
        if message:
            ShowInformation(None, self._prefsIO, message)

    # -----------------------------------------------------------------------

    def SetPrefs(self, prefs):
        """
        Fix new preferences.
        """
        self._prefsIO = prefs
        self.SetBackgroundColour(self._prefsIO.GetValue('M_BG_COLOUR'))
        self.SetForegroundColour(self._prefsIO.GetValue('M_FG_COLOUR'))
        self.SetFont(self._prefsIO.GetValue('M_FONT'))

        self._brun.SetFont(self._prefsIO.GetValue('M_FONT'))
        self.link_btn.SetBackgroundColour(self._prefsIO.GetValue('M_BG_COLOUR'))

        self.steplist_panel.SetBackgroundColour(self._prefsIO.GetValue('M_BG_COLOUR'))
        for sp in self.step_panels:
            sp.SetPrefs(prefs)

        self.parameters.set_output_format(self._prefsIO.GetValue('M_OUTPUT_EXT'))
