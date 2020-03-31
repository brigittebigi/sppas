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

    src.ui.phoenix.windows.datactrls.pointctrlold.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""

import wx
import random
import wx.lib.newevent

from sppas.src.anndata import sppasPoint
from sppas.src.utils import b


def CreateCursorFromXPMData(xpm_data, hot_spot):
    """Return a wx.Cursor from a vectorized image.

    """
    d = list()
    for line in xpm_data:
        d.append(b(line))

    # get cursor image
    bmp = wx.Bitmap(d)
    image = wx.ImageFromBitmap(bmp)

    # since this image didn't come from a .cur file,
    # tell it where the hot spot is
    # image.SetOptionInt(wx.IMAGE_OPTION_CUR_HOTSPOT_X, hot_spot)
    # image.SetOptionInt(wx.IMAGE_OPTION_CUR_HOTSPOT_Y, hot_spot)

    # make the image into a cursor
    return wx.CursorFromImage(image)


def LightenColor(crColor, byIncreaseVal):
    """Lightens a colour."""

    byRed = crColor.Red()
    byGreen = crColor.Green()
    byBlue = crColor.Blue()

    byRed = (byRed + byIncreaseVal <= 255 and [byRed + byIncreaseVal] or [255])[0]
    byGreen = (byGreen + byIncreaseVal <= 255 and [byGreen + byIncreaseVal] or [255])[0]
    byBlue = (byBlue + byIncreaseVal <= 255 and [byBlue + byIncreaseVal] or [255])[0]

    return wx.Colour(byRed, byGreen, byBlue)


def DarkenColor(crColor, byReduceVal):
    """Darkens a colour."""

    byRed   = crColor.Red()
    byGreen = crColor.Green()
    byBlue  = crColor.Blue()

    byRed   = (byRed >= byReduceVal and [byRed - byReduceVal] or [0])[0]
    byGreen = (byGreen >= byReduceVal and [byGreen - byReduceVal] or [0])[0]
    byBlue  = (byBlue >= byReduceVal and [byBlue - byReduceVal] or [0])[0]

    return wx.Colour(byRed, byGreen, byBlue)


def ContrastiveColour(crColor):
    """Return a contrastive (ie lighten or darken) color."""

    byRed   = crColor.Red()
    byGreen = crColor.Green()
    byBlue  = crColor.Blue()

    if byRed+byGreen+byBlue < 191:
        return LightenColor(crColor, random.sample(range(15,30),1)[0])

    if byRed+byGreen+byBlue < 382:
        return LightenColor(crColor, random.sample(range(40,60),1)[0])

    if byRed+byGreen+byBlue < 510:
        return DarkenColor(crColor, random.sample(range(15,30),1)[0])

    return DarkenColor(crColor, random.sample(range(40,60),1)[0])

# ----------------------------------------------------------------------------
# Constants
# ----------------------------------------------------------------------------


MIN_W = 3
MIN_H = 6

COLOUR_MID = wx.Colour(20, 20, 20)
COLOUR_RADIUS = wx.Colour(170, 170, 250)

STYLE = wx.NO_BORDER | wx.NO_FULL_REPAINT_ON_RESIZE

# ----------------------------------------------------------------------------
# Events
# ----------------------------------------------------------------------------

# While the point is moving, the event is sent,
# with the new position as attribute.

PointMovingEvent, spEVT_MOVING = wx.lib.newevent.NewEvent()
PointMovingCommandEvent, spEVT_MOVING_COMMAND = wx.lib.newevent.NewCommandEvent()

PointMovedEvent, spEVT_MOVED = wx.lib.newevent.NewEvent()
PointMovedCommandEvent, spEVT_MOVED_COMMAND = wx.lib.newevent.NewCommandEvent()

# While the point is resizing, the event is sent,
# with the new position and the new size as attribute.

PointResizingEvent, spEVT_RESIZING = wx.lib.newevent.NewEvent()
PointResizingCommandEvent, spEVT_RESIZING_COMMAND = wx.lib.newevent.NewCommandEvent()

PointResizedEvent, spEVT_RESIZED = wx.lib.newevent.NewEvent()
PointResizedCommandEvent, spEVT_RESIZED_COMMAND = wx.lib.newevent.NewCommandEvent()

# While the point is clicked with the left button, the event is sent,
# without attribute.

PointLeftEvent, spEVT_POINT_LEFT = wx.lib.newevent.NewEvent()
PointLeftCommandEvent, spEVT_POINT_LEFT_COMMAND = wx.lib.newevent.NewCommandEvent()

# ----------------------------------------------------------------------------
# Pixmaps
# ----------------------------------------------------------------------------

