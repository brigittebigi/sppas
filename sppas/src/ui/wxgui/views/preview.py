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

    wxgui.views.preview.py
    ~~~~~~~~~~~~~~~~~~~~~~

"""
import wx
import wx.richtext
from xml.etree import ElementTree as ET

from sppas.src.anndata.aio.aioutils import serialize_labels
from sppas.src.anndata.aio.xra import sppasXRA
from sppas.src.ui.wxgui.dialogs.basedialog import spBaseDialog
from sppas.src.ui.wxgui.sp_icons import TIER_PREVIEW

from sppas.src.ui.wxgui.ui.CustomListCtrl import LineListCtrl

# ----------------------------------------------------------------------------
# Constants
# ----------------------------------------------------------------------------

DARK_GRAY = wx.Colour(35, 35, 35)
LIGHT_GRAY = wx.Colour(235, 235, 235)
LIGHT_BLUE = wx.Colour(230, 230, 250)
LIGHT_RED = wx.Colour(250, 230, 230)

SILENCE_FG_COLOUR = wx.Colour(45, 45, 190)
SILENCE_BG_COLOUR = wx.Colour(230, 230, 250)
LAUGH_FG_COLOUR = wx.Colour(190, 45, 45)
LAUGH_BG_COLOUR = wx.Colour(250, 230, 230)
NOISE_FG_COLOUR = wx.Colour(45, 190, 45)
NOISE_BG_COLOUR = wx.Colour(230, 250, 230)

# ----------------------------------------------------------------------------


class PreviewTierDialog(spBaseDialog):
    """Frame allowing to show details of a tier.
    
    :author:  Brigitte Bigi
    :contact: develop@sppas.org
    :license: GPL

    """

    def __init__(self, parent, preferences, tiers=[]):
        """Dialog constructor.

        :param parent: a wx.Window or wx.Frame or wx.Dialog
        :param preferences: (Preferences or Preferences_IO)
        :param tiers: a list of tiers to display

        """
        spBaseDialog.__init__(self, parent, preferences, title=" - Preview")
        wx.GetApp().SetAppName("log")

        self.tiers = tiers

        titlebox = self.CreateTitle(TIER_PREVIEW, "Preview of tier(s)")
        contentbox = self._create_content()
        buttonbox = self._create_buttons()

        self.LayoutComponents(titlebox,
                              contentbox,
                              buttonbox)

    # ------------------------------------------------------------------------
    # Create the GUI
    # ------------------------------------------------------------------------

    def _create_buttons(self):
        btn_close = self.CreateCloseButton()
        return self.CreateButtonBox([], [btn_close])

    def _create_content(self):
        self.notebook = wx.Notebook(self)

        page1 = TierAsListPanel(self.notebook, self.preferences)
        page2 = TierDetailsPanel(self.notebook, self.preferences)
        page3 = TierGraphicPanel(self.notebook, self.preferences)

        # add the pages to the notebook with the label to show on the tab
        self.notebook.AddPage(page1, "Quick view")
        self.notebook.AddPage(page2, "Details")
        self.notebook.AddPage(page3, "Timeline")

        # TODO: view all tiers
        if len(self.tiers) > 0:
            page1.ShowTier(self.tiers[0])
        self.notebook.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED, self.OnNotebookPageChanged)
        return self.notebook

    # ------------------------------------------------------------------------
    # Callbacks to events
    # ------------------------------------------------------------------------

    def OnNotebookPageChanged(self, event):
        old_selection = event.GetOldSelection()
        new_selection = event.GetSelection()
        if old_selection != new_selection:
            page = self.notebook.GetPage(new_selection)
            # TODO: view all tiers [not done because it's very slow!!!]
            if len(self.tiers) > 0:
                page.ShowTier(self.tiers[0])

# ----------------------------------------------------------------------------


class BaseTierPanel(wx.Panel):
    """Base tier panel.
    
    :author:  Brigitte Bigi
    :contact: develop@sppas.org
    :license: GPL

    """
    def __init__(self, parent, prefsIO):
        wx.Panel.__init__(self, parent)
        self.preferences = prefsIO

        self.sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.SetSizer(self.sizer)
        self.ShowNothing()
        self.sizer.Fit(self)

    # ------------------------------------------------------------------------

    def ShowNothing(self):
        """
        Method to show a message in the panel.

        """
        self.sizer.DeleteWindows()
        st = wx.StaticText(self, -1, "Nothing to view!")
        st.SetMinSize((320, 200))
        self.sizer.Add(st, 1, flag=wx.ALL | wx.EXPAND, border=5)

    # ------------------------------------------------------------------------

    def ShowTier(self, tier):
        """Base method to show a tier in the panel."""
        self.ShowNothing()

# ----------------------------------------------------------------------------


class TierAsListPanel(BaseTierPanel):
    """List-view of a tier.
    
    :author:  Brigitte Bigi
    :contact: develop@sppas.org
    :license: GPL

    """

    def __init__(self, parent, prefsIO):
        BaseTierPanel.__init__(self, parent, prefsIO)

    # ------------------------------------------------------------------------

    def ShowTier(self, tier):
        """Show a tier as list."""
        
        if not tier:
            self.ShowNothing()
            return

        tier_ctrl = LineListCtrl(self, style=wx.LC_REPORT)
        tier_ctrl.SetForegroundColour(self.preferences.GetValue('M_FG_COLOUR'))
        tier_ctrl.SetBackgroundColour(self.preferences.GetValue('M_BG_COLOUR'))

        # create columns
        is_point_tier = tier.is_point()
        if not is_point_tier:
            cols = ("Begin", "End", "Label")
        else:
            cols = ("Time", "Label")
        for i, col in enumerate(cols):
            tier_ctrl.InsertColumn(i, col)
            tier_ctrl.SetColumnWidth(i, 100)
        tier_ctrl.SetColumnWidth(len(cols)-1, 400)

        # fill rows
        for i, a in enumerate(tier):

            # fix location
            if not is_point_tier:
                tier_ctrl.InsertStringItem(i, str(a.get_lowest_localization().get_midpoint()))
                tier_ctrl.SetStringItem(i, 1, str(a.get_highest_localization().get_midpoint()))
                labeli = 2
            else:
                tier_ctrl.InsertStringItem(i, str(a.get_highest_localization().get_midpoint()))
                labeli = 1

            # fix label
            label_str = serialize_labels(a.get_labels(), separator=" - ")
            tier_ctrl.SetStringItem(i, labeli, label_str)

            # customize label look
            if label_str in ['#', 'sil']:
                tier_ctrl.SetItemTextColour(i, SILENCE_FG_COLOUR)
                tier_ctrl.SetItemBackgroundColour(i, SILENCE_BG_COLOUR)
            if label_str == '+':
                tier_ctrl.SetItemTextColour(i, SILENCE_FG_COLOUR)
            if label_str in ['@', '@@', 'lg', 'laugh']:
                tier_ctrl.SetItemTextColour(i, LAUGH_FG_COLOUR)
                tier_ctrl.SetItemBackgroundColour(i, LAUGH_BG_COLOUR)
            if label_str in ['*', 'gb', 'noise', 'dummy']:
                tier_ctrl.SetItemTextColour(i, NOISE_FG_COLOUR)
                tier_ctrl.SetItemBackgroundColour(i, NOISE_BG_COLOUR)

        self.sizer.DeleteWindows()
        self.sizer.Add(tier_ctrl, 1, flag=wx.ALL | wx.EXPAND, border=5)
        self.sizer.Fit(self)

# ----------------------------------------------------------------------------


class TierDetailsPanel(BaseTierPanel):
    """Detailed-view of a tiers.
    
    :author:  Brigitte Bigi
    :contact: develop@sppas.org
    :license: GPL

    """

    def __init__(self, parent, prefsIO):
        BaseTierPanel.__init__(self, parent, prefsIO)

    # ------------------------------------------------------------------------

    def ShowTier(self, tier):
        """
        Show a tier in a rich text control object, with detailed information.

        """
        self.text_ctrl = wx.richtext.RichTextCtrl(self,
                                                  style=wx.VSCROLL | wx.HSCROLL | wx.NO_BORDER)
        self.text_ctrl.SetForegroundColour(self.preferences.GetValue('M_FG_COLOUR'))
        self.text_ctrl.SetBackgroundColour(self.preferences.GetValue('M_BG_COLOUR'))
        self.text_ctrl.SetMinSize((600, 380))
        self.text_ctrl.SetEditable(False)
        self._set_styles()
        self._create_text_content(tier)

        self.sizer.DeleteWindows()
        self.sizer.Add(self.text_ctrl, 1, flag=wx.ALL | wx.EXPAND, border=5)
        self.sizer.Fit(self)

    # ------------------------------------------------------------------------

    def _set_styles(self):
        """Fix a set of styles to be used in the RichTextCtrl."""
        fs = self.preferences.GetValue('M_FONT').GetPointSize()

        # SetFont(pointSize, family, style, weight, underline, face, encoding)
        self.labelStyle = wx.richtext.RichTextAttr()
        self.labelStyle.SetBackgroundColour(LIGHT_RED)
        self.labelStyle.SetTextColour(wx.BLACK)
        self.labelStyle.SetFont(wx.Font(fs, wx.SWISS, wx.NORMAL, wx.NORMAL, False, u'Courier New'))

        self.nlineStyle = wx.richtext.RichTextAttr()
        self.nlineStyle.SetBackgroundColour(LIGHT_GRAY)
        self.nlineStyle.SetTextColour(DARK_GRAY)
        self.nlineStyle.SetFont(wx.Font(fs+1, wx.ROMAN, wx.NORMAL, wx.BOLD, False, u'Courier New'))

        self.timeStyle = wx.richtext.RichTextAttr()
        self.timeStyle.SetBackgroundColour(LIGHT_BLUE)
        self.timeStyle.SetTextColour(wx.BLACK)
        self.timeStyle.SetFont(wx.Font(fs, wx.SWISS, wx.NORMAL, wx.NORMAL, False, u'Courier New'))

    def _create_text_content(self, tier):
        """Add the content of the tier in the RichTextCtrl."""

        if not tier:
            self.text_ctrl.WriteText("Nothing to view!")
            return

        # creating a richtextctrl can work for a while...
        dialog = wx.ProgressDialog("Detailed view progress", 
                                   "Please wait while creating the detailed view...", 
                                   len(tier),
                                   style=wx.PD_ELAPSED_TIME | wx.PD_REMAINING_TIME)

        try:
            # Make the XML tree
            tier_root = ET.Element('Tier')
            sppasXRA.format_tier(tier_root, tier)
            # Convert to string and add in the text ctrl
            str_tier = ET.tostring(tier_root).decode()
        except Exception as e:
            str_tier = str(e)

        self._append_text(str_tier, self.timeStyle)

        # progress finished!
        dialog.Destroy()

    def _append_text(self, text, style):
        """Append a text with the appropriate style."""
        self.text_ctrl.BeginStyle(style)
        self.text_ctrl.WriteText(text)
        self.text_ctrl.EndStyle()

# ----------------------------------------------------------------------------


class TierGraphicPanel(BaseTierPanel):
    """Graphical-view of tiers (TODO).
    
    :author:  Brigitte Bigi
    :contact: develop@sppas.org
    :license: GPL

    """

    def __init__(self, parent, prefsIO):
        BaseTierPanel.__init__(self, parent, prefsIO)

# ----------------------------------------------------------------------------


def ShowPreviewDialog(parent, preferences, tiers):
    dialog = PreviewTierDialog(parent, preferences,tiers)
    dialog.ShowModal()
    dialog.Destroy()

# ---------------------------------------------------------------------------


if __name__ == "__main__":
    app = wx.PySimpleApp()
    ShowPreviewDialog(None, None, [])
    app.MainLoop()
