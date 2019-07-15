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
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""

import logging
import wx
import wx.lib.newevent

from sppas import msg
from sppas import u

from ..dialogs import Error
from ..windows import sppasPanel
from ..windows import sppasToolbar
from ..windows import sppasStaticLine
from ..windows import RadioButton
from ..main_events import TabChangeEvent

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


TAB_TITLE = "Tabs: "
TAB_ACT_OPEN = "Open files"
TAB_ACT_NEW_TAB = "New tab"
TAB_ACT_CLOSE_TAB = "Close tab"
TAB_VIEW_LIST = "Summary"
TAB_VIEW_TIME = "Time line"
TAB_VIEW_TEXT = "Text edit"
TAB_VIEW_GRID = "Grid details"
TAB_VIEW_STAT = "Statistics"

TAB_MSG_CONFIRM_SWITCH = "Confirm switch of tab?"
TAB_MSG_CONFIRM = "The current tab contains not saved work that " \
                  "will be lost. Are you sure you want to change tab?"
TAB_ACT_SAVECURRENT_ERROR = "The current tab can not be saved due to " \
                     "the following error: {:s}\nAre you sure you want " \
                     "to change tab?"

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

        self.__counter = 0

        # Construct the panel
        self._create_content()
        self._setup_events()
        self.Layout()

    # ------------------------------------------------------------------------
    # Private methods to construct the panel.
    # ------------------------------------------------------------------------

    def _create_content(self):
        """Create the main content."""
        tb = self.__create_toolbar()
        cv = TabsPanel(self, name="tabslist")

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(tb, 0, wx.EXPAND, 0)
        sizer.Add(self.__create_hline(), 0, wx.EXPAND, 0)
        sizer.Add(cv, 2, wx.EXPAND, 0)

        self.SetMinSize(wx.Size(128, -1))
        self.SetSizer(sizer)

    # -----------------------------------------------------------------------

    def __create_toolbar(self):
        """Create the toolbar."""
        tb = sppasToolbar(self, orient=wx.VERTICAL)
        tb.set_focus_color(TabsManager.HIGHLIGHT_COLOUR)
        tb.AddTitleText(TAB_TITLE, TabsManager.HIGHLIGHT_COLOUR)
        tb.AddButton("files-edit-file", TAB_ACT_OPEN)
        tb.AddButton("tab-add", TAB_ACT_NEW_TAB)
        tb.AddButton("tab-del", TAB_ACT_CLOSE_TAB)
        tb.AddText("Views: ")
        tb.AddToggleButton("data-view-list", TAB_VIEW_LIST, value=True, group_name="view")
        tb.AddToggleButton("data-view-timeline", TAB_VIEW_TIME, value=False, group_name="view")
        tb.AddToggleButton("data-view-text", TAB_VIEW_TEXT, value=False, group_name="view")
        tb.AddToggleButton("data-view-grid", TAB_VIEW_GRID, value=False, group_name="view")
        tb.AddToggleButton("data-view-stats", TAB_VIEW_STAT, value=False, group_name="view")
        return tb

    # ------------------------------------------------------------------------

    def __create_hline(self):
        """Create an horizontal line, used to separate the panels."""
        line = sppasStaticLine(self, orient=wx.LI_HORIZONTAL)
        line.SetMinSize(wx.Size(-1, 20))
        line.SetPenStyle(wx.PENSTYLE_SHORT_DASH)
        line.SetDepth(1)
        line.SetForegroundColour(self.GetForegroundColour())
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

        # The user clicked (LeftDown - LeftUp) an action button of the toolbar
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
        logging.debug('Tabs manager received the key event {:d}'
                      ''.format(key_code))
        logging.debug('Key event skipped by the tab manager.')
        event.Skip()

    # ------------------------------------------------------------------------

    def _process_tab_changed(self, event):
        """Process a change of tab event: the active tab changed.
        
        Notify the parent of this change.

        :param event: (wx.Event) TabChangeEvent

        """
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
        event_name = event.GetButtonObj().GetName()
        logging.debug('action {:s}'.format(event_name))

        if event_name == "files-edit-file":
            self.open_files()

        elif event_name == "tab-add":
            self.append_tab()

        elif event_name == "tab-del":
            self.remove_tab()

        elif event_name.startswith("view-"):
            pass

        event.Skip()

    # ------------------------------------------------------------------------
    # Actions to perform on the tabs
    # ------------------------------------------------------------------------

    def open_files(self):
        """Open the checked files into the current tab."""
        logging.debug("Open checked file(s).")
        tabs = self.FindWindow("tabslist")
        current = tabs.get_current()
        # we did not created a tab anymore
        if current == -1:
            Error("No tab is checked to open files.")
        else:

            cur_name = tabs.get_name(current)
            if cur_name is not None:
                evt = TabChangeEvent(action="open",
                                     cur_tab=cur_name,
                                     dest_tab=None)
                evt.SetEventObject(self)
                wx.PostEvent(self.GetParent(), evt)

    # ------------------------------------------------------------------------

    def append_tab(self):
        """Append a tab to the list."""
        tabs = self.FindWindow("tabslist")
        self.__counter += 1
        page_name = "page_analyze_{:d}".format(self.__counter)
        dest = None

        # Append in the list of tabs
        tabs.append(page_name)

        # If this is the first tab, we have to switch on it.
        if tabs.get_count() == 1:
            tabs.switch_to(0)
            dest = page_name

        # Send the new page name to the parent
        evt = TabChangeEvent(action="append",
                             cur_tab=page_name,
                             dest_tab=dest)
        evt.SetEventObject(self)
        wx.PostEvent(self.GetParent(), evt)

    # -----------------------------------------------------------------------

    def remove_tab(self):
        """Remove a tab to the list."""
        tabs = self.FindWindow("tabslist")
        nb_tabs = tabs.get_count()
        # we never created a tab before or we have only one tab
        if nb_tabs <= 1:
            return

        # Remove of the list of tabs (if we can)
        try:
            current = tabs.get_current()
            cur_name = tabs.get_name(current)
            tabs.remove(current)
        except Exception:
            return

        # We have to switch to the previous tab (or the next one)
        if current > 0:
            dest_index = current - 1
            dest = tabs.get_name(current - 1)
        else:
            dest = tabs.get_name(0)
            dest_index = 0

        tabs.switch_to(dest_index)

        # Send the removed and destination page names to the parent
        evt = TabChangeEvent(action="remove",
                             cur_tab=cur_name,
                             dest_tab=dest)
        evt.SetEventObject(self)
        wx.PostEvent(self.GetParent(), evt)

