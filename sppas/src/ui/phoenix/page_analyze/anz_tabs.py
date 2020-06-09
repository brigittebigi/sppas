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

    ui.phoenix.page_analyze.anz_tabs.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""

import wx
import wx.lib.newevent

from sppas.src.config import msg
from sppas.src.utils import u

from ..windows import Error
from ..windows import sppasPanel
from ..windows import sppasToolbar
from ..windows import sppasStaticLine
from ..windows import RadioButton

from ..main_events import TabChangeEvent, EVT_TAB_CHANGE

# ---------------------------------------------------------------------------
# Internal use of an event, when the tab has changed.

TabChangedEvent, EVT_TAB_CHANGED = wx.lib.newevent.NewEvent()
TabChangedCommandEvent, EVT_TAB_CHANGED_COMMAND = wx.lib.newevent.NewCommandEvent()

TabCreatedEvent, EVT_TAB_CREATED = wx.lib.newevent.NewEvent()
TabCreatedCommandEvent, EVT_TAB_CREATED_COMMAND = wx.lib.newevent.NewCommandEvent()


# ---------------------------------------------------------------------------
# List of displayed messages:


def _(message):
    return u(msg(message, "ui"))


TAB_TITLE = _("Tabs: ")
TAB = _("Tab")
TAB_ACT_OPEN = _("Open files")
TAB_ACT_NEW_TAB = _("New tab")
TAB_ACT_CLOSE_TAB = _("Close tab")

# ---------------------------------------------------------------------------


