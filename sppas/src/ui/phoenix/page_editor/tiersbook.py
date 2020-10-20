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

    src.ui.phoenix.page_editor.tiersbook.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""

import os
import wx
import wx.lib.newevent

from sppas.src.config import paths
from sppas.src.anndata import sppasRW

from ..windows.book import sppasSimplebook
from ..windows.panels import sppasPanel
from ..anz_panels.tierlist import sppasTierListCtrl
from ..windows import sppasComboBox

# ---------------------------------------------------------------------------

PageChangeEvent, EVT_PAGE_CHANGE = wx.lib.newevent.NewEvent()
PageChangeCommandEvent, EVT_PAGE_CHANGE_COMMAND = wx.lib.newevent.NewCommandEvent()

# ---------------------------------------------------------------------------


class sppasTiersBook(sppasSimplebook):
    """Create a book to display the content of tiers in lists.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2020  Brigitte Bigi

    """

    def __init__(self, parent, name="tiers_book"):
        super(sppasTiersBook, self).__init__(
            parent=parent,
            style=wx.BORDER_SIMPLE | wx.TAB_TRAVERSAL | wx.WANTS_CHARS,
            name=name
        )
        self.SetEffectsTimeouts(150, 150)

    # -----------------------------------------------------------------------

    def add_tiers(self, filename, tiers):
        """Add a set of tiers of the file.

        If no tier was previously selected, select the first one.

        :param filename: (str)
        :param tiers: (list of sppasTier)
        :return: selected tier changed

        """
        if self.GetPageCount() > 0:
            # A page is already selected
            sel_tier = False
        else:
            sel_tier = True

        for tier in tiers:
            if len(tier) > 0:
                page = sppasTierListCtrl(self, tier, filename, style=wx.BORDER_SIMPLE)

                if sel_tier is None:
                    self.ShowNewPage(page)
                    sel_tier = True
                else:
                    self.AddPage(page, "")

            else:
                wx.LogError("Page not created. "
                            "No annotation in tier: {:s}".format(tier.get_name()))

        return sel_tier

    # -----------------------------------------------------------------------

    def remove_tiers(self, filename, tiers):
        """Remove a set of tiers of the file.

        If the selected tier is among the removed one, select another one.

        :param filename: (str)
        :param tiers: (list of sppasTier)
        :return: (bool) The page was changed

        """
        wx.LogDebug(" = remove_tiers of the tierbook with {:s}".format(filename))
        wx.LogDebug(" = the tierbook contains {:d} pages".format(self.GetPageCount()))
        tier_names = [tier.get_name() for tier in tiers]
        for page_index in reversed(range(self.GetPageCount())):
            page = self.GetPage(page_index)
            if page.get_filename() == filename:
                if page.get_tiername() in tier_names:
                    wx.LogDebug("Delete page of tier {:s} at index {:d}".format(page.get_tiername(), page_index))
                    self.DeletePage(page_index)

        wx.LogDebug(" = the tierbook now contains {:d} pages".format(self.GetPageCount()))
        if self.GetPageCount() > 0:
            page_sel = self.GetSelection()
            wx.LogDebug(" -> new page selection index: {}".format(page_sel))
            if page_sel != wx.NOT_FOUND:
                wx.LogDebug(" -> new selected tier: {}".format(self.GetPage(page_sel).get_tiername()))
                return True

        return False

    # -----------------------------------------------------------------------

    def get_selected_tiername(self):
        page_sel = self.GetSelection()
        if page_sel != wx.NOT_FOUND:
            page = self.GetPage(page_sel)
            return self.GetPage(page_sel).get_tiername()
        return None

    # -----------------------------------------------------------------------

    def get_selected_filename(self):
        page_sel = self.GetSelection()
        if page_sel != wx.NOT_FOUND:
            return self.GetPage(page_sel).get_filename()
        return None

    # -----------------------------------------------------------------------
    # Events management
    # -----------------------------------------------------------------------

    def _setup_events(self):
        """Associate a handler function with the events.

        It means that when an event occurs then the process handler function
        will be called.

        """
        # Capture keys
        # self.Bind(wx.EVT_CHAR_HOOK, self._process_key_event)

        # Change the displayed page
        self.Bind(EVT_PAGE_CHANGE, self._process_page_change)

    # ------------------------------------------------------------------------

    def _process_page_change(self, event):
        """Process a PageChangeEvent.

        :param event: (wx.Event)

        """
        try:
            destination = event.to_page
        except AttributeError:
            destination = 0

        self.show_page(destination)

    # -----------------------------------------------------------------------
    # Public methods to navigate
    # -----------------------------------------------------------------------

    def show_page(self, page_index):
        """ChangeSelection with a top/bottom effect.

        :param page_index: (str) Index of the page to switch to

        """
        p = page_index
        if p == -1:
            p = 0

        # Current page number
        c = self.FindPage(self.GetCurrentPage())  # current page position

        # Showing the current page is already done!
        if c == p:
            return

        # Assign the effect
        if c < p:
            self.SetEffects(showEffect=wx.SHOW_EFFECT_SLIDE_TO_TOP,
                            hideEffect=wx.SHOW_EFFECT_SLIDE_TO_TOP)
        elif c > p:
            self.SetEffects(showEffect=wx.SHOW_EFFECT_SLIDE_TO_BOTTOM,
                            hideEffect=wx.SHOW_EFFECT_SLIDE_TO_BOTTOM)

        # Change to the destination page
        self.ChangeSelection(p)

# ---------------------------------------------------------------------------


class TestPanel(sppasPanel):

    def __init__(self, parent):
        super(TestPanel, self).__init__(parent, name="Test Tiers List Editor")

        p = sppasTiersBook(self)

        f1 = os.path.join(paths.samples, "annotation-results", "samples-fra", "F_F_B003-P8-palign.xra")
        f2 = os.path.join(paths.samples, "annotation-results", "samples-fra", "F_F_B003-P8-phon.xra")

        parser = sppasRW(f1)
        trs1 = parser.read()
        parser.set_filename(f2)
        trs2 = parser.read()
        p.add_tiers(f1, trs1.get_tier_list())
        p.add_tiers(f2, trs2.get_tier_list())

        all_tiers = [t.get_name() for t in trs1.get_tier_list()]
        for t in trs2.get_tier_list():
            all_tiers.append(t.get_name())
        c = sppasComboBox(self, choices=all_tiers)

        s = wx.BoxSizer(wx.VERTICAL)
        s.Add(c, 0, wx.EXPAND)
        s.Add(p, 1, wx.EXPAND)
        self.SetSizer(s)
        c.Bind(wx.EVT_COMBOBOX, self._on_page_change)

    # -----------------------------------------------------------------------

    def _on_page_change(self, event):
        """Switch page..."""
        c = event.GetEventObject()
        idx = c.GetSelection()
        p = self.FindWindow("tiers_book")
        p.show_page(idx)

    # -----------------------------------------------------------------------

    def _process_view_event(self, evt):
        wx.LogDebug("Received action {} with value {}".format(evt.action, str(evt.value)))

