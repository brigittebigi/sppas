#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# ---------------------------------------------------------------------------
#            ___   __    __    __    ___
#           /     |  \  |  \  |  \  /              Automatic
#           \__   |__/  |__/  |___| \__             Annotation
#              \  |     |     |   |    \             of
#           ___/  |     |     |   | ___/              Speech
#
#
#                           http://www.sppas.org/
#
# ---------------------------------------------------------------------------
#            Laboratoire Parole et Langage, Aix-en-Provence, France
#                   Copyright (C) 2011-2016  Brigitte Bigi
#
#                   This banner notice must not be removed
# ---------------------------------------------------------------------------
# Use of this software is governed by the GNU Public License, version 3.
#
# SPPAS is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# SPPAS is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with SPPAS. If not, see <http://www.gnu.org/licenses/>.
#
# ---------------------------------------------------------------------------
# File: spControl.py
# ----------------------------------------------------------------------------

__docformat__ = """epytext"""
__authors__   = """Brigitte Bigi"""
__copyright__ = """Copyright (C) 2011-2015  Brigitte Bigi"""

# ---------------------------------------------------------------------------
# Imports
# ---------------------------------------------------------------------------

import logging
import wx
import wx.lib.newevent

# ----------------------------------------------------------------------------
# Constants
# ----------------------------------------------------------------------------

FG_COLOUR       = wx.BLACK   # object foreground
BG_COLOUR       = wx.WHITE   # object background
TEXT_COLOUR     = wx.Colour(70, 70, 70)
HANDLES_COLOUR  = wx.BLACK   # color of the handles when object is selected

PANE_WIDTH  = 100

FONT_SIZE_MIN = 6
FONT_SIZE_MAX = 32

HANDLES_SIZE  = 6
H_MARGIN_SIZE = 6
# Known bug:
# this margin size corresponds to left/right borders for the handles because...
# if handles are larger than the margin, they must be drawn over the content and:
# - handles are not displayed if they are over a label of a tier (why??)
# - the content of a newly de-selected object must be redrawn
V_MARGIN_SIZE = 0
# this margin size corresponds to top/bottom borders.
# Known bug:
# this value can't be something else than 0! the WaveCtrl is doing crazy things instead...

MIN_W=2*H_MARGIN_SIZE+PANE_WIDTH+HANDLES_SIZE
MIN_H=2*H_MARGIN_SIZE+HANDLES_SIZE


# ----------------------------------------------------------------------------


# ----------------------------------------------------------------------------
# Events
# ----------------------------------------------------------------------------

# When the spControl is clicked, the event is sent with the state as attribute.

ControlSelectedEvent, spEVT_CTRL_SELECTED = wx.lib.newevent.NewEvent()
ControlSelectedCommandEvent, spEVT_CTRL_SELECTED_COMMAND = wx.lib.newevent.NewCommandEvent()

# ----------------------------------------------------------------------------


# ---------------------------------------------------------------------------
# Class spControl
# ---------------------------------------------------------------------------

