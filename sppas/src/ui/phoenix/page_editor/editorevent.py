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

    src.ui.phoenix.page_editor.editorevent.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""

import wx.lib.newevent


# Internal use of events by classes displaying files in a list-style
ListViewEvent, EVT_LIST_VIEW = wx.lib.newevent.NewEvent()
ListViewCommandEvent, EVT_LIST_VIEW_COMMAND = wx.lib.newevent.NewCommandEvent()

# Internal use of events by classes displaying files in a timeline-style
TimeViewEvent, EVT_TIME_VIEW = wx.lib.newevent.NewEvent()
TimeViewCommandEvent, EVT_TIME_VIEW_COMMAND = wx.lib.newevent.NewCommandEvent()
