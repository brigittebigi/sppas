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

    src.ui.phoenix.windows.button.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Description
    ===========

    This module implements various forms of generic buttons, meaning that
    they are not built on native controls but are self-drawn.

    They act like normal buttons.


    Sample usage:
    ============

        import wx
        import buttons

        class appFrame(wx.Frame):
            def __init__(self, parent, title):

                wx.Frame.__init__(self, parent, wx.ID_ANY, title, size=(400, 300))
                panel = wx.Panel(self)
                btn = buttons.BaseButton(panel, -1, pos=(50, 50), size=(128, 32))

        app = wx.App()
        frame = appFrame(None, 'Button Test')
        frame.Show()
        app.MainLoop()

"""

import random
import wx
import wx.lib.scrolledpanel as sc
import wx.lib.newevent
from wx.lib.buttons import GenBitmapTextButton, GenButton, GenBitmapButton

from ..tools import sppasSwissKnife
from .image import ColorizeImage
from .basedraw import sppasBaseWindow
from .basedraw import WindowState

# ---------------------------------------------------------------------------

DEFAULT_STYLE = wx.BORDER_NONE | wx.TAB_TRAVERSAL | wx.WANTS_CHARS

# ---------------------------------------------------------------------------


class sppasTextButton(GenButton):
    """Create a simple text button. Inherited from the wx.Button.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2018  Brigitte Bigi

    """
    def __init__(self, parent, label, name):
        super(sppasTextButton, self).__init__(
           parent,
           wx.ID_ANY,
           label,
           style=DEFAULT_STYLE,
           name=name)

        self.SetInitialSize()
        self.Enable(True)
        self.SetBezelWidth(0)
        self.SetUseFocusIndicator(False)

# ---------------------------------------------------------------------------


class sppasBitmapTextButton(GenBitmapTextButton):
    """Create a simple text button.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2018  Brigitte Bigi

    Create a button with bitmap and text. A tooltip can optionally be added.

    >>> button = sppasBitmapTextButton(None, "Exit", "exit")
    >>> button.SetToolTipString("Quit the application")

    """

    def __init__(self, parent, label, name, style=DEFAULT_STYLE):
        btn_height = int(parent.GetSize()[1])
        super(sppasBitmapTextButton, self).__init__(
            parent,
            id=wx.NewId(),
            bitmap=sppasSwissKnife.get_bmp_icon(name, height=btn_height),
            label=" "+label+" ",
            style=style,
            name=name
        )

        self.SetInitialSize()
        self.Enable(True)
        self.SetBezelWidth(0)
        self.SetUseFocusIndicator(False)

    # -----------------------------------------------------------------------

    def SetForegroundColour(self, colour):
        """Override. Apply fg colour to both the image and the text.

        :param colour: (wx.Colour)

        """
        current = self.GetForegroundColour()
        try:
            bmp = self.GetBitmapLabel()
            img = bmp.ConvertToImage()
            ColorizeImage(img, current, colour)
            self.SetBitmapLabel(wx.Bitmap(img))
        except:
            wx.LogDebug('SetForegroundColour not applied to image'
                        'for button {:s}'.format(self.GetName()))

        GenBitmapTextButton.SetForegroundColour(self, colour)

# ---------------------------------------------------------------------------


class sppasBitmapButton(GenBitmapButton):
    """Create a simple bitmap button.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2018  Brigitte Bigi

    Create a button with bitmap. A tooltip can optionally be added.

    >>> button = sppasBitmapButton(None, "exit")
    >>> button.SetToolTipString("Quit the application")

    """

    def __init__(self, parent, name, style=DEFAULT_STYLE, height=None):

        if height is None:
            height = int(parent.GetSize()[1])
        super(sppasBitmapButton, self).__init__(
            parent,
            id=wx.NewId(),
            bitmap=sppasSwissKnife.get_bmp_icon(name, height=height),
            style=style,
            name=name
        )

        self.SetInitialSize()
        self.Enable(True)
        self.SetBezelWidth(0)
        self.SetUseFocusIndicator(False)

    # -----------------------------------------------------------------------

    def SetForegroundColour(self, colour):
        """Override. Apply fg colour to the image.

        :param colour: (wx.Colour)

        """
        try:
            bmp = self.GetBitmapLabel()
            img = bmp.ConvertToImage()
            current = self.GetForegroundColour()
            ColorizeImage(img, current, colour)
            self.SetBitmapLabel(wx.Bitmap(img))
        except:
            wx.LogDebug('SetForegroundColour not applied to image'
                        'for button {:s}'.format(self.GetName()))

        GenBitmapButton.SetForegroundColour(self, colour)

# ---------------------------------------------------------------------------
# Custom buttons
# ---------------------------------------------------------------------------


class ButtonEvent(wx.PyCommandEvent):
    """Base class for an event sent when the button is activated."""

    def __init__(self, event_type, event_id):
        """Default class constructor.

        :param event_type: the event type;
        :param event_id: the event identifier.

        """
        super(ButtonEvent, self).__init__(event_type, event_id)
        self.__button = None

    # ------------------------------------------------------------------------

    def SetButtonObj(self, btn):
        """Set the event object for the event.

        :param btn: the button object

        """
        self.__button = btn

    # ------------------------------------------------------------------------

    def GetButtonObj(self):
        """Return the object associated with this event."""
        return self.__button

    # -----------------------------------------------------------------------

    Button = property(GetButtonObj, SetButtonObj)


# ---------------------------------------------------------------------------


class ToggleButtonEvent(ButtonEvent):
    """Base class for an event sent when the toggle button is activated."""

    def __init__(self, event_type, event_id):
        """Default class constructor.

        :param event_type: the event type;
        :param event_id: the event identifier.

        """
        super(ToggleButtonEvent, self).__init__(event_type, event_id)
        self.__isdown = False

    # -----------------------------------------------------------------------

    def SetIsDown(self, is_down):
        """Set the button toggle status as 'down' or 'up'.

        :param is_down: (bool) True if the button is clicked, False otherwise.

        """
        self.__isdown = bool(is_down)

    # -----------------------------------------------------------------------

    def GetIsDown(self):
        """Return the button toggle status as True if the button is down.

        :returns: (bool)

        """
        return self.__isdown

# ---------------------------------------------------------------------------


class BaseButton(sppasBaseWindow):
    """BaseButton is a custom type of window to represent a button.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2020  Brigitte Bigi

    """

    def __init__(self, parent,
                 id=wx.ID_ANY,
                 pos=wx.DefaultPosition,
                 size=wx.DefaultSize,
                 name=wx.ButtonNameStr):
        """Default class constructor.

        :param parent: (wx.Window) parent window. Must not be ``None``;
        :param id: (int) window identifier. A value of -1 indicates a default value;
        :param pos: the control position. A value of (-1, -1) indicates a default
         position, chosen by either the windowing system or wxPython, depending on
         platform;
        :param size: the control size. A value of (-1, -1) indicates a default size,
         chosen by either the windowing system or wxPython, depending on platform;
        :param name: (str) Name of the button.

        """
        super(BaseButton, self).__init__(
            parent, id, pos, size,
            style=wx.BORDER_NONE | wx.TRANSPARENT_WINDOW | wx.TAB_TRAVERSAL | wx.WANTS_CHARS | wx.FULL_REPAINT_ON_RESIZE,
            name=name)

        # By default, our buttons don't have borders
        self._vert_border_width = 0
        self._horiz_border_width = 0

        self._min_width = 12
        self._min_height = 12

        # Setup Initial Size
        self.SetInitialSize(size)

    # -----------------------------------------------------------------------

    def Notify(self):
        """Sends a wx.EVT_BUTTON event to the listener (if any)."""
        evt = ButtonEvent(wx.wxEVT_COMMAND_BUTTON_CLICKED, self.GetId())
        evt.SetButtonObj(self)
        evt.SetEventObject(self)
        self.GetEventHandler().ProcessEvent(evt)

# ---------------------------------------------------------------------------


class BitmapTextButton(BaseButton):

    def __init__(self, parent,
                 id=wx.ID_ANY,
                 label=None,
                 pos=wx.DefaultPosition,
                 size=wx.DefaultSize,
                 name=wx.ButtonNameStr):
        """Default class constructor.

        :param parent: the parent (required);
        :param id: window identifier.
        :param label: label text of the button (None for a BitmapButton);
        :param pos: the position;
        :param size: the size;
        :param name: the name of the bitmap.

        By default, the name of the button is the name of its bitmap.

        The label is optional.
        By default, the label is under the bitmap.

        """
        super(BitmapTextButton, self).__init__(
            parent, id, pos, size, name)

        self._label = label
        self._labelpos = wx.BOTTOM
        self._spacing = 4
        self._default_bitmapcolor = self.GetPenForegroundColour()
        self._bitmapcolor = self._default_bitmapcolor
        self._align = wx.ALIGN_CENTER  # or LEFT or RIGHT

        # The icon image
        self._image = None
        if name != wx.ButtonNameStr:
            self.SetImage(name)

    # -----------------------------------------------------------------------

    def SetImage(self, image_name):
        """Set a new image.

        :param image_name: (str) Name of the image or full filename

        """
        self._image = image_name

    # -----------------------------------------------------------------------

    def SetForegroundColour(self, colour):
        """Override. Apply fg colour to both the image and the text.

        :param colour: (wx.Colour)

        """
        BaseButton.SetForegroundColour(self, colour)
        if self._bitmapcolor == self._default_bitmapcolor:
            self._bitmapcolor = self.GetPenForegroundColour()

        self._default_bitmapcolor = self.GetPenForegroundColour()

    # -----------------------------------------------------------------------

    def DoGetBestSize(self):
        """Overridden base class virtual.

        Determines the best size of the button based on the label.

        """
        label = self.GetLabel()
        if not label:
            return wx.Size(32, 32)

        dc = wx.ClientDC(self)
        dc.SetFont(self.GetFont())
        ret_width, ret_height = dc.GetTextExtent(label)

        width = int(max(ret_width, ret_height) * 1.5)
        return wx.Size(width, width)

    # -----------------------------------------------------------------------

    def GetBitmapColour(self):
        return self._bitmapcolor

    def SetBitmapColour(self, color):
        self._bitmapcolor = color

    # -----------------------------------------------------------------------

    def GetSpacing(self):
        return self._spacing

    def SetSpacing(self, value):
        self._spacing = max(int(value), 2)

    # -----------------------------------------------------------------------

    def GetLabelPosition(self):
        return self._labelpos

    def SetLabelPosition(self, pos=wx.BOTTOM):
        """Set the position of the label: top, bottom, left, right."""
        if pos not in [wx.TOP, wx.BOTTOM, wx.LEFT, wx.RIGHT]:
            return
        self._labelpos = pos

    # -----------------------------------------------------------------------

    def GetAlign(self):
        return self._align

    def SetAlign(self, align=wx.ALIGN_CENTER):
        """Set the position of the label: top, bottom, left, right."""
        if align not in [wx.ALIGN_CENTER, wx.ALIGN_LEFT, wx.ALIGN_RIGHT]:
            return
        self._align = align

    # ------------------------------------------------------------------------

    def GetLabel(self):
        """Return the label text as it was passed to SetLabel."""
        return self._label

    # ------------------------------------------------------------------------

    def SetLabel(self, label):
        """Set the label text.

        :param label: (str) Label text.

        """
        self._label = label

    # -----------------------------------------------------------------------

    LabelPosition = property(GetLabelPosition, SetLabelPosition)
    BitmapColour = property(GetBitmapColour, SetBitmapColour)
    Spacing = property(GetSpacing, SetSpacing)
    Align = property(GetAlign, SetAlign)

    # -----------------------------------------------------------------------

    def DrawContent(self, dc, gc):
        x, y, w, h = self.GetContentRect()
        if w >= 4 and h >= 4:
            # No label is defined.
            # Draw the square bitmap icon at the center with a 5% margin all around
            if self._label is None:
                x_pos, y_pos, bmp_size = self.__get_bitmap_properties(x, y, w, h)
                designed = self.__draw_bitmap(dc, gc, x_pos, y_pos, bmp_size)
                if designed is False:
                    pen = wx.Pen(self.GetPenForegroundColour(), 1, self._border_style)
                    pen.SetCap(wx.CAP_BUTT)
                    dc.SetPen(pen)
                    dc.DrawRectangle(self._vert_border_width,
                                     self._horiz_border_width,
                                     w - (2 * self._vert_border_width),
                                     h - (2 * self._horiz_border_width))
            else:
                self._DrawContentLabel(dc, gc, x, y, w, h)

    # -----------------------------------------------------------------------

    def _DrawContentLabel(self, dc, gc, x, y, w, h):

        tw, th = self.get_text_extend(dc, gc, self._label)

        if self._labelpos == wx.BOTTOM or self._labelpos == wx.TOP:
            # spacing is applied vertically
            x_bmp, y_pos, bmp_size = self.__get_bitmap_properties(
                x, y + th + self._spacing,
                w, h - th - 2 * self._spacing)
            if bmp_size > 15:
                margin = h - bmp_size - th - self._spacing
                y += (margin // 2)

            if self._labelpos == wx.BOTTOM:
                #self.__draw_bitmap(dc, gc, (w - bmp_size) // 2, y, bmp_size)
                self.__draw_bitmap(dc, gc, x_bmp, y, bmp_size)
                self.__draw_label(dc, gc, (w - tw) // 2, h - th)

            if self._labelpos == wx.TOP:
                self.__draw_label(dc, gc, (w - tw) // 2, y)
                self.__draw_bitmap(dc, gc, x_bmp, y_pos, bmp_size)

        if self._labelpos == wx.LEFT or self._labelpos == wx.RIGHT:
            # spacing is applied horizontally
            x_bmp, y_bmp, bmp_size = self.__get_bitmap_properties(
                x, y, w - tw - self._spacing, h)

            if bmp_size > 8:
                margin = w - bmp_size - tw - self._spacing
                if self._align == wx.ALIGN_RIGHT:
                    x += margin
                elif self._align == wx.ALIGN_CENTER:
                    x += (margin // 2)

                if self._labelpos == wx.LEFT:
                    self.__draw_label(dc, gc, x, (h - (th//2)) // 2)
                    self.__draw_bitmap(dc, gc, x_bmp + self._spacing + tw, y_bmp, bmp_size)

                if self._labelpos == wx.RIGHT:
                    self.__draw_bitmap(dc, gc, x_bmp, y_bmp, bmp_size)
                    self.__draw_label(dc, gc, x_bmp + bmp_size + self._spacing, (h - (th//2)) // 2)

            else:
                # not enough room for a bitmap.
                if self._align == wx.ALIGN_CENTER:
                    self.__draw_label(dc, gc, (w - tw) // 2, (h - (th//2)) // 2)
                elif self._align == wx.ALIGN_LEFT:
                    self.__draw_label(dc, gc, x, (h - (th//2)) // 2)
                elif self._align == wx.ALIGN_RIGHT:
                    self.__draw_label(dc, gc, (w - tw), (h - (th//2)) // 2)

    # -----------------------------------------------------------------------

    def __get_bitmap_properties(self, x, y, w, h):
        # w, h is the available size
        bmp_size = min(w, h)                  # force a squared button
        margin = max(int(bmp_size * 0.2), 2)  # optimal margin (20% of btn size)
        bmp_size -= margin
        y_pos = y + (margin // 2)
        if self._align == wx.ALIGN_LEFT:
            x_pos = x
        elif self._align == wx.ALIGN_RIGHT:
            x_pos = w - bmp_size
        else:
            x_pos = x + (margin // 2)

        if w < h:
            y_pos = (h - bmp_size + margin) // 2
        else:
            if self._align == wx.ALIGN_CENTER:
                x_pos = (w - bmp_size + margin) // 2

        return x_pos, y_pos, bmp_size

    # -----------------------------------------------------------------------

    def __draw_bitmap(self, dc, gc, x, y, btn_size):
        # if no image was given
        if self._image is None:
            return False

        try:
            # get the image from its name
            img = sppasSwissKnife.get_image(self._image)
            # re-scale the image to the expected size
            sppasSwissKnife.rescale_image(img, btn_size)
            # re-colorize
            ColorizeImage(img, wx.BLACK, self._bitmapcolor)
            # convert to bitmap
            bitmap = wx.Bitmap(img)
            # draw it to the dc or gc
            if wx.Platform == '__WXGTK__':
                dc.DrawBitmap(bitmap, x, y)
            else:
                gc.DrawBitmap(bitmap, x, y)
        except Exception as e:
            wx.LogWarning('Draw image error: {:s}'.format(str(e)))
            return False

        return True

    # -----------------------------------------------------------------------

    @staticmethod
    def get_text_extend(dc, gc, text):
        if wx.Platform == '__WXGTK__':
            return dc.GetTextExtent(text)
        return gc.GetTextExtent(text)

    # -----------------------------------------------------------------------

    def __draw_label(self, dc, gc, x, y):
        font = self.GetFont()
        gc.SetFont(font)
        dc.SetFont(font)
        if wx.Platform == '__WXGTK__':
            dc.SetTextForeground(self.GetPenForegroundColour())
            dc.DrawText(self._label, x, y)
        else:
            gc.SetTextForeground(self.GetPenForegroundColour())
            gc.DrawText(self._label, x, y)

# ---------------------------------------------------------------------------


class TextButton(BaseButton):

    def __init__(self, parent,
                 id=wx.ID_ANY,
                 label="",
                 pos=wx.DefaultPosition,
                 size=wx.DefaultSize,
                 name=wx.ButtonNameStr):
        """Default class constructor.

        :param parent: the parent (required);
        :param id: window identifier.
        :param label: label text of the check button;
        :param pos: the position;
        :param size: the size;
        :param name: the name of the bitmap.

        The label is required.

        """
        super(TextButton, self).__init__(parent, id, pos, size, name)

        self._label = label
        self._labelpos = wx.CENTER

    # -----------------------------------------------------------------------

    def DoGetBestSize(self):
        """Overridden base class virtual.

        Determines the best size of the button based on the label.

        """
        label = self.GetLabel()
        if not label:
            return wx.Size(32, 32)

        dc = wx.ClientDC(self)
        dc.SetFont(self.GetFont())
        retWidth, retHeight = dc.GetTextExtent(label)

        width = int(max(retWidth, retHeight) * 1.5)
        return wx.Size(width, width)

    # -----------------------------------------------------------------------

    def GetLabelPosition(self):
        return self._labelpos

    def SetLabelPosition(self, pos=wx.BOTTOM):
        """Set the position of the label: top, bottom, left, right."""
        if pos not in [wx.TOP, wx.BOTTOM, wx.LEFT, wx.RIGHT]:
            return
        self._labelpos = pos

    # -----------------------------------------------------------------------

    LabelPosition = property(GetLabelPosition, SetLabelPosition)

    # -----------------------------------------------------------------------

    def DrawContent(self, dc, gc):

        x, y, w, h = self.GetClientRect()
        x += self._vert_border_width
        y += self._horiz_border_width
        w -= (2 * self._vert_border_width)
        h -= ((2 * self._horiz_border_width) + self._focus_width + 2)

        # No label is defined.
        tw, th = self.get_text_extend(dc, gc, self._label)

        if self._labelpos == wx.BOTTOM:
            self.__draw_label(dc, gc, (w - tw) // 2, h - th)

        elif self._labelpos == wx.TOP:
            self.__draw_label(dc, gc, (w - tw) // 2, y)

        elif self._labelpos == wx.LEFT:
            self.__draw_label(dc, gc, 2, (h - th) // 2)

        elif self._labelpos == wx.RIGHT:
            self.__draw_label(dc, gc, w - tw - 2, (h - th) // 2)

        else:
            # Center the text.
            self.__draw_label(dc, gc, (w - tw) // 2, (h - th) // 2)

    # -----------------------------------------------------------------------

    @staticmethod
    def get_text_extend(dc, gc, text):
        if wx.Platform == '__WXGTK__':
            return dc.GetTextExtent(text)
        return gc.GetTextExtent(text)

    # -----------------------------------------------------------------------

    def __draw_label(self, dc, gc, x, y):
        font = self.GetFont()
        gc.SetFont(font)
        dc.SetFont(font)
        if wx.Platform == '__WXGTK__':
            dc.SetTextForeground(self.GetPenForegroundColour())
            dc.DrawText(self._label, x, y)
        else:
            gc.SetTextForeground(self.GetPenForegroundColour())
            gc.DrawText(self._label, x, y)

# ---------------------------------------------------------------------------


class BitmapButton(BitmapTextButton):
    def __init__(self, parent,
                 id=wx.ID_ANY,
                 pos=wx.DefaultPosition,
                 size=wx.DefaultSize,
                 name=wx.ButtonNameStr):
        """A BitmapTextButton, without the text.

        :param parent: the parent (required);
        :param id: window identifier.
        :param pos: the position;
        :param size: the size;
        :param name: the name of the bitmap.

        """
        super(BitmapButton, self).__init__(
            parent, id, None, pos, size, name)

# ---------------------------------------------------------------------------


class ToggleButton(BitmapTextButton):

    def __init__(self, parent,
                 id=wx.ID_ANY,
                 label=None,
                 pos=wx.DefaultPosition,
                 size=wx.DefaultSize,
                 name=wx.ButtonNameStr):
        """Default class constructor."""
        super(ToggleButton, self).__init__(
            parent, id, label=label, pos=pos, size=size, name=name)
        self._pressed = False

    # -----------------------------------------------------------------------

    def IsPressed(self):
        """Return if button is pressed.

        :returns: (bool)

        """
        return self._pressed

    # -----------------------------------------------------------------------

    def GetValue(self):
        return self._pressed

    # -----------------------------------------------------------------------

    def SetValue(self, value):
        if self._pressed != value:
            self._pressed = value
            if value:
                self._set_state(WindowState().selected)
            else:
                self._set_state(WindowState().normal)
            self.Refresh()

    # -----------------------------------------------------------------------
    # Override BaseButton
    # -----------------------------------------------------------------------

    def OnMouseLeftDown(self, event):
        """Handle the wx.EVT_LEFT_DOWN event.

        :param event: a wx.MouseEvent event to be processed.

        """
        if self.IsEnabled() is True:
            self._pressed = not self._pressed
            BaseButton.OnMouseLeftDown(self, event)

    # -----------------------------------------------------------------------

    def OnMouseLeftUp(self, event):
        """Handle the wx.EVT_LEFT_UP event.

        :param event: a wx.MouseEvent event to be processed.

        """
        if not self.IsEnabled():
            return

        # Mouse was down outside of the button (but is up inside)
        if not self.HasCapture():
            return

        # Directs all mouse input to this window
        self.ReleaseMouse()

        # If the button was down when the mouse was released...
        if self._state[1] == WindowState().selected:
            self.Notify()

            if self._pressed:
                self._set_state(WindowState().selected)
            else:
                self._set_state(WindowState().focused)

            # test self, in case the button was destroyed in the eventhandler
            if self:
                # self.Refresh()  # done in set_state
                event.Skip()

    # -----------------------------------------------------------------------

    def OnMouseLeave(self, event):
        """Handle the wx.EVT_LEAVE_WINDOW event.

        :param event: a wx.MouseEvent event to be processed.

        """
        if self._pressed is True:
            self._set_state(WindowState().selected)
            return

        if self._state[1] == WindowState().focused:
            self._set_state(WindowState().normal)
            self.Refresh()
            event.Skip()

        elif self._state[1] == WindowState().selected:
            self._state[0] = WindowState().normal
            self.Refresh()
            event.Skip()

        self._pressed = False

    # -----------------------------------------------------------------------

    def GetBackgroundBrush(self):
        """Get the brush for drawing the background of the window.

        :returns: (wx.Brush)

        """
        if self._pressed is False:
            if self._bgcolor is None:
                # Transparent background
                if wx.Platform == '__WXMAC__':
                    return wx.TRANSPARENT_BRUSH
                color = self.GetBackgroundColour()
                return wx.Brush(color, wx.BRUSHSTYLE_TRANSPARENT)
            else:
                return wx.Brush(self._bgcolor, wx.SOLID)

        else:
            if self._bgcolor is None:
                color = self.GetBackgroundColour()
            else:
                color = self._bgcolor

            r = color.Red()
            g = color.Green()
            b = color.Blue()
            if (r + g + b) > 384:
                color = wx.Colour(r, g, b, 64).ChangeLightness(140)
            else:
                color = wx.Colour(r, g, b, 64).ChangeLightness(60)
            return wx.Brush(color, wx.SOLID)

    # -----------------------------------------------------------------------

    def Notify(self):
        """Sends a wx.EVT_TOGGLEBUTTON event to the listener (if any)."""
        evt = ToggleButtonEvent(wx.wxEVT_COMMAND_TOGGLEBUTTON_CLICKED, self.GetId())
        evt.SetButtonObj(self)
        evt.SetEventObject(self)
        self.GetEventHandler().ProcessEvent(evt)

# ---------------------------------------------------------------------------


class BaseCheckButton(BaseButton):

    def __init__(self, parent,
                 id=wx.ID_ANY,
                 pos=wx.DefaultPosition,
                 size=wx.DefaultSize,
                 name=wx.PanelNameStr):
        """Default class constructor.

        :param parent: (wx.Window) parent window. Must not be ``None``;
        :param id: (int) window identifier. A value of -1 indicates a default value;
        :param pos: the button position. A value of (-1, -1) indicates a default
         position, chosen by either the windowing system or wxPython, depending on
         platform;
        :param size: the button size. A value of (-1, -1) indicates a default size,
         chosen by either the windowing system or wxPython, depending on platform;
        :param name: (str) the button name.

        """
        super(BaseCheckButton, self).__init__(parent, id, pos, size, name)

        self._pressed = False

    # -----------------------------------------------------------------------

    def IsPressed(self):
        """Return if button is pressed.

        :returns: (bool)

        """
        return self._pressed

    # -----------------------------------------------------------------------

    def Check(self, value):
        if self._pressed != value:
            self._pressed = value
            if value:
                self._set_state(WindowState().selected)
            else:
                self._set_state(WindowState().normal)
            self.Refresh()

    # -----------------------------------------------------------------------
    # Override BaseButton
    # -----------------------------------------------------------------------

    def OnMouseLeftDown(self, event):
        """Handle the wx.EVT_LEFT_DOWN event.

        :param event: a wx.MouseEvent event to be processed.

        """
        if self.IsEnabled() is True:
            self._pressed = not self._pressed
            BaseButton.OnMouseLeftDown(self, event)

    # -----------------------------------------------------------------------

    def OnMouseLeftUp(self, event):
        """Handle the wx.EVT_LEFT_UP event.

        :param event: a wx.MouseEvent event to be processed.

        """
        if not self.IsEnabled():
            return

        # Mouse was down outside of the button (but is up inside)
        if not self.HasCapture():
            return

        # Directs all mouse input to this window
        self.ReleaseMouse()

        # If the button was down when the mouse was released...
        if self._state[1] == WindowState().selected:
            self.Notify()

            if self._pressed:
                self._set_state(WindowState().selected)
            else:
                self._set_state(WindowState().focused)

            # test self, in case the button was destroyed in the eventhandler
            if self:
                # self.Refresh()  # done in set_state
                event.Skip()

    # ------------------------------------------------------------------------

    def OnMouseLeave(self, event):
        """Handle the wx.EVT_LEAVE_WINDOW event.

        :param event: a wx.MouseEvent event to be processed.

        """
        if self._pressed is True:
            self._set_state(WindowState().selected)
            return

        if self._state[1] == WindowState().focused:
            self._set_state(WindowState().normal)
            self.Refresh()
            event.Skip()

        elif self._state[1] == WindowState().selected:
            self._state[0] = WindowState().normal
            self.Refresh()
            event.Skip()

        self._pressed = False

    # ------------------------------------------------------------------------

    def Notify(self):
        """Actually sends the wx.wxEVT_COMMAND_CHECKBOX_CLICKED event."""
        evt = ButtonEvent(wx.wxEVT_COMMAND_CHECKBOX_CLICKED, self.GetId())
        evt.SetButtonObj(self)
        evt.SetEventObject(self)
        self.GetEventHandler().ProcessEvent(evt)

# ---------------------------------------------------------------------------


class CheckButton(BaseCheckButton):

    def __init__(self, parent,
                 id=wx.ID_ANY,
                 label=None,
                 pos=wx.DefaultPosition,
                 size=wx.DefaultSize,
                 name=wx.ButtonNameStr):
        """Default class constructor.

        :param parent: the parent (required);
        :param id: window identifier.
        :param label: label text of the check button;
        :param pos: the position;
        :param size: the size;
        :param name: the name.

        """
        super(CheckButton, self).__init__(
            parent, id, pos, size, name)

        self._borderwidth = 0
        self._label = label
        self._radio = False

        # Set the spacing between the check bitmap and the label to 6.
        # This can be changed using SetSpacing later.
        self._spacing = 6

    # ------------------------------------------------------------------------

    def GetLabel(self):
        """Return the label text as it was passed to SetLabel."""
        return self._label

    # ------------------------------------------------------------------------

    def IsChecked(self):
        """Return if button is checked.

        :returns: (bool)

        """
        return self._pressed

    # ------------------------------------------------------------------------

    def SetSpacing(self, spacing):
        """Set a new spacing between the check bitmap and the text.

        :param spacing: (int) Value between 0 and 30.

        """
        spacing = int(spacing)
        if spacing < 0:
            spacing = 0
        if spacing > 30:
            # wx.LogWarning('Spacing of a button is maximum 30px width. '
            #                'Got {:d}.'.format(spacing))
            spacing = 30
        # we should check if spacing < self height or width
        self._spacing = spacing

    # ------------------------------------------------------------------------

    def GetSpacing(self):
        """Return the spacing between the bitmap and the text."""
        return self._spacing

    # ------------------------------------------------------------------------

    def SetValue(self, value):
        """Set the state of the button.

        :param value: (bool)

        """
        self.Check(value)
        #self._pressed = bool(value)

    # ------------------------------------------------------------------------

    def GetValue(self):
        """Return the state of the button."""
        return self._pressed

    # ------------------------------------------------------------------------

    def DrawCheckImage(self, dc, gc):
        """Draw the check image.

        """
        w, h = self.GetClientSize()

        if self._label is None or len(self._label) == 0:
            prop_size = int(min(h * 0.7, 32))
            img_size = max(16, prop_size)
        else:
            tw, th = CheckButton.__get_text_extend(dc, gc, "XX")
            img_size = int(float(th) * 1.2)

        box_x = self._borderwidth + 2
        box_y = (h - img_size) // 2

        # Adjust image size then draw
        if self._pressed:
            if self._radio:
                img = sppasSwissKnife.get_image('radio_checked')
            else:
                img = sppasSwissKnife.get_image('choice_checked')
        else:
            if self._radio:
                img = sppasSwissKnife.get_image('radio_unchecked')
            else:
                img = sppasSwissKnife.get_image('choice_checkbox')

        sppasSwissKnife.rescale_image(img, img_size)
        ColorizeImage(img, wx.BLACK, self.GetPenForegroundColour())

        # Draw image as bitmap
        bmp = wx.Bitmap(img)
        if wx.Platform == '__WXGTK__':
            dc.DrawBitmap(bmp, box_x, box_y)
        else:
            gc.DrawBitmap(bmp, box_x, box_y)

        return img_size

    # ------------------------------------------------------------------------

    @staticmethod
    def __get_text_extend(dc, gc, text):
        if wx.Platform == '__WXGTK__':
            return dc.GetTextExtent(text)
        return gc.GetTextExtent(text)

    # ------------------------------------------------------------------------

    def __DrawLabel(self, dc, gc, x):
        w, h = self.GetClientSize()
        tw, th = CheckButton.__get_text_extend(dc, gc, self._label)
        y = ((h - th) // 2)
        font = self.GetFont()
        gc.SetFont(font)
        dc.SetFont(font)
        if wx.Platform == '__WXGTK__':
            dc.SetTextForeground(self.GetPenForegroundColour())
            dc.DrawText(self._label, x, y)
        else:
            gc.SetTextForeground(self.GetPenForegroundColour())
            gc.DrawText(self._label, x, y)

    # ------------------------------------------------------------------------

    def DrawContent(self, dc, gc):
        img_size = self.DrawCheckImage(dc, gc)
        if self._label:
            self.__DrawLabel(dc, gc, img_size + self._spacing)

# ---------------------------------------------------------------------------


class RadioButton(CheckButton):

    def __init__(self, parent,
                 id=wx.ID_ANY,
                 label="",
                 pos=wx.DefaultPosition,
                 size=wx.DefaultSize,
                 name=wx.ButtonNameStr):
        """Default class constructor.

        :param parent: the parent (required);
        :param id: window identifier.
        :param label: label text of the check button;
        :param pos: the position;
        :param size: the size;
        :param name: the name.

        """
        super(RadioButton, self).__init__(parent, id, label, pos, size, name)
        self._radio = True

    # ------------------------------------------------------------------------

    def Notify(self):
        """Sends a wx.EVT_RADIOBUTTON event to the listener (if any)."""
        evt = ButtonEvent(wx.EVT_RADIOBUTTON.typeId, self.GetId())
        evt.SetButtonObj(self)
        evt.SetEventObject(self)
        self.GetEventHandler().ProcessEvent(evt)

# ----------------------------------------------------------------------------
# Panels to test
# ----------------------------------------------------------------------------


class TestPanelBaseButton(wx.Panel):

    def __init__(self, parent):
        super(TestPanelBaseButton, self).__init__(
            parent,
            style=wx.BORDER_NONE | wx.WANTS_CHARS,
            name="Test BaseButton")

        self.SetForegroundColour(wx.Colour(150, 160, 170))
        st = [wx.PENSTYLE_SHORT_DASH,
              wx.PENSTYLE_LONG_DASH,
              wx.PENSTYLE_DOT_DASH,
              wx.PENSTYLE_SOLID,
              wx.PENSTYLE_HORIZONTAL_HATCH]

        # play with the border
        x = 10
        w = 100
        h = 50
        c = 10
        for i in range(1, 6):
            btn = BaseButton(self, pos=(x, 10), size=(w, h))
            btn.SetBorderWidth(i)
            btn.SetBorderColour(wx.Colour(c, c, c))
            btn.SetBorderStyle(st[i-1])
            c += 40
            x += w + 10
            btn.Bind(wx.EVT_BUTTON, self.on_btn_event)

        # play with the focus
        x = 10
        w = 100
        h = 50
        c = 10
        for i in range(1, 6):
            btn = BaseButton(self, pos=(x, 70), size=(w, h))
            btn.SetBorderWidth(1)
            btn.SetFocusWidth(i)
            btn.SetFocusColour(wx.Colour(c, c, c))
            btn.SetFocusStyle(st[i-1])
            c += 40
            x += w + 10
            btn.Bind(wx.EVT_BUTTON, self.on_btn_event)

        vertical = BaseButton(self, pos=(560, 10), size=(50, 110))
        vertical.SetBackgroundColour(wx.Colour(128, 255, 196))

    # -----------------------------------------------------------------------

    def SetForegroundColour(self, colour):
        wx.Panel.SetForegroundColour(self, colour)
        for c in self.GetChildren():
            c.SetForegroundColour(colour)

    # -----------------------------------------------------------------------

    def on_btn_event(self, event):
        obj = event.GetEventObject()

# ----------------------------------------------------------------------------


class TestPanelBitmapButton(wx.Panel):

    def __init__(self, parent):
        super(TestPanelBitmapButton, self).__init__(
            parent,
            style=wx.BORDER_NONE | wx.WANTS_CHARS,
            name="Test BitmapButton")

        b1 = BitmapButton(self, pos=(10, 10), size=(50, 50))
        b2 = BitmapButton(self, pos=(70, 10), size=(50, 50))
        b3 = BitmapButton(self, pos=(130, 10), size=(100, 50), name="like")
        b4 = BitmapButton(self, pos=(240, 10), size=(30, 50), name="like")
        b5 = BitmapButton(self, pos=(280, 10), size=(30, 30), name="like")
        b6 = BitmapButton(self, pos=(320, 10), size=(50, 30), name="like")
        b7 = BitmapButton(self, pos=(380, 10), size=(50, 50), name="add")
        b7.SetFocusColour(wx.Colour(30, 120, 240))
        b7.SetFocusWidth(3)
        b7.SetFocusStyle(wx.PENSTYLE_SOLID)
        b8 = BitmapTextButton(self, pos=(440, 10), size=(50, 50), name="remove")
        b8.SetFocusColour(wx.Colour(30, 120, 240))
        b8.SetBitmapColour(wx.Colour(230, 120, 40))
        b8.SetFocusWidth(3)
        b8.SetFocusStyle(wx.PENSTYLE_SOLID)
        b9 = BitmapTextButton(self, pos=(500, 10), size=(50, 50), name="delete")
        b9.SetFocusColour(wx.Colour(30, 120, 240))
        b9.SetBitmapColour(wx.Colour(240, 10, 10))
        b9.SetFocusWidth(3)
        b9.SetFocusStyle(wx.PENSTYLE_SOLID)

    # -----------------------------------------------------------------------

    def SetForegroundColour(self, colour):
        wx.Panel.SetForegroundColour(self, colour)
        for c in self.GetChildren():
            c.SetForegroundColour(colour)


# ----------------------------------------------------------------------------


class TestPanelBitmapTextButton(wx.Panel):

    def __init__(self, parent):
        super(TestPanelBitmapTextButton, self).__init__(
            parent,
            style=wx.BORDER_NONE | wx.WANTS_CHARS,
            name="Test TextBitmapButton")

        b1 = BitmapTextButton(self, label="sppas_64", pos=(10, 10), size=(50, 50))
        #font = self.GetFont().MakeBold()
        #b1.SetFont(font)

        b2 = BitmapTextButton(self, label="boldfont", pos=(70, 10), size=(100, 50))
        # bold_font = wx.Font(15,                      # point size
        #                     wx.FONTFAMILY_DEFAULT,   # family,
        #                     wx.FONTSTYLE_NORMAL,     # style,
        #                     wx.FONTWEIGHT_BOLD,      # weight,
        #                     underline=False,
        #                     faceName="Lucida sans",
        #                     encoding=wx.FONTENCODING_SYSTEM)
        # b2.SetFont(bold_font)

        b3 = BitmapTextButton(self, label="sppas_colored", pos=(180, 10), size=(50, 50))
        b3.SetBorderWidth(1)

        b4 = BitmapTextButton(self, label="Add", pos=(240, 10), size=(100, 50), name="add")
        b4.SetBorderWidth(2)
        b4.SetLabel("ADD")
        b4.SetLabelPosition(wx.RIGHT)
        b4.Refresh()

        b5 = BitmapTextButton(self, label="Add", pos=(350, 10), size=(100, 50), name="add_lower")
        b5.SetLabelPosition(wx.LEFT)
        b6 = BitmapTextButton(self, label="Room for a tiny bitmap", pos=(460, 10), size=(150, 50), name="tiny")
        b6.SetLabelPosition(wx.LEFT)

    # -----------------------------------------------------------------------

    def SetForegroundColour(self, colour):
        wx.Panel.SetForegroundColour(self, colour)
        for c in self.GetChildren():
            c.SetForegroundColour(colour)

# ----------------------------------------------------------------------------


class TestPanelCheckButton(wx.Panel):

    def __init__(self, parent):
        super(TestPanelCheckButton, self).__init__(
            parent,
            style=wx.BORDER_NONE | wx.WANTS_CHARS | wx.FULL_REPAINT_ON_RESIZE,
            name="Test CheckButton")

        self.SetForegroundColour(wx.Colour(150, 160, 170))

        btn_check_xs = CheckButton(self, pos=(25, 10), size=(32, 32), name="yes")
        btn_check_xs.Check(True)
        btn_check_xs.Bind(wx.EVT_BUTTON, self.on_btn_event)

        btn_check_s = CheckButton(self, label="disabled", pos=(100, 10), size=(128, 64), name="yes")
        btn_check_s.Enable(False)

        btn_check_m = CheckButton(self, label='The text label', pos=(200, 10), size=(384, 128), name="yes")
        font = self.GetFont().MakeBold().Scale(1.4)
        btn_check_m.SetFont(font)
        btn_check_m.Bind(wx.EVT_BUTTON, self.on_btn_event)

    def on_btn_event(self, event):
        obj = event.GetEventObject()

    # -----------------------------------------------------------------------

    def SetForegroundColour(self, colour):
        wx.Panel.SetForegroundColour(self, colour)
        for c in self.GetChildren():
            c.SetForegroundColour(colour)

# ----------------------------------------------------------------------------


class TestPanelRadioButton(wx.Panel):

    def __init__(self, parent):
        super(TestPanelRadioButton, self).__init__(
            parent,
            style=wx.BORDER_NONE | wx.WANTS_CHARS | wx.FULL_REPAINT_ON_RESIZE,
            name="Test RadioButton")

        self.SetForegroundColour(wx.Colour(150, 160, 170))

        btn_check_xs = RadioButton(self, pos=(25, 10), size=(32, 32), name="yes")
        btn_check_xs.Check(True)
        btn_check_xs.Bind(wx.EVT_BUTTON, self.on_btn_event)

        btn_check_s = RadioButton(self, label="disabled", pos=(100, 10), size=(128, 64), name="dis")
        btn_check_s.Enable(False)

        btn_check_m = RadioButton(self, label='The text label', pos=(200, 10), size=(384, 128), name="radio")
        font = self.GetFont().MakeBold().Scale(1.4)
        btn_check_m.SetFont(font)
        btn_check_m.Bind(wx.EVT_BUTTON, self.on_btn_event)
        btn_check_m.SetBorderWidth(8)

    def on_btn_event(self, event):
        obj = event.GetEventObject()

    # -----------------------------------------------------------------------

    def SetForegroundColour(self, colour):
        wx.Panel.SetForegroundColour(self, colour)
        for c in self.GetChildren():
            c.SetForegroundColour(colour)

# ----------------------------------------------------------------------------


class TestToggleButtonPanel(wx.Panel):

    def __init__(self, parent):
        super(TestToggleButtonPanel, self).__init__(
            parent,
            style=wx.BORDER_NONE | wx.WANTS_CHARS | wx.FULL_REPAINT_ON_RESIZE,
            name="Test ToggleButton")

        self.SetForegroundColour(wx.Colour(150, 160, 170))
        # b1 = BitmapTextButton(self, label="sppas_colored")
        # b2 = BitmapTextButton(self, name="like")

        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(ToggleButton(self), 1, wx.EXPAND, 0)
        sizer.Add(ToggleButton(self), 1, wx.EXPAND, 0)
        sizer.Add(ToggleButton(self), 1, wx.EXPAND, 0)
        self.SetSizer(sizer)
        self.SetAutoLayout(True)

    # -----------------------------------------------------------------------

    def SetForegroundColour(self, colour):
        wx.Panel.SetForegroundColour(self, colour)
        for c in self.GetChildren():
            c.SetForegroundColour(colour)

# ----------------------------------------------------------------------------


class TestPanel(sc.ScrolledPanel):

    def __init__(self, parent):
        super(TestPanel, self).__init__(
            parent,
            style=wx.BORDER_NONE | wx.WANTS_CHARS,
            name="Test Buttons")

        sizer = wx.BoxSizer(wx.VERTICAL)

        tbpanel = wx.Panel(self, size=(-1, 64), )
        tbsizer = wx.BoxSizer(wx.HORIZONTAL)

        bgbtn = BitmapTextButton(tbpanel, name="bg_color")
        bgbtn.SetFocusWidth(0)
        fgbtn = BitmapTextButton(tbpanel, name="font_color")
        fgbtn.SetFocusWidth(0)
        fontbtn = BitmapTextButton(tbpanel, name="font")
        fontbtn.SetFocusWidth(0)

        self.Bind(wx.EVT_BUTTON, self.on_bg_color, bgbtn)
        self.Bind(wx.EVT_BUTTON, self.on_fg_color, fgbtn)
        self.Bind(wx.EVT_BUTTON, self.on_font, fontbtn)
        tbsizer.AddSpacer(3)
        tbsizer.Add(bgbtn, 0, wx.LEFT | wx.RIGHT, 4)
        tbsizer.Add(fgbtn, 0, wx.LEFT | wx.RIGHT, 4)
        tbsizer.Add(fontbtn, 0, wx.LEFT | wx.RIGHT, 4)
        tbsizer.AddSpacer(3)
        tbpanel.SetSizer(tbsizer)
        sizer.Add(tbpanel, 0, wx.EXPAND | wx.TOP | wx.BOTTOM, 2)

        sizer.Add(wx.StaticText(self, label="BaseButton()"), 0, wx.TOP | wx.BOTTOM, 2)
        sizer.Add(TestPanelBaseButton(self), 1, wx.EXPAND | wx.TOP | wx.BOTTOM, 2)
        sizer.Add(wx.StaticLine(self))
        sizer.Add(wx.StaticText(self, label="BitmapButton() - no text"), 0, wx.TOP | wx.BOTTOM, 2)
        sizer.Add(TestPanelBitmapButton(self), 1, wx.EXPAND | wx.TOP | wx.BOTTOM, 2)
        sizer.Add(wx.StaticLine(self))
        sizer.Add(wx.StaticText(self, label="BitmapTextButton() - with text"), 0, wx.TOP | wx.BOTTOM, 2)
        sizer.Add(TestPanelBitmapTextButton(self), 1, wx.EXPAND | wx.TOP | wx.BOTTOM, 2)
        sizer.Add(wx.StaticText(self, label="Toggle Buttons in a sizer:"), 0, wx.TOP | wx.BOTTOM, 2)
        sizer.Add(TestToggleButtonPanel(self), 1, wx.EXPAND | wx.TOP | wx.BOTTOM, 2)
        sizer.Add(wx.StaticText(self, label="Checked buttons:"), 0, wx.TOP | wx.BOTTOM, 2)
        sizer.Add(TestPanelCheckButton(self), 1, wx.EXPAND | wx.TOP | wx.BOTTOM, 2)
        sizer.Add(wx.StaticText(self, label="Radio buttons:"), 0, wx.TOP | wx.BOTTOM, 2)
        sizer.Add(TestPanelRadioButton(self), 1, wx.EXPAND | wx.TOP | wx.BOTTOM, 2)

        self.SetSizer(sizer)
        self.SetupScrolling()

    def on_bg_color(self, event):
        self.SetBackgroundColour(wx.Colour(
            random.randint(10, 250),
            random.randint(10, 250),
            random.randint(10, 250)
        ))
        self.Refresh()

    def on_fg_color(self, event):
        color = wx.Colour(
            random.randint(10, 250),
            random.randint(10, 250),
            random.randint(10, 250))
        self.SetForegroundColour(color)
        for c in self.GetChildren():
            c.SetForegroundColour(color)
        self.Refresh()

    def on_font(self, event):
        data = wx.FontData()
        data.EnableEffects(True)
        data.SetColour(wx.GetApp().settings.fg_color)
        data.SetInitialFont(wx.GetApp().settings.text_font)
        dlg = wx.FontDialog(self, data)
        if dlg.ShowModal() == wx.ID_OK:
            data = dlg.GetFontData()
            font = data.GetChosenFont()
            self.SetFont(font)
            for c in self.GetChildren():
                c.SetFont(font)
        self.Refresh()