class spControl(wx.Window):
    """
    @author:  Brigitte Bigi
    @contact: develop@sppas.org
    @license: GPL, v3
    @summary: This class is a generic Control object.

    spControl implements a generic control object that can be placed
    anywhere to any wxPython widget:
      - only refresh if asked.
      - a timer is used. It gives the double-buffered contents a chance
      to redraw even when idle events are disabled (like during resize and
      scrolling).
      - top/bottom/left/right independent margins.
      - draw handles at the corners (in left/right margins) if selected.
      - automatic font size.

    """

    def __init__(self, parent, id=wx.ID_ANY,
                 pos=wx.DefaultPosition,
                 size=wx.DefaultSize):
        """
        Constructor.
        """
        style=wx.NO_BORDER|wx.NO_FULL_REPAINT_ON_RESIZE|wx.CLIP_CHILDREN|wx.WANTS_CHARS

        wx.Window.__init__(self, parent, id, pos, size, style)
        self.SetDoubleBuffered(True)
        self.SetBackgroundStyle(wx.BG_STYLE_CUSTOM)

        self.Initialize(size)

        # Bind the events related to our control:

        # Only refresh drawing when resizing is finished
        wx.EVT_PAINT(self, self.OnPaint)
        wx.EVT_SIZE(self,  self.OnSize)
        wx.EVT_IDLE(self,  self.OnIdle)
        wx.EVT_CLOSE(self, self.OnClose)
        wx.EVT_ERASE_BACKGROUND(self, lambda event: None)

        # Bind the events related to this control:
        wx.EVT_LEFT_UP(self, self.OnMouseLeftUp)

        # Start the background redraw timer.
        # This is optional, but it gives the double-buffered contents a
        # chance to redraw even when idle events are disabled (like during
        # resize and scrolling)
        self.redrawTimer = wx.Timer(self)
        self.redrawTimer.Start(500)

    # End __init__
    # ------------------------------------------------------------------------


    def Initialize(self, size):
        """
        Re-Initialize all values.
        """
        # Set initial dc mode to fast
        self.__initializeMembers()
        self.__initializeColours()
        self.__initializeSize(size)

        #self.buffer = wx.EmptyBitmap(max(1,size[0]),max(1,size[1]))
        self.InitBuffer()

    # End Initialize
    # ------------------------------------------------------------------------



    # -------------------------------------------------------------------------
    # Members
    # -------------------------------------------------------------------------


    def GetTime(self):
        """
        Return a tuple of time values.

        """
        return (self._mintime,self._maxtime)

    # End GetTime
    # -------------------------------------------------------------------------


    def GetBegin(self):
        """
        Return the min time value (float).

        """
        return self._mintime

    # End GetBegin
    # -------------------------------------------------------------------------


    def GetEnd(self):
        """
        Return the max time value (float).

        """
        return self._maxtime


    # End GetEnd
    # -------------------------------------------------------------------------


    def SetTime(self, start, end):
        """
        Define a new period to display.
        Request to redraw only if the period has changed.

        @param start (float) begin time value
        @param end (float) end time value

        """
        torepaint = False

        if start > end:
            b = start
            end = start
            start = b

        if self._mintime != start:
            self._mintime = start
            torepaint = True

        if self._maxtime != end:
            self._maxtime = end
            torepaint = True

        if torepaint is True: self.RequestRedraw()

    # End SetTime
    # -------------------------------------------------------------------------


    def IsSelected(self):
        """
        Return (Boolean) whether the spControl is selected or not.

        """
        return self._isselected

    # End IsSelected
    # ------------------------------------------------------------------------


    def SetSelected(self, value):
        """
        Activate/Disable selected.

        @param value (Boolean)

        """
        if self.isselectable is False:
            self._isselected = False
            return

        if self._isselected != value:
            self._isselected = value
            self.RequestRedraw()

    # End SetSelected
    # ------------------------------------------------------------------------


    def SetFontAutoAdjust(self, value):
        """
        Activate/Disable automatic adjustment of the font size.

        @param value (Boolean)

        """
        if self._fontsizeauto != value:
            self._fontsizeauto = value
            self.AutoAdjustFont()
            self.RequestRedraw()

    # End SetFontAutoAdjust
    # ------------------------------------------------------------------------


    def GetPanePosition(self):
        """
        Return the position of the information pane.

        The position is one of wx.ALIGN_LEFT, wx.ALIGN_CENTRE or wx.ALIGN_RIGHT

        """
        return self._infopanep

    # End GetPanePosition
    # -------------------------------------------------------------------------


    def SetPanePosition(self, value):
        """
        Fix the position of the information pane.

        @param value is one of wx.ALIGN_LEFT, wx.ALIGN_CENTRE or wx.ALIGN_RIGHT

        """
        if value not in [ wx.ALIGN_LEFT, wx.ALIGN_RIGHT, wx.ALIGN_CENTRE ]:
            raise TypeError

        if self._infopanep != value:
            self._infopanep = value
            self.RequestRedraw()

    # End SetPanePosition
    # -------------------------------------------------------------------------


    def GetPaneWidth(self):
        """
        Return the width of the information pane.

        """
        return self._infopanew

    # End GetPaneWidth
    # -----------------------------------------------------------------------


    def SetPaneWidth(self, value):
        """
        Fix the width of the information pane.

        @param value (int) is between 10 and 200.

        """

        value = min(200, max(10, int(value)))
        if self._infopanew != value:
            self._infopanew = value
            self.RequestRedraw()

    # End SetPaneWidth
    # -------------------------------------------------------------------------


    def MoveWindow(self, pos, size):
        """
        Define a new position and/or size to display.
        Ask to redraw only if something has changed.

        @param pos (wx.Point)
        @param size (wx.Size)

        """
        torepaint = False
        (w,h) = size
        (x,y) = pos
        (ow,oh) = self.GetSize()
        (ox,oy) = self.GetPosition()

        # New width
        if ow != w:
            self.SetSize(wx.Size(w,oh))
            torepaint = True

        # New height
        if oh != h:
            self.SetHeight(h)
            torepaint = True

        # New position (x and/or y)
        if ox != x or oy != y:
            self.Move(pos)
            torepaint = True

        if torepaint is True: self.RequestRedraw()

    # End MoveWindow
    # -------------------------------------------------------------------------


    # -------------------------------------------------------------------------
    # Look & style
    # -------------------------------------------------------------------------


    def GetBackgroundColour(self):
        """
        Return the spControl background color.

        """
        return self._bgcolor

    # End GetBackgroundColour
    # -------------------------------------------------------------------------


    def SetBackgroundColour(self, colour):
        """
        Sets the spControl background color.

        @param colour (wx.Colour)

        """

        if colour != self._bgcolor:
            self._bgcolor = colour
            self._bgpen   = wx.Pen(colour,1,wx.SOLID)
            self._bgbrush = wx.Brush(colour, wx.SOLID)
            self.RequestRedraw()

    # End SetBackgroundColour
    # -------------------------------------------------------------------------


    def GetForegroundColour(self):
        """
        Return the spControl foreground color.

        """
        return self._fgcolor

    # End GetBackgroundColour
    # -------------------------------------------------------------------------


    def SetForegroundColour(self, colour):
        """
        Sets the spControl foreground color.

        @param colour (wx.Colour)

        """

        if colour != self._fgcolor:
            self._fgcolor = colour
            self._fgpen   = wx.Pen(colour,1,wx.SOLID)
            self._fgbrush = wx.Brush(colour, wx.SOLID)
            self.RequestRedraw()

    # End SetForegroundColour
    # -------------------------------------------------------------------------


    def GetHandlesColour(self):
        """
        Return (wx.Colour) the color of handles.

        """
        return self._handlescolor

    # End GetHandlesColour
    # -------------------------------------------------------------------------


    def SetHandlesColour(self, colour):
        """
        Sets the spControl handles color.

        @param colour (wx.Colour)

        """

        if colour != self._handlescolor:
            self._handlescolor = colour
            self._handlespen   = wx.Pen(colour, 1, wx.SOLID)
            self._handlesbrush = wx.Brush(colour, wx.SOLID)
            if self._isselected:
                self.RequestRedraw()

    # End SetHandlesColour
    # -------------------------------------------------------------------------


    def GetTextColour(self):
        """
        Return (wx.Colour) the text font color.

        """
        return self._textcolor

    # End GetTextColour
    # -------------------------------------------------------------------------


    def SetTextColour(self, colour):
        """
        Sets the spControl text color.

        @param colour (wx.Colour)

        """

        if colour != self._textcolor:
            self._textcolor = colour
            self._textpen   = wx.Pen(colour,1,wx.SOLID)
            self.RequestRedraw()

    # End SetTextColour
    # -------------------------------------------------------------------------


    def SetLeftMargin(self, margin):
        """
        Fix left margin (in pixels).

        """
        if margin != self._margins.Left:
            self._margins.Left = margin
            self.RequestRedraw()

    # End SetLeftMargin
    # ------------------------------------------------------------------------


    def SetRightMargin(self, margin):
        """
        Fix right margin (in pixels).

        """
        if margin != self._margins.Right:
            self._margins.Right = margin
            self.RequestRedraw()

    # End SetRightMargin
    # ------------------------------------------------------------------------


    def SetTopMargin(self, margin):
        """
        Fix a top margin (in pixels).

        """
        if margin != self._margins.Top:
            self._margins.Top = margin
            self.RequestRedraw()

    # End SetTopMargin
    # ------------------------------------------------------------------------


    def SetBottomMargin(self, margin):
        """
        Fix a bottom margin (in pixels).

        """
        if margin != self._margins.Bottom:
            self._margins.Bottom = margin
            self.RequestRedraw()

    # End SetBottomMargin
    # ------------------------------------------------------------------------


    def SetFontSize(self, s):
        """
        Fix a font size (int) in Point.

        @param s (int) is a value between 6 and 32.

        """
        sreal = min(max(FONT_SIZE_MIN,s),FONT_SIZE_MAX)
        if sreal != self._font.GetPointSize():
            self._font.SetPointSize(sreal)
            self.RequestRedraw()

    # End SetFontSize
    # -------------------------------------------------------------------------


    def GetFont(self):
        """
        Return the font (wx.Font).

        """
        return self._font

    # End GetFont
    # -------------------------------------------------------------------------


    def SetFont(self, font):
        """
        Fix a font.
        Automatically adjust the size (compared to the previous one).

        @param font (wx.Font)

        """
        if font != self._font:

            self._font = font

            if self._fontsizeauto:
                self.AutoAdjustFont()

            self.RequestRedraw()

    # End SetFont
    # -------------------------------------------------------------------------


    def AutoAdjustFont(self):
        """
        Fix the biggest font size (depending on the available height).

        """

        h = self.GetDrawingSize()[1]
        if not h: return

        fontsize = FONT_SIZE_MIN
        self._font.SetPointSize(fontsize)

        pxh = self.__getTextHeight()
        pxmax = int(0.6*h)
        while fontsize < FONT_SIZE_MAX and pxh<pxmax:
            fontsize = fontsize + 1
            self._font.SetPointSize(fontsize)
            pxh = self.__getTextHeight()

    # End AutoAdjustFont
    # -------------------------------------------------------------------------


    def VertZoom(self, z):
        """
        Apply a vertical zoom to the spControl (fix a new height).

        @param z (float) Zoom coefficient.

        """
        self.SetHeight(int(z * self.GetHeight()))

    # End VertZoom
    # -----------------------------------------------------------------------


    def GetHeight(self):
        """
        Return the current spControl height.

        """
        return self.GetSize()[1]

    # End GetHeight
    # -----------------------------------------------------------------------


    def SetHeight(self, height):
        """
        Set the height of the spControl.

        @param height (int) in pixels

        """
        w,h = self.GetSize()

        if h != height:

            # apply new height
            new_height = max(MIN_H, height)
            self.SetSize(wx.Size(w,int(new_height)))

            # adjust font size
            if self._fontsizeauto: # and new_height>0:
                self.AutoAdjustFont()

            self.RequestRedraw()

    # End SetHeight
    # -------------------------------------------------------------------------


    # -------------------------------------------------------------------------
    # Callbacks
    # -------------------------------------------------------------------------


    def OnMouseLeftUp(self, event):
        """
        Event handler used when the mouse clicked on the spControl.
        """

        wx.PostEvent(self.GetParent().GetEventHandler(), event)

        if self.isselectable is False:
            return

        self._isselected = not self._isselected
        self.RequestRedraw()

        evt = ControlSelectedEvent(value=self._isselected)
        evt.SetEventObject(self)
        wx.PostEvent(self.GetParent(), evt)

    # End OnMouseLeftUp
    # -------------------------------------------------------------------------


    def OnClose(self, event):
        """
        Handles the wx.EVT_CLOSE event for spControl.
        """

        self.redrawTimer.Stop()
        self.Destroy()

    # End OnClose
    # -------------------------------------------------------------------------


    def OnSize(self, event):
        """
        Handles the wx.EVT_SIZE event for spControl.
        """

        self.RequestRedraw()
        event.Skip()

    # End OnSize
    # -------------------------------------------------------------------------


    def OnIdle(self, event):
        """
        If something was changed then resize the bitmap used for double
        buffering to match the window size.  We do it in Idle time so
        there is only one refresh after resizing is done, not lots while
        it is happening.
        """

        if self.IsShown() and self._requestredraw is True:
            self.InitBuffer()
            self.Refresh(False)

    # End OnIdle
    # -------------------------------------------------------------------------


    def OnPaint(self, event):
        """
        Handles the wx.EVT_PAINT event for spControl.
        """

        dc = wx.BufferedPaintDC(self, self.buffer)

    # OnPaint
    # -------------------------------------------------------------------------


    # -------------------------------------------------------------------------
    # Painting
    # -------------------------------------------------------------------------


    def RequestRedraw(self):
        """
        Requests a redraw of the drawing panel contents.

        The actual redrawing doesn't happen until the next idle time.
        """
        self._requestredraw = True

    # End RequestRedraw
    # -------------------------------------------------------------------------


    def InitBuffer(self):
        """
        Initialize the bitmap used for buffering the display.
        """

        w,h = self.GetSize()

        self.buffer = wx.EmptyBitmap(max(1,w),max(1,h))
        dc = wx.BufferedDC(None, self.buffer)
        dc.Clear()
        self.Draw(dc)
        del dc  # commits all drawing to the buffer

        self._requestredraw = False

    # End InitBuffer
    # -------------------------------------------------------------------------


    def GetDrawingSize(self):
        """
        Return the size available to draw (without the pane and without margins).
        """

        # Get the actual client size of ourselves
        (w,h) = self.GetClientSize()

        # Adjust height
        h = max(MIN_H, h - self._margins.Top - self._margins.Bottom)

        # Adjust width
        if self._infopanep == wx.ALIGN_LEFT:
            w = w - self._infopanew
        elif self._infopanep == wx.ALIGN_RIGHT:
            w = w - self._infopanew

        w = max(MIN_W, w - self._margins.Left - self._margins.Right)

        return (w,h)

    # End GetDrawingSize
    # -------------------------------------------------------------------------


    def GetDrawingPosition(self):
        """
        Return the position to draw (without the pane and without margins).
        """

        # Get the actual position of ourselves
        (x,y) = (0,0)

        # Adjust x
        if self._infopanep == wx.ALIGN_LEFT:
            x = x + self._infopanew

        return (x+self._margins.Left, y+self._margins.Top)

    # End GetDrawingPosition
    # -------------------------------------------------------------------------


    def Draw(self, dc):
        """
        Draw the spControl on the DC.

        1. fill the background,
        2. draw the pane,
        3. draw the content,
        4. draw handles.

        @param dc (PaintDC, MemoryDC, BufferedDC...) the Device Context

        """

        # Get the actual client size of ourselves
        (rw, rh) = self.GetClientSize()   # self.GetSize()
        (w, h) = self.GetDrawingSize()
        (x, y) = self.GetDrawingPosition()

        # Nothing to do, we still don't have dimensions!
        if rw*rh == 0: 
            return

        # Fill background
        dc.SetBackground(self._bgbrush)
        dc.Clear()

        try:
            # Info Pane
            if self._infopanep == wx.ALIGN_LEFT:
                self.DrawPane(dc, self._margins.Left, y, self._infopanew, h)
            elif self._infopanep == wx.ALIGN_RIGHT:
                self.DrawPane(dc, w-self._infopanew, y, self._infopanew, h)
        except Exception as e:
            logging.debug(' [ERROR] while drawing pane. {:s}'.format(str(e)))
            pass

        try:
            # Content
            if w*h > 0:
                self.DrawContent(dc, x, y, w, h)
        except Exception as e:
            logging.debug(' [ERROR] while drawing content. {:s}'.format(str(e)))
            pass

        # Draws selection handles
        if self._isselected is True:
            self.DrawHandles(dc, 0, 0, rw, rh)

    # -------------------------------------------------------------------------

    def DrawHandles(self, dc, x,y, w,h):
        """Draw selection handles for this spControl.
        
        Default is to draw selection handles at all four corners.

        @param dc (PaintDC, MemoryDC, BufferedDC...)
        @param x,y (int,int) are coord. of top left corner from which drawing
        @param w,h (int,int) are width and height available for drawing.

        """
        dc.SetBrush(self._handlesbrush)
        dc.SetPen(self._handlespen)
        l = self._handlessize
        r = self._handlessize

        dc.DrawRectangle(x,     y,     l, l)
        dc.DrawRectangle(x+w-r, y,     r, r)
        dc.DrawRectangle(x,     y+h-l, l, l)
        dc.DrawRectangle(x+w-r, y+h-r, r, r)

    # ------------------------------------------------------------------------

    def DrawPane(self, dc, x,y, w,h):
        """Draw something inside the pane of the spControl. Must be overridden.

        @param dc (PaintDC, MemoryDC, BufferedDC...)
        @param x,y (int,int) are coord. of top left corner from which drawing
        @param w,h (int,int) are width and height available for drawing.

        """
        raise NotImplementedError

    # -------------------------------------------------------------------------

    def DrawContent(self, dc, x,y, w,h):
        """Draw something inside the spControl. Must be overridden.

        @param dc (PaintDC, MemoryDC, BufferedDC...)
        @param x,y (int,int) are coord. of top left corner from which drawing
        @param w,h (int,int) are width and height available for drawing.

        """
        raise NotImplementedError

    # -------------------------------------------------------------------------
    # Private
    # -------------------------------------------------------------------------

    def __initializeMembers(self):
        """Initialize all members."""

        # Fix a default font
        self._font = wx.Font(FONT_SIZE_MIN, wx.SWISS, wx.NORMAL, wx.BOLD)
        # Adjust font size when self is resized or when a new font is fixed:
        self._fontsizeauto = False

        # When an object is selected, 4 handles are drawn (at the corners).
        self._isselected  = False
        self.isselectable = True

        # Displayed period of time (can be taken from the Parent)
        self._mintime = 0.
        self._maxtime = 4.

        # A pane that can be placed at left or right (or nowhere).
        self._infopanep = wx.ALIGN_LEFT   # position (CENTRE means nowhere)
        self._infopanew = PANE_WIDTH      # width

        # Margins are required to draw handles.
        self._margins = Margins()
        self._margins.Left = H_MARGIN_SIZE
        self._margins.Right = H_MARGIN_SIZE
        self._margins.Top = V_MARGIN_SIZE
        self._margins.Bottom = V_MARGIN_SIZE

        # Handles
        self._handlessize = HANDLES_SIZE

    # -------------------------------------------------------------------------

    def __initializeColours(self):
        """Create the pens and brush with default colors."""

        self._bgcolor    = BG_COLOUR
        self._bgpen      = wx.Pen(BG_COLOUR, 1, wx.SOLID)
        self._bgbrush    = wx.Brush(BG_COLOUR, wx.SOLID)

        self._fgcolor    = FG_COLOUR
        self._fgpen      = wx.Pen(FG_COLOUR, 1, wx.SOLID)
        self._fgbrush    = wx.Brush(FG_COLOUR, wx.SOLID)

        self._handlescolor = HANDLES_COLOUR
        self._handlespen   = wx.Pen(HANDLES_COLOUR, 1, wx.SOLID)
        self._handlesbrush = wx.Brush(HANDLES_COLOUR, wx.SOLID)

        self._textcolor  = TEXT_COLOUR
        self._textpen    = wx.Pen(TEXT_COLOUR,1,wx.SOLID)

    # -------------------------------------------------------------------------

    def __initializeSize(self, size):
        """Initialize the size."""

        self.SetMinSize(wx.Size(MIN_W,MIN_H))
        self.SetSize(size)

    # -------------------------------------------------------------------------

    def __getTextHeight(self):
        dc = wx.ClientDC(self)
        dc.SetFont(self._font)
        return dc.GetTextExtent('azertyuiopqsdfghjklmwxcvbn')[1]

