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

    src.ui.phoenix.windows.panels.panel.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""

import wx
import wx.lib.scrolledpanel as sc

from ..buttons import BitmapButton
from ..buttons import ToggleButton
from ..buttons import BitmapTextButton
from .panel import sppasPanel
from ..popup import LabelPopup

# ---------------------------------------------------------------------------


class sppasBaseRisePanel(sppasPanel):
    """A rise panel is a window on which controls are placed.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2020  Brigitte Bigi

    """

    def __init__(self, parent, id=wx.ID_ANY, label="", pos=wx.DefaultPosition,
                 size=wx.DefaultSize, style=0, name="rise_panel"):
        """Create a base class for any type of collapsible/expandable panel.

        :param parent: (wx.Window) Parent window must NOT be none
        :param id: (int) window identifier or -1
        :param label: (string) Label of the button
        :param pos: (wx.Pos) the control position
        :param size: (wx.Size) the control size
        :param style: (int) the underlying window style
        :param name: (str) the widget name.

        The parent can Bind the wx.EVT_COLLAPSIBLEPANE_CHANGED.

        """
        super(sppasBaseRisePanel, self).__init__(parent, id, pos, size, style, name)

        # Look&feel
        try:
            s = wx.GetApp().settings
            self.SetBackgroundColour(s.bg_color)
            self.SetForegroundColour(s.fg_color)
            self.SetFont(s.text_font)
        except AttributeError:
            self.InheritAttributes()

        # Private members
        self._label = label
        self._img_collapsed = "arrow_collapsed"
        self._img_expanded = "arrow_expanded"
        self._collapsed = True

        self._btn = None
        self._tools_panel = sppasPanel(self)
        self._create_toolbar()

        self._child_panel = sppasPanel(self, style=wx.TAB_TRAVERSAL | wx.NO_BORDER, name="content")
        self._child_panel.Hide()
        self._child_panel.SetAutoLayout(True)
        self._child_panel.SetSizer(wx.BoxSizer(wx.VERTICAL))

        # Bind the events
        self.SetInitialSize(size)

        # Associate a handler function with the events.
        self.Bind(wx.EVT_SIZE, self._process_size_event)
        if self._btn is not None:
            self._btn.Bind(wx.EVT_BUTTON, self._process_collapse_event)

        self.Layout()

    # -----------------------------------------------------------------------

    def SetCollapsedIcon(self, name="arrow_collapsed"):
        self._img_collapsed = name
        self.Refresh()

    def SetExpandedIcon(self, name="arrow_expanded"):
        self._img_expanded = name
        self.Refresh()

    # -----------------------------------------------------------------------

    def GetPane(self):
        """Return a reference to the embedded pane window."""
        return self._child_panel

    # -----------------------------------------------------------------------

    def IsChild(self, obj):
        """Return true if obj is one of the children."""
        for c in self.GetChildren():
            if c is obj:
                return True
            for cc in c.GetChildren():
                if cc is obj:
                    return True
        return False

    # -----------------------------------------------------------------------

    def SetPane(self, pane):
        """Set given pane to the embedded pane window.

        The parent of pane must be self.

        """
        if pane.GetParent() != self:
            raise ValueError("Bad parent for pane {:s}.".format(pane.GetName()))
        if self._child_panel:
            self._child_panel.Destroy()
        self._child_panel = pane
        if self._collapsed is True:
            self._child_panel.Hide()
        self.Layout()

    # -----------------------------------------------------------------------

    def Collapse(self, collapse=True):
        """Collapse or expand the pane window.

        :param collapse: True to collapse the pane window, False to expand it.

        """
        collapse = bool(collapse)

        # update our state
        self.Freeze()
        if collapse is True:
            self._btn.SetImage(self._img_collapsed)
        else:
            self._btn.SetImage(self._img_expanded)

        if self._child_panel:
            if collapse is True:
                self._child_panel.Hide()
            else:
                self._child_panel.Show()
        self._collapsed = collapse
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
        return self._collapsed

    # -----------------------------------------------------------------------

    def IsExpanded(self):
        """ Returns True` if the pane window is currently shown. """
        return not self.IsCollapsed()

    # ------------------------------------------------------------------------

    def GetLabel(self):
        """Return the label text of the collapsible button."""
        return self._label

    # -----------------------------------------------------------------------

    def EnableButton(self, icon, value):
        """Enable or disable a button of the tools panel.

        :param icon: (str) Name of the .png file of the icon
        :param value: (bool)

        """
        btn = self._tools_panel.FindWindow(icon)
        if btn is None or btn == self._btn:
            return
        btn.Enable(value)

    # -----------------------------------------------------------------------

    def FindButton(self, icon):
        """Return the button with the given icon name or None."""
        for child in self._tools_panel.GetChildren():
            if child.GetName() == icon and child != self._btn:
                return child
        return None

    # -----------------------------------------------------------------------

    def Layout(self):
        """Do the layout."""
        raise NotImplementedError

    # -----------------------------------------------------------------------

    def SetStateChange(self, sz):
        """Handles the status changes (collapsing/expanding).

        :param sz: an instance of Size.

        """
        self.SetSize(sz)
        top = self.GetParent()

        if top.GetSizer():
            # if (wx.Platform == "__WXGTK__" and self.IsCollapsed()) or \
            #        wx.Platform != "__WXGTK__":
            top.GetSizer().SetSizeHints(top)

        if self.IsCollapsed():
            # expanded -> collapsed transition
            if top.GetSizer():
                sz = top.GetSizer().CalcMin()
                top.SetClientSize(sz)
        else:
            # collapsed -> expanded transition
            top.Fit()
            self.SetFocus()

        wx.GetTopLevelParent(self).Layout()
        self.Refresh()

    # ------------------------------------------------------------------------
    # Event handlers
    # ------------------------------------------------------------------------

    def _process_collapse_event(self, event):
        """Handle the wx.EVT_BUTTON event of the collapse button.

        :param event: a CommandEvent event to be processed.

        """
        if event.GetEventObject() == self._btn:
            # Collapse the panel
            self.Collapse(not self.IsCollapsed())
            # Send the CollapsiblePaneEvent to the event handler
            ev = wx.CollapsiblePaneEvent(self, self.GetId(), self.IsCollapsed())
            self.GetEventHandler().ProcessEvent(ev)

        else:
            # we should never been here!
            event.Skip()

    # ------------------------------------------------------------------------

    def _process_size_event(self, event):
        """Handle the wx.EVT_SIZE event.

        :param event: a SizeEvent event to be processed.

        """
        # each time our size is changed, the child panel needs a resize.
        self.Layout()

    # -----------------------------------------------------------------------

    def _create_toolbar(self):
        """Create a panel with tools, including the collapsible button."""
        raise NotImplementedError

    # -----------------------------------------------------------------------

    def _create_tool_button(self, icon, label=None):
        raise NotImplementedError

    def _create_tool_togglebutton(self, icon, label=None):
        raise NotImplementedError

    # -----------------------------------------------------------------------

    def _create_collapsible_button(self):
        img_name = self._img_expanded
        if self.IsCollapsed():
            img_name = self._img_collapsed
        return self._create_tool_button(img_name, label=None)

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


