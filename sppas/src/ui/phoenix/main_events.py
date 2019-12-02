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

    src.ui.phoenix.main_events.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Custom events for the main GUI.

"""

import wx.lib.newevent

# ---------------------------------------------------------------------------
# Event to be used when the data have changed.

DataChangedEvent, EVT_DATA_CHANGED = wx.lib.newevent.NewEvent()
DataChangedCommandEvent, EVT_DATA_CHANGED_COMMAND = wx.lib.newevent.NewCommandEvent()


# ---------------------------------------------------------------------------
# Event to be used when a change has to be done on a tab.
# The event must contain 2 members: "action, "dest_tab" (can be None)

TabChangeEvent, EVT_TAB_CHANGE = wx.lib.newevent.NewEvent()
TabChangeCommandEvent, EVT_TAB_CHANGE_COMMAND = wx.lib.newevent.NewCommandEvent()


# ---------------------------------------------------------------------------
# Event to be used when a switch has to be done on a view of files.
# The event must contain 1 member: the name of the view to switch on
# among: list, timeline, text, grid, stats
ViewChangeEvent, EVT_VIEW_CHANGE = wx.lib.newevent.NewEvent()
ViewChangeCommandEvent, EVT_VIEW_CHANGE_COMMAND = wx.lib.newevent.NewCommandEvent()


# ---------------------------------------------------------------------------
# Event to be used when something has to be done on a view of files.
# The event must contain 1 member: the 'action' to perform.
ViewEvent, EVT_VIEW = wx.lib.newevent.NewEvent()
ViewCommandEvent, EVT_VIEW_COMMAND = wx.lib.newevent.NewCommandEvent()