class TabsManager(sppasPanel):
    """Manage the tabs and actions to perform on them.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      contact@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2019  Brigitte Bigi

    """

    HIGHLIGHT_COLOUR = wx.Colour(96, 196, 196, 196)

    def __init__(self, parent, name=wx.PanelNameStr):
        super(TabsManager, self).__init__(
            parent,
            id=wx.ID_ANY,
            pos=wx.DefaultPosition,
            size=wx.DefaultSize,
            style=wx.BORDER_NONE | wx.TAB_TRAVERSAL | wx.WANTS_CHARS | wx.NO_FULL_REPAINT_ON_RESIZE,
            name=name)

        # Construct the panel
        self._create_content()
        self._setup_events()
        self.Layout()

    # ------------------------------------------------------------------------
    # Actions to perform on the tabs
    # ------------------------------------------------------------------------

    def get_selected_tab(self):
        """Return the index of the currently selected tab, or -1."""
        tabs = self.FindWindow("tabslist")
        return tabs.get_current()

    # -----------------------------------------------------------------------

    def get_tab_color(self, index):
        """Return the color of a tab.

        :param index: (int) Index of the tab to search for the color.

        """
        tabs = self.FindWindow("tabslist")
        return tabs.get_color(index)

    # -----------------------------------------------------------------------

    def set_tab_color(self, index, color):
        """Set the color of a tab.

        :param index: (int) Index of the tab to fix the color.
        :param color: (wx.Colour)

        """
        tabs = self.FindWindow("tabslist")
        return tabs.set_color(index, color)

    # -----------------------------------------------------------------------

    def append_tab(self):
        """Append a new tab in the list of tabs.

        :return: (int) Index of the tab.

        """
        tabs = self.FindWindow("tabslist")
        index = tabs.append()
        return index

    # -----------------------------------------------------------------------

    def remove_tab(self, index):
        """Remove the tab at the given index.

        :param index: (int) Index of the tab
        :return: (bool)

        """
        tabs = self.FindWindow("tabslist")
        try:
            tabs.remove(index)
        except Exception as e:
            wx.LogError("Tab not removed at index {:d}: "
                        "{:s}".format(index, str(e)))
            return False

        return True

    # -----------------------------------------------------------------------

    def switch_to_tab(self, index):
        """Switch to the tab matching the given name.

        :param index: (int) Index of the tab
        :return: (bool)

        """
        tabs = self.FindWindow("tabslist")
        try:
            tabs.switch_to(index)
        except Exception as e:
            wx.LogError("Tab not switched to index {:d}: "
                        "{:s}".format(index, str(e)))
            return False

        return True

    # ------------------------------------------------------------------------
    # Private methods to construct the panel.
    # ------------------------------------------------------------------------

    def _create_content(self):
        """Create the main content."""
        tb = self.__create_toolbar()
        tabs = TabsPanel(self, name="tabslist")

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(tb, 0, wx.EXPAND, 0)
        sizer.Add(self.__create_hline(), 0, wx.EXPAND, 0)
        sizer.Add(tabs, 2, wx.EXPAND, 0)

        self.SetSizer(sizer)

    # -----------------------------------------------------------------------

    def __create_toolbar(self):
        """Create the toolbar."""
        tb = sppasToolbar(self, orient=wx.VERTICAL, name="TabsManager-toolbar")
        tb.set_focus_color(TabsManager.HIGHLIGHT_COLOUR)
        tb.AddTitleText(TAB_TITLE, TabsManager.HIGHLIGHT_COLOUR)
        tb.AddButton("files-edit-file", TAB_ACT_OPEN)
        tb.AddButton("tab-add", TAB_ACT_NEW_TAB)
        tb.AddButton("tab-del", TAB_ACT_CLOSE_TAB)

        return tb

    # ------------------------------------------------------------------------

    def __create_hline(self):
        """Create an horizontal line, used to separate the panels."""
        line = sppasStaticLine(self, orient=wx.LI_HORIZONTAL)
        line.SetMinSize(wx.Size(-1, 20))
        line.SetPenStyle(wx.PENSTYLE_SHORT_DASH)
        line.SetDepth(1)
        return line

    # -----------------------------------------------------------------------
    # Events management
    # -----------------------------------------------------------------------

    def _setup_events(self):
        """Associate a handler function with the events.

        It means that when an event occurs then the process handler function
        will be called.

        """
        # The user pressed a key of its keyboard
        self.Bind(wx.EVT_KEY_DOWN, self._process_key_event)

        # The user clicked an action button of the toolbar
        self.Bind(wx.EVT_BUTTON, self._process_action)

        # The tab has changed.
        # This event is sent by the 'tabslist' child window.
        self.Bind(EVT_TAB_CHANGED, self._process_tab_changed)

    # -----------------------------------------------------------------------

    def _process_key_event(self, event):
        """Process a key event.

        :param event: (wx.Event)

        """
        key_code = event.GetKeyCode()
        wx.LogDebug('Tabs manager received the key event {:d}'
                      ''.format(key_code))
        wx.LogDebug('Key event skipped by the tab manager.')
        event.Skip()

    # ------------------------------------------------------------------------

    def _process_tab_changed(self, event):
        """Process a change of tab event: the active tab changed.
        
        Notify the parent of this change.

        :param event: (wx.Event) TabChangeEvent

        """
        wx.LogDebug('Tabs manager received a tab change event.')

        evt = TabChangeEvent(action="show",
                             cur_tab=event.cur_tab,
                             dest_tab=event.dest_tab)
        evt.SetEventObject(self)
        wx.PostEvent(self.GetParent(), evt)

    # ------------------------------------------------------------------------

    def _process_action(self, event):
        """Process a button event: an action has to be performed.

        :param event: (wx.Event)

        """
        wx.LogDebug('Tabs manager received a button event.')
        event_name = event.GetButtonObj().GetName()

        if event_name == "files-edit-file":
            self.__event_open_files()

        elif event_name == "tab-add":
            self.__event_append_tab()

        elif event_name == "tab-del":
            self.__event_remove_tab()

        event.Skip()

    # ------------------------------------------------------------------------

    def __event_append_tab(self):
        """Notify the parent the user asked to append a tab."""
        wx.LogDebug('Tabs manager notify the parent to append a tab.')
        evt = TabChangeEvent(action="append",
                             dest_tab=None)
        evt.SetEventObject(self)
        wx.PostEvent(self.GetParent(), evt)

    # ------------------------------------------------------------------------

    def __event_remove_tab(self):
        """Notify the parent the user asked to remove a tab."""
        wx.LogDebug('Tabs manager notify the parent to remove a tab.')
        tabs = self.FindWindow("tabslist")

        nb_tabs = tabs.get_count()
        # we never created a tab before
        if nb_tabs == 0:
            wx.LogError("There's no tab in the list to remove")
            return

        current = tabs.get_current()
        wx.LogDebug(" ... tab at index = {:d}".format(current))
        if current == -1:
            wx.LogError("No tab is checked to be closed.")
        else:
            evt = TabChangeEvent(action="remove",
                                 dest_tab=None)
            evt.SetEventObject(self)
            wx.PostEvent(self.GetParent(), evt)

    # -----------------------------------------------------------------------

    def __event_open_files(self):
        """Notify the parent to open files into the current tab."""
        tabs = self.FindWindow("tabslist")
        current = tabs.get_current()
        if current == -1:
            Error("No tab is checked to open files.")
        else:
            evt = TabChangeEvent(action="open", dest_tab=None)
            evt.SetEventObject(self)
            wx.PostEvent(self.GetParent(), evt)


# ----------------------------------------------------------------------------
# Panel to display list of available tabs
# ----------------------------------------------------------------------------


