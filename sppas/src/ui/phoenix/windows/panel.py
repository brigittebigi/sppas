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

    src.ui.phoenix.windows.panel.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""

import wx
import wx.lib.scrolledpanel as sc


# ---------------------------------------------------------------------------


class sppasPanel(wx.Panel):
    """A panel is a window on which controls are placed.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2019  Brigitte Bigi

    Possible constructors:

        - sppasPanel()
        - sppasPanel(parent, id=ID_ANY, pos=DefaultPosition, size=DefaultSize,
              style=TAB_TRAVERSAL, name=PanelNameStr)

    """

    def __init_(self, *args, **kw):
        super(sppasPanel, self).__init__(*args, **kw)
        s = wx.GetApp().settings
        self.SetBackgroundColour(s.bg_color)
        self.SetForegroundColour(s.fg_color)
        self.SetFont(s.text_font)
        self.SetAutoLayout(True)
        self.SetMinSize(wx.Size(320, 200))

    # -----------------------------------------------------------------------

    def SetBackgroundColour(self, colour):
        """Override."""
        wx.Panel.SetBackgroundColour(self, colour)
        for c in self.GetChildren():
            c.SetBackgroundColour(colour)

    # -----------------------------------------------------------------------

    def SetForegroundColour(self, colour):
        """Override."""
        wx.Panel.SetForegroundColour(self, colour)
        for c in self.GetChildren():
            c.SetForegroundColour(colour)

    # -----------------------------------------------------------------------

    def SetFont(self, font):
        """Override."""
        wx.Panel.SetFont(self, font)
        for c in self.GetChildren():
            c.SetFont(font)
        self.Layout()

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


# ---------------------------------------------------------------------------


class sppasScrolledPanel(sc.ScrolledPanel):
    """A panel is a window on which controls are placed.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2018  Brigitte Bigi

    Possible constructors:

        - sppasScrolledPanel()
        - sppasScrolledPanel(parent, id=ID_ANY, pos=DefaultPosition,
            size=DefaultSize, style=TAB_TRAVERSAL, name=PanelNameStr)

    """

    def __init_(self, *args, **kw):
        super(sppasScrolledPanel, self).__init__(*args, **kw)
        s = wx.GetApp().settings
        self.SetBackgroundColour(s.bg_color)
        self.SetForegroundColour(s.fg_color)
        self.SetFont(s.text_font)

    # -----------------------------------------------------------------------

    def SetBackgroundColour(self, colour):
        """Override."""
        sc.ScrolledPanel.SetBackgroundColour(self, colour)
        for c in self.GetChildren():
            c.SetBackgroundColour(colour)

    # -----------------------------------------------------------------------

    def SetForegroundColour(self, colour):
        """Override."""
        sc.ScrolledPanel.SetForegroundColour(self, colour)
        for c in self.GetChildren():
            c.SetForegroundColour(colour)

    # -----------------------------------------------------------------------

    def SetFont(self, font):
        """Override."""
        sc.ScrolledPanel.SetFont(self, font)
        for c in self.GetChildren():
            c.SetFont(font)
        self.Layout()

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


# ---------------------------------------------------------------------------


class sppasCollapsiblePanel(wx.CollapsiblePane):
    """A collapsible panel is a window on which controls are placed.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2019  Brigitte Bigi

    """

    def __init_(self, *args, **kw):
        super(sppasCollapsiblePanel, self).__init__(*args, **kw)
        s = wx.GetApp().settings
        self.SetBackgroundColour(s.bg_color)
        self.SetForegroundColour(s.fg_color)
        self.SetFont(s.text_font)

    # -----------------------------------------------------------------------

    def SetBackgroundColour(self, colour):
        """Override."""
        wx.CollapsiblePane.SetBackgroundColour(self, colour)
        for c in self.GetChildren():
            c.SetBackgroundColour(colour)

    # -----------------------------------------------------------------------

    def SetForegroundColour(self, colour):
        """Override."""
        wx.CollapsiblePane.SetForegroundColour(self, colour)
        for c in self.GetChildren():
            c.SetForegroundColour(colour)

    # -----------------------------------------------------------------------

    def SetFont(self, font):
        """Override."""
        wx.CollapsiblePane.SetFont(self, font)
        for c in self.GetChildren():
            c.SetFont(font)
        self.Layout()

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


# -----------------------------------------------------------------------------
# PyCollapsiblePane
# -----------------------------------------------------------------------------