class sppasHorizontalRisePanel(sppasBaseRisePanel):
    """An horizontally oriented rise panel.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2020  Brigitte Bigi

    """

    def __init__(self, parent, id=wx.ID_ANY, label="", pos=wx.DefaultPosition,
                 size=wx.DefaultSize, style=0, name="collapsible_panel"):
        """Create a sppasHorizontalRisePanel.

        :param parent: (wx.Window) Parent window must NOT be none
        :param id: (int) window identifier or -1
        :param label: (string) Label of the button
        :param pos: (wx.Pos) the control position
        :param size: (wx.Size) the control size
        :param style: (int) the underlying window style
        :param name: (str) the widget name.

        The parent can Bind the wx.EVT_COLLAPSIBLEPANE_CHANGED.

        """
        self._border = sppasPanel.fix_size(4)
        super(sppasHorizontalRisePanel, self).__init__(
            parent, id, label, pos, size, style, name=name)

    # -----------------------------------------------------------------------

    def AddButton(self, icon):
        """Append a button into the toolbar.

        :param icon: (str) Name of the .png file of the icon or None

        """
        btn = self._create_tool_button(icon, label=None)
        self._tools_panel.GetSizer().Add(btn, 0, wx.TOP, 1)

        return btn

    # -----------------------------------------------------------------------

    def SetLabel(self, value):
        """Set a new label to the collapsible button.

        :param value: (str) New string label

        """
        self._label = value
        self._btn.SetLabel(value)
        self._btn.Refresh()

    # -----------------------------------------------------------------------

    def SetBorder(self, value):
        """Left-Border to be applied to the child panel."""
        self._border = int(value)

    # -----------------------------------------------------------------------
    # Manage the size of the panel when expanded or collapsed
    # -----------------------------------------------------------------------

    def GetButtonHeight(self):
        """Return the height assigned to the button in the toolbar."""
        return int(float(self.get_font_height()) * 1.6)

    # -----------------------------------------------------------------------

    def DoGetBestSize(self):
        """Get the size which best suits the window."""
        tb_w, tb_h = self._tools_panel.GetSize()
        best_w = tb_w
        best_h = tb_h

        if self.IsExpanded() and self._child_panel:
            child_w, child_h = self._child_panel.GetBestSize()
            best_w = max(tb_w, child_w + self._border)
            best_h = tb_h + child_h

        return wx.Size(best_w, best_h)

    # -----------------------------------------------------------------------

    def SetInitialSize(self, size=None):
        """Calculate and set a good size.

        :param size: an instance of wx.Size.

        """
        tb_w, tb_h = self._tools_panel.GetMinSize()
        min_w = tb_w
        min_h = tb_h
        self.SetMinSize(wx.Size(min_w, min_h))
        if size is None:
            size = wx.DefaultSize
        wx.Window.SetInitialSize(self, size)

    SetBestSize = SetInitialSize

    # -----------------------------------------------------------------------

    def Layout(self):
        """Do the layout.

        There's a border at left.

        """
        # we need to complete the creation first
        if not self._tools_panel or not self._child_panel:
            return False

        w, h = self.GetClientSize()
        tw = w
        th = self.GetButtonHeight()
        # fix pos and size of the top panel with tools
        self._tools_panel.SetPosition((0, 0))
        self._tools_panel.SetSize(wx.Size(tw, th))

        if self.IsExpanded():
            # fix pos and size of the child window
            x = self._border   # shift the child panel
            y = th
            self._child_panel.SetPosition((x, y))
            pw = w - x
            ph = h - y
            self._child_panel.SetSize(wx.Size(pw, ph))
            self._child_panel.Show(True)
            self._child_panel.Layout()

        return True

    # -----------------------------------------------------------------------

    def _create_toolbar(self):
        """Create a panel with tools, including the collapsible button."""
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        self._btn = self._create_collapsible_button()
        sizer.Add(self._btn, 1, wx.EXPAND, 0)
        self._tools_panel.SetSizer(sizer)

    # -----------------------------------------------------------------------

    def _create_tool_button(self, icon, label=None):
        btn = BitmapButton(self._tools_panel, name=icon)
        btn.SetAlign(wx.ALIGN_CENTER)
        btn.SetFocusWidth(0)
        btn.SetSpacing(0)
        btn.SetBorderWidth(0)
        btn_h = self.GetButtonHeight()
        btn.SetSize(wx.Size(btn_h, btn_h))
        btn.SetMinSize(wx.Size(btn_h, btn_h))
        return btn

    # -----------------------------------------------------------------------

    def _create_tool_togglebutton(self, icon, label=None):
        btn = ToggleButton(self._tools_panel, name=icon)
        btn.SetAlign(wx.ALIGN_CENTER)
        btn.SetFocusWidth(0)
        btn.SetSpacing(0)
        btn.SetBorderWidth(0)
        btn_h = self.GetButtonHeight()
        btn.SetSize(wx.Size(btn_h, btn_h))
        btn.SetMinSize(wx.Size(btn_h, btn_h))
        return btn