# -----------------------------------------------------------------------------


class Margins:
    """Represents margins of an object, with 4 values: Top, Bottom, Left, Right.

    Margins are represented by integer values. Default values are 0.

    """

    def __init__(self, margin=0):
        """Create a new Margins() instance with default values.
            Parameters:
              - margin (int) margin value set to Top, Bottom, Left and Right.
        """
        try:
            margin = int(margin)
        except ValueError:
            raise TypeError("Margins. Integer argument required, not %r" % margin)

        self._left   = margin
        self._right  = margin
        self._top    = margin
        self._bottom = margin

    # -------------------------------------------------------------------------
    # Getters...
    # -------------------------------------------------------------------------

    def GetLeft(self):
        """
        Return left margin value (int).
        """
        return self._left

    # -------------------------------------------------------------------------

    def GetRight(self):
        """
        Return right margin value (int).
        """
        return self._right

    # -------------------------------------------------------------------------

    def GetTop(self):
        """
        Return top margin value (int).
        """
        return self._top

    # -------------------------------------------------------------------------

    def GetBottom(self):
        """
        Return left margin value (int).
        """
        return self._bottom

    # -------------------------------------------------------------------------
    # Setters...
    # -------------------------------------------------------------------------

    def SetValue(self, margin):
        """
        Set all margins to a specific value (int).
        """
        self._left   = self.__setint(margin)
        self._right  = margin
        self._top    = margin
        self._bottom = margin

    # -------------------------------------------------------------------------

    def SetLeft(self, margin):
        """
        Set left margin to a specific value (int).
        """
        self._left = margin

    # -------------------------------------------------------------------------

    def SetRight(self, margin):
        """
        Set right margin to a specific value (int).
        """
        self._right = margin

    # -------------------------------------------------------------------------

    def SetTop(self, margin):
        """
        Set top margin to a specific value (int).
        """
        self._top = margin

    # -------------------------------------------------------------------------

    def SetBottom(self, margin):
        """
        Set bottom margin to a specific value (int).
        """
        self._bottom = margin

    # -------------------------------------------------------------------------
    # Properties
    # -------------------------------------------------------------------------

    Top    = property(GetTop,    SetTop)
    Bottom = property(GetBottom, SetBottom)
    Left   = property(GetLeft,   SetLeft)
    Right  = property(GetRight,  SetRight)
