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

    ui.phoenix.anz_panels.option.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""

import logging
import wx
import wx.lib.agw.floatspin

from sppas.src.structs.baseoption import sppasOption

from ..windows import sppasFileDialog
from ..windows import sppasScrolledPanel
from ..windows import sppasStaticText
from ..windows import sppasTextCtrl
from ..windows import BitmapTextButton
from ..windows import CheckButton

# ---------------------------------------------------------------------------


class sppasOptionsPanel(sppasScrolledPanel):
    """Create a panel to manage values of a list of sppasOption() instances.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2020  Brigitte Bigi

    """

    def __init__(self, parent, options, name="options_panel"):
        super(sppasOptionsPanel, self).__init__(
            parent=parent,
            style=wx.BORDER_NONE,
            name=name
        )

        # wx objects to fill option values
        self._items = list()
        self.file_buttons = dict()
        self.__apply_settings(self)

        self._create_content(options)

        self.SetMinSize(wx.Size(sppasScrolledPanel.fix_size(320),
                                sppasScrolledPanel.fix_size(180)))
        self.SetupScrolling(scroll_x=True, scroll_y=True)
        self.Layout()

    # ------------------------------------------------------------------------

    def GetItems(self):
        """Return the objects created from the given options.

        :returns: wx objects

        """
        return self._items

    # ------------------------------------------------------------------------
    # Private methods to construct the panel.
    # ------------------------------------------------------------------------

    def _create_content(self, options):
        """Create the main content."""
        sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(sizer)

        for opt in options:

            if opt.get_type() == "bool":
                self.__add_bool(opt.get_text(), value=opt.get_value())

            elif opt.get_type() == "int":
                self.__add_int(opt.get_text(), value=opt.get_value())

            elif opt.get_type() == "float":
                self.__add_float(opt.get_text(), value=opt.get_value())

            elif opt.get_type().startswith("file"):
                self.__add_file(opt.get_text(), opt.get_value(), opt.get_type())

            else:  # if opt.get_type() == "str":
                self.__add_text(opt.get_text(), value=opt.get_value())

    # ------------------------------------------------------------------------

    def __add_bool(self, label, value=True):
        """Add a checkbox to the panel.

        :param label: (str) the description of the value
        :param value: (bool) the current value

        """
        cb = CheckButton(self, label=label)
        cb.SetMinSize(wx.Size(sppasScrolledPanel.fix_size(300),
                              self.get_font_height()*2))
        cb.SetFocusWidth(0)
        cb.SetValue(value)
        self.GetSizer().Add(cb, 0, wx.EXPAND | wx.LEFT | wx.BOTTOM, sppasScrolledPanel.fix_size(4))
        self._items.append(cb)

    # ------------------------------------------------------------------------

    def __add_int(self, label, smin=0, smax=2000, value=1, width=130):
        """Add a spinner to the panel.

        :param label: (str) the description of the value
        :param smin: (int) the minimum value
        :param smax: (int) the maximum value
        :param value: (int) the current value

        """
        st = sppasStaticText(self, label=label)

        sc = wx.SpinCtrl(self, -1, label,
                         wx.Point(30, 20), wx.Size(width, -1))
        sc.SetRange(smin, smax)
        sc.SetValue(value)
        self.__apply_settings(sc)

        self.GetSizer().Add(st, 0, wx.EXPAND | wx.LEFT, sppasScrolledPanel.fix_size(4))
        self.GetSizer().Add(sc, 0, wx.LEFT | wx.BOTTOM, sppasScrolledPanel.fix_size(12))

        self._items.append(sc)

    # ------------------------------------------------------------------------

    def __add_float(self, label, smin=0, smax=2000, incr=0.01, value=1.0, width=130):
        """Add a float spinner to the panel.

        :param label: (str) the description of the value
        :param smin: (float) the minimum value
        :param smax: (float) the maximum value
        :param incr: (float) increment for every evt_floatspin events
        :param value: (float) the current value

        """
        st = sppasStaticText(self, label=label)

        fsc = wx.lib.agw.floatspin.FloatSpin(self, -1, size=(width, -1), increment=incr, digits=3)
        fsc.SetRange(smin, smax)
        fsc.SetValue(value)
        self.__apply_settings(fsc)

        self.GetSizer().Add(st, 0, wx.EXPAND | wx.LEFT, sppasScrolledPanel.fix_size(4))
        self.GetSizer().Add(fsc, 0, wx.LEFT | wx.BOTTOM, sppasScrolledPanel.fix_size(12))

        self._items.append(fsc)

    # ------------------------------------------------------------------------

    def __add_text(self, label, value=""):
        """Add a TextCtrl to the panel.

        :param label: (string) the description of the value
        :param value: (string) the current value

        """
        st = sppasStaticText(self, label=label)

        textctrl = sppasTextCtrl(self, size=(sppasScrolledPanel.fix_size(300), -1))
        textctrl.SetValue(value)

        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(textctrl)

        self.GetSizer().Add(st, 0, wx.EXPAND | wx.LEFT, sppasScrolledPanel.fix_size(4))
        self.GetSizer().Add(sizer, 0, wx.EXPAND | wx.LEFT | wx.BOTTOM, sppasScrolledPanel.fix_size(12))

        self._items.append(textctrl)

    # ------------------------------------------------------------------------

    def __add_file(self, label, value, opt_type):
        """Add a TextCtrl with a filename to the panel.

        :param label: (str) the description of the value
        :param value: (str) the current value

        """
        st = sppasStaticText(self, label=label)

        filetext = sppasTextCtrl(self, size=(sppasScrolledPanel.fix_size(300), -1))
        filetext.SetValue(value)

        filebtn = BitmapTextButton(self, name="folder-add")
        filebtn.SetMinSize(wx.Size(sppasScrolledPanel.fix_size(24),
                                   sppasScrolledPanel.fix_size(24)))
        filebtn.SetSpacing(0)
        filebtn.Bind(wx.EVT_BUTTON, self.__on_select_filename)

        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(filetext, 1, wx.EXPAND)
        sizer.Add(filebtn, 0, wx.LEFT, border=4)

        self.GetSizer().Add(st, 0, wx.EXPAND | wx.LEFT, sppasScrolledPanel.fix_size(4))
        self.GetSizer().Add(sizer, 0, wx.EXPAND | wx.LEFT | wx.BOTTOM, sppasScrolledPanel.fix_size(12))

        self.file_buttons[filebtn] = filetext
        self._items.append(filetext)

    # ------------------------------------------------------------------------

    def __apply_settings(self, wx_object):
        """Set font, background color and foreground color to an object."""
        try:
            settings = wx.GetApp().settings
            wx_object.SetFont(settings.text_font)
            wx_object.SetForegroundColour(settings.fg_color)
            wx_object.SetBackgroundColour(settings.bg_color)
        except:
            pass

    # ------------------------------------------------------------------------

    def __on_select_filename(self, event):
        """Open a dialog to choose a filename or a dirname."""
        dlg = sppasFileDialog(self, style=wx.FC_OPEN | wx.FC_NOSHOWHIDDEN)
        if dlg.ShowModal() == wx.ID_OK:
            filename = dlg.GetPath()
            btn_obj = event.GetEventObject()
            obj = self.file_buttons[btn_obj]
            obj.SetValue(filename)
            obj.SetFocus()
            obj.Refresh()
        dlg.Destroy()

# ----------------------------------------------------------------------------
# Panels to test
# ----------------------------------------------------------------------------


class TestPanel(sppasOptionsPanel):

    def __init__(self, parent):

        # Create a bunch of options to be displayed
        o1 = sppasOption("bool_test1", option_type="bool", option_value=False)
        o1.set_text("Test a bool with False value")

        o2 = sppasOption("bool_test2", option_type="bool", option_value=True)
        o2.set_text("Test a bool with True value")

        o3 = sppasOption("int_test", option_type="int", option_value=5)
        o3.set_text("Test an int with '5' value")

        o4 = sppasOption("float_test", option_type="float", option_value=0.20)
        o4.set_text("Test a float with '0.2' value")

        o5 = sppasOption("text_test", option_type="str", option_value="")
        o5.set_text("Test a text with empty value")

        o6 = sppasOption("file_test", option_type="filename", option_value="")
        o6.set_text("Test a filename selection")

        super(TestPanel, self).__init__(parent, [o1, o2, o3, o4, o5, o6],
                                        name="Test sppasOptionsPanel")
