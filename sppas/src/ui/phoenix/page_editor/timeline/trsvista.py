import wx
import wx.lib.newevent

from sppas.src.anndata import sppasTranscription

from sppas.src.ui.phoenix.windows.panels import sppasPanel
from sppas.src.ui.phoenix.windows.panels import sppasScrolledPanel

from ..datactrls import sppasTierWindow

# ---------------------------------------------------------------------------


TrsEvent, EVT_TRS = wx.lib.newevent.NewEvent()
TrsCommandEvent, EVT_TRS_COMMAND = wx.lib.newevent.NewCommandEvent()

# ---------------------------------------------------------------------------


class TranscriptionVista(sppasPanel):
    """Display a transcription in a timeline view.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      contact@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2020 Brigitte Bigi

    Event emitted by this class is TRS_EVENT with:

        - action="select_tier", value=name of the tier to be selected

    """

    def __init__(self, parent, name="trsvista_panel"):
        super(TranscriptionVista, self).__init__(parent, name=name)
        self.__trs = None
        self._create_content()

    # -----------------------------------------------------------------------

    def set_transcription(self, transcription):
        """Fix the transcription object if it wasn't done when init.

        """
        if self.__trs is not None:
            raise Exception("A sppasTranscription is already defined.")

        if isinstance(transcription, sppasTranscription):
            self.__trs = transcription
            for tier in self.__trs:
                self._add_tier_to_panel(tier)
            self.SetMinSize(wx.Size(-1, len(self.__trs)*sppasPanel.fix_size(24)))

    # -----------------------------------------------------------------------

    def write_transcription(self, parser):
        """Write the transcription object with the given parser.

        :param parser: (sppasRW)

        """
        parser.write(self.__trs)

    # -----------------------------------------------------------------------

    def get_draw_period(self):
        for child in self.GetChildren():
            s, e = child.GetDrawPeriod()
            return int(s * 1000.), int(e * 1000.)
        return 0, 0

    # -----------------------------------------------------------------------

    def set_draw_period(self, start, end):
        """Period to display (in milliseconds)."""
        for child in self.GetChildren():
            child.SetDrawPeriod(
                float(start) / 1000.,
                float(end) / 1000.)

    # -----------------------------------------------------------------------

    def set_select_period(self, start, end):
        raise NotImplementedError

    # -----------------------------------------------------------------------

    def get_select_period(self):
        for child in self.GetChildren():
            if child.IsSelected() is True:
                period = child.get_selected_localization()
                start = int(period[0] * 1000.)
                end = int(period[1] * 1000.)
                return start, end

        return 0, 0

    # -----------------------------------------------------------------------

    def get_selected_tiername(self):
        for child in self.GetChildren():
            if child.IsSelected() is True:
                return child.get_tiername()
        return None

    # -----------------------------------------------------------------------

    def set_selected_tiername(self, tier_name=None):
        """Set the selected tier.

        :param tier_name: (str)

        """
        if self.__trs is None:
            return

        if tier_name is not None:
            assert tier_name in [t.get_name() for t in self.__trs]

        for child in self.GetChildren():
            if child.IsSelected() is True:
                child.SetBorderColour(self.GetForegroundColour())
                child.SetSelected(False)
                child.Refresh()
            if child.get_tiername() == tier_name:
                child.SetBorderColour(wx.RED)
                child.SetSelected(True)
                child.Refresh()

    # -----------------------------------------------------------------------

    def get_tier_list(self):
        """Return the list of tiers."""
        if self.__trs is not None:
            return self.__trs.get_tier_list()
        return list()

    # -----------------------------------------------------------------------

    def get_selected_ann(self):
        for child in self.GetChildren():
            if child.IsSelected() is True:
                return child.get_selected_ann()

        return -1

    # -----------------------------------------------------------------------

    def set_selected_ann(self, idx):
        """An annotation was selected."""
        for child in self.GetChildren():
            if child.IsSelected() is True:
                child.set_selected_ann(idx)

    # -----------------------------------------------------------------------

    def update_ann(self, idx):
        """An annotation was modified."""
        for child in self.GetChildren():
            if child.IsSelected() is True:
                child.update_ann(idx)

    # -----------------------------------------------------------------------

    def delete_ann(self, idx):
        """An annotation was deleted."""
        for child in self.GetChildren():
            if child.IsSelected() is True:
                child.delete_ann(idx)

    # -----------------------------------------------------------------------

    def create_ann(self, idx):
        """An annotation was created."""
        for child in self.GetChildren():
            if child.IsSelected() is True:
                child.create_ann(idx)

    # -----------------------------------------------------------------------

    def _add_tier_to_panel(self, tier):
        tier_ctrl = sppasTierWindow(self, data=tier)
        tier_ctrl.SetMinSize(wx.Size(-1, sppasPanel.fix_size(24)))
        tier_ctrl.Bind(wx.EVT_COMMAND_LEFT_CLICK, self._process_tier_click)

        self.GetSizer().Add(tier_ctrl, 0, wx.EXPAND, 0)

    # -----------------------------------------------------------------------
    # Construct the GUI
    # -----------------------------------------------------------------------

    def _create_content(self):
        sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(sizer)

    # -----------------------------------------------------------------------

    def notify(self, action, value=None):
        """Send a EVT_TIMELINE_VIEW event to the listener (if any)."""
        evt = TrsEvent(action=action, value=value)
        evt.SetEventObject(self)
        wx.PostEvent(self.GetParent(), evt)

    # -----------------------------------------------------------------------

    def _process_tier_click(self, event):
        """Process a click on a tier.

        :param event: (wx.Event)

        """
        tier = event.GetObj()
        self.notify(action="select_tier", value=tier.get_name())

# ---------------------------------------------------------------------------


class TestPanel(sppasScrolledPanel):
    def __init__(self, parent):
        super(TestPanel, self).__init__(parent, name="TrsVista Panel")

        return