class TabsPanel(sppasPanel):
    """Manager of the list buttons of the available tabs in the software.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      contact@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2019  Brigitte Bigi

    The parent has to handle EVT_TAB_CHANGED event to be informed that a
    tab changed.

    """

    HIGHLIGHT_COLOUR = wx.Colour(92, 192, 192, 128)

    # -----------------------------------------------------------------------

    def __init__(self, parent, name="tabslist"):
        super(TabsPanel, self).__init__(
            parent,
            id=wx.ID_ANY,
            pos=wx.DefaultPosition,
            size=wx.DefaultSize,
            style=wx.BORDER_NONE | wx.NO_FULL_REPAINT_ON_RESIZE,
            name=name)

        self.__current = -1
        self.__counter = 0
        self.__colors = dict()

        self._create_content()
        self._setup_events()
        self.Layout()

    # -----------------------------------------------------------------------
    # Manage the tabs
    # -----------------------------------------------------------------------

    def check_index(self, index):
        """Check if the given index is matching a tab.

        :param index: (int) Index to check

        """
        index = int(index)
        if index < 0 or index >= self.GetSizer().GetItemCount():
            raise IndexError("Tab index {:d} out of range (0..{:d})"
                             "".format(index, self.GetSizer().GetItemCount()-1))
        return index

    # -----------------------------------------------------------------------

    def get_count(self):
        """Return the number of tabs."""
        return self.GetSizer().GetItemCount()

    # -----------------------------------------------------------------------

    def get_current(self):
        """Return the index of the current tab."""
        return self.__current

    # -----------------------------------------------------------------------

    def get_name(self, index):
        """Return the name of the page.

        :param index: (int) Index of the tab to get the name
        :raise: IndexError
        :return: (str)

        """
        index = self.check_index(index)
        btn_name = self.GetSizer().GetItem(index).GetWindow().GetName()
        return btn_name.replace("btn_", "page_")

    # -----------------------------------------------------------------------

    def get_index(self, name):
        """Return the index from the name of the page.

        :param name: (str)
        :return: int
        :raise: ValueError

        """
        n = name.replace("page_", "btn_")
        for i, child in enumerate(self.GetSizer().GetChildren()):
            if child.GetWindow().GetName() == n:
                return i

        raise ValueError("Unknown page name {:s}".format(name))

    # -----------------------------------------------------------------------

    def get_color(self, index):
        """Return the highlight color of the button.

        :param index: (int) Index of the tab to get the name
        :raise: IndexError

        """
        index = self.check_index(index)
        btn = self.GetSizer().GetItem(index).GetWindow()
        return self.__colors[btn]

    # -----------------------------------------------------------------------

    def set_color(self, index, color):
        """Set the a new color to the tab at the given index.

        :param index: (int) Index of the tab
        :param color: (wx.Colour)

        """
        index = self.check_index(index)
        btn = self.GetSizer().GetItem(index).GetWindow()
        if isinstance(color, wx.Colour):
            self.__colors[btn] = color

    # -----------------------------------------------------------------------

    def append(self):
        """Add a button corresponding to the name of a tab.

        :returns: Index of the button in the sizer

        """
        self.__counter += 1
        name = "btn_tab_anz_{:d}".format(self.__counter)
        label = TAB + " #{:d}".format(self.__counter)

        btn = RadioButton(self, label=label, name=name)
        btn.SetBorderWidth(2)
        btn.SetValue(False)
        btn.SetSpacing(sppasPanel.fix_size(12))
        btn.SetMinSize(wx.Size(-1, sppasPanel.fix_size(32)))
        btn.SetSize(wx.Size(-1, sppasPanel.fix_size(32)))
        self.__colors[btn] = TabsPanel.HIGHLIGHT_COLOUR
        self.__set_normal_btn_style(btn)
        self.GetSizer().Add(btn, 0, wx.EXPAND | wx.ALL, 2)
        self.Layout()
        self.Refresh()

        return self.GetSizer().GetItemCount() - 1

    # -----------------------------------------------------------------------

    def remove(self, index):
        """Remove a button at the given index.

        :param index: (int) Index of the tab to remove
        :raise: IndexError

        """
        index = self.check_index(index)

        # Delete windows and remove of the list
        item = self.GetSizer().GetItem(index)
        btn = item.GetWindow()
        self.__colors.pop(btn)

        item.DeleteWindows()
        self.GetSizer().Remove(index)
        self.Layout()
        self.Refresh()

        if index == self.__current:
            self.__current = -1

    # -----------------------------------------------------------------------

    def switch_to(self, index):
        """Switch from the current tab to the one at the given index.

        :param index: (int) Index of the tab to switch on

        """
        index = self.check_index(index)

        # set the current button in a normal state
        if self.__current != -1:
            btn = self.GetSizer().GetItem(self.__current).GetWindow()
            self.__btn_set_state(btn, False)

        # the one we want to switch on
        self.__current = index
        btn = self.GetSizer().GetItem(self.__current).GetWindow()
        self.__btn_set_state(btn, True)

    # -----------------------------------------------------------------------
    # Private methods to construct the panel.
    # -----------------------------------------------------------------------

    def _create_content(self):
        """Create the main content."""
        sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(sizer)
        self.SetMinSize(wx.Size(sppasPanel.fix_size(128),
                                sppasPanel.fix_size(32)*self.GetSizer().GetItemCount()))

    # -----------------------------------------------------------------------

    def __set_normal_btn_style(self, button):
        """Set a normal style to a button."""
        button.SetBorderWidth(0)
        button.BorderColour = self.GetForegroundColour()
        button.BorderStyle = wx.PENSTYLE_SOLID
        button.FocusColour = TabsManager.HIGHLIGHT_COLOUR

    # -----------------------------------------------------------------------

    def __set_active_btn_style(self, button):
        """Set a special style to the button."""
        button.SetBorderWidth(1)
        button.SetBorderStyle(wx.PENSTYLE_SOLID)
        button.SetFocusColour(self.GetForegroundColour())
        if button in self.__colors:
            button.SetBorderColour(self.__colors[button])

    # -----------------------------------------------------------------------
    # Events management
    # -----------------------------------------------------------------------

    def _setup_events(self):
        """Associate a handler function with the events.

        It means that when an event occurs then the process handler function
        will be called.

        """
        self.Bind(wx.EVT_RADIOBUTTON, self.__process_checked)

    # -----------------------------------------------------------------------

    def __process_checked(self, event):
        """Process a checkbox event.

        :param event: (wx.Event)

        """
        # the button we want to switch on
        tab_btn = event.GetButtonObj()
        tab_index = 0
        while self.GetSizer().GetItem(tab_index).GetWindow() != tab_btn:
            tab_index += 1

        # the current button
        if self.__current != -1:
            cur_btn = self.GetSizer().GetItem(self.__current).GetWindow()
        else:
            cur_btn = None

        # user clicked a different button, not the current one
        if cur_btn == tab_btn:
            # user clicked the current tab
            tab_btn.SetValue(True)

        else:
            # set the current button in a normal state
            # if cur_btn is not None:
            #     self.__btn_set_state(cur_btn, False)
            # assign the new tab
            # self.__current = tab_index
            # self.__btn_set_state(tab_btn, True)

            # the parent will decide what to exactly do with this change
            evt = TabChangedEvent(cur_tab=self.__current,
                                  dest_tab=tab_index)
            evt.SetEventObject(self)
            wx.PostEvent(self.GetParent(), evt)

    # -----------------------------------------------------------------------
    # Private methods
    # -----------------------------------------------------------------------

    def __btn_set_state(self, btn, state):
        if state is True:
            self.__set_active_btn_style(btn)
        else:
            self.__set_normal_btn_style(btn)
        btn.SetValue(state)
        btn.Refresh()