class PyCollapsiblePane(sppasPanel):

    def __init__(self, parent, id=wx.ID_ANY, label="", pos=wx.DefaultPosition,
                 size=wx.DefaultSize, style=0, name="CollapsiblePane"):
        """Create a CollapsiblePanel.
        
        :param parent: (wx.Window) Parent window must NOT be none
        :param id: (int) window identifier or -1
        :param label: (string) Label of the button
        :param pos: (wx.Pos) the control position
        :param size: (wx.Size) the control size
        :param style: (int) the underlying window style
        :param name: (str) the widget name.

        """
        sppasPanel.__init__(self, parent, id, pos, size, style, name)

        self.__btn = wx.Button(self, wx.ID_ANY, label, style=wx.BU_EXACTFIT)
        self.__btn.SetMinSize(wx.Size(64, 32))
        self.__child_panel = sppasPanel(self, style=wx.TAB_TRAVERSAL | wx.NO_BORDER)
        self.__child_panel.Hide()
        self.__collapsed = True

        self.Bind(wx.EVT_BUTTON, self.OnButton, self.__btn)
        self.Bind(wx.EVT_SIZE, self.OnSize)
        # self.SetInitialSize()
        self.Layout()

    def GetPane(self):
        """Return a reference to the pane window."""
        return self.__child_panel

    def GetBorder(self):
        """Return the border in pixels (platform dependent). """
        if wx.Platform == "__WXMAC__":
            return 6
        elif wx.Platform == "__WXGTK__":
            return 3
        elif wx.Platform == "__WXMSW__":
            return self.__btn.ConvertDialogSizeToPixels(wx.Size(2, 0)).x
        else:
            return 5

    def Collapse(self, collapse=True):
        """Collapse or expand the pane window.

        :param collapse: True` to collapse the pane window, False` to expand it.

        """
        if self.IsCollapsed() == collapse:
            return

        # to reduce your UI from appearing to flicker
        self.Freeze()
        # update our state
        self.__child_panel.Show(not collapse)
        self.__collapsed = collapse
        self.InvalidateBestSize()
        # then display our changes
        self.Thaw()
        self.SetStateChange(self.GetBestSize())

    def Expand(self):
        """Same as Collapse(False). """
        self.Collapse(False)

    def IsCollapsed(self):
        """Return True if the pane window is currently hidden."""
        return self.__collapsed

    def IsExpanded(self):
        """ Returns True` if the pane window is currently shown. """
        return not self.IsCollapsed()

    def DoGetBestSize(self):
        """Get the size which best suits the window."""
        # size = self.__btn.GetMinSize()
        size = self.__btn.GetSize()

        if self.IsExpanded():
            pbs = self.__child_panel.GetBestSize()
            wx.LogDebug("  -> child panel best size = {:s}".format(str(pbs)))
            size.width = max(size.GetWidth(), pbs.x)
            size.height = size.y + self.GetBorder() + pbs.y

        wx.LogDebug("  -> returned size {:s}".format(str(size)))
        return size

    def Layout(self):
        """Do the layout."""
        # we need to complete the creation first
        if not self.__btn or not self.__child_panel:
            wx.LogDebug("  -> we need to complete the creation first")
            return False

        w, h = self.GetSize()
        bw = w
        bh = self.__btn.GetMinSize().GetHeight()
        # move & resize the button
        self.__btn.SetPosition((0, 0))
        self.__btn.SetSize(wx.Size(bw, bh))

        if self.IsExpanded():
            # move & resize the container window
            pw, ph = self.GetSize()
            yoffset = bh + self.GetBorder()
            self.__child_panel.SetSize(wx.Size(w, ph - yoffset))
            self.__child_panel.SetPosition((0, yoffset))

            # this is very important to make the pane window layout show correctly
            self.__child_panel.Show(True)
            self.__child_panel.Layout()
            self.__child_panel.Refresh()

        return True

    def SetStateChange(self, sz):
        """Handles the status changes (collapsing/expanding).

        :param sz: an instance of Size.

        """
        self.SetSize(sz)

        ###top = wx.GetTopLevelParent(self)
        top = self.GetParent()

        if top.GetSizer():
            if (wx.Platform == "__WXGTK__" and self.IsCollapsed()) or wx.Platform != "__WXGTK__":
                top.GetSizer().SetSizeHints(top)

        if self.IsCollapsed():
            # expanded -> collapsed transition
            if top.GetSizer():
                # we have just set the size hints...
                sz = top.GetSizer().CalcMin()

                # use SetClientSize() and not SetSize() otherwise the size for
                # e.g. a wxFrame with a menubar wouldn't be correctly set
                top.SetClientSize(sz)
            else:
                top.Layout()
        else:
            # collapsed . expanded transition
            # force our parent to "fit", i.e. expand so that it can honour
            # our best size
            top.Fit()

    def SetInitialSize(self, size=None):
        """Calculate and set a good size.

        :param size: an instance of wx.Size.

        """
        bw, bh = self.__btn.GetMinSize()
        self.SetMinSize(wx.Size(bw, bh))
        wx.LogDebug("  -> min size: ({:d}, {:d}) ".format(bw, bh))

        if size is None:
            size = wx.DefaultSize
        wx.Window.SetInitialSize(self, size)
        wx.LogDebug("  -> size: {:s}".format(str(size)))

    SetBestSize = SetInitialSize

    # -----------------------------------------------------------------------------
    # Event handlers
    # -----------------------------------------------------------------------------

    def OnButton(self, event):
        """Handle the wx.EVT_BUTTON event.

        :param event: a CommandEvent event to be processed.

        """
        if event.GetEventObject() != self.__btn:
            event.Skip()
            return

        self.Collapse(not self.IsCollapsed())

        ev = wx.CollapsiblePaneEvent(self, self.GetId(), self.IsCollapsed())
        self.GetEventHandler().ProcessEvent(ev)

    def OnSize(self, event):
        """Handle the wx.EVT_SIZE event.

        :param event: a SizeEvent event to be processed.

        """
        # each time our size is changed, the child panel needs a resize.
        self.Layout()