# ---------------------------------------------------------------------------


class sppasVerticalRisePanel(sppasBaseRisePanel):
    """A vertically oriented rise panel.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2020  Brigitte Bigi

    """
    def __init__(self, parent, id=wx.ID_ANY, label="", pos=wx.DefaultPosition,
                 size=wx.DefaultSize, style=0, name="collapsible_panel"):
        """Create a sppasVerticalRisePanel.

        :param parent: (wx.Window) Parent window must NOT be none
        :param id: (int) window identifier or -1
        :param label: (string) Label of the button
        :param pos: (wx.Pos) the control position
        :param size: (wx.Size) the control size
        :param style: (int) the underlying window style
        :param name: (str) the widget name.

        The parent can Bind the wx.EVT_COLLAPSIBLEPANE_CHANGED.

        """
        super(sppasVerticalRisePanel, self).__init__(
            parent, id, label, pos, size, style, name=name)

    # -----------------------------------------------------------------------

    def AddButton(self, icon):
        """Append a button into the toolbar.

        :param icon: (str) Name of the .png file of the icon or None

        """
        btn = self._create_tool_button(icon, label=None)
        sizer = self._tools_panel.GetSizer()
        sizer.Add(btn, 0, wx.TOP, 1)
        w = self.GetButtonWidth()
        self._tools_panel.SetMinSize(wx.Size(w, w*sizer.GetItemCount()))

        return btn

    # -----------------------------------------------------------------------

    def GetButtonWidth(self):
        """Return the width of the buttons in the toolbar."""
        return int(float(self.get_font_height()) * 1.8)

    # -----------------------------------------------------------------------

    def SetInitialSize(self, size=None):
        """Calculate and set a good size.

        :param size: an instance of wx.Size.

        """
        tb_w, tb_h = self._tools_panel.GetMinSize()
        min_w = tb_w
        min_h = tb_h
        self.SetMinSize(wx.Size(min_w, min_h))

        if size is None:
            size = wx.DefaultSize
        wx.Window.SetInitialSize(self, size)

    SetBestSize = SetInitialSize

    # -----------------------------------------------------------------------

    def DoGetBestSize(self):
        """Get the size which best suits the window."""
        tb_w, tb_h = self._tools_panel.GetSize()
        best_w = tb_w
        best_h = tb_h

        if self.IsExpanded() and self._child_panel:
            child_w, child_h = self._child_panel.GetBestSize()
            best_w = tb_w + child_w
            best_h = max(child_h, tb_h)

        return wx.Size(best_w, best_h)

    # -----------------------------------------------------------------------

    def Layout(self):
        """Do the layout."""
        # we need to complete the creation first
        if not self._tools_panel or not self._child_panel:
            return False

        w, h = self.GetClientSize()
        tw = self.GetButtonWidth()
        th = self.GetButtonWidth()

        if self.IsExpanded():
            sizer = self._tools_panel.GetSizer()
            th *= sizer.GetItemCount()

            th = max(h, th)
            # fix pos and size of the child window
            x = tw
            y = 0
            pw = w - x
            ph = th - y
            self._child_panel.SetSize(wx.Size(pw, ph))
            self._child_panel.SetPosition((x, y))
            self._child_panel.Show(True)
            self._child_panel.Layout()

        # fix pos and size of the left panel with tools
        self._tools_panel.SetPosition((0, 0))
        self._tools_panel.SetSize(wx.Size(tw, th))
        self._tools_panel.SetMinSize(wx.Size(tw, th))

        return True

    # -----------------------------------------------------------------------

    def _create_toolbar(self):
        """Create a panel with tools, including the collapsible button."""
        sizer = wx.BoxSizer(wx.VERTICAL)
        self._btn = self._create_collapsible_button()
        sizer.Add(self._btn, 0, wx.FIXED_MINSIZE, 0)

        label_btn = self._create_tool_button("slashdot")
        label_btn.Bind(wx.EVT_BUTTON, self._process_label_event)
        sizer.Add(label_btn, 0, wx.FIXED_MINSIZE | wx.TOP, 1)

        self._tools_panel.SetSizer(sizer)
        w = self.GetButtonWidth()
        self._tools_panel.SetMinSize(wx.Size(w, w*2))

    # -----------------------------------------------------------------------

    def _create_tool_button(self, icon, label=None):
        btn = BitmapButton(self._tools_panel, name=icon)
        btn.SetAlign(wx.ALIGN_CENTER)
        btn.SetFocusWidth(0)
        btn.SetSpacing(0)
        btn.SetBorderWidth(0)
        btn_w = self.GetButtonWidth()
        btn.SetSize(wx.Size(btn_w, btn_w))
        btn.SetMinSize(wx.Size(btn_w, btn_w))
        return btn

    # -----------------------------------------------------------------------

    def _create_tool_togglebutton(self, icon, label=None):
        btn = ToggleButton(self._tools_panel, name=icon)
        btn.SetAlign(wx.ALIGN_CENTER)
        btn.SetFocusWidth(0)
        btn.SetSpacing(0)
        btn.SetBorderWidth(0)
        btn_h = self.GetButtonWidth()
        btn.SetSize(wx.Size(btn_h, btn_h))
        btn.SetMinSize(wx.Size(btn_h, btn_h))
        return btn

    # ------------------------------------------------------------------------

    def _process_label_event(self, event):
        """Handle the wx.EVT_BUTTON event.

        :param event: a CommandEvent event to be processed.

        """
        evt_obj = event.GetEventObject()
        if evt_obj.GetName() == "slashdot":
            # Open a "window" to show the label
            win = LabelPopup(self.GetTopLevelParent(), wx.SIMPLE_BORDER, self._label)
            # Show the popup right below or above the button
            # depending on available screen space...
            pos = evt_obj.ClientToScreen((0, 0))
            # the label popup will hide the button.
            win.Position(pos, (0, 0))
            win.Show(True)

        else:
            # we shouldn't be here
            event.Skip()