# ----------------------------------------------------------------------------
# Panel tested by test_glob.py
# ----------------------------------------------------------------------------


class TestPanel(sppasPanel):

    def __init__(self, parent):
        super(TestPanel, self).__init__(parent)
        self.SetBackgroundColour(wx.Colour(128, 128, 128))
        self.tabs = TabsManager(parent=self)
        s = wx.BoxSizer()
        s.Add(self.tabs, 1, wx.EXPAND)
        self.SetSizer(s)
        self.Layout()
        self.Bind(EVT_TAB_CHANGE, self._process_tab_change)

    # -----------------------------------------------------------------------

    def _process_tab_change(self, event):
        """Process a change of tab.

        A tab is matching a page of the book. When the tab changed, the page
        displaying the files has to be changed too.

        :param event: (wx.Event)

        """
        wx.LogDebug("Process tab change event (show/open/append/remove).")
        emitted = event.GetEventObject()
        try:
            action = event.action
            dest_index = event.dest_tab
        except:
            wx.LogError('Malformed event emitted by {:s}'
                        '.'.format(emitted.GetName()))
            return

        if action == "open":
            wx.LogDebug(" --- event tab change with action open")

        elif action == "append":
            wx.LogDebug(" --- event tab change with action append")
            i = self.tabs.append_tab()
            if i == 0:
                self.tabs.switch_to_tab(i)

        elif action == "remove":
            wx.LogDebug(" --- event tab change with action remove")
            cur_index = self.tabs.get_selected_tab()
            self.tabs.remove_tab(cur_index)
            # Here we could switch to another tab...

        elif action == "show":
            wx.LogDebug(" --- event tab change with action show")
            self.tabs.switch_to_tab(dest_index)
