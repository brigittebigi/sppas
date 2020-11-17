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
# File: timerulerctrl.py
# ----------------------------------------------------------------------------

__docformat__ = """epytext"""
__authors__   = """Brigitte Bigi (contact@sppas.org)"""
__copyright__ = """Copyright (C) 2011-2015  Brigitte Bigi"""


import logging
import math
import wx
import wx.lib.newevent

from sppas.src.ui.wxgui.sp_icons import RULER_RED, RULER_GREEN, RULER_BLUE
from sppas.src.ui.wxgui.cutils.imageutils import spBitmap

from .spControl import spControl, FONT_SIZE_MIN

# ----------------------------------------------------------------------------
# Constants
# ----------------------------------------------------------------------------

TICK_HEIGHT=8
LABEL_SPACING=4

# ---------------------------------------------------------------------------
# Events
# ---------------------------------------------------------------------------

IndicatorChangingEvent, spEVT_INDICATOR_CHANGING = wx.lib.newevent.NewEvent()
IndicatorChangingCommandEvent, spEVT_INDICATOR_CHANGING_COMMAND = wx.lib.newevent.NewCommandEvent()

IndicatorChangedEvent, spEVT_INDICATOR_CHANGED = wx.lib.newevent.NewEvent()
IndicatorChangedCommandEvent, spEVT_INDICATOR_CHANGED_COMMAND = wx.lib.newevent.NewCommandEvent()

# ---------------------------------------------------------------------------
# Class Label
# ---------------------------------------------------------------------------


class RulerLabel:
    """
    Label holds information about a label in RulerCtrl.
    """

    def __init__(self, pos=-1, lx=-1, ly=-1, text=""):
        """Constructor."""

        self.pos  = pos
        self.lx   = lx
        self.ly   = ly
        self.text = text

    # End __init__
    # -----------------------------------------------------------------------



# ---------------------------------------------------------------------------
# Class Indicator
# ---------------------------------------------------------------------------

class Indicator:
    """
    Indicator holds information about a single indicator inside a RulerCtrl.
    """

    def __init__(self, parent, id=wx.ID_ANY, value=0):
        """Constructor."""

        self._parent = parent
        if id == wx.ID_ANY:
            id = wx.NewId()

        self._id = id
        self._colour = None

        self._img = wx.ImageFromBitmap( spBitmap( RULER_BLUE ) )
        self.RotateImage()

        self.SetValue(value)

    # End __init__
    # -----------------------------------------------------------------------


    def ScaleImage(self, width, height):
        """
        Scale the indicator bitmap.

        @param width (int)
        @param height (int)

        """

        self._img = self._img.Scale(width, height, wx.IMAGE_QUALITY_HIGH)

    # End ScaleImage
    # -----------------------------------------------------------------------


    def RotateImage(self):
        """
        Rotates the indicator bitmap.
        """

        w,h = self._img.GetWidth(), self._img.GetHeight()
        wcenter = int(w/2)
        hcenter = int(h/2)

        self._img = self._img.Rotate(math.pi, (wcenter, hcenter), True)

    # End RotateImage
    # -----------------------------------------------------------------------


    # -----------------------------------------------------------------------
    # Getters
    # -----------------------------------------------------------------------

    def GetId(self):
        """
        Returns the indicator id (int).

        """

        return self._id

    # End GetId
    # -----------------------------------------------------------------------


    def GetImageSize(self):
        """Return the indicator bitmap size."""

        return self._img.GetWidth(), self._img.GetHeight()

    # End GetImageSize
    # -----------------------------------------------------------------------


    def GetRect(self):
        """Return the indicator rect."""

        return self._rect

    # End GetRect
    # -----------------------------------------------------------------------


    def GetValue(self):
        """Return the indicator value."""

        return self._value

    # End GetValue
    # -----------------------------------------------------------------------


    def GetPosition(self):
        """
        Returns the position at which we should draw the indicator bitmap.
        """

        (px,py) = self._parent.GetDrawingPosition()
        (pw,ph) = self._parent.GetDrawingSize()
        minval = self._parent._mintime
        maxval = self._parent._maxtime

        value = self._value
        pos = float(value-minval)/abs(maxval - minval)
        xpos = px + int(pos*pw) - int(self._img.GetWidth()/2)

        if self._parent._flip is True:
            ypos = py
        else:
            ypos = py + ph - self._img.GetHeight()

        return xpos, ypos

    # End GetPosition
    # -----------------------------------------------------------------------



    # -----------------------------------------------------------------------
    # Setters
    # -----------------------------------------------------------------------


    def SetValue(self, value):
        """Sets the indicator value."""

        self._value = value
        self._rect  = wx.Rect()

    # End SetValue
    # -----------------------------------------------------------------------


    def SetColour(self, colour):
        """Sets the indicator color (red, green or blue)."""

        (r,g,b) = colour.Red(), colour.Green(), colour.Blue()
        if r >= g and r >= b:
            bmp = spBitmap( RULER_RED )
        elif g >= r and g >= b:
            bmp = spBitmap( RULER_GREEN )
        else:
            bmp = spBitmap( RULER_BLUE )
        self._img = wx.ImageFromBitmap(bmp)

        #self.RotateImage()

    # End SetColour
    # -----------------------------------------------------------------------


    # -----------------------------------------------------------------------
    # Draw on a DC (then set the self._rect value)
    # -----------------------------------------------------------------------


    def Draw(self, dc):
        """Actually draws the indicator on the dc."""
        xpos,ypos = self.GetPosition()

        bmp = wx.BitmapFromImage(self._img)
        dc.DrawBitmap(bmp, xpos, ypos, True)

        self._rect = wx.Rect(xpos, ypos, self._img.GetWidth(), self._img.GetHeight())

    # End Draw
    # -----------------------------------------------------------------------


