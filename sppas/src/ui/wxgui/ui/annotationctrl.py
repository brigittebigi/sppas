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
# File: annotationctrl.py
# ----------------------------------------------------------------------------

__docformat__ = """reST"""
__authors___  = """Brigitte Bigi (contact@sppas.org)"""
__copyright__ = """Copyright (C) 2011-2015  Brigitte Bigi"""

import logging
import wx
import wx.lib.newevent

from pointctrl import PointCtrl
from pointctrl import spEVT_MOVING
from pointctrl import MIN_W as pointctrlMinWidth

from labelctrl import LabelCtrl

# ----------------------------------------------------------------------------
# Constants
# ----------------------------------------------------------------------------

MIN_W = 4
MIN_H = 8

NORMAL_COLOUR = wx.Colour(0, 0, 0)
UNCERTAIN_COLOUR = wx.Colour(70, 70, 180)

STYLE = wx.NO_BORDER | wx.NO_FULL_REPAINT_ON_RESIZE

FONT_SIZE_MIN = 8
FONT_SIZE_MAX = 32

PANE_WIDTH_MIN = 10
PANE_WIDTH_MAX = 200
PANE_WIDTH = 100

BORDER_WIDTH = 2

# ----------------------------------------------------------------------------


class AnnotationCtrl(wx.Window):
    """This class is used to display an annotation.
    
    :author:  Brigitte Bigi
    :contact: contact@sppas.org
    :license: GPL, v3

    """
    def __init__(self, parent, id=wx.ID_ANY,
                 pos=wx.DefaultPosition,
                 size=wx.DefaultSize,
                 ann=None):
        """Constructor.

        Non-wxpython related parameters:

        :param ann: (sppasAnnotation) the annotation to be represented.

        The size is representing the available area to draw the annotation.
        The member _pxsec must be fixed for the annotation to draw inside this
        area. It represents the number of pixels required for 1 second.

        """
        self._pointctrl1 = None
        self._pointctrl2 = None
        self._labelctrl = None
        self._pxsec = 0  # the number of pixels to represent 1 second of time

        wx.Window.__init__(self, parent, id, pos, size, STYLE)
        self.SetBackgroundStyle(wx.BG_STYLE_CUSTOM)
        self.SetDoubleBuffered(True)

        # Members, Initializations
        self._ann = None
        if ann is not None:
            self.SetAnn(ann)
        self.Reset(size)

        # Bind the events related to our control
        wx.EVT_PAINT(self, self.OnPaint)
        wx.EVT_ERASE_BACKGROUND(self, lambda event: None)
        wx.EVT_MOUSE_EVENTS(self, self.OnMouseEvents)
        spEVT_MOVING(self, self.OnPointMoving)

    # ------------------------------------------------------------------------

    def Reset(self, size=None):
        """Reset all members to their default.

        @param size (wx.Size)

        """
        self._selected = False
        self.__initializeColours()
        if size:
            self.__initialSize(size)

    # ------------------------------------------------------------------------
    # Look & style
    # ------------------------------------------------------------------------

    def SetLabelFont(self, font):
        """Override. Set a new font."""

        if self._labelctrl:
            self._labelctrl.SetFont(font)

    # ------------------------------------------------------------------------

    def SetLabelAlign(self, value):
        """Fix the position of the text of an annotation.

        :param value: is one of wx.ALIGN_LEFT, wx.ALIGN_CENTRE or wx.ALIGN_RIGHT

        """
        if self._labelctrl:
            self._labelctrl.SetAlign(value)

    # ------------------------------------------------------------------------

    def SetPointColours(self, colourmidpoint=None, colourradius=None):
        """Change the main colors of the Points."""

        if self._pointctrl1:
            self._pointctrl1.SetColours(colourmidpoint, colourradius)
        if self._pointctrl2:
            self._pointctrl2.SetColours(colourmidpoint, colourradius)

    # ------------------------------------------------------------------------

    def SetLabelColours(self, bgcolour=None, fontnormalcolour=None, fontuncertaincolour=None):
        """Change the main colors of the Label.

        Notice that uncertain labels can be of a different color,
        like links in web browsers.

        :param bgcolour: (wx.Colour)
        :param fontcolour: (wx.Colour)
        :param fontuncertaincolour: (wx.Colour)

        """
        if self._labelctrl is None: return
        # if self._labelctrl.GetValue().GetSize() == 1:
        self._labelctrl.SetColours(bgcolour, fontnormalcolour)
        # else:
        #    self._labelctrl.SetColours(bgcolour, fontuncertaincolour)

    # ------------------------------------------------------------------------

    def SetBorderColour(self, colour):
        """Fix the color of the top/bottom lines."""
        self._penbordercolor = wx.Pen(colour, 1, wx.SOLID)

    # ------------------------------------------------------------------------

    def GetHeight(self):
        """Return the current height."""
        return self.GetSize().height

    # -----------------------------------------------------------------------

    def GetAnn(self):
        """Return the annotation to draw."""
        return self._ann

    # -----------------------------------------------------------------------

    def SetAnn(self, ann):
        """Set the annotation.

        @param ann (annotation)

        """
        loc = ann.get_location().get_best()
        if loc.is_interval():
            self._pointctrl1 = PointCtrl(self, id=-1, point=loc.get_begin())
            self._pointctrl2 = PointCtrl(self, id=-1, point=loc.get_end())
        elif loc.is_point():
            self._pointctrl1 = PointCtrl(self, id=-1, point=loc)
            self._pointctrl2 = None
        else:
            raise NotImplemented('Disjoint intervals are not supported yet!')

        l = ann.serialize_labels(separator=" ", empty="", alt=True)
        self._labelctrl = LabelCtrl(self, id=-1, label=l)
        self._ann = ann

    # ------------------------------------------------------------------------

    def SetPxSec(self, value):
        if value < 0:
            raise ValueError
        self._pxsec = int(value)
        self.Refresh()

    # ------------------------------------------------------------------------
    # Methods to move/resize objects
    # ------------------------------------------------------------------------

    def SetHeight(self, height):
        """Set the height (int).

        :param height: (int) in pixels

        """
        if height < MIN_H:
            height = MIN_H

        w, h = self.GetSize()
        if h != height:
            if self._labelctrl:
                self._labelctrl.SetHeight(height)
            self.SetSize(wx.Size(w, height))

    # ------------------------------------------------------------------------

    def MoveWindow(self, pos, size):
        """Define a new position and/or size to display.

        :param pos: (wx.Point)
        :param size: (wx.Size)

        """
        (w, h) = size
        (x, y) = pos
        (ow, oh) = self.GetSize()
        (ox, oy) = self.GetPosition()

        # New width
        if ow != w:
            if w < MIN_W:
                w = MIN_W
            self.SetSize(wx.Size(w, oh))

        # New height
        if oh != h:
            self.SetHeight(h)

        # New position (x and/or y)
        if ox != x or oy != y:
            self.Move(pos)

    # ------------------------------------------------------------------------

    # ------------------------------------------------------------------------
    # Callbacks
    # ------------------------------------------------------------------------

    def OnMouseEvents(self, event):
        """
        Handles the wx.EVT_MOUSE_EVENTS event for AnnotationCtrl.

        """

        if (event.Entering() and not self._selected) or \
           (event.Leaving() and self._selected):
            logging.debug(' event entering or leaving (selected=%s)'%self._selected)
            self._selected = not self._selected
            logging.debug('  --> (selected=%s)' % self._selected)
            #self.OnPaint(event)
            self.Refresh()

        wx.PostEvent(self.GetParent(), event)
        event.Skip()

    # -----------------------------------------------------------------------

    def OnPointMoving(self, event):
        logging.debug('ANNOTAION. OnPointMoving.')

        # which point is moving and what is new size?
        ptr = event.GetEventObject()
        (x, y) = event.pos
        (w, h) = ptr.GetSize()
        logging.debug(' ... point %s: x=%d,y=%d, w=%d,h=%d' % (ptr.GetValue(), x, y, w, h))

        # self coordinates
        sw, sh = self.GetClientSize()
        sx, sy = self.GetPosition()

        # get new time value
        b = ptr.get_midpoint() - ptr.get_radius()
        e = ptr.get_midpoint() + ptr.get_radius()
        logging.debug(' ... moving point %s: FROM b=%f,e=%f' % (ptr.GetValue(), b, e))
        logging.debug(' ... ... calcT=%f' % self._calcT(x))
        if x < 0:
            x = -x
            b = b - self._calcT(x)
        else:
            b = b + self._calcT(x)
        e = e + self._calcT(w)

        midpoint = b + ((e-b)/2.)
        logging.debug(' ... moving point %s: TO b=%f,e=%f' % (ptr.GetValue(), b, e))

        # Create a copy of the current point, then apply the modification.
        pointcopy = ptr.GetValue().Copy()
        pointcopy.SetMidpoint(midpoint)

        # try to fix the new point to this annotation
        try:
            if self._ann.get_location().get_best().is_point():
                self._ann.get_location().get_best().set(pointcopy)
            else:
                self._ann.get_location().get_best().set_begin(pointcopy)
            ptr.SetValue(pointcopy)
            if ptr is self._pointctrl1:
                sx = sx + event.pos.x
            sw = sw - event.pos.x
            logging.debug(' ---> new content sx=%d, sw=%d' % (sx, sw))
            self.MoveWindow(pos=(sx, sy), size=(sw, sh))
        except Exception as e:
            logging.debug(' ... Exception: %s' % e)
            pass

        self.GetTopLevelParent().GetStatusBar().SetStatusText('Point moving: %d' % sx)

    # ------------------------------------------------------------------------
    # Painting
    # ------------------------------------------------------------------------

    def OnPaint(self, event):
        """Handles the wx.EVT_PAINT event for AnnotationCtrl."""

        dc = wx.BufferedPaintDC(self)
        self.Draw(dc)

    # ------------------------------------------------------------------------

    def Draw(self, dc):
        """Draw the AnnotationCtrl on the DC.

        :param dc: (wx.DC) The device context to draw on.

        """
        logging.debug('AnnotationCtrl.Draw...')

        # Get the actual client size of ourselves
        # Notice that the size is corresponding to the available size on screen
        # for that annotation. It can often happen that the annotation-duration
        # is larger than the available width.
        w, h = self.GetClientSize()

        # Nothing to do, we still don't have dimensions!
        if w*h == 0:
            return

        # Initialize the DC
        dc.SetBackgroundMode(wx.TRANSPARENT)
        dc.Clear()

        x = 0
        y = 0
        if self._selected is True:
            # Draw borders: simply a rectangle
            self.DrawBorders(dc, w, h)

            # Update position and size for the points and the label
            x = BORDER_WIDTH
            y = BORDER_WIDTH
            w = w - (2 * BORDER_WIDTH)
            h = h - (2 * BORDER_WIDTH)

        # Content
        self.DrawContent(dc, x, y, w, h)

    # ------------------------------------------------------------------------

    def DrawContent(self, dc, x, y, w, h):
        """Draw the annotation on the DC.

        :param dc: (PaintDC, MemoryDC, BufferedDC...)
        :param x,y: (int,int) are coord. of top left corner from which drawing
        :param w,h: (int,int) are width and height available for drawing.

        """
        if self._ann is None:
            return

        # logging.debug('  Draw content for ann %s: x=%d,y=%d,  w=%d, h=%d' % (self._ann, x, y, w, h))

        wpt1 = max(pointctrlMinWidth, self._calcW(self._pointctrl1.GetValue().duration().get_margin()))
        if wpt1 > w:
            wpt1 = w

        if self._pointctrl2 is None:
            tw = min(50, self.__getTextWidth(self._labelctrl.GetValue())+2)
            if (wpt1+tw) > w:  # ensure to stay in our allocated area
                tw = w - wpt1  # reduce width to the available area
            tw = max(0, tw)
            self._labelctrl.MoveWindow(wx.Point(wpt1, y), wx.Size(tw, h))
        else:
            wpt2 = max(pointctrlMinWidth, self._calcW(self._pointctrl2.GetValue().duration().get_margin()))
            xpt2 = w-wpt2+1
            tx = x + wpt1
            tw = xpt2 - tx
            if (tx+tw) > w:            # ensure to stay in our allocated area
                tw = tw - ((tx+tw)-w)  # reduce width to the available area
            tw = max(0, tw)
            # logging.debug(' ...draw label: x=%d, w=%d' % (tx, tw))
            self._labelctrl.MoveWindow(wx.Point(tx, y), wx.Size(tw, h))
        self._labelctrl.Show()

        # Draw the points
        self._drawPoint(self._pointctrl1, x, y, wpt1, h)
        if self._pointctrl2 is not None:
            self._drawPoint(self._pointctrl2, xpt2, y, wpt2, h)

    # ------------------------------------------------------------------------

    def DrawBorders(self, dc, w, h):
        """Draw the borders on the DC.

        :param dc: (PaintDC, MemoryDC, BufferedDC...)
        :param x,y: (int,int) are coord. of top left corner from which drawing
        :param w,h: (int,int) are width and height available for drawing.

        """
        x = int(BORDER_WIDTH / 2)
        y = int(BORDER_WIDTH / 2)
        bw = w-BORDER_WIDTH
        bh = h-y

        dc.SetBackgroundMode(wx.TRANSPARENT)
        dc.Clear()

        dc.SetPen(self._penbordercolor)
        dc.SetBrush(wx.TRANSPARENT_BRUSH)
        dc.DrawRectangle(x, y, bw, bh)

    # ------------------------------------------------------------------------
    # Private
    # ------------------------------------------------------------------------

    def _drawPoint(self, point, x,y, w,h):
        """Display a point."""
        #logging.debug(' ...draw point: x=%d, w=%d'%(x,w))
        sw = self.GetSize().width
        # Do not draw if point is outsite the available area!
        if x > sw:
            point.Hide()
            return
        point.MoveWindow(wx.Point(x, y), wx.Size(w, h))
        point.Show()

    # ------------------------------------------------------------------------

    def __initializeColours(self):
        """Create the pens and brush with default colors."""

        self.SetBackgroundColour(self.GetParent().GetBackgroundColour())
        self._penbordercolor = wx.Pen(wx.RED, 2, wx.SOLID)

    # ------------------------------------------------------------------------

    def __initialSize(self, size):
        """Initialize the size."""

        self.SetMinSize(wx.Size(MIN_W, MIN_H))
        if size:
            (w, h) = size
            if w < MIN_W:
                w = MIN_W
            if h < MIN_H: h = \
                MIN_H
            self.SetSize(wx.Size(w, h))

    # ------------------------------------------------------------------------

    def _calcW(self, duration):
        return int(duration * float(self._pxsec))

    def _calcT(self, width):
        return float(width) / float(self._pxsec)

    # ------------------------------------------------------------------------

    def __getTextWidth(self, text):
        dc = wx.ClientDC(self)
        dc.SetFont(self.GetFont())
        return dc.GetTextExtent(text)[0]