# ---------------------------------------------------------------------------


class sppasCollapsiblePanel(sppasHorizontalRisePanel):
    """A collapsible panel is a window on which controls are placed.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2020  Brigitte Bigi

    """

    def __init__(self, parent, id=wx.ID_ANY, label="", pos=wx.DefaultPosition,
                 size=wx.DefaultSize, style=0, name="collapsible_panel"):
        """Create a sppasCollapsiblePanel.

        :param parent: (wx.Window) Parent window must NOT be none
        :param id: (int) window identifier or -1
        :param label: (string) Label of the button
        :param pos: (wx.Pos) the control position
        :param size: (wx.Size) the control size
        :param style: (int) the underlying window style
        :param name: (str) the widget name.

        The parent can Bind the wx.EVT_COLLAPSIBLEPANE_CHANGED.

        """
        super(sppasCollapsiblePanel, self).__init__(
            parent, id, label, pos, size, style, name=name)
        self._btn.SetLabel(label)
        self._btn.SetLabelPosition(wx.RIGHT)
        self._btn.SetAlign(wx.ALIGN_LEFT)

    # -----------------------------------------------------------------------

    def _create_tool_button(self, icon, label=None):
        if label is None:
            btn = BitmapButton(self._tools_panel, name=icon)
        else:
            btn = BitmapTextButton(self._tools_panel, label=label, name=icon)
            btn.SetLabelPosition(wx.LEFT)

        btn.SetAlign(wx.ALIGN_CENTER)
        btn.SetFocusWidth(0)
        btn.SetSpacing(0)
        btn.SetBorderWidth(0)
        btn_h = self.GetButtonHeight()
        btn.SetSize(wx.Size(btn_h, btn_h))
        btn.SetMinSize(wx.Size(btn_h, btn_h))
        return btn

    # -----------------------------------------------------------------------

    def GetToolsPane(self):
        """Return a reference to the embedded collapse tool window."""
        return self._tools_panel

    # -----------------------------------------------------------------------

    def AddButton(self, icon, direction=-1):
        """Override. Append or prepend a button into the toolbar.

        :param icon: (str) Name of the .png file of the icon or None
        :param direction: (int) Negative: at left, positive: at right.

        """
        btn = self._create_tool_button(icon)
        if direction >= 0:
            self._tools_panel.GetSizer().Add(btn, 0, wx.LEFT | wx.RIGHT, 1)
        else:
            self._tools_panel.GetSizer().Prepend(btn, 0, wx.LEFT | wx.RIGHT, 1)

        return btn