# ---------------------------------------------------------------------------


class RulerCtrl( spControl ):
    """
    @author:  Brigitte Bigi
    @contact: contact@sppas.org
    @license: GPL
    @summary: This class is used to display a Ruler.

    RulerCtrl implements an horizontal ruler that can be placed anywhere to
    any wxPython widget:
      - Possibility to add a number of "indicators", small arrows that point at
        the current indicator position;
      - Customizable background color, tick color, label color;
      - Possibility to flip the ruler (i.e. changing the tick alignment);
      - Draw a thin line over a selected window when moving an indicator.

    """

    def __init__(self, parent, id=wx.ID_ANY,
                 pos=wx.DefaultPosition,
                 size=wx.DefaultSize):
        """
        Constructor.

        Notice that the style can't be changed. Fixed to NO_BORDER.

        """
        spControl.__init__(self, parent, id, pos, size)

        self.Reset()
        self.InitBuffer()

        # Bind the events related to our control:
        self.Bind(wx.EVT_MOUSE_EVENTS, self.OnMouseEvents)

    # End __init__
    #-------------------------------------------------------------------------


    def Reset(self):
        """Reset all values to their default."""

        self.__initializeMembers()
        self.__initializeColours()
        self.__initializeFonts()

    # End Reset
    #-------------------------------------------------------------------------


    #-------------------------------------------------------------------------
    # Indicators Getters and Setters
    #-------------------------------------------------------------------------


    def SetIndicatorValue(self, sendEvent=True, x=0, y=0):
        """Sets the indicator value."""

        if self._currentIndicator is None:
            return

        cx,cy = self.GetDrawingPosition()
        x = x - cx
        cw,ch = self.GetDrawingSize()

        deltarange = abs(self._maxtime - self._mintime)
        value = deltarange*float(x)/(cw)# - x)
        value += self._mintime

        if value < self._mintime or value > self._maxtime:
            return

        if sendEvent:
            evt = IndicatorChangingEvent(value=self._currentIndicator.GetValue())
            evt.SetEventObject(self)
            wx.PostEvent(self.GetParent(), evt)

            if self.GetEventHandler().ProcessEvent(evt):
                self.DrawOnParent(self._currentIndicator)
                return

        self.DrawOnParent(self._currentIndicator)
        self._currentIndicator.SetValue(value)

        evt = IndicatorChangedEvent(value=self._currentIndicator.GetValue())
        evt.SetEventObject(self)
        wx.PostEvent(self.GetParent(), evt)

