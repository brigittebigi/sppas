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

    src.ui.phoenix.page_analyze.filters.relation.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    A dialog to fix a list of filters and any parameter needed.
    The dialog only allows to fix and format properly the filters, it doesn't
    apply them on any data.

"""

import wx
import wx.dataview
try:
    from agw import floatspin as FS
    import agw.ultimatelistctrl as ulc
except ImportError:
    import wx.lib.agw.floatspin as FS
    import wx.lib.agw.ultimatelistctrl as ulc

from sppas.src.config import msg
from sppas.src.utils import u

from sppas.src.ui.phoenix.windows import sppasDialog
from sppas.src.ui.phoenix.windows import sppasPanel
from sppas.src.ui.phoenix.windows import CheckButton
from sppas.src.ui.phoenix.windows import sppasTextCtrl, sppasStaticText

# --------------------------------------------------------------------------


def _(message):
    return u(msg(message, "ui"))


MSG_HEADER_TIERSFILTER = _("Filter annotations of tiers")

MSG_ANNOT_FORMAT = _("Replace the tag by the name of the filter")
MSG_FIT = _("Keep only the intersection of X intervals with Y ones, i.e. fit the tiers.")
MSG_NAME = _("Name")
MSG_OPT = _("Option")

# ---------------------------------------------------------------------------

Relations = (
               ('equals', ' Equals', '', '', ''),
               ('before', ' Before', 'Max delay\nin seconds: ', 3.0, 'max_delay'),
               ('after', ' After', 'Max delay\nin seconds: ', 3.0, 'max_delay'),
               ('meets', ' Meets', '', '', ''),
               ('metby', ' Met by', '', '', ''),
               ('overlaps', ' Overlaps', 'Min overlap\n in seconds: ', 0.030, 'overlap_min'),
               ('overlappedby', ' Overlapped by', 'Min overlap\n in seconds: ', 0.030, 'overlapped_min'),
               ('starts', ' Starts', '', '', ''),
               ('startedby', ' Started by', '', '', ''),
               ('finishes', ' Finishes', '', '', ''),
               ('finishedby', ' Finished by', '', '', ''),
               ('during', ' During', '', '', ''),
               ('contains', ' Contains', '', '', '')
            )

Illustrations = (
               # equals
               ('X |-----|\n'
                'Y |-----|',
                'Non efficient',
                'Non efficient',
                'X |\nY |'),
               # before
               ('X |-----|\nY' + ' ' * 15 + '|-----|',
                'X |-----|\nY' + ' ' * 15 + '|',
                'X |\nY   |-----|',
                'X |\nY   |'),
               # after
               ('X' + ' ' * 15 + '|-----|\nY |-----|',
                'X' + ' ' * 15 + '|\nY |-----|',
                'X   |-----|\nY |',
                'X   |\nY |'),
               # meets
               ('X |-----|\nY' + ' ' * 8 + '|-----|',
                'Non efficient',
                'Non efficient',
                'Non efficient'),
               # metby
               ('X' + ' ' * 8 + '|-----|\nY |-----|',
                'Non efficient',
                'Non efficient',
                'Non efficient'),
               # overlaps
               ('X |-----|\nY ' + ' ' * 5 + '|-----|',
                'Non efficient',
                'Non efficient',
                'Non efficient'),
               # overlappedby
               ('X' + ' ' * 5 + '|-----|\nY |-----|',
                'Non efficient',
                'Non efficient',
                'Non efficient'),
               # starts
               ('X |---|\n'
                'Y |-------|',
                'Non efficient',
                'Non efficient',
                'Non efficient'),
               # startedby
               ('X |-------|\n'
                'Y |---|',
                'Non efficient',
                'Non efficient',
                'Non efficient'),
               # finishes
               ('X       |---|\n'
                'Y |---------|',
                'Non efficient',
                'Non efficient',
                'Non efficient'),
               # finishedby
               ('X |--------|\n'
                'Y      |---|',
                'Non efficient',
                'Non efficient',
                'Non efficient'),
               # during
               ('X    |---|\n'
                'Y |--------|',
                'Non efficient',
                'X      |\nY |------|',
                'Non efficient'),
               # contains
               ('X |--------|\n'
                'Y    |---|',
                'X |-----|\nY     |',
                'Non efficient',
                'Non efficient'),
               )

ALLEN_RELATIONS = tuple(row + Illustrations[i] for i, row in enumerate(Relations))

# ---------------------------------------------------------------------------


class sppasTiersRelationFilterDialog(sppasDialog):
    """A dialog to filter annotations of tiers.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2020  Brigitte Bigi

    Returns wx.ID_OK if ShowModal().

    """

    def __init__(self, parent):
        """Create a dialog to fix settings.

        :param parent: (wx.Window)
        :param tiers: dictionary with key=filename, value=list of selected tiers

        """
        super(sppasTiersRelationFilterDialog, self).__init__(
            parent=parent,
            title="Tiers Relation Filter",
            style=wx.CAPTION | wx.RESIZE_BORDER | wx.CLOSE_BOX | wx.MAXIMIZE_BOX | wx.STAY_ON_TOP,
            name="tierfilter_dialog")

        self.CreateHeader(MSG_HEADER_TIERSFILTER, "tier_ann_view")
        self._create_content()
        self.CreateActions([wx.ID_CANCEL, wx.ID_OK])

        self.LayoutComponents()
        self.GetSizer().Fit(self)
        self.CenterOnParent()
        self.FadeIn()

    # -----------------------------------------------------------------------

    def SetFont(self, font):
        sppasDialog.SetFont(self, font)
        w = self.FindWindow("listctrl")
        mono_font = wx.Font(font.GetPointSize(),    # point size
                            wx.FONTFAMILY_TELETYPE,  # family,
                            wx.FONTSTYLE_NORMAL,   # style,
                            wx.FONTWEIGHT_NORMAL,  # weight,
                            underline=False,
                            encoding=wx.FONTENCODING_SYSTEM)
        w.SetFont(mono_font)

    # -----------------------------------------------------------------------
    # Public methods
    # -----------------------------------------------------------------------

    def get_filters(self):
        """Return a tuple ([list of functions], [list of options])."""
        w = self.FindWindow("listctrl")
        return w.get_selected_relations()

    # -----------------------------------------------------------------------

    def get_tiername(self):
        """Return the expected name of the filtered tier."""
        w = self.FindWindow("tiername_textctrl")
        return w.GetValue()

    # -----------------------------------------------------------------------

    def get_relation_tiername(self):
        """Return the tier Y."""
        w = self.FindWindow("y_tier_textctrl")
        return w.GetValue()

    # -----------------------------------------------------------------------

    def get_annot_format(self):
        """Return True if the label has to be replaced by the filter name."""
        w = self.FindWindow("annotformat_checkbutton")
        return w.GetValue()

    # -----------------------------------------------------------------------

    def get_fit(self):
        """Return True if the result tier must fit the Y tier."""
        w = self.FindWindow("fit_checkbutton")
        return w.GetValue()

    # -----------------------------------------------------------------------
    # Construct the GUI
    # -----------------------------------------------------------------------

    def _create_content(self):
        """Create the content of the message dialog."""
        b = sppasPanel.fix_size(6)
        panel = sppasPanel(self, name="content")

        # The list of relations and their options
        lst = AllensRelationsTable(panel, name="listctrl")

        # The name of the filtered tier
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        st = sppasStaticText(panel, label="Name of the filtered tier: ")
        hbox.Add(st, 1, wx.EXPAND | wx.ALL, b)
        nt = sppasTextCtrl(panel, value="Filtered", name="tiername_textctrl")
        hbox.Add(nt, 3, wx.EXPAND | wx.ALL, b)

        # The annot_format option (replace label by the name of the relation)
        an_box = CheckButton(panel, label=MSG_ANNOT_FORMAT)
        an_box.SetMinSize(wx.Size(-1, self.get_font_height()*2))
        an_box.SetFocusWidth(0)
        an_box.SetValue(False)
        an_box.SetName("annotformat_checkbutton")

        fit_box = CheckButton(panel, label=MSG_FIT)
        fit_box.SetMinSize(wx.Size(-1, panel.get_font_height()*2))
        fit_box.SetFocusWidth(0)
        fit_box.SetValue(False)
        fit_box.SetName("fit_checkbutton")

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(lst, 1, wx.EXPAND | wx.ALL, b)
        sizer.Add(hbox, 0, wx.EXPAND)
        sizer.Add(an_box, 0, wx.EXPAND | wx.ALL, b)
        sizer.Add(fit_box, 0, wx.EXPAND | wx.ALL, b)

        panel.SetSizer(sizer)
        panel.SetAutoLayout(True)
        self.SetContent(panel)

# ---------------------------------------------------------------------------


class AllensRelationsTable(ulc.UltimateListCtrl):

    def __init__(self, parent, *args, **kwargs):
        agw_style = ulc.ULC_REPORT | ulc.ULC_VRULES | ulc.ULC_HRULES |\
                    ulc.ULC_HAS_VARIABLE_ROW_HEIGHT | ulc.ULC_NO_HEADER
        ulc.UltimateListCtrl.__init__(self, parent, agwStyle=agw_style, *args, **kwargs)
        self._optionCtrlList = []
        self.InitUI()

    # -----------------------------------------------------------------------

    def InitUI(self):
        headers = ('Name',
                   'Option',
                   'X: Interval \nY: Interval',
                   'X: Interval \nY: Point',
                   'X: Point \nY: Interval',
                   'X: Point \nY: Point'
                   )
        # Create columns
        for i, col in enumerate(headers):
            self.InsertColumn(col=i, heading=col)

        p = sppasPanel()
        self.SetColumnWidth(col=0, width=p.fix_size(150))
        self.SetColumnWidth(col=1, width=p.fix_size(180))
        self.SetColumnWidth(col=2, width=p.fix_size(150))
        self.SetColumnWidth(col=3, width=p.fix_size(100))
        self.SetColumnWidth(col=4, width=p.fix_size(100))
        self.SetColumnWidth(col=5, width=p.fix_size(100))

        # Create first row, used as an header.
        index = self.InsertStringItem(0, headers[0])
        for i, col in enumerate(headers[1:], 1):
            self.SetStringItem(index, i, col)

        # Add rows for relations
        for i, row in enumerate(ALLEN_RELATIONS, 1):
            func, name, opt_label, opt_value, opt_name, desc1, desc2, desc3, desc4 = row

            opt_panel = wx.Panel(self)
            opt_sizer = wx.BoxSizer(wx.HORIZONTAL)

            if isinstance(opt_value, float):
                opt_ctrl = FS.FloatSpin(opt_panel,
                                        min_val=0.005,
                                        increment=0.010,
                                        value=opt_value,
                                        digits=3)
            elif isinstance(opt_value, int):
                opt_ctrl = wx.SpinCtrl(opt_panel, min=1, value=str(opt_value))
            else:
                opt_ctrl = wx.StaticText(opt_panel, label="")

            self._optionCtrlList.append(opt_ctrl)
            opt_text = wx.StaticText(opt_panel, label=opt_label)
            opt_sizer.Add(opt_text)
            opt_sizer.Add(opt_ctrl)
            opt_panel.SetSizer(opt_sizer)

            index = self.InsertStringItem(i, name, 1)
            self.SetItemWindow(index, 1, opt_panel, expand=True)
            self.SetStringItem(index, 2, desc1)
            self.SetStringItem(index, 3, desc2)
            self.SetStringItem(index, 4, desc3)
            self.SetStringItem(index, 5, desc4)

        item = self.GetItem(1)
        self._mainWin.CheckItem(item)
        self.SetMinSize(wx.Size(
            p.fix_size(780),
            p.fix_size(520)
        ))

    # -----------------------------------------------------------------------

    def get_selected_relations(self):
        """Return a tuple with a list of functions and a list of options."""
        fcts = list()
        opts = list()

        for i, option in enumerate(self._optionCtrlList, 1):
            if self.IsItemChecked(i, col=0):
                func_name = ALLEN_RELATIONS[i-1][0]
                fcts.append(func_name)

                try:
                    option_value = option.GetValue()
                    option_name = ALLEN_RELATIONS[i-1][4]
                    opts.append((option_name, option_value))
                except:
                    pass

        return fcts, opts

# ---------------------------------------------------------------------------


class TestPanel(sppasPanel):

    def __init__(self, parent, pos=wx.DefaultPosition, size=wx.DefaultSize):
        super(TestPanel, self).__init__(parent, pos=pos, size=size,
                                        name="Relation Filters")

        btn = wx.Button(self, label="Relation filter")
        btn.SetMinSize(wx.Size(150, 40))
        btn.SetPosition(wx.Point(10, 10))
        self.Bind(wx.EVT_BUTTON, self._process_event)

    # -----------------------------------------------------------------------

    def _process_event(self, event):
        """Process any kind of events.

        :param event: (wx.Event)

        """
        dlg = sppasTiersRelationFilterDialog(self)
        response = dlg.ShowModal()
        if response in (wx.ID_OK, wx.ID_APPLY):
            filters = dlg.get_filters()
            wx.LogMessage("List of filters {:s}:\n".format("\n".join([str(f) for f in filters])))
        dlg.Destroy()