# ----------------------------------------------------------------------------
# Panel to display opened files
# ----------------------------------------------------------------------------


class TabsPanel(sppasPanel):
    """Manager of a list buttons of the available tabs in the software.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      contact@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2019  Brigitte Bigi

    The parent has to handle EVT_TAB_CHANGED event to be informed that a
    tab changed.

    """

    def __init__(self, parent, name="tabslist", tabs=list()):
        super(TabsPanel, self).__init__(
            parent,
            id=wx.ID_ANY,
            pos=wx.DefaultPosition,
            size=wx.DefaultSize,
            style=wx.BORDER_NONE | wx.NO_FULL_REPAINT_ON_RESIZE,
            name=name)

        self.__tabs = tabs
        self.__current = -1

        self._create_content()
        self._setup_events()
        self.Layout()

    # -----------------------------------------------------------------------
    # Manage the tabs
    # -----------------------------------------------------------------------

    def get_count(self):
        """Return the number of tabs."""
        return len(self.__tabs)

    # -----------------------------------------------------------------------

    def get_current(self):
        """Return the index of the current tab."""
        return self.__current

    # -----------------------------------------------------------------------

    def get_name(self, index):
        """Return the name of the tab or None."""
        try:
            return self.__tabs[index]
        except IndexError:
            return None

    # -----------------------------------------------------------------------

    def set_value(self, name, value=False):
        """"""
        index = self.__tabs.index(name)
        item = self.GetSizer().GetItem(index)
        btn = item.GetWindow()
        btn.SetValue(value)
        if value is False:
            self.__set_normal_btn_style(btn)
        else:
            self.__set_active_btn_style(btn)
        btn.Refresh()

    # -----------------------------------------------------------------------

    def append(self, name):
        """Add a button corresponding to the name of a tab.

        :param name: (str)
        :param value: (bool)
        :returns: index of the newly created workspace

        """
        logging.debug('APPEND BUTTON {:s}'.format(name))
        if name in self.__tabs:
            raise ValueError('Name {:s} is already in the list of tabs.')

        btn = RadioButton(self, label=name, name=name)
        btn.SetValue(False)
        btn.SetSpacing(sppasPanel.fix_size(12))
        btn.SetMinSize(wx.Size(-1, sppasPanel.fix_size(32)))
        btn.SetSize(wx.Size(-1, sppasPanel.fix_size(32)))
        self.__tabs.append(name)
        self.__set_normal_btn_style(btn)
        self.GetSizer().Add(btn, 0, wx.EXPAND | wx.ALL, 2)
        self.Layout()
        self.Refresh()

    # -----------------------------------------------------------------------

    def remove(self, index):
        """Remove a button corresponding to the name of a tab.

        :param index: (str)

        """
        index = int(index)
        if index < 0 or index >= len(self.__tabs):
            raise IndexError("Tab index {:d} out of range (0..{:d})"
                             "".format(index, len(self.__tabs)-1))

        if len(self.__tabs) == 1:
            raise ValueError("At least one tab must exist")

        self.GetSizer().GetItem(index).DeleteWindows()
        self.GetSizer().Remove(index)
        self.Layout()
        self.Refresh()

        # Delete of the list
        self.__tabs.pop(index)
        if index == self.__current:
            self.__current = -1

    # -----------------------------------------------------------------------

    def switch_to(self, index):
        """Set the current tab at the given index.

        :param index: (int) Index of the tab to switch on

        """
        index = int(index)
        if index < 0 or index >= len(self.__tabs):
            raise IndexError("Tab index {:d} out of range (0..{:d})"
                             "".format(index, len(self.__tabs)-1))

        # set the current button in a normal state
        if self.__current != -1:
            cur_btn = self.GetSizer().GetItem(self.__current).GetWindow()
            self.__btn_set_state(cur_btn, False)

        # the one we want to switch on
        idx_btn = self.GetSizer().GetItem(index).GetWindow()
        self.__btn_set_state(idx_btn, True)
        self.__current = index

    # -----------------------------------------------------------------------
    # Private methods to construct the panel.
    # -----------------------------------------------------------------------

    def _create_content(self):
        """Create the main content."""
        sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(sizer)
        for name in self.__tabs:
            self.append(name)
        self.SetMinSize(wx.Size(sppasPanel.fix_size(128),
                                sppasPanel.fix_size(32)*len(self.__tabs)))

    # -----------------------------------------------------------------------

    def __set_normal_btn_style(self, button):
        """Set a normal style to a button."""
        button.BorderWidth = 1
        button.BorderColour = self.GetForegroundColour()
        button.BorderStyle = wx.PENSTYLE_SOLID
        button.FocusColour = TabsManager.HIGHLIGHT_COLOUR

    # -----------------------------------------------------------------------

    def __set_active_btn_style(self, button):
        """Set a special style to the button."""
        button.BorderWidth = 2
        button.BorderColour = TabsManager.HIGHLIGHT_COLOUR
        button.BorderStyle = wx.PENSTYLE_SOLID
        button.FocusColour = self.GetForegroundColour()

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

        Skip the event in order to allow the parent to handle it: it's to
        update the other windows with data of the new selected workspace.

        :param event: (wx.Event)

        """
        # the button we want to switch on
        tab_btn = event.GetButtonObj()
        tab_name = tab_btn.GetLabel()
        tab_index = self.__tabs.index(tab_name)

        # the current button
        if self.__current != -1:
            cur_btn = self.GetSizer().GetItem(self.__current).GetWindow()
            cur_name = self.get_name(self.__current)
        else:
            cur_btn = None
            cur_name = None

        # user clicked a different tab
        if cur_btn != tab_btn:

            evt = TabChangedEvent(cur_tab=cur_name,
                                  dest_tab=tab_name)
            evt.SetEventObject(self)

            if cur_btn is not None:
                # set the current button in a normal state
                self.__btn_set_state(cur_btn, False)

            # assign the new tab
            self.__current = tab_index
            self.__btn_set_state(tab_btn, True)

            # the parent will decide what to exactly do with this change
            wx.PostEvent(self.GetParent(), evt)

        else:
            # user clicked the current tab
            logging.info('Tab {:s} is already active.'
                         ''.format(tab_btn.GetLabel()))
            tab_btn.SetValue(True)

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
        logging.debug('Tab {:s} is checked: {:s}'
                      ''.format(btn.GetLabel(), str(state)))

# ----------------------------------------------------------------------------
# Panel tested by test_glob.py
# ----------------------------------------------------------------------------


class TestPanel(TabsManager):

    def __init__(self, parent):
        super(TestPanel, self).__init__(parent)
        self.SetBackgroundColour(wx.Colour(128, 128, 128))
