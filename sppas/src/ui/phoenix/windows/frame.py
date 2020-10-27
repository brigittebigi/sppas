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

import threading
import os
import wx
import time

from sppas.src.config import sg, paths

from ..tools import sppasSwissKnife
from .line import sppasStaticLine
from .basedcwindow import sppasImageDCWindow

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
        self.delta = None
        self.timer1 = None
        self.timer2 = None

        # Fix this frame properties
        self.CenterOnScreen(wx.BOTH)

    # -----------------------------------------------------------------------

    def _init_infos(self):
        """Initialize the main frame.

        Set the title, the icon and the properties of the frame.

        """
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
        try:
            settings = wx.GetApp().settings
            self.SetBackgroundColour(settings.bg_color)
            self.SetForegroundColour(settings.fg_color)
            self.SetFont(settings.text_font)
        except AttributeError:
            self.InheritAttributes()

    # -----------------------------------------------------------------------
    # Fade-in at start-up and Fade-out at close
    # -----------------------------------------------------------------------

    def FadeIn(self, delta=None):
        """Fade-in opacity."""
        if delta is None:
            try:
                delta = wx.GetApp().settings.fade_in_delta
            except AttributeError:
                delta = -5
        self.delta = delta
        self.SetTransparent(self.opacity_in)
        self.timer1 = wx.Timer(self, -1)
        self.timer1.Start(5)
        self.Bind(wx.EVT_TIMER, self.__alpha_cycle_in, self.timer1)

    def DestroyFadeOut(self, delta=None):
        """Destroy with a fade-out opacity."""
        if delta is None:
            try:
                delta = wx.GetApp().settings.fade_out_delta
            except AttributeError:
                delta = -5
        self.delta = int(delta)
        self.timer2 = wx.Timer(self, -1)
        self.timer2.Start(5)
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
        self.opacity_in += self.delta
        if self.opacity_in <= 0:
            self.delta = -self.delta
            self.opacity_in = 0

        if self.opacity_in >= 255:
            self.delta = -self.delta
            self.opacity_in = 255
            self.timer1.Stop()

        self.SetTransparent(self.opacity_in)

    # ---------------------------------------------------------------------------

    def __alpha_cycle_out(self, *args):
        """Fade-out opacity of the dialog."""
        self.opacity_out += self.delta

        if self.opacity_out >= 255:
            self.delta = -self.delta
            self.opacity_out = 255
            self.timer2.Stop()

        if self.opacity_out <= 0:
            self.delta = -self.delta
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
    :copyright:    Copyright (C) 2011-2020  Brigitte Bigi

    """

    def __init__(self, *args, **kw):
        """Create a frame.

        Possible constructors:

            - sppasTopFrame()
            - sppasTopFrame(parent, id=ID_ANY, title="",
                     pos=DefaultPosition,
                     size=DefaultSize, style=DEFAULT_DIALOG_STYLE,
                     name=DialogNameStr)

        """
        super(sppasTopFrame, self).__init__(*args, **kw)
        self._init_infos()

        # To fade-in and fade-out the opacity
        self.opacity_in = 0
        self.opacity_out = 255
        self.delta = None
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
        # Fix minimum frame size
        self.SetMinSize(wx.Size(320, 200))

        # Fix frame name
        self.SetName('{:s}-{:d}'.format(sg.__name__, self.GetId()))

        # icon
        _icon = wx.Icon()
        bmp = sppasSwissKnife.get_bmp_icon("sppas_64", height=64)
        _icon.CopyFromBitmap(bmp)
        self.SetIcon(_icon)

        # colors & font
        try:
            settings = wx.GetApp().settings
            self.SetBackgroundColour(settings.bg_color)
            self.SetForegroundColour(settings.fg_color)
            self.SetFont(settings.text_font)
        except AttributeError:
            self.InheritAttributes()

    # -----------------------------------------------------------------------
    # Fade-in at start-up and Fade-out at close
    # -----------------------------------------------------------------------

    def FadeIn(self, delta=None):
        """Fade-in opacity."""
        if delta is None:
            try:
                delta = wx.GetApp().settings.fade_in_delta
            except AttributeError:
                delta = -5
        self.delta = int(delta)
        self.SetTransparent(self.opacity_in)
        self.timer1 = wx.Timer(self, -1)
        self.timer1.Start(1)
        self.Bind(wx.EVT_TIMER, self.__alpha_cycle_in, self.timer1)

    def DestroyFadeOut(self, delta=None):
        """Destroy with a fade-out opacity."""
        if delta is None:
            try:
                delta = wx.GetApp().settings.fade_out_delta
            except AttributeError:
                delta = -5
        self.delta = int(delta)
        self.timer2 = wx.Timer(self, -1)
        self.timer2.Start(5)   # call the cycle out every 5 milliseconds
        self.Bind(wx.EVT_TIMER, self.__alpha_cycle_out, self.timer2)

    # -----------------------------------------------------------------------

    def SetHeader(self, window):
        """Assign the header window to this dialog.

        :param window: (wx.Window) Any kind of wx.Window, wx.Panel, ...

        """
        window.SetName("header")
        window.SetBackgroundColour(wx.GetApp().settings.header_bg_color)
        window.SetForegroundColour(wx.GetApp().settings.header_fg_color)
        window.SetFont(wx.GetApp().settings.header_text_font)

    # -----------------------------------------------------------------------

    def SetContent(self, window):
        """Assign the content window to this dialog.

        :param window: (wx.Window) Any kind of wx.Window, wx.Panel, ...

        """
        window.SetName("content")
        window.SetBackgroundColour(wx.GetApp().settings.bg_color)
        window.SetForegroundColour(wx.GetApp().settings.fg_color)
        window.SetFont(wx.GetApp().settings.text_font)

    # -----------------------------------------------------------------------

    def SetActions(self, window):
        """Assign the actions window to this dialog.

        :param window: (wx.Window) Any kind of wx.Window, wx.Panel, ...

        """
        window.SetName("actions")
        window.SetBackgroundColour(wx.GetApp().settings.action_bg_color)
        window.SetForegroundColour(wx.GetApp().settings.action_fg_color)
        window.SetFont(wx.GetApp().settings.action_text_font)

    # -----------------------------------------------------------------------

    @property
    def content(self):
        return self.FindWindow("content")

    @property
    def actions(self):
        return self.FindWindow("actions")

    @property
    def header(self):
        return self.FindWindow("header")

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
    # Put the whole content of the dialog in a sizer
    # ---------------------------------------------------------------------------

    def LayoutComponents(self):
        """Create the sizer and layout the components of the dialog."""
        sizer = wx.BoxSizer(wx.VERTICAL)

        # Add header
        header = self.FindWindow("header")
        if header is not None:
            sizer.Add(header, 0, wx.EXPAND, 0)
            sizer.Add(self.HorizLine(self), 0, wx.ALL | wx.EXPAND, 0)

        # Add content
        content = self.FindWindow("content")
        if content is not None:
            sizer.Add(content, 1, wx.EXPAND, 0)
        else:
            sizer.AddSpacer(1)

        # Add action buttons
        actions = self.FindWindow("actions")
        if actions is not None:
            sizer.Add(self.HorizLine(self), 0, wx.ALL | wx.EXPAND, 0)
            # proportion is 0 to ask the sizer to never hide the buttons
            sizer.Add(actions, 0, wx.EXPAND, 0)

        # Since Layout doesn't happen until there is a size event, you will
        # sometimes have to force the issue by calling Layout yourself. For
        # example, if a frame is given its size when it is created, and then
        # you add child windows to it, and then a sizer, and finally Show it,
        # then it may not receive another size event (depending on platform)
        # in order to do the initial layout. Simply calling self.Layout from
        # the end of the frame's __init__ method will usually resolve this.
        self.SetSizer(sizer)
        self.Layout()

    # ---------------------------------------------------------------------------
    # Private
    # ---------------------------------------------------------------------------

    def __alpha_cycle_in(self, *args):
        """Fade-in opacity of the dialog."""
        self.opacity_in += self.delta
        if self.opacity_in <= 0:
            self.delta = -self.delta
            self.opacity_in = 0

        if self.opacity_in >= 255:
            self.delta = -self.delta
            self.opacity_in = 255
            self.timer1.Stop()

        self.SetTransparent(self.opacity_in)

    # ---------------------------------------------------------------------------

    def __alpha_cycle_out(self, *args):
        """Fade-out opacity of the dialog."""
        self.opacity_out += self.delta

        if self.opacity_out >= 255:
            self.delta = -self.delta
            self.opacity_out = 255
            self.timer2.Stop()

        if self.opacity_out <= 0:
            self.delta = -self.delta
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
    # -----------------------------------------------------------------------
    # GUI
    # -----------------------------------------------------------------------

    def UpdateUI(self):
        """Apply settings to all anz_panels and refresh."""
        # apply new (or not) 'wx' values to content.
        p = self.FindWindow("content")
        p.SetBackgroundColour(wx.GetApp().settings.bg_color)
        p.SetForegroundColour(wx.GetApp().settings.fg_color)
        p.SetFont(wx.GetApp().settings.text_font)

        # apply new (or not) 'wx' values to header.
        p = self.FindWindow("header")
        p.SetBackgroundColour(wx.GetApp().settings.header_bg_color)
        p.SetForegroundColour(wx.GetApp().settings.header_fg_color)
        p.SetFont(wx.GetApp().settings.header_text_font)

        # apply new (or not) 'wx' values to actions.
        p = self.FindWindow("actions")
        p.SetBackgroundColour(wx.GetApp().settings.action_bg_color)
        p.SetForegroundColour(wx.GetApp().settings.action_fg_color)
        p.SetFont(wx.GetApp().settings.action_text_font)

        self.Refresh()

# ----------------------------------------------------------------------------


class sppasImageFrame(wx.TopLevelWindow):
    """A frame with only an image as background.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2020  Brigitte Bigi

    """

    def __init__(self, *args, **kw):
        """Create a frame.

        Possible constructors:

            - sppasImageFrame()
            - sppasImageFrame(parent, id=ID_ANY, title="",
                     image=filename,
                     pos=DefaultPosition,
                     size=DefaultSize, style=DEFAULT_DIALOG_STYLE,
                     name=DialogNameStr)

        """
        img_name = None
        if "image" in kw:
            img_name = kw["image"]
            kw.pop("image")

        super(sppasImageFrame, self).__init__(*args, **kw)
        self._init_infos()
        self._create_content()
        self.SetBackgroundImage(img_name)

        # Fix this frame properties
        self.CenterOnScreen(wx.BOTH)
        self.SetAutoLayout(True)

    # -----------------------------------------------------------------------

    def _init_infos(self):
        """Initialize the main frame.

        Set the title, the icon and the properties of the frame.

        """
        # Fix minimum frame size
        self.SetMinSize(wx.Size(320, 200))

        # Fix frame name
        self.SetName('{:s}-{:d}'.format(sg.__name__, self.GetId()))

        # icon
        _icon = wx.Icon()
        bmp = sppasSwissKnife.get_bmp_icon("sppas_64", height=64)
        _icon.CopyFromBitmap(bmp)
        self.SetIcon(_icon)

        # colors & font
        try:
            settings = wx.GetApp().settings
            self.SetBackgroundColour(settings.bg_color)
            self.SetForegroundColour(settings.fg_color)
            self.SetFont(settings.text_font)
        except AttributeError:
            self.InheritAttributes()

    # -----------------------------------------------------------------------

    def SetBackgroundImage(self, filename=None):
        """Set the image filename, but do not refresh.

        :param filename: (str)

        """
        self.FindWindow("img_window").SetBackgroundImage(filename)

    # -----------------------------------------------------------------------

    def SetBackgroundImageArray(self, image):
        """Set the image, but do not refresh.

        :param image: (sppasImage, np.array)

        """
        self.FindWindow("img_window").SetBackgroundImageArray(image)

    # -----------------------------------------------------------------------

    def _create_content(self):
        wi = sppasImageDCWindow(self, name="img_window")
        wi.SetBorderWidth(0)

        sizer = wx.BoxSizer()
        sizer.Add(wi, 1, wx.EXPAND)
        self.SetSizer(sizer)

# ----------------------------------------------------------------------------
# Panels to test
# ----------------------------------------------------------------------------


class TestPanel(wx.Panel):

    img1 = os.path.join(paths.etc, "images", "trbg1.png")
    img2 = os.path.join(paths.etc, "images", "trbg2.png")

    def __init__(self, parent):
        super(TestPanel, self).__init__(
            parent,
            name="sppasImageFrame")

        btn1 = wx.Button(self, label="Open frame", pos=(10, 10), size=(96, 64))
        btn2 = wx.Button(self, label="Close frame", pos=(120, 10), size=(96, 64))
        self._img_frame = sppasImageFrame(
            parent=self,   # if self is destroyed, the frame will be too
            title="Frame with a background image",
            image=TestPanel.img1,
            style=wx.CAPTION | wx.RESIZE_BORDER | wx.MAXIMIZE_BOX | wx.MINIMIZE_BOX | wx.DIALOG_NO_PARENT)
        self._img_frame.SetBackgroundColour(wx.WHITE)

        self.Bind(wx.EVT_BUTTON, self._on_open_imgframe, btn1)
        self.Bind(wx.EVT_BUTTON, self._on_close_imgframe, btn2)

        self.i = 0
        self.timerObject = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.change_bitmap, self.timerObject)

    # -----------------------------------------------------------------------

    def _on_open_imgframe(self, event):
        self._img_frame.Show()
        self.timerObject.Start(500)

    # -----------------------------------------------------------------------

    def _on_close_imgframe(self, event):
        if self._img_frame is not None:
            self._img_frame.Hide()
            self.i = 0
            self.timerObject.Stop()

    # -----------------------------------------------------------------------

    def change_bitmap(self, evt):
        if self.i % 2 == 0:
            self._img_frame.SetBackgroundImage("/Users/bigi/Projects/sppas/sppas/etc/images/bg1.png")
        else:
            self._img_frame.SetBackgroundImage("/Users/bigi/Projects/sppas/sppas/etc/images/bg2.png")
        self.i += 1
        self._img_frame.Refresh()