#       self.DrawOnParent(self._currentIndicator) ###########################

        self.RequestRedraw()

    # End SetIndicatorValue
    #-------------------------------------------------------------------------


    def GetIndicator(self, mousePos):
        """Return the indicator located at the mouse position mousePos (if any)."""

        for indicator in self._indicators:
            if indicator.GetRect().Contains(mousePos):
                self._currentIndicator = indicator
                break

    # End GetIndicator
    #-------------------------------------------------------------------------


    def GetCurrentIndicator(self, idx):
        """Return the indicator given its idx."""

        self._currentIndicator = None
        for indicator in self._indicators:
            if indicator.GetId() == idx:
                self._currentIndicator = indicator
                break

    # End GetCurrentIndicator
    #-------------------------------------------------------------------------


    def GetIndicatorFromId(self, idx):
        """Return the indicator of an Id."""

        for indicator in self._indicators:
            if indicator.GetId() == idx:
                return indicator

        return None

    # End GetIndicatorFromId
    #-------------------------------------------------------------------------


    def GetIndicators(self):
        """Return the indicators."""

        return self._indicators

    # End GetIndicators
    #-------------------------------------------------------------------------


    def AddIndicator(self, idx, value):
        """
        Adds an indicator to RulerCtrl. You should pass a unique id and a starting
        value for the indicator.
        """

        self._indicators.append(Indicator(self, idx, value))
        self.RequestRedraw()

    # End AddIndicator
    #-------------------------------------------------------------------------


    def RemoveIndicator(self, idx):
        """
        Removes an indicator to RulerCtrl. You should pass the unique id of the indicator.
        """

        if idx in self._indicators:
            self._indicators.remove(idx)
        self.RequestRedraw()

    # End RemoveIndicator
    #-------------------------------------------------------------------------


    def SetIndicatorColour(self, idx, colour=None):
        """Change the color of all indicators."""

        if colour is None:
            colour = wx.BLUE

        for indicator in self._indicators:
            if indicator.GetId() == idx:
                indicator.SetColour(colour)
                break

        self.RequestRedraw()

    # End SetIndicatorColour
    #-------------------------------------------------------------------------


    #-------------------------------------------------------------------------
    # Look & style
    #-------------------------------------------------------------------------


    def SetTicksColour(self, colour):
        """Sets the color of ticks."""

        if colour != self._tickcolor:
            self._tickcolor = colour
            self._tickpen   = wx.Pen(colour, 1, wx.SOLID)
            self.RequestRedraw()

    # End SetTicksColour
    #-------------------------------------------------------------------------


    def GetFlip(self):
        """Return true if the orientation of the tick marks is reversed."""

        return self._flip

    # End GetFlip
    #-------------------------------------------------------------------------


    def SetFlip(self, flip=True):
        """Sets whether the orientation of the tick marks should be reversed."""

        # If this is True, the orientation of the tick marks is reversed from
        # the default eg. above the line instead of below

        if self._flip != flip:
            self._flip = flip
            for indicator in self._indicators:
                indicator.RotateImage()
            self.RequestRedraw()

    # End SetFlip
    #-------------------------------------------------------------------------


    def SetFont(self, font):
        """Sets the fonts for minor and major tick labels."""

        spControl.SetFont( self, font )
        fontsize = max(FONT_SIZE_MIN,int( 0.7 * self._font.GetPointSize() ))
        self._minorfont.SetPointSize( fontsize )

        self.RequestRedraw()

    #-------------------------------------------------------------------------


    def SetDrawingParent(self, dparent):
        """Sets the window to which RulerCtrl draws a thin line over."""

        self._drawingparent = dparent
        self.RequestRedraw()

    #-------------------------------------------------------------------------


    def GetDrawingParent(self):
        """Return the window to which RulerCtrl draws a thin line over."""

        return self._drawingparent


    #-------------------------------------------------------------------------



    # -----------------------------------------------------------------------
    # Callbacks
    # -----------------------------------------------------------------------


    def OnMouseEvents(self, event):
        """Handles the wx.EVT_MOUSE_EVENTS event for RulerCtrl."""

        if not self._indicators:
            event.Skip()
            return

        mousePos = event.GetPosition()

        if event.LeftDown():
            self.GetIndicator(mousePos)
            self.SetIndicatorValue(False, mousePos.x , mousePos.y)

        elif event.Dragging():
            if self._currentIndicator is not None:
                self.SetIndicatorValue(True, mousePos.x , mousePos.y)

        elif event.LeftUp():
            self.SetIndicatorValue(False, mousePos.x , mousePos.y)
            self._currentIndicator = None

        else:
            if self._currentIndicator is not None:
                self.SetIndicatorValue(False, mousePos.x , mousePos.y)
            self._currentIndicator = None

        event.Skip()

    # End OnMouseEvents
    # -----------------------------------------------------------------------


    #-------------------------------------------------------------------------
    # Painting
    #-------------------------------------------------------------------------


    def DrawPane(self, dc, x,y, w,h):
        """
        Override. Draw an empty pane.

        @param dc (PaintDC, MemoryDC, BufferedDC...)
        @param x,y (int,int) are coord. of top left corner from which drawing
        @param w,h (int,int) are width and height available for drawing.

        """
        pass

    # End DrawPane
    # -----------------------------------------------------------------------


    def DrawContent(self, dc, x,y, w,h):
        """
        Draw the ruler on the DC.

        @param dc (PaintDC, MemoryDC, BufferedDC...)
        @param x,y (int,int) are coord. of top left corner from which drawing
        @param w,h (int,int) are width and height available for drawing.

        """
        self._majorlabels = []
        self._minorlabels = []
        self._bits = []
        self._userbits = []
        self._userbitlen = 0
        self.Update(dc)

        dc.SetTextForeground( self._textcolor )
        dc.SetPen( self._tickpen )

        # Line at top or bottom depending on the flip.
        if self._flip is True:
            dc.DrawLine(x, y, x + w, y)
        else:
            dc.DrawLine(x, y + h - 1, x + w, y + h - 1)

        # Draw major ticks
        dc.SetFont( self._font )
        for label in self._majorlabels:
            pos = label.pos

            if self._flip:
                dc.DrawLine(x + pos, y,
                            x + pos, y + TICK_HEIGHT)
            else:
                dc.DrawLine(x + pos, y + h - TICK_HEIGHT,
                            x + pos, y + h)

            if label.text != "":
                dc.DrawText(label.text, label.lx, label.ly)

        # Draw minor ticks
        dc.SetFont(self._minorfont)
        for label in self._minorlabels:
            pos = label.pos

            if self._flip:
                dc.DrawLine(x + pos, y,
                            x + pos, y + int(TICK_HEIGHT/2))
            else:
                dc.DrawLine(x + pos, h - int(TICK_HEIGHT/2),
                            x + pos, h)

            if label.text != "":
                dc.DrawText(label.text, label.lx, label.ly)

        for indicator in self._indicators:
            indicator.Draw(dc)


    def DrawOnParent(self, indicator):
        """Actually draws the thin line over the drawing parent window."""

        if not self._drawingparent:
            return

        xpos, ypos = indicator.GetPosition()
        parentrect = self._drawingparent.GetClientRect()

        dc = wx.ScreenDC()
        dc.SetLogicalFunction(wx.INVERT)
        dc.SetPen( self._fgpen )
        dc.SetBrush(wx.TRANSPARENT_BRUSH)

        imgx, imgy = indicator.GetImageSize()

        x1 = xpos + imgx/2
        y1 = parentrect.y + ypos + imgy
        x2 = x1
        y2 = y1 + parentrect.height - imgy
        x1, y1 = self.ClientToScreenXY(x1, y1)
        x2, y2 = self.ClientToScreenXY(x2, y2)

        dc.DrawLine(x1, y1, x2, y2)
        dc.SetLogicalFunction(wx.COPY)


    def DrawGridOnParent(self, xpos, ypos):
        """TO BE DEBUGGED. Actually draws a thin dotted gray line over the drawing parent window."""

        if not self._drawingparent:
            return

        parentrect = self._drawingparent.GetClientRect()

        dc = wx.ScreenDC()
        dc.SetLogicalFunction(wx.INVERT)
        dc.SetPen(wx.Pen(wx.Colour(110,120,110), 1, wx.LONG_DASH))
        dc.SetBrush(wx.TRANSPARENT_BRUSH)

        (w,h) = self.GetDrawingSize()
        imgx, imgy = xpos, h

        x1 = xpos + imgx/2
        y1 = parentrect.y + ypos + imgy
        x2 = x1
        y2 = y1 + parentrect.height - imgy
        x1, y1 = self.ClientToScreenXY(x1, y1)
        x2, y2 = self.ClientToScreenXY(x2, y2)

        dc.DrawLine(x1, y1, x2, y2)
        dc.SetLogicalFunction(wx.COPY)


    # ================================================


    def FindLinearTickSizes(self, UPP):
        """Used internally."""

        # Given the dimensions of the ruler, the range of values it
        # has to display figure out how many units are in one Minor tick, and
        # in one Major tick.
        #
        # The goal is to always put tick marks on nice round numbers
        # that are easy for humans to grok.  This is the most tricky
        # with time.

        # As a heuristic, we want at least 16 pixels between each minor tick
        units = 16.0*abs(UPP)
        d = 0.000001
        self._digits = 6

        while 1:
            if units < d:
                self._minor = d
                self._major = d*5.0
                return

            d = d*5.0
            if units < d:
                self._minor = d
                self._major = d*2.0
                return

            d = d*2.0
            self._digits = self._digits - 1


    def LabelString(self, d, major=None):
        """Used internally."""

        # Given a value, turn it into a string.  The number of digits of
        # accuracy depends on the resolution of the ruler,
        # i.e. how far zoomed in or out you are.

        s = ""

        if d < 0.0 and d + self._minor > 0.0:
            d = 0.0

        if self._minor >= 1.0:
            s = "%d" % int(math.floor(d+0.5))
        else:
            s = (("%." + str(self._digits) + "f") % d).strip()

        return s


    def Tick(self, dc, pos, d, major):
        """Tick a particular position."""

        (x,y) = self.GetDrawingPosition()
        (w,h) = self.GetDrawingSize()

        if major:
            label = RulerLabel()
            self._majorlabels.append(label)
        else:
            label = RulerLabel()
            self._minorlabels.append(label)

        label.pos = pos
        label.lx =  -2000  # don't display
        label.ly =  -2000  # don't display
        label.text = ""

        if major:
            dc.SetFont( self._font )
        else:
            dc.SetFont( self._minorfont )

        l = self.LabelString(d, major)
        strw, strh = dc.GetTextExtent(l)

        strlen = strw
        strpos = pos - strw/2
        if strpos < 0:
            strpos = 0
        if strpos + strw >= w:
            strpos = w - strw
        strleft = x + strpos
        if self._flip is True:
            strtop = y + TICK_HEIGHT
            self._maxheight = max(self._maxheight, h - TICK_HEIGHT)
        else:
            strtop = h - strh - TICK_HEIGHT
            self._maxheight = max(self._maxheight, strh + TICK_HEIGHT)


        # See if any of the pixels we need to draw this label is already covered

        #if major and self._labelmajor or not major and self._labelminor:
        for ii in xrange(strlen):
            if self._bits[strpos+ii]:
                return

        # If not, position the label and give it text
        label.lx = strleft
        label.ly = strtop
        label.text = l

        if major:
            #if self._tickmajor and not self._labelmajor:
            #    label.text = ""
            self._majorlabels[-1] = label

        else:
            #if self._tickminor and not self._labelminor:
            #    label.text = ""
            #label.text = label.text.replace(self._units, "")
            self._minorlabels[-1] = label

        # And mark these pixels, plus some surrounding
        # ones (the spacing between labels), as covered

        #if (not major and self._labelminor) or (major and self._labelmajor):

        leftmargin = LABEL_SPACING

        if strpos < leftmargin:
            leftmargin = strpos

        strpos = strpos - leftmargin
        strlen = strlen + leftmargin

        rightmargin = LABEL_SPACING

        if strpos + strlen > w - 2: #self._spacing:
            rightmargin = w - strpos - strlen

        strlen = strlen + rightmargin

        for ii in xrange(strlen):
            self._bits[strpos+ii] = 1


    def Update(self, dc):
        """Updates all the ticks calculations."""

        # This gets called when something has been changed
        # (i.e. we've been invalidated).  Recompute all
        # tick positions.
        (w,h) = self.GetDrawingSize()

        self._maxwidth  = w
        self._maxheight = 0

        self._bits = [0]*(w+self._infopanew+1)
        self._middlepos = []

        if self._userbits:
            for ii in xrange(w):
                self._bits[ii] = self._userbits[ii]
        else:
            for ii in xrange(w):
                self._bits[ii] = 0

        UPP = (self._maxtime - self._mintime)/float(w)  # Units per pixel
        self.FindLinearTickSizes(UPP)

        # Zero (if it's in the middle somewhere)
        if self._mintime*self._maxtime < 0.0:
            mid = int(w*(self._mintime/(self._mintime-self._maxtime)) + 0.5)
            self.Tick(dc, mid, 0.0, major=True)

        sg = ((UPP > 0.0) and [1.0] or [-1.0])[0]

        # Major ticks
        d = self._mintime - UPP/2
        lastd = d
        majorint = int(math.floor(sg*d/self._major))
        ii = -1

        while ii <= w:
            ii = ii + 1
            lastd = d
            d = d + UPP

            if int(math.floor(sg*d/self._major)) > majorint:
                majorint = int(math.floor(sg*d/self._major))
                self.Tick(dc, ii, sg*majorint*self._major, major=True)

        # Minor ticks
        d = self._mintime - UPP/2
        lastd = d
        minorint = int(math.floor(sg*d/self._minor))
        ii = -1

        while ii <= w:
            ii = ii + 1
            lastd = d
            d = d + UPP

            if int(math.floor(sg*d/self._minor)) > minorint:
                minorint = int(math.floor(sg*d/self._minor))
                self.Tick(dc, ii, sg*minorint*self._minor, major=False)


    #-------------------------------------------------------------------------
    # Private
    #-------------------------------------------------------------------------


    def __initializeMembers(self):
        """Initialize all members."""

        #  Display a vertical line on the parent while moving an indicator.
        self._drawingparent = None

        # from top to bottom, or from bottom to top.
        self._flip = False

        # Arrows on the ruler
        self._indicators = []
        self._currentIndicator = None

        # Text indicating values
        self._majorlabels = []
        self._minorlabels = []

        self._bits = []
        self._userbits = []
        self._userbitlen = 0

    # End InitializeMembers
    #-------------------------------------------------------------------------


    def __initializeColours(self):
        """Create the pens and brush with default colors."""

        self._tickcolor = self._fgcolor
        self._tickpen   = wx.Pen(self._fgcolor, 1, wx.SOLID)

    # End InitializeColours
    #-------------------------------------------------------------------------


    def __initializeFonts(self):
        """Create the fonts."""

        self._fontsizeauto = True
        self.AutoAdjustFont()

        self._minorfont = self._font
        fontsize = max(FONT_SIZE_MIN,int( 0.7 * self._font.GetPointSize() ))
        self._minorfont.SetPointSize( fontsize )

        #if wx.Platform == "__WXMAC__":
        #    self._minorfont.SetNoAntiAliasing(True)

    # End InitializeFonts
    #-------------------------------------------------------------------------




