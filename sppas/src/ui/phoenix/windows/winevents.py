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

    src.ui.phoenix.windows.winevents.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""

import wx

# ---------------------------------------------------------------------------


class sppasWindowEvent(wx.PyCommandEvent):
    """Base class for an event sent when needed.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2020  Brigitte Bigi

    """

    def __init__(self, event_type, event_id):
        """Default class constructor.

        :param event_type: the event type;
        :param event_id: the event identifier.

        """
        super(sppasWindowEvent, self).__init__(event_type, event_id)
        self.__window = None

    # ------------------------------------------------------------------------

    def SetObj(self, win):
        """Set the event object for the event.

        :param win: (wx.Window) the window object

        """
        self.__window = win

    # ------------------------------------------------------------------------

    def GetObj(self):
        """Return the object associated with this event."""
        return self.__window

    # -----------------------------------------------------------------------

    Window = property(GetObj, SetObj)

