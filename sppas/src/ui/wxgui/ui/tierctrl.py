# coding=UTF8
# Copyright (C) 2014  Brigitte Bigi
#
# This file is part of DataEditor.
#
# DataEditor is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# DataEditor is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with DataEditor.  If not, see <http://www.gnu.org/licenses/>.
#

import logging

import wx
import wx.lib.newevent

from sppas.src.anndata.aio.aioutils import serialize_labels

from sppas.src.ui.wxgui.cutils.textutils import TextAsNumericValidator
from sppas.src.ui.wxgui.cutils.colorutils import PickRandomColour, ContrastiveColour

from .spControl import spControl
from .pointctrl import PointCtrl
from .pointctrl import MIN_W as pointctrlMinWidth
from .labelctrl import LabelCtrl

# ----------------------------------------------------------------------------
# Constants
# ----------------------------------------------------------------------------

MIN_W = 2
MIN_H = 6

NORMAL_COLOUR = wx.Colour(20, 20, 20)
UNCERTAIN_COLOUR = wx.Colour(70, 70, 180)


class TierCtrl(spControl):
    """Used to display a Tier (see anndata for details).

    :author:  Brigitte Bigi
    :contact: contact@sppas.org
    :license: GPL

    """

    def __init__(self, parent, id=wx.ID_ANY,
                 pos=wx.DefaultPosition,
                 size=wx.DefaultSize,
                 tier=None):
        """Constructor.

        Non-wxpython related parameter:
            - tier (Tier) the Tier to draw.

        """
        self._tier = tier
        spControl.__init__(self, parent, id, pos, size)

        self.isselectable = False

        # Tier Members
        self._pointsctrl = list()
        self._labelsctrl = list()
        self._anns = {}  # To link the annotations to the displayed controls

        # disable margins (then handles)
        self._margins.Left = 0
        self._margins.Right = 0

        self._bgcolor = self.GetParent().GetBackgroundColour()
        self._bgpen   = wx.Pen(self._bgcolor, 1, wx.SOLID)
        self._bgbrush = wx.Brush(self._bgcolor, wx.SOLID)

        self._fgcolor = PickRandomColour(180,250)
        self._fgpen = wx.Pen(self._fgcolor, 1, wx.SOLID)
        self._fgbrush = wx.Brush(self._fgcolor, wx.SOLID)

        self._midpointcolor = wx.BLACK

        if self._tier is not None and self._tier.is_point():
            self._labelalign = wx.ALIGN_LEFT  # Label in each annotation
        else:
            self._labelalign = wx.ALIGN_CENTRE  # Label in each annotation
        self._labelbgcolor = self._fgcolor
        self._labelfgucolor = None   # uncertain label

        self._fontsizeauto = True
        self.AutoAdjustFont()

    # ------------------------------------------------------------------------
    # Members
    # ------------------------------------------------------------------------

    def GetTier(self):
        return self._tier

    # ------------------------------------------------------------------------

    def SetLabelAlign(self, value):
        """Fix the position of the text of an annotation.

        :param value: is one of wx.ALIGN_LEFT, wx.ALIGN_CENTRE or wx.ALIGN_RIGHT

        """
        if self._tier.is_point():
            return

        if self._labelalign != value:
            # Apply this new value to self.
            self._labelalign = value
            # propagate to all label controls
            for label in self._labelsctrl:
                label.SetAlign(value)

    # -----------------------------------------------------------------------

    def SetFont(self, font):
        """Override. Change the font of all texts (self and labels)."""

        # Apply this new font to self.
        spControl.SetFont(self, font)

        # propagate to all label controls
        for label in self._labelsctrl:
            label.SetFont(self._font)

    # -----------------------------------------------------------------------

    def SetLabelColours(self, bgcolour=None, fontnormalcolour=None, fontuncertaincolour=None):
        """Change the main colors of the Labels.

        :param bgcolour: (wx.Colour)
        :param fontcolour: (wx.Colour)
        :param fontuncertaincolour: (wx.Colour)

        Notice that uncertain labels are of a different color (like links in web browsers).

        """
        redraw = False

        if fontnormalcolour is not None:
            self.SetTextColour(fontnormalcolour)

        if fontuncertaincolour is not None:
            self._labelfgucolor = fontuncertaincolour
            redraw = True

        if bgcolour is not None and bgcolour != self._labelbgcolor:
            self._labelbgcolor = bgcolour

            for label in self._labelsctrl:
                #if label.GetValue().GetSize() == 1:
                label.SetColours(bgcolour, fontnormalcolour)
                #else:
                #    label.SetColours(bgcolour, fontuncertaincolour)

            for point in self._pointsctrl:
                point.SetColours(self._midpointcolor, colourradius=bgcolour)

            redraw = True

        if redraw:
            self.RequestRedraw()

    # -----------------------------------------------------------------------

    def SetPointColour(self, colourmidpoint=None):
        """
        Change the color of the PointCtrl. Only the midpoint can be fixed.
        The color of the radius depends on the tier background color.

        :param colourmidpoint: (wx.Colour)

        """

        if colourmidpoint is not None:
            self._midpointcolor = colourmidpoint

        for point in self._pointsctrl:
            point.SetColours(self._midpointcolor, colourradius=None)

    # -----------------------------------------------------------------------

    def GetLabelAlign(self):
        return self._labelalign

    # -----------------------------------------------------------------------

    def MoveWindow(self, pos, size):
        """Override. Define a new position and/or size to display.

        Ask to redraw only if something has changed.

        :param pos: (wx.Point)
        :param size: (wx.Size)

        """
        fsize = self._font.GetPointSize()
        spControl.MoveWindow(self, pos, size)

        # If MoveWindow has changed the font size:
        if self._fontsizeauto and fsize != self._font.GetPointSize():
            for label in self._labelsctrl:
                label.SetFont(self._font)

    # ------------------------------------------------------------------------

    def VertZoom(self, z):
        """
        Override. Apply a vertical zoom to the spControl.
        """
        f = self._font
        spControl.VertZoom(self, z)

        h = self.GetSize().height

        for point in self._pointsctrl:
            point.SetHeight(h)

        for label in self._labelsctrl:
            label.SetHeight(h)
            label.SetFont(self._font)

    # -----------------------------------------------------------------------

    def SetHeight(self, height):
        """Set the height (int).

        Ask to redraw only if height is different of the actual one.

        :param height: (int) in pixels

        """
        spControl.SetHeight(self, height)

        h = self.GetSize().height

        for point in self._pointsctrl:
            point.SetHeight(h)

        for label in self._labelsctrl:
            label.SetHeight(h)
            label.SetFont(self._font)

    # -----------------------------------------------------------------------
    # Callbacks
    # -----------------------------------------------------------------------

    def OnPointEdit(self, event):
        """Point Edit. Open a dialog to edit the point values."""

        logging.info('TIER. OnPointEdit. Not implemented.')
        return

        # get point from the event
        # point = event.GetEventObject()
        # # show point editor
        # dlg = PointEditor(self, point.get_midpoint(), point.get_radius())
        # if dlg.ShowModal() == wx.ID_OK:
        #     (m,r) = dlg.GetValues()
        #     # do something with the new value (accept or reject)
        #
        # dlg.Destroy()

    # ------------------------------------------------------------------------

    def OnPointResizing(self, event):
        """Point Resizing means a new radius value for the TimePoint."""
        logging.info('TIER. OnPointResizing. Disabled.')
        return

        # which point is resized and what are new coordinates?
        # ptr = event.GetEventObject()
        # (x, y) = event.pos
        # (w, h) = event.size
        #
        # # self coordinates
        # sx, sy = self.GetPosition()
        # sw, sh = self.GetSize()

        # self.Repaint()

    # ------------------------------------------------------------------------

    def OnPointMoving(self, event):
        logging.info('TIER. OnPointMoving. Disabled.')
        return

        # ptr = event.GetEventObject()
        # (x, y) = event.pos
        # (w, h) = ptr.GetSize()
        # sx, sy = self.GetPosition()
        # sw, sh = self.GetSize()

        # self.Repaint()

    # ------------------------------------------------------------------------
    # Painting
    # ------------------------------------------------------------------------

    def DrawBackground(self, dc, x,y, w, h):
        """Draw the background of the tier.

        @param dc (PaintDC, MemoryDC, BufferedDC...)
        @param w,h (int,int) are width and height available for drawing.

        """
        # Gradient background
        mid = h / 5
        box_rect = wx.Rect(x, y, w, mid)
        dc.GradientFillLinear(box_rect, self._bgcolor, self._fgcolor, wx.NORTH)
        box_rect = wx.Rect(x, 4*mid, w, mid)  #+1)
        dc.GradientFillLinear(box_rect, self._bgcolor, self._fgcolor, wx.SOUTH)

        dc.SetPen(self._bgpen)
        dc.SetBrush(self._bgbrush)
        dc.DrawRectangle(x, mid, w, mid)

        # Top and Bottom lines
        dc.SetPen(self._bgpen)
        dc.DrawLine(x, y, x+w, y)
        dc.DrawLine(x, h-1, x+w, h-1)

    # ------------------------------------------------------------------------

    def DrawPane(self, dc, x, y, w, h):
        """Draw a pane with the tier name.

        @param dc (PaintDC, MemoryDC, BufferedDC...)
        @param x,y (int,int) are coord. of top left corner from which drawing
        @param w,h (int,int) are width and height available for drawing.

        """
        if self._tier is None:
            return  # not initialized

        #self.DrawBackground(dc, x, y, w, h)

        # Top and Bottom lines
        dc.SetPen(self._fgpen)
        dc.DrawLine(x, y+1, x+w, y+1)
        dc.DrawLine(x, h-2, x+w, h-2)

        # Write the tier name
        textwidth, textheight = dc.GetTextExtent(self._tier.get_name())
        # Vertical position
        y = (h - textheight)/2
        # Write text
        dc.SetBackgroundMode(wx.TRANSPARENT)
        dc.SetTextBackground(wx.NullColour)
        dc.SetFont(self._font)
        dc.SetTextForeground(self._textcolor)
        dc.DrawText(self._tier.get_name(), x+1, y)

    # ------------------------------------------------------------------------

    def DrawContent(self, dc, x, y, w, h):
        """Draw the tier on the DC.

        :param dc: (PaintDC, MemoryDC, BufferedDC...)
        :param x, y: (int,int) are coord. of top left corner from which drawing
        :param w, h: (int,int) are width and height available for drawing.

        """
        logging.debug(" ... DrawContent of tier: {:s}".format(self._tier.get_name()))
        if not self._tier:
            return   # not declared
        if self._tier is None:
            return   # not initialized

        # Nothing to do, we still don't have dimensions!
        if not w or not h:
            return

        tier_begin = self._tier.get_first_point().get_midpoint()
        tier_end = self._tier.get_last_point().get_midpoint()

        # the period is overlaping this tier: draw partly
        logging.debug(" ... DrawContent begin={:f}, end={:f}".format(tier_begin, tier_end))

        # Adjust width, if tier ends before the max
        if self._mintime < tier_end and self._maxtime > tier_end:
            ## reduce w (to cover until the end of the tier)
            missing = self._maxtime - tier_end
            w = w - int((missing * float(w)) / (self._maxtime-self._mintime))

        # Adjust x if tier starts after the min
        if self._maxtime > tier_begin and self._mintime < tier_begin:
            missing = tier_begin - self._mintime
            x = x + int((missing * float(w)) / (self._maxtime-self._mintime))

        self.DrawBackground(dc, x, y, w, h)
        logging.debug(" ... DrawBackground done.")

        # keep in memory the current list of all created controls, just hide them
        for point in self._pointsctrl:
            point.Hide()
        for label in self._labelsctrl:
            label.Hide()

        # get the list of annotations to display
        annotations = self._tier.find(self._mintime, self._maxtime, overlaps=True)
        logging.debug(" ... There are {:d} annotations to display in the selected period.".format(len(annotations)))

        # displayed annotations
        for ann in annotations:
            # Must create new controls
            if ann not in self._anns:
                logging.debug(' ... {:s} is drawn for the first time'.format(ann))
                if self._tier.is_point():
                    self._addAnnotationPoint(ann)
                else:
                    logging.debug(" ... add annotationinterval is called")
                    self._addAnnotationInterval(ann)
                    logging.debug(" ... add annotationinterval is done")

            # Show controls
            logging.debug(" ... draw annotation {:s}".format(ann))
            self._drawAnnotation(ann)

    # ----------------------------------------------------------------------------
    # Private
    # ----------------------------------------------------------------------------

    def _drawPoint(self, point, x, y, h):
        """Display a point."""

        xpt, wpt = self._calcPointXW(point.GetValue())

        if self._tier.is_point():
            point.MoveWindow(wx.Point(x+xpt, y+1), wx.Size(wpt, int(h*0.65)))
        else:
            point.MoveWindow(wx.Point(x+xpt, y+1), wx.Size(wpt, h-2))
        point.Show()

    # -----------------------------------------------------------------------

    def _drawAnnotation(self, ann):
        """Display an existing annotation."""

        # logging.debug(' ... _drawAnnotation: {:s}'.format(ann))
        label = self._anns[ann][0]
        point = self._anns[ann][1]
        point2 = self._anns[ann][2]

        (tw, th) = self.GetDrawingSize()
        (tx, ty) = self.GetDrawingPosition()

        # Draw the label
        xpt1, wpt1 = self._calcPointXW(point.GetValue())
        if self._tier.is_point():
            label.MoveWindow(wx.Point(tx+xpt1+wpt1, ty+1), wx.Size(50, th))
        else:
            xpt2, wpt2 = self._calcPointXW(point2.GetValue())
            label.MoveWindow(wx.Point(tx+xpt1+wpt1, ty+1), wx.Size(xpt2-xpt1-wpt1, th-2))
        label.Show()

        # Draw the points
        self._drawPoint(point, tx, ty, th)
        if self._tier.is_interval():
            self._drawPoint(point2, tx, ty, th)

    # -----------------------------------------------------------------------

    def _addAnnotationInterval(self, ann):
        """Create new controls for an annotation, or link to existing controls."""

        ti = ann.get_location().get_best()

        tp1 = ti.get_begin()
        tp2 = ti.get_end()

        p1 = None
        p2 = None

        # Is there a pointctrl at the same place?
        for point in self._pointsctrl:
            if tp1 == point.GetValue():
                p1 = point
                break
            if tp2 == point.GetValue():
                p2 = point

        if p1 is None:
            p1 = PointCtrl(self, id=-1, point=tp1)
            self._pointsctrl.append(p1)

        if p2 is None:
            p2 = PointCtrl(self, id=-1, point=tp2)
            self._pointsctrl.append(p2)

        logging.debug(" ... ... create the label control")
        l = serialize_labels(ann.get_labels(), separator=" ", empty="", alt=True)
        label = LabelCtrl(self, id=-1, label=l)
        self._labelsctrl.append(label)
        logging.debug(" ... ... label control successfully created")

        self._anns[ann] = [label, p1, p2]

        # Fix properties
        label.SetAlign(self._labelalign)
        label.SetFont(self._font)
        #if label.GetValue().GetSize() == 1:
        label.SetColours(self._labelbgcolor, self._textcolor)
        #else:
        #    label.SetColours(self._labelbgcolor, self._labelfgucolor)
        p1.SetColours(colourmidpoint=self._midpointcolor,
                      colourradius=self._labelbgcolor)

        if self._tier.is_point():
            p2.SetColours(colourmidpoint=self._midpointcolor,
                          colourradius=self._labelbgcolor)

    # -----------------------------------------------------------------------

    def _addAnnotationPoint(self, ann):
        """Create new controls for an annotation, or link to existing controls."""

        tp = ann.get_location().get_best()

        p = None

        # Is there a pointctrl at the same place?
        for point in self._pointsctrl:
            if tp.get_midpoint() == point.get_midpoint():
                p = point
                break

        if p is None:
            p = PointCtrl(self, id=-1, point=tp)
            self._pointsctrl.append(p)

        l = serialize_labels(ann.get_labels(), separator=" ", empty="", alt=True)
        label = LabelCtrl(self, id=-1, label=l)
        self._labelsctrl.append(label)

        self._anns[ann] = [label, p, None]

        # Fix properties
        label.SetAlign(self._labelalign)
        label.SetFont(self._font)
        #if label.GetValue().GetSize() == 1:
        label.SetColours(self._labelbgcolor, self._textcolor)
        #else:
        #    label.SetColours(self._labelbgcolor, self._labelfgucolor)
        p.SetColours(colourmidpoint=self._midpointcolor,
                     colourradius=self._labelbgcolor)

    # -----------------------------------------------------------------------

    def _calcPointXW(self, point):

        # Get information
        tierwidth, tierheight = self.GetDrawingSize()
        tiermintime, tiermaxtime = self.GetTime()
        tierduration = tiermaxtime - tiermintime

        # Fix position and width of the point
        b = point.get_midpoint() - point.get_radius()
        e = point.get_midpoint() + point.get_radius()
        # hum.... take care:
        # b can be "before" tiermintime
        # e can be "after" tiermaxtime

        delta = max(0., b - tiermintime)
        ptbx = delta * float(tierwidth) / tierduration
        delta = max(0., e - tiermintime)
        ptex = delta * float(tierwidth) / tierduration

        x = round(ptbx, 0)   #int(ptbx) #
        w = max(int(ptex-ptbx), pointctrlMinWidth)

        return x, w