# ---------------------------------------------------------------------------


class TimeRulerCtrl( RulerCtrl ):
    """
    A specific RulerCtrl indicating 3 indicators:
         - one for the player,
         - two for the time selection.
    """

    def __init__(self, parent, id, pos, size):
        RulerCtrl.__init__(self, parent, id, pos=pos, size=size)

        # First indicator is used by the player to indicate the playing position
        idx = wx.NewId()
        self._playerind = self.AddIndicator(idx, self._mintime)
        self.SetIndicatorColour(idx, wx.GREEN)

        # Second and Third indicators are used to indicate a selection range
        idx = wx.NewId()
        self.AddIndicator(idx, self._mintime)
        self.SetIndicatorColour(idx, wx.BLUE)

        idx = wx.NewId()
        self.AddIndicator(idx, self._mintime)
        self.SetIndicatorColour(idx, wx.BLUE)

    # End __init__
    #------------------------------------------------------------------------


    #------------------------------------------------------------------------
    # Player indicator
    #------------------------------------------------------------------------


    def GetPlayerIndicatorValue(self):
        """Return the value of the player indicator."""

        return self._indicators[0].GetValue()


    def SetPlayerIndicatorValue(self, v):
        """Set the value of the player indicator."""

        self._indicators[0].SetValue(v)


    #------------------------------------------------------------------------
    # Period Selection indicator
    #------------------------------------------------------------------------


    def GetSelectionIndicatorValues(self):
        """Return the selection interval."""

        minv = self.GetSelectionIndicatorMinValue()
        maxv = self.GetSelectionIndicatorMaxValue()
        return minv,maxv


    def GetSelectionIndicatorMinValue(self):
        """Return the selection min value."""

        # which is the min indicator?
        i = self._getmin()
        # set the new value
        return self._indicators[i].GetValue()


    def GetSelectionIndicatorMaxValue(self):
        """Return the selection max value."""

        # which is the min indicator?
        i = self._getmax()
        # set the new value
        return self._indicators[i].GetValue()


    def SetSelectionIndicatorValues(self, minv, maxv):
        """Move selection indicators to minv and maxv."""

        # which is the min indicator?
        i = self._getmin()
        # which is the max indicator?
        j = self._getmax()

        logging.debug('SetSelectionIndicatorValues from %f to %f'%(self._indicators[i].GetValue(),self._indicators[j].GetValue()))

        # set the new value
        self._indicators[i].SetValue(minv)
        # set the new value
        self._indicators[j].SetValue(maxv)

    #------------------------------------------------------------------------


    #------------------------------------------------------------------------
    # Private...
    #------------------------------------------------------------------------

    def _getmin(self):
        if self._indicators[1].GetValue() <= self._indicators[2].GetValue():
            return 1
        return 2

    def _getmax(self):
        if self._indicators[2].GetValue() >= self._indicators[1].GetValue():
            return 2
        return 1

    #------------------------------------------------------------------------

# ---------------------------------------------------------------------------