# ----------------------------------------------------------------------------
# class BorderCtrl (un-used)
# ----------------------------------------------------------------------------


class BorderCtrl(wx.Window):
    """This class is used to display a border as an object.

    @author:  Brigitte Bigi
    @contact: contact@sppas.org
    @license: GPL, v3

    BorderCtrl implements a transparent rectangle line that can be placed
    anywhere to any wxPython widget.

    """
    def __init__(self, parent, id=wx.ID_ANY,
                 pos=wx.DefaultPosition,
                 size=wx.DefaultSize):
        """BorderCtrl constructor."""

        wx.Window.__init__(self, parent, id, pos, size, STYLE)

        self.SetBackgroundStyle(wx.BG_STYLE_CUSTOM)
        self.SetDoubleBuffered(True)

        # Members, Initializations
        self.Reset(size)

        # Bind the events related to our control
        wx.EVT_PAINT(self, self.OnPaint)
        wx.EVT_ERASE_BACKGROUND(self, lambda event: None)

    # ------------------------------------------------------------------------

    def Reset(self, size=None):
        """Reset all members to their default.

        :param size: (wx.Size)

        """
        self.__initializeColours()
        if size:
            self.__initialSize(size)

    # ------------------------------------------------------------------------

    def SetHeight(self, height):
        """
        Change the height of the PointCtrl.

        @param height (int) is the new height.

        """
        if self.GetSize().height != height:
            self.SetSize(wx.Size(self.GetSize().width, int(height)))
            self.Refresh()

    # ------------------------------------------------------------------------

    # ------------------------------------------------------------------------
    # Look & style
    # ------------------------------------------------------------------------

    def SetBorderColour(self, colour):
        """Fix the color of the border lines while annotation is highlighted."""

        self._penbordercolor = wx.Pen(colour, 1, wx.SOLID)
        self.Refresh()

    # ------------------------------------------------------------------------
    # Painting
    # ------------------------------------------------------------------------

    def OnPaint(self, event):
        """Handles the wx.EVT_PAINT event for PointCtrl."""

        dc = wx.BufferedPaintDC(self)
        self.Draw(dc)

    # ------------------------------------------------------------------------

    def Draw(self, dc):
        """Draw the BorderCtrl on the DC.

        :param dc: (wx.DC) The device context to draw on.

        """
        # Get the actual client size of ourselves
        # Notice that the size is corresponding to the available size on screen
        # for that annotation. It can often happen that the annotation-duration
        # is larger than the available width.
        w, h = self.GetClientSize()
        # Nothing to do, we still don't have dimensions!
        if w*h == 0:
            return

        x = int(BORDER_WIDTH / 2)
        y = int(BORDER_WIDTH / 2)
        w = w-x
        h = h-y

        # Initialize the DC
        dc.SetBackgroundMode(wx.TRANSPARENT)
        dc.Clear()

        # Top and Bottom lines
        dc.SetPen(self._penbordercolor)
        dc.SetBrush(wx.TRANSPARENT_BRUSH)
        dc.DrawRectangle(x, y, w, h)

    # ------------------------------------------------------------------------
    # Private
    # ------------------------------------------------------------------------

    def __initializeColours(self):
        """Create the pens and brush with default colors."""

        self._penbordercolor = wx.Pen(wx.RED, 2, wx.SOLID)

    # ------------------------------------------------------------------------

    def __initialSize(self, size):
        """Initialize the size."""

        mins = BORDER_WIDTH * 2

        self.SetMinSize(wx.Size(mins, mins))
        if size:
            (w, h) = size
            if w < mins:
                w = mins
            if h < mins:
                h = mins
            self.SetSize(wx.Size(w, h))
