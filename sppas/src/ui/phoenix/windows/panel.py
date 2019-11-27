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

    A panel is a window on which controls are placed.
    Panels of SPPAS allow to propagate properly fonts and colors defined in
    the settings.

"""

import wx
import wx.lib.scrolledpanel as sc

from .button import BitmapTextButton

# ---------------------------------------------------------------------------


class sppasPanel(wx.Panel):
    """A panel with colors and fonts defined in the settings.

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
        try:
            s = wx.GetApp().settings
            self.SetBackgroundColour(s.bg_color)
            self.SetForegroundColour(s.fg_color)
            self.SetFont(s.text_font)
        except AttributeError:
            wx.LogWarning("Settings not defined. Use default colors and fonts.")
            pass
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
        try:
            s = wx.GetApp().settings
            self.SetBackgroundColour(s.bg_color)
            self.SetForegroundColour(s.fg_color)
            self.SetFont(s.text_font)
        except AttributeError:
            wx.LogWarning("Settings not defined. Use default colors and fonts.")
            pass

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


class sppasCollapsiblePanel(sppasPanel):

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

        The parent can Bind the wx.EVT_COLLAPSIBLEPANE_CHANGED.

        """
        
        sppasPanel.__init__(self, parent, id, pos, size, style, name)

        self.__collapsed = True
        self.__btn = None
        self.__tools_panel = self.create_toolbar(label)
        self.__child_panel = sppasPanel(self, style=wx.TAB_TRAVERSAL | wx.NO_BORDER, name="content")
        self.__child_panel.Hide()
        self.__child_panel.SetAutoLayout(True)
        self.__child_panel.SetSizer(wx.BoxSizer(wx.VERTICAL))
        self.__border = sppasCollapsiblePanel.fix_size(2)

        try:
            s = wx.GetApp().settings
            self.SetBackgroundColour(s.bg_color)
            self.SetForegroundColour(s.fg_color)
            self.SetFont(s.text_font)
        except AttributeError:
            wx.LogWarning("Settings not defined. Use default colors and fonts.")
            pass

        self.Bind(wx.EVT_BUTTON, self.OnButton, self.__btn)
        self.Bind(wx.EVT_SIZE, self.OnSize)
        self.SetInitialSize()
        self.Layout()

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

    def GetPane(self):
        """Return a reference to the embedded pane window."""
        return self.__child_panel

    # -----------------------------------------------------------------------

    def SetPane(self, pane):
        """Set given pane to the embedded pane window.

        The parent of pane must be self.

        """
        if pane.GetParent() != self:
            raise ValueError("Bad parent for pane {:s}.".format(pane.GetName()))
        self.__child_panel.Destroy()
        self.__child_panel = pane
        if self.__collapsed is True:
            self.__child_panel.Hide()
        self.Layout()

    # -----------------------------------------------------------------------

    def Collapse(self, collapse=True):
        """Collapse or expand the pane window.

        :param collapse: True` to collapse the pane window, False` to expand it.

        """
        if self.IsCollapsed() == collapse:
            return

        # update our state
        self.Freeze()
        if collapse is True:
            self.__btn.SetImage("arrow_collapsed")
        else:
            self.__btn.SetImage("arrow_expanded")

        if collapse is True:
            self.__child_panel.Hide()
        else:
            self.__child_panel.Show()
        self.__collapsed = collapse
        self.InvalidateBestSize()

        # then display our changes
        self.Thaw()
        self.SetStateChange(self.GetBestSize())

    # -----------------------------------------------------------------------

    def Expand(self):
        """Same as Collapse(False). """
        self.Collapse(False)

    # -----------------------------------------------------------------------

    def IsCollapsed(self):
        """Return True if the pane window is currently hidden."""
        return self.__collapsed

    # -----------------------------------------------------------------------

    def IsExpanded(self):
        """ Returns True` if the pane window is currently shown. """
        return not self.IsCollapsed()

    # -----------------------------------------------------------------------

    def FindButton(self, icon):
        """Return the button with the given icon name or None."""
        for child in self.__tools_panel.GetChildren():
            if child.GetName() == icon:
                return child
        return None

    # -----------------------------------------------------------------------

    def AddButton(self, icon):
        """Prepend a button into the toolbar.

        :param icon: (str) Name of the .png file of the icon or None

        """
        btn = BitmapTextButton(self.__tools_panel, name=icon)
        btn.SetLabelPosition(wx.RIGHT)
        btn.SetFocusWidth(0)
        btn.SetSpacing(0)
        btn.SetBorderWidth(0)
        btn.SetBitmapColour(self.GetForegroundColour())
        h = self.GetButtonHeight()
        btn_h = sppasPanel.fix_size(h)
        btn_w = btn_h
        btn.SetMinSize(wx.Size(btn_w, btn_h))
        btn.SetSize(wx.Size(btn_w, btn_h))
        self.__tools_panel.GetSizer().Prepend(btn, 0, wx.LEFT | wx.RIGHT | wx.EXPAND, 0)

        return btn

    # -----------------------------------------------------------------------

    def GetButtonHeight(self):
        """Return the height assigned to the buttons in the toolbar."""
        return self.get_line_height() * 2

    # -----------------------------------------------------------------------

    def DoGetBestSize(self):
        """Get the size which best suits the window."""
        # size = self.__btn.GetMinSize()
        # size = self.__btn.GetSize()
        size = self.__tools_panel.GetSize()

        if self.IsExpanded():
            pbs = self.__child_panel.GetBestSize()
            size.width = max(size.GetWidth(), pbs.x)
            size.height = size.y + self.__border + pbs.y

        return size

    # -----------------------------------------------------------------------

    def Layout(self):
        """Do the layout."""
        # we need to complete the creation first
        if not self.__tools_panel or not self.__child_panel:
            return False

        w, h = self.GetSize()
        bw = w - self.__border
        bh = self.GetButtonHeight()
        wx.LogDebug("CollapsiblePanel: buttons size is {:d} px".format(bh))
        # fix pos and size of the top panel with tools
        self.__tools_panel.SetPosition((self.__border, 0))
        self.__tools_panel.SetSize(wx.Size(bw, bh))

        if self.IsExpanded():
            # fix pos and size of the child window
            pw, ph = self.GetSize()
            x = self.__border + bh  # shift of the icon size (a square).
            y = bh + self.__border
            pw = pw - x - self.__border      # left-right borders
            ph = ph - y - self.__border      # top-bottom borders
            self.__child_panel.SetSize(wx.Size(pw, ph))
            self.__child_panel.SetPosition((x, y))
            self.__child_panel.Show(True)
            self.__child_panel.Layout()
            self.__child_panel.Refresh()

        return True

    # -----------------------------------------------------------------------

    def SetStateChange(self, sz):
        """Handles the status changes (collapsing/expanding).

        :param sz: an instance of Size.

        """
        self.SetSize(sz)
        top = self.GetParent()

        if top.GetSizer():
            if (wx.Platform == "__WXGTK__" and self.IsCollapsed()) or \
                    wx.Platform != "__WXGTK__":
                top.GetSizer().SetSizeHints(top)

        if self.IsCollapsed():
            # expanded -> collapsed transition
            if top.GetSizer():
                sz = top.GetSizer().CalcMin()
                top.SetClientSize(sz)
        else:
            # collapsed -> expanded transition
            top.Fit()

        wx.GetTopLevelParent(self).Layout()
        self.Refresh()

    # -----------------------------------------------------------------------

    def SetInitialSize(self, size=None):
        """Calculate and set a good size.

        :param size: an instance of wx.Size.

        """
        bw, bh = self.__tools_panel.GetMinSize()
        self.SetMinSize(wx.Size(bw, bh + self.__border))
        if size is None:
            size = wx.DefaultSize
        wx.Window.SetInitialSize(self, size)

    SetBestSize = SetInitialSize

    # ------------------------------------------------------------------------
    # Event handlers
    # ------------------------------------------------------------------------

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

    # ------------------------------------------------------------------------

    def OnSize(self, event):
        """Handle the wx.EVT_SIZE event.

        :param event: a SizeEvent event to be processed.

        """
        # each time our size is changed, the child panel needs a resize.
        self.Layout()

    # -----------------------------------------------------------------------

    def get_line_height(self):
        font = self.GetFont()
        return int(float(font.GetPixelSize()[1]))

    # -----------------------------------------------------------------------

    def create_toolbar(self, label):
        """Create a panel with tools, including the collapsible button."""
        panel = sppasPanel(self)
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.__btn = self.create_collapsible_button(panel, label)
        sizer.Add(self.__btn, 1, wx.EXPAND, 0)
        panel.SetSizer(sizer)
        return panel

    # -----------------------------------------------------------------------

    def create_collapsible_button(self, parent, text):
        if self.__collapsed is True:
            icon = "arrow_collapsed"
        else:
            icon = "arrow_expanded"
        btn = BitmapTextButton(parent, label=text, name=icon)
        btn.LabelPosition = wx.RIGHT
        btn.Align = wx.ALIGN_LEFT

        btn.FocusStyle = wx.PENSTYLE_SOLID
        btn.FocusWidth = 1
        btn.FocusColour = self.GetForegroundColour()
        btn.Spacing = sppasPanel.fix_size(4)
        btn.BorderWidth = 0
        btn.BitmapColour = self.GetForegroundColour()
        h = self.GetButtonHeight()
        btn_w = sppasPanel.fix_size(h*10)
        btn_h = sppasPanel.fix_size(h)
        btn.SetMinSize(wx.Size(btn_w, btn_h))
        btn.SetSize(wx.Size(btn_w, btn_h))

        return btn

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


class TestPanel(sc.ScrolledPanel):

    def __init__(self, parent):
        super(TestPanel, self).__init__(
            parent,
            style=wx.BORDER_NONE | wx.WANTS_CHARS | wx.HSCROLL | wx.VSCROLL,
            name="Test Panels")
        self.SetBackgroundColour(wx.WHITE)

        p1 = sppasPanel(self)
        self.MakePanelContent(p1)

        p2 = sppasCollapsiblePanel(self, label="SPPAS Collapsible Panel...")
        p2.AddButton("folder")
        child_panel = p2.GetPane()
        child_panel.SetBackgroundColour(wx.BLUE)
        self.MakePanelContent(child_panel)
        p2.Expand()
        checkbox = p2.AddButton("choice_checkbox")
        self.Bind(wx.EVT_COLLAPSIBLEPANE_CHANGED, self.OnCollapseChanged, p2)
        checkbox.Bind(wx.EVT_BUTTON, self.OnCkeckedPanel)

        p3 = sppasCollapsiblePanel(self, label="SPPAS Collapsible Panel using SetPane...")
        child_panel = sppasPanel(p3)
        child_panel.SetBackgroundColour(wx.YELLOW)
        self.MakePanelContent(child_panel)
        p3.SetPane(child_panel)
        self.Bind(wx.EVT_COLLAPSIBLEPANE_CHANGED, self.OnCollapseChanged, p3)

        p4 = sppasCollapsiblePanel(self, label="wx.CollapsiblePane")
        child_panel = p4.GetPane()
        child_panel.SetBackgroundColour(wx.GREEN)
        self.MakePanelContent(child_panel)
        self.Bind(wx.EVT_COLLAPSIBLEPANE_CHANGED, self.OnCollapseChanged, p4)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(p1, 0, wx.EXPAND)
        sizer.Add(p2, 0, wx.EXPAND | wx.ALIGN_LEFT | wx.ALL, border=10)
        sizer.Add(p3, 0, wx.EXPAND | wx.ALIGN_LEFT | wx.ALL, border=10)
        sizer.Add(p4, 0, wx.EXPAND | wx.ALL, border=10)

        self.SetSizerAndFit(sizer)
        self.Layout()
        self.SetupScrolling(scroll_x=True, scroll_y=True)
        self.SetAutoLayout(True)
        self.Refresh()

        self.Bind(wx.EVT_SIZE, self.OnSize)

    def OnCollapseChanged(self, evt=None):
        panel = evt.GetEventObject()
        panel.SetFocus()
        self.ScrollChildIntoView(panel)

    def OnCkeckedPanel(self, evt):
        button = evt.GetEventObject()
        if button.GetName() == "choice_checked":
            button.SetImage("choice_checkbox")
            button.SetName("choice_checkbox")
        else:
            button.SetImage("choice_checked")
            button.SetName("choice_checked")

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

    def OnSize(self, evt):
        self.Layout()
