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
# File: labelctrl.py
# ---------------------------------------------------------------------------

__docformat__ = """epytext"""
__authors__ = """Brigitte Bigi (contact@sppas.org)"""
__copyright__ = """Copyright (C) 2011-2015  Brigitte Bigi"""

# ----------------------------------------------------------------------------
# Imports
# ---------------------------------------------------------------------------

import wx
import wx.lib.newevent

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

MIN_W = 2
MIN_H = 6

# transparent background by default, black font for the text
BG_COLOUR = None
FG_COLOUR = wx.BLACK

STYLE = wx.NO_BORDER | wx.NO_FULL_REPAINT_ON_RESIZE


# ---------------------------------------------------------------------------
# Class LabelCtrl
# ---------------------------------------------------------------------------

class LabelCtrl(wx.Window):
    """Used to display a Label (see anndata for details).
    
    @author:  Brigitte Bigi
    @contact: contact@sppas.org
    @license: GPL, v3

    LabelCtrl implements a static text label.

    """

    def __init__(self, parent, id=-1,
                 pos=wx.DefaultPosition,
                 size=wx.DefaultSize,
                 label=None):
        """LabelCtrl constructor.

        Notice that each change of the object implies a refresh.

        Non-wxpython related parameter:
            - label (Label) the Label of an annotation. It is never modified.

        """
        wx.Window.__init__(self, parent, id, pos, size, STYLE)
        self.SetBackgroundStyle(wx.BG_STYLE_CUSTOM)
        self.SetDoubleBuffered(True)

        # Members, Initializations
        self.Reset(size)

        self._label = label
        self._underlined = False
        # self.SetValue(label)

        # Bind the events related to our control
        wx.EVT_PAINT(self, self.OnPaint)
        wx.EVT_ERASE_BACKGROUND(self, lambda event: None)
        wx.EVT_MOUSE_EVENTS(self, self.OnMouseEvents)

    # -----------------------------------------------------------------------

    def Reset(self, size=None):
        """Reset all values to their default.

        @param size (wx.Size)

        """
        self.__initializeColours()
        self.__initializeStyle()
        if size:
            self.__initialSize(size)

    # -----------------------------------------------------------------------
    # Members: Getters and Setters
    # -----------------------------------------------------------------------

    def SetValue(self, label):
        """Set the label.

        @param label (Label)

        """
        # if not (label is self._label):
        #     self._label = label
        #     if self._label.GetSize() > 1:  # ambiguous label
        #         self._underlined = True
        #     else:
        #         self._underlined = False
        #    self.SetToolTip(wx.ToolTip(self.__tooltip()))

    # -----------------------------------------------------------------------

    def GetValue(self):
        """Retrieve the label associated to the LabelCtrl."""
        return self._label

    # -----------------------------------------------------------------------

    def SetUnderlined(self, underlined=False):
        """Sets if the label must be underlined.

        By default, an ambiguous label is systematically underlined.

        :param underlined: (Boolean) sets whether a label has to be underlined or not.

        """
        if underlined != self._underlined:
            self._underlined = underlined
            self.Refresh()

    # -----------------------------------------------------------------------

    def GetUnderlined(self):
        """Return whether a label has to be underlined or not."""
        return self._underlined

    # -----------------------------------------------------------------------

    def SetBold(self, bold=False):
        """Set if the label must be bold.

        :param bold: (Boolean) sets whether a label has to be bold or not.

        """
        if bold != self._bold:
            self._bold = bold
            self.Refresh()

    # -----------------------------------------------------------------------

    def GetBold(self):
        """Return whether the label has to be bold or not."""
        return self._bold

    # -----------------------------------------------------------------------

    def SetAlign(self, value=wx.ALIGN_CENTRE):
        """Fix the position of the label.

        @param value is one of wx.ALIGN_LEFT, wx.ALIGN_CENTRE or wx.ALIGN_RIGHT

        """
        if value != self._align:
            self._align = value
            self.Refresh()

    # -----------------------------------------------------------------------

    def GetAlign(self):
        """Return the label alignment value.

        :returns: one of wx.ALIGN_LEFT, wx.ALIGN_CENTRE or wx.ALIGN_RIGHT

        """
        return self._align

    # -----------------------------------------------------------------------
    # Look & style
    # -----------------------------------------------------------------------

    def SetColours(self, bgcolour=None, fontcolour=None):
        """Change the main colors of the LabelCtrl.

        :param bgcolour: (wx.Colour)   Background color
        :param fontcolour: (wx.Colour) Font color

        """
        if bgcolour is not None and bgcolour != self._bgcolour:
            self._bgcolour = bgcolour
            self._bgpen = wx.Pen(bgcolour, 1, wx.SOLID)
            self._bgbrush = wx.Brush(bgcolour, wx.SOLID)
            self.SetBackgroundColour(bgcolour)

        if fontcolour is not None and fontcolour != self.GetForegroundColour():
            self.SetForegroundColour(fontcolour)

    # -----------------------------------------------------------------------

    def SetFont(self, font):
        """Override. Set a new font."""
        if font != self.GetFont():
            wx.Window.SetFont(self, font)

    # -----------------------------------------------------------------------
    # Callbacks
    # -----------------------------------------------------------------------

    def OnMouseEvents(self, event):
        """Handle the wx.EVT_MOUSE_EVENTS event for PointCtrl."""
        if event.Entering() or event.Leaving():
            self._highlight = not self._highlight
            self.Refresh()

        wx.PostEvent(self.GetParent().GetEventHandler(), event)
        event.Skip()

    # -----------------------------------------------------------------------

    def SetHeight(self, height):
        """Change the height of the LabelCtrl.

        @param height (int) is the new height.

        """
        if height < MIN_H:
            height = MIN_H
        if self.GetSize().height != height:
            self.SetSize(wx.Size(self.GetSize().width, int(height)))
            #self.Refresh()

    # -----------------------------------------------------------------------

    def MoveWindow(self, pos, size):
        """Define a new position and/or size to display.

        Refresh only if something has changed.

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
            #self.Refresh()

    # -----------------------------------------------------------------------
    # Painting
    # -----------------------------------------------------------------------

    def OnPaint(self, event):
        """Handle the wx.EVT_PAINT event for LabelCtrl."""
        dc = wx.BufferedPaintDC(self)
        self.Draw(dc)

    # -----------------------------------------------------------------------

    def Draw(self, dc):
        """Draw the label on the DC, starting at (x,y).

        :param dc: (DC) Drawing Context of the LabelCtrl.

        """
        # Get the actual client size of ourselves
        w, h = self.GetClientSize()

        # Nothing to do, we still don't have dimensions!
        if not w or not h:
            return

        # Initialize
        if not self._bgcolour:
            dc.SetBackgroundMode(wx.TRANSPARENT)
        else:
            dc.SetBackgroundMode(wx.SOLID)
            dc.SetBackground(self._bgbrush)
            dc.SetTextBackground(self._bgcolour)
        dc.Clear()

        # Set the font with the expected style
        font_face = self.GetFont()
        font_face.SetUnderlined(self._underlined)
        if self._bold is True:
            font_face.SetWeight(wx.FONTWEIGHT_BOLD)
        else:
            font_face.SetWeight(wx.FONTWEIGHT_NORMAL)
        dc.SetFont(font_face)
        dc.SetTextForeground(self.GetForegroundColour())

        # Adjust position
        if self._label is not None:
            text_width, text_height = dc.GetTextExtent(self._label)
            if self._align == wx.ALIGN_LEFT:
                x = 0
            elif self._align == wx.ALIGN_RIGHT:
                x = max(1, w-text_width-1)
            else:
                x = (w-text_width)/2
            y = (h-text_height)/2
            dc.DrawText(self._label, x, y)

        # If highlighted
        if self._highlight is True:
            dc.SetPen(wx.BLACK_DASHED_PEN)
            dc.DrawLine(0, 0, w, 0)
            dc.DrawLine(0, h-1, w, h-1)

    # -----------------------------------------------------------------------
    # Private
    # -----------------------------------------------------------------------

    def __initializeStyle(self):
        """Initialize the label style."""

        self._align = wx.ALIGN_LEFT
        self._underlined = False
        self._bold = False
        self._highlight = False

    # -----------------------------------------------------------------------

    def __initializeColours(self):
        """Initialize the pens."""

        self._bgpen = wx.Pen(BG_COLOUR, 1, wx.SOLID)
        self._bgbrush = wx.Brush(BG_COLOUR, wx.SOLID)
        self._bgcolour = BG_COLOUR

        self.SetBackgroundColour(BG_COLOUR)
        self.SetForegroundColour(FG_COLOUR)

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
        """Set a tooltip string with the label."""

        if self._label is not None:
            #if self._label.GetSize() > 1:
            alltexts = self._label  #.GetLabels()
            #s = ""
            #for t in alltexts:
            #    s += t.Value + " (score=" + str(t.Score) + ")\n"
            #return s[:-1]
            return self._label
        return ""