cursor_move = [
"16 16 2 1",
" 	c None",
".	c #000000",
"       ..       ",
"       ..       ",
"       ..       ",
"       ..       ",
"   .   ..   .   ",
"  ..   ..   ..  ",
" ..... .. ..... ",
"...... .. ......",
"...... .. ......",
" ..... .. ..... ",
"  ..   ..   ..  ",
"   .   ..   .   ",
"       ..       ",
"       ..       ",
"       ..       ",
"       ..       "
]

cursor_expand = [
"16 16 2 1",
" 	c None",
".	c #000000",
"      .  .      ",
"      .  .      ",
"     ..  ..     ",
"    ...  ...    ",
"   ....  ....   ",
"  .....  .....  ",
" ......  ...... ",
".......  .......",
".......  .......",
" ......  ...... ",
"  .....  .....  ",
"   ....  ....   ",
"    ...  ...    ",
"     ..  ..     ",
"      .  .      ",
"      .  .      "
]

# ---------------------------------------------------------------------------


class PointCtrl(wx.Window):
    """Used to display a sppasPoint instance.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2020  Brigitte Bigi

    PointCtrl implements a vertical line that can be placed anywhere to any
    wxPython widget.

    It represents a sppasPoint of an annotation, defined by both:
        
        - a midpoint value m (float),
        - a radius value r (float).

    A PointCtrl displays the interval [m-r,m+r],
    and fill with a gradient color from the midpoint to the bounds.

    """

    def __init__(self, parent, 
                 id=wx.ID_ANY,
                 pos=wx.DefaultPosition,
                 size=wx.DefaultSize,
                 point=None):
        """PointCtrl constructor.
        
        Notice that each change of the object implies a refresh.

        Non-wxpython related parameters:

        @param point (TimePoint) the TimePoint to be represented,
        indicating the midpoint value and the radius value.
        point will only be used to display the time values in the
        tooltip. It is never modified.

        """

        wx.Window.__init__(self, parent, id, pos, size, STYLE)
        self.SetBackgroundStyle(wx.BG_STYLE_CUSTOM)
        self.SetDoubleBuffered(True)

        # Members, Initializations
        self._point = point
        self.SetToolTip(wx.ToolTip(self.__tooltip()))
        self.Reset(size)

        # Allows to move/resize the PointCtrl
        self._ml_dragging = None         # left button + mouse moving
        self._shift_ml_dragging = None   # shift key + left button + mouse moving
        self._starting = None

        # Bind the events related to our control
        wx.EVT_PAINT(self, self.OnPaint)
        wx.EVT_ERASE_BACKGROUND(self, lambda event: None)
        wx.EVT_MOUSE_EVENTS(self, self.OnMouseEvents)

    # -----------------------------------------------------------------------

    def Reset(self, size=None):
        """Reset all members to their default.

        @param size (wx.Size)

        """
        self.__initializeColours()
        self.__initializeCursors()
        if size:
            self.__initialSize(size)

    # -----------------------------------------------------------------------
    # Members: Getters and Setters
    # -----------------------------------------------------------------------

    def SetValue(self, point):
        """Set the TimePoint member.

        @param point (TimePoint) the TimePoint to be represented, indicating
        the midpoint value and the radius value.

        """
        if point != self._point:
            self._point = point
            self.SetToolTip(wx.ToolTip(self.__tooltip()))

    # -----------------------------------------------------------------------

    def GetValue(self):
        """Retrieve the point associated to the PointCtrl.

        @return TimePoint instance.

        """
        return self._point

    # -----------------------------------------------------------------------
    # Look & style
    # -----------------------------------------------------------------------

    def SetColours(self, colourmidpoint=None, colourradius=None):
        """Change the color settings of the PointCtrl.

        Repaint only if necessary.

        @param colourmidpoint (wx.Colour) Color to fill the center
        @param colourradius (wx.Colour) Color to fill the gradient

        """
        torepaint = False

        if colourmidpoint is not None and colourmidpoint != self._colourmidpoint:
            self._penmidpoint = wx.Pen(colourmidpoint, 1, wx.SOLID)
            self._colourmidpoint = colourmidpoint
            torepaint = True

        if colourradius is not None and colourradius != self._colourradius:
            self._penbounds = wx.Pen(ContrastiveColour(colourradius), 1, wx.SOLID)
            self._colourradius = colourradius
            torepaint = True

        if torepaint:
            self.Refresh()

    # -----------------------------------------------------------------------

    def SetWidth(self, width):
        """Change the width of the PointCtrl, only if necessary.

        Changing the width means that a different radius value was set to the
        TimePoint.

        @param width (int) is the new width.

        """
        if width < MIN_W:
            width = MIN_W
        if self.GetSize().width != width:
            self.SetSize(wx.Size(int(width), self.GetSize().height))
            self.Refresh()

    # -----------------------------------------------------------------------

    def GetWidth(self):
        """Return the current width.

        :returns: (int) the current width in pixels.

        """
        return self.GetSize().width

    # -----------------------------------------------------------------------

    def SetHeight(self, height):
        """Change the height of the PointCtrl.

        :param height: (int) is the new height.

        """
        if height < MIN_H:
            height = MIN_H
        if self.GetSize().height != height:
            self.SetSize(wx.Size(self.GetSize().width, int(height)))
            self.Refresh()

    # -----------------------------------------------------------------------

    def MoveWindow(self, pos, size):
        """Define a new position and/or size to display.

        :param pos: (wx.Point)
        :param size: (wx.Size)

        """
        (w, h) = size
        (x, y) = pos
        (ow, oh) = self.GetSize()
        (ox, oy) = self.GetPosition()

        if ow != w or oh != h:
            self.SetSize(size)
            self.Refresh()

        if ox != x or oy != y:
            self.SetPosition(pos)

    # -----------------------------------------------------------------------
    # Callbacks
    # -----------------------------------------------------------------------

    def OnMouseEvents(self, event):
        """Handles the wx.EVT_MOUSE_EVENTS event for PointCtrl."""

        if event.Entering():
            # change cursor to something else to denote possible event capture
            if self._highlight is False:
                self._highlight = True
                self.SetCursor(wx.StockCursor(wx.CURSOR_HAND))

        elif event.Leaving():
            if self._highlight is True:
                self._highlight = False
                self.SetCursor(wx.NullCursor)
                self._ml_dragging = None
                self._shift_ml_dragging = None

        elif event.LeftDown():
            self.OnMouseLeftDown(event)

        elif event.LeftUp():
            self.OnMouseLeftUp(event)

        elif event.ShiftDown() and event.Dragging():
            # SHIFT + moving while a button is pressed
            self.OnResize(event)

        elif event.Dragging():
            # moving while a button is pressed
            self.OnMouseDragging(event)

        wx.PostEvent(self.GetParent().GetEventHandler(), event)
        event.Skip()

    # -----------------------------------------------------------------------

    def OnMouseLeftDown(self, event):
        """Respond to mouse events."""

        self._ml_dragging = None
        self._shift_ml_dragging = None

        (x, y) = self.GetPosition()
        (ex, ey) = event.GetPosition()

        self._starting = x+ex
        if event.ShiftDown():
            self.SetCursor(self._cursorexpand)
            self._shift_ml_dragging = x + ex
            # logging.debug('PointCtrl. MouseLeftDown + Shift. %d'%self._shift_ml_dragging)
        else:
            self.SetCursor(self._cursormove)
            self._ml_dragging = x + ex
            # logging.debug('PointCtrl. MouseLeftDown. %d'%self._ml_dragging)

    # -----------------------------------------------------------------------

    def OnMouseLeftUp(self, event):
        """Respond to mouse events.

        Send spEVT_MOVED to the parent.

        """
        (x, y) = self.GetPosition()
        (ex, ey) = event.GetPosition()
        self.SetCursor(wx.NullCursor)

        # just clicked
        if (self._ml_dragging is not None and self._ml_dragging == self._starting) or \
           (self._shift_ml_dragging is not None and self._shift_ml_dragging == self._starting):
            evt = PointLeftEvent()
            evt.SetEventObject(self)
            wx.PostEvent(self.GetParent(), evt)
            return

        self._ml_dragging = None
        self._shift_ml_dragging = None
        self._starting = None
        # send the event to the parent.
        # the parent will decide what to do!

        if self._ml_dragging is not None:
            evt = PointMovedEvent(pos=wx.Point(x, y))
            evt.SetEventObject(self)
            wx.PostEvent(self.GetParent(), evt)

        if self._shift_ml_dragging is not None:
            evt = PointResizedEvent(pos=self.GetPosition(), size=self.GetSize())
            evt.SetEventObject(self)
            wx.PostEvent(self.GetParent(), evt)

    # -----------------------------------------------------------------------

    def OnMouseDragging(self, event):
        """Respond to mouse events."""
        x, y = self.GetPosition()     # absolute
        ex, ey = event.GetPosition()  # relative

        if self._ml_dragging is None:
            self.SetCursor(self._cursormove)
            self._ml_dragging = x

        shift = x + ex - self._ml_dragging
        #logging.debug('PointCtrl. MouseDragging. -->> x=%d ; ex=%d ; ml_dragging=%d, shift=%d '%(x,ex,self._ml_dragging,shift))

        if shift != 0:
            self._ml_dragging = self._ml_dragging + shift
            newx = x + shift
            # send the event to the parent.
            # the parent will decide what to do!
            evt = PointMovingEvent(pos=wx.Point(newx, y))
            evt.SetEventObject(self)
            wx.PostEvent(self.GetParent(), evt)

    # -----------------------------------------------------------------------

    def OnResize(self, event):
        """Respond to mouse events: dragging."""

        x, y = self.GetPosition()    # absolute
        ex, ey = event.GetPosition() # relative
        (w, h) = self.GetSize()

        direction = 2  # must be an even number, not odd
        if self._shift_ml_dragging is None:
            self._shift_ml_dragging = x

        if (self._shift_ml_dragging-x-ex) > 0:
            direction = -direction

        if direction > 0 or w > 2:
            self._shift_ml_dragging = self._shift_ml_dragging + (direction/2)
            # send the event to the parent.
            # the parent will decide what to do!
            p = wx.Point(x-(direction/2), y)
            s = wx.Size(w+direction, h)
            evt = PointResizingEvent(pos=p, size=s)
            evt.SetEventObject(self)
            wx.PostEvent(self.GetParent(), evt)

    # -----------------------------------------------------------------------
    # Painting
    # -----------------------------------------------------------------------

    def OnPaint(self, event):
        """Handles the wx.EVT_PAINT event for PointCtrl."""
        dc = wx.BufferedPaintDC(self)
        self.Draw(dc)

    # -----------------------------------------------------------------------

    def Draw(self, dc):
        """Draw the PointCtrl on the DC.

        @param dc (wx.DC) The device context to draw on.

        """
        # Get the actual client size of ourselves
        w, h = self.GetClientSize()

        # Nothing to do, we still don't have dimensions!
        if w*h == 0:
            return

        # Initialize the DC
        dc.SetBackgroundMode(wx.TRANSPARENT)
        dc.Clear()

        # If highlighted
        if self._highlight is True:
            c1 = self._colourradius
            c2 = self._colourmidpoint
        else:
            c1 = self._colourmidpoint
            c2 = self._colourradius

        if w > 5:
            mid = int(w / 2)
            box_rect = wx.Rect(0, 0, mid, h)
            dc.GradientFillLinear(box_rect, c2, c1, wx.EAST)
            box_rect = wx.Rect(mid, 0, mid, h)
            dc.GradientFillLinear(box_rect, c2, c1, wx.WEST)
            dc.SetPen(self._penbounds)
            dc.DrawLine(0, 0, 0, h)
            dc.DrawLine(w-1, 0, w-1, h)
        else:
            dc.SetPen(self._penmidpoint)
            for i in range(w):
                dc.DrawLine(i, 0, i, h)

    # -----------------------------------------------------------------------
    # Private
    # -----------------------------------------------------------------------

    def __initializeColours(self):
        """Create the pens and brush with default colors."""

        self._highlight = False
        self._colourmidpoint = COLOUR_MID
        self._colourradius = COLOUR_RADIUS

        self._penmidpoint = wx.Pen(COLOUR_MID, 1, wx.SOLID)
        self._penbounds = wx.Pen(ContrastiveColour(COLOUR_RADIUS), 1, wx.SOLID)

    # -----------------------------------------------------------------------

    def __initializeCursors(self):
        """Create new cursors to be used while Moving or Resizing."""

        # Cursor while moving
        self._cursormove = CreateCursorFromXPMData(cursor_move, 8)

        # Cursor while resizing
        self._cursorexpand = CreateCursorFromXPMData(cursor_expand, 8)

    # -----------------------------------------------------------------------

    def __initialSize(self, size):
        """Initialize the size."""

        self.SetMinSize(wx.Size(MIN_W, MIN_H))
        if size:
            (w, h) = size
            if w < MIN_W:
                w = MIN_W
            if h < MIN_H:
                h = MIN_H
            self.SetSize(wx.Size(w, h))

    # -----------------------------------------------------------------------

    def __tooltip(self):
        """Set a tooltip string indicating the midpoint and the radius values."""

        if self._point is not None:
            if self._point.get_radius() is not None:
                return "Point: "+str(self._point.get_midpoint())+"\nRadius: "+str(self._point.get_radius())
            else:
                return "Point: " + str(self._point.get_midpoint())

        return "No point"

# ----------------------------------------------------------------------------
# Panels to test
# ----------------------------------------------------------------------------


class TestPanel(wx.Panel):

    def __init__(self, parent):
        super(TestPanel, self).__init__(
            parent,
            style=wx.BORDER_NONE | wx.WANTS_CHARS,
            name="Test PointCtrl")

        p1 = PointCtrl(self, pos=(50, 50), size=(10, 50),
                       point=sppasPoint(2.3))