# -----------------------------------------------------------------------


class TestPanelCollapsiblePanel(sc.ScrolledPanel):

    def __init__(self, parent):
        super(TestPanelCollapsiblePanel, self).__init__(
            parent,
            style=wx.BORDER_NONE | wx.WANTS_CHARS | wx.HSCROLL | wx.VSCROLL,
            name="Test Collapsible Panels")

        p1 = sppasVerticalRisePanel(self, label="SPPAS Vertical rise panel...")
        child_panel = p1.GetPane()
        child_panel.SetBackgroundColour(wx.RED)
        self.MakePanelContent(child_panel)
        self.Bind(wx.EVT_COLLAPSIBLEPANE_CHANGED, self.OnCollapseChanged, p1)

        p2 = sppasHorizontalRisePanel(self, label="this label should not be visible...")
        p2.SetExpandedIcon("arrow_combo")
        p2.SetBorder(0)
        child_panel = sppasPanel(p2)
        p2.SetBackgroundColour(wx.YELLOW)
        self.MakePanelContent(child_panel)
        p2.SetPane(child_panel)
        self.Bind(wx.EVT_COLLAPSIBLEPANE_CHANGED, self.OnCollapseChanged, p2)

        p3 = sppasCollapsiblePanel(self, label="SPPAS Collapsible Panel...")
        p3.AddButton("folder", direction=1)
        child_panel = p3.GetPane()
        child_panel.SetBackgroundColour(wx.BLUE)
        self.MakePanelContent(child_panel)
        p3.Expand()
        checkbox = p3.AddButton("choice_checkbox")
        self.Bind(wx.EVT_COLLAPSIBLEPANE_CHANGED, self.OnCollapseChanged, p3)
        checkbox.Bind(wx.EVT_BUTTON, self.OnCkeckedPanel)

        p4 = sppasCollapsiblePanel(self, label="this label should not be visible")
        p4.SetLabel("This text is readable")
        child_panel = p4.GetPane()
        child_panel.SetBackgroundColour(wx.GREEN)
        self.MakePanelContent(child_panel)
        self.Bind(wx.EVT_COLLAPSIBLEPANE_CHANGED, self.OnCollapseChanged, p4)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(p1, 0, wx.ALIGN_LEFT | wx.ALL, border=10)
        sizer.Add(p2, 0, wx.ALIGN_LEFT | wx.ALL, border=10)
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