# ----------------------------------------------------------------------------


class PointEditor(wx.Dialog):
    """Show a dialog to display/change midpoint and radius."""

    def __init__(self, parent, middle, radius):
        wx.Dialog.__init__(self, parent,
                           title="Point",
                           size=(320, 150),
                           style=wx.DEFAULT_DIALOG_STYLE | wx.STAY_ON_TOP)

        self.middle = middle
        self.radius = radius

        fontsize = 10
        if wx.Platform == "__WXMSW__":
            fontsize = 8
        font = wx.Font(fontsize, wx.SWISS, wx.NORMAL, wx.NORMAL)

        # create the main sizer.
        gbs = wx.GridBagSizer(hgap=5, vgap=5)

        txtfrom = wx.StaticText(self, label="  Middle: ", size=(80, 24))
        txtfrom.SetFont(font)
        txtto = wx.StaticText(self, label="  Radius: ", size=(80, 24))
        txtto.SetFont(font)

        self.fieldfrom = wx.TextCtrl(self, -1, str(self.middle), size=(150, 24), validator=TextAsNumericValidator())
        self.fieldfrom.SetFont(font)
        self.fieldfrom.SetInsertionPoint(0)
        self.fieldto = wx.TextCtrl(self, -1, str(self.radius),  size=(150, 24), validator=TextAsNumericValidator())
        self.fieldto.SetFont(font)
        self.fieldto.SetInsertionPoint(0)

        gbs.Add(txtfrom, (0, 0), flag=wx.ALL, border=2)
        gbs.Add(self.fieldfrom, (0, 1), flag=wx.EXPAND, border=2)
        gbs.Add(txtto, (1, 0), flag=wx.ALL, border=2)
        gbs.Add(self.fieldto, (1, 1), flag=wx.EXPAND, border=2)

        # the buttons for close, and cancellation
        Buttons = wx.StdDialogButtonSizer()
        ButtonClose = wx.Button(self, wx.ID_OK)
        Buttons.AddButton(ButtonClose)
        ButtonCancel = wx.Button(self, wx.ID_CANCEL)
        Buttons.AddButton(ButtonCancel)
        Buttons.Realize()
        gbs.Add(Buttons, (2, 0), (1, 2),
                flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_CENTER_HORIZONTAL,
                border=5)

        self.SetMinSize((300, 120))
        self.SetSizer(gbs)
        self.Layout()
        self.Refresh()

    # ------------------------------------------------------------------------

    def GetValues(self):
        """Return the new midpoint/radius values."""
        return self.fieldfrom.GetValue(), self.fieldto.GetValue()