# -----------------------------------------------------------------------


class TestPanel(sc.ScrolledPanel):

    def __init__(self, parent):
        super(TestPanel, self).__init__(
            parent,
            style=wx.BORDER_NONE | wx.WANTS_CHARS | wx.VSCROLL,
            name="Test Panels")

        p1 = sppasPanel(self)
        self.MakePanelContent(p1)

        p2 = PyCollapsiblePane(self, label="SPPAS Collapsible Panel (1)...")
        child_panel = p2.GetPane()
        child_panel.SetBackgroundColour(wx.BLUE)
        self.MakePanelContent(child_panel)
        self.Bind(wx.EVT_COLLAPSIBLEPANE_CHANGED, self.OnCollapseChanged, p2)

        p3 = PyCollapsiblePane(self, label="SPPAS Collapsible Panel (2)...")
        child_panel = p3.GetPane()
        child_panel.SetBackgroundColour(wx.YELLOW)
        self.MakePanelContent(child_panel)
        self.Bind(wx.EVT_COLLAPSIBLEPANE_CHANGED, self.OnCollapseChanged, p3)

        p4 = PyCollapsiblePane(self, label="wx.CollapsiblePane")
        child_panel = p4.GetPane()
        child_panel.SetBackgroundColour(wx.GREEN)
        self.MakePanelContent(child_panel)
        self.Bind(wx.EVT_COLLAPSIBLEPANE_CHANGED, self.OnCollapseChanged, p4)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(p1, 0, wx.EXPAND)
        sizer.Add(p2, 0, wx.EXPAND | wx.ALL, border=10)
        sizer.Add(p3, 0, wx.EXPAND | wx.ALL, border=10)
        sizer.Add(p4, 0, wx.EXPAND | wx.ALL, border=10)

        self.SetSizer(sizer)
        sizer.Fit(self)
        self.Layout()
        self.SetupScrolling(scroll_x=False, scroll_y=True)
        self.SetAutoLayout(True)

    def OnCollapseChanged(self, evt=None):
        panel = evt.GetEventObject()
        panel.SetFocus()
        # self.OnChildFocus(evt)
        # self.ScrollChildIntoView(panel)
        self.Layout()
        self.Refresh()

    def MakePanelContent(self, pane):
        """Just make a few controls to put on the collapsible pane."""
        nameLbl = wx.StaticText(pane, -1, "Name:")
        name = wx.TextCtrl(pane, -1, "")

        addrLbl = wx.StaticText(pane, -1, "Address:")
        addr1 = wx.TextCtrl(pane, -1, "")
        addr2 = wx.TextCtrl(pane, -1, "")

        cstLbl = wx.StaticText(pane, -1, "City, State, Zip:")
        city = wx.TextCtrl(pane, -1, "", size=(150, -1))
        state = wx.TextCtrl(pane, -1, "", size=(50, -1))
        zip = wx.TextCtrl(pane, -1, "", size=(70, -1))

        addrSizer = wx.FlexGridSizer(cols=2, hgap=10, vgap=10)
        addrSizer.AddGrowableCol(1)
        addrSizer.Add(nameLbl, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL)
        addrSizer.Add(name, 0, wx.EXPAND)
        addrSizer.Add(addrLbl, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL)
        addrSizer.Add(addr1, 0, wx.EXPAND)
        addrSizer.Add((5, 5))
        addrSizer.Add(addr2, 0, wx.EXPAND)

        addrSizer.Add(cstLbl, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL)

        cstSizer = wx.BoxSizer(wx.HORIZONTAL)
        cstSizer.Add(city, 1)
        cstSizer.Add(state, 0, wx.LEFT | wx.RIGHT, 5)
        cstSizer.Add(zip)
        addrSizer.Add(cstSizer, 0, wx.EXPAND)

        border = wx.BoxSizer()
        border.Add(addrSizer, 1, wx.EXPAND | wx.ALL, 5)
        pane.SetSizer(border)
        pane.Layout()
