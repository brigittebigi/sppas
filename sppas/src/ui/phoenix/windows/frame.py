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

    src.ui.phoenix.windows.frame.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""

import wx

from sppas.src.config import sg
from sppas.src.config import ui_translation

from ..tools import sppasSwissKnife
from . import sppasBitmapTextButton
from . import sppasStaticBitmap
from . import sppasStaticLine
from . import sppasPanel

# ----------------------------------------------------------------------------


class sppasFrame(wx.Frame):
    """Base class for frames in SPPAS.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2019  Brigitte Bigi

    """

    def __init__(self, *args, **kw):
        """Create a frame.

        Possible constructors:

            - sppasFrame()
            - sppasFrame(parent, id=ID_ANY, title="", pos=DefaultPosition,
                     size=DefaultSize, style=DEFAULT_DIALOG_STYLE,
                     name=DialogNameStr)

        """
        super(sppasFrame, self).__init__(*args, **kw)
        self._init_infos()
        self.SetAutoLayout(True)

        # To fade-in and fade-out the opacity
        self.opacity_in = 0
        self.opacity_out = 255
        self.deltaN = -10
        self.timer1 = None
        self.timer2 = None

        # Fix this frame properties
        self.CenterOnScreen(wx.BOTH)
        # self.FadeIn(deltaN=-4)

    # -----------------------------------------------------------------------

    def _init_infos(self):
        """Initialize the main frame.

        Set the title, the icon and the properties of the frame.

        """
        settings = wx.GetApp().settings

        # Fix minimum frame size
        self.SetMinSize(wx.Size(320, 200))

        # Fix frame name
        self.SetName('{:s}-{:d}'.format(sg.__name__, self.GetId()))

        # icon
        _icon = wx.Icon()
        bmp = sppasSwissKnife.get_bmp_icon("sppas_32", height=64)
        _icon.CopyFromBitmap(bmp)
        self.SetIcon(_icon)

        # colors & font
        self.SetBackgroundColour(wx.GetApp().settings.bg_color)
        self.SetForegroundColour(wx.GetApp().settings.fg_color)
        self.SetFont(wx.GetApp().settings.text_font)

    # -----------------------------------------------------------------------
    # Fade-in at start-up and Fade-out at close
    # -----------------------------------------------------------------------

    def FadeIn(self, deltaN=-10):
        """Fade-in opacity."""
        self.deltaN = int(deltaN)
        self.SetTransparent(self.opacity_in)
        self.timer1 = wx.Timer(self, -1)
        self.timer1.Start(1)
        self.Bind(wx.EVT_TIMER, self.__alpha_cycle_in, self.timer1)

    def DestroyFadeOut(self, deltaN=-10):
        """Destroy with a fade-out opacity."""
        self.deltaN = int(deltaN)
        self.timer2 = wx.Timer(self, -1)
        self.timer2.Start(1)
        self.Bind(wx.EVT_TIMER, self.__alpha_cycle_out, self.timer2)

    # -----------------------------------------------------------------------

    def SetContent(self, window):
        """Assign the content window to this dialog.

        :param window: (wx.Window) Any kind of wx.Window, wx.Panel, ...

        """
        window.SetName("content")
        window.SetBackgroundColour(wx.GetApp().settings.bg_color)
        window.SetForegroundColour(wx.GetApp().settings.fg_color)
        window.SetFont(wx.GetApp().settings.text_font)

    # ------------------------------------------------------------------------

    def VertLine(self, parent, depth=1):
        """Return a vertical static line."""
        line = sppasStaticLine(parent, orient=wx.LI_VERTICAL)
        line.SetMinSize(wx.Size(depth, -1))
        line.SetSize(wx.Size(depth, -1))
        line.SetPenStyle(wx.PENSTYLE_SOLID)
        line.SetDepth(depth)
        return line

    # ------------------------------------------------------------------------

    def HorizLine(self, parent, depth=3):
        """Return an horizontal static line."""
        line = sppasStaticLine(parent, orient=wx.LI_HORIZONTAL)
        line.SetMinSize(wx.Size(-1, depth))
        line.SetSize(wx.Size(-1, depth))
        line.SetPenStyle(wx.PENSTYLE_SOLID)
        line.SetDepth(depth)
        return line

    # ---------------------------------------------------------------------------
    # Private
    # ---------------------------------------------------------------------------

    def __alpha_cycle_in(self, *args):
        """Fade-in opacity of the dialog."""
        self.opacity_in += self.deltaN
        if self.opacity_in <= 0:
            self.deltaN = -self.deltaN
            self.opacity_in = 0

        if self.opacity_in >= 255:
            self.deltaN = -self.deltaN
            self.opacity_in = 255
            self.timer1.Stop()

        self.SetTransparent(self.opacity_in)

    # ---------------------------------------------------------------------------

    def __alpha_cycle_out(self, *args):
        """Fade-out opacity of the dialog."""
        self.opacity_out += self.deltaN

        if self.opacity_out >= 255:
            self.deltaN = -self.deltaN
            self.opacity_out = 255
            self.timer2.Stop()

        if self.opacity_out <= 0:
            self.deltaN = -self.deltaN
            self.opacity_out = 0
            wx.CallAfter(self.Destroy)

        self.SetTransparent(self.opacity_out)

    # -----------------------------------------------------------------------

    @staticmethod
    def fix_size(value):
        """Return a proportional size value.

        :param value: (int)
        :returns: (int)

        """
        try:
            obj_size = int(float(value) * wx.GetApp().settings.size_coeff)
        except AttributeError:
            obj_size = int(value)
        return obj_size


# ----------------------------------------------------------------------------


class sppasTopFrame(wx.TopLevelWindow):
    """Base class for frames in SPPAS.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2019  Brigitte Bigi

    """

    def __init__(self, *args, **kw):
        """Create a frame.

        Possible constructors:

            - sppasFrame()
            - sppasFrame(parent, id=ID_ANY, title="", pos=DefaultPosition,
                     size=DefaultSize, style=DEFAULT_DIALOG_STYLE,
                     name=DialogNameStr)

        """
        super(sppasTopFrame, self).__init__(*args, **kw)
        self._init_infos()

        # To fade-in and fade-out the opacity
        self.opacity_in = 0
        self.opacity_out = 255
        self.deltaN = -10
        self.timer1 = None
        self.timer2 = None

        # Fix this frame properties
        self.CenterOnScreen(wx.BOTH)
        self.SetAutoLayout(True)

    # -----------------------------------------------------------------------

    def _init_infos(self):
        """Initialize the main frame.

        Set the title, the icon and the properties of the frame.

        """
        settings = wx.GetApp().settings

        # Fix minimum frame size
        self.SetMinSize(wx.Size(320, 200))

        # Fix frame name
        self.SetName('{:s}-{:d}'.format(sg.__name__, self.GetId()))

        # icon
        _icon = wx.Icon()
        bmp = sppasSwissKnife.get_bmp_icon("sppas_32", height=64)
        _icon.CopyFromBitmap(bmp)
        self.SetIcon(_icon)

        # colors & font
        self.SetBackgroundColour(wx.GetApp().settings.bg_color)
        self.SetForegroundColour(wx.GetApp().settings.fg_color)
        self.SetFont(wx.GetApp().settings.text_font)

    # -----------------------------------------------------------------------
    # Fade-in at start-up and Fade-out at close
    # -----------------------------------------------------------------------

    def FadeIn(self, deltaN=-10):
        """Fade-in opacity."""
        self.deltaN = int(deltaN)
        self.SetTransparent(self.opacity_in)
        self.timer1 = wx.Timer(self, -1)
        self.timer1.Start(1)
        self.Bind(wx.EVT_TIMER, self.__alpha_cycle_in, self.timer1)

    def DestroyFadeOut(self, deltaN=-10):
        """Destroy with a fade-out opacity."""
        self.deltaN = int(deltaN)
        self.timer2 = wx.Timer(self, -1)
        self.timer2.Start(1)
        self.Bind(wx.EVT_TIMER, self.__alpha_cycle_out, self.timer2)

    # -----------------------------------------------------------------------

    def SetContent(self, window):
        """Assign the content window to this dialog.

        :param window: (wx.Window) Any kind of wx.Window, wx.Panel, ...

        """
        window.SetName("content")
        window.SetBackgroundColour(wx.GetApp().settings.bg_color)
        window.SetForegroundColour(wx.GetApp().settings.fg_color)
        window.SetFont(wx.GetApp().settings.text_font)

    # ------------------------------------------------------------------------

    def VertLine(self, parent, depth=1):
        """Return a vertical static line."""
        line = sppasStaticLine(parent, orient=wx.LI_VERTICAL)
        line.SetMinSize(wx.Size(depth, -1))
        line.SetSize(wx.Size(depth, -1))
        line.SetPenStyle(wx.PENSTYLE_SOLID)
        line.SetDepth(depth)
        return line

    # ------------------------------------------------------------------------

    def HorizLine(self, parent, depth=3):
        """Return an horizontal static line."""
        line = sppasStaticLine(parent, orient=wx.LI_HORIZONTAL)
        line.SetMinSize(wx.Size(-1, depth))
        line.SetSize(wx.Size(-1, depth))
        line.SetPenStyle(wx.PENSTYLE_SOLID)
        line.SetDepth(depth)
        return line

    # ---------------------------------------------------------------------------
    # Private
    # ---------------------------------------------------------------------------

    def __alpha_cycle_in(self, *args):
        """Fade-in opacity of the dialog."""
        self.opacity_in += self.deltaN
        if self.opacity_in <= 0:
            self.deltaN = -self.deltaN
            self.opacity_in = 0

        if self.opacity_in >= 255:
            self.deltaN = -self.deltaN
            self.opacity_in = 255
            self.timer1.Stop()

        self.SetTransparent(self.opacity_in)

    # ---------------------------------------------------------------------------

    def __alpha_cycle_out(self, *args):
        """Fade-out opacity of the dialog."""
        self.opacity_out += self.deltaN

        if self.opacity_out >= 255:
            self.deltaN = -self.deltaN
            self.opacity_out = 255
            self.timer2.Stop()

        if self.opacity_out <= 0:
            self.deltaN = -self.deltaN
            self.opacity_out = 0
            wx.CallAfter(self.Destroy)

        self.SetTransparent(self.opacity_out)

    # -----------------------------------------------------------------------

    @staticmethod
    def fix_size(value):
        """Return a proportional size value.

        :param value: (int)
        :returns: (int)

        """
        try:
            obj_size = int(float(value) * wx.GetApp().settings.size_coeff)
        except AttributeError:
            obj_size = int(value)
        return obj_size
