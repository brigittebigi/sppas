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

    Only one tier must be selected at a time and only one annotation can be
    selected in the selected tier.

    Event emitted by this class is TRS_EVENT with:

        - action="select_tier", value=name of the tier to be selected

    """

    def __init__(self, parent, name="trsvista_panel"):
        super(TranscriptionVista, self).__init__(parent, name=name)
        self.__trs = None
        self._create_content()

    # -----------------------------------------------------------------------

    def SetFont(self, font):
        """Override to keep the tier height proportional."""
        wx.Panel.SetFont(self, font)
        for tier_ctrl in self.GetChildren():
            tier_ctrl.SetFont(font)
            tier_ctrl.SetMinSize(wx.Size(-1, self.get_font_height() * 2))
        self.Layout()

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

            self.SetMinSize(wx.Size(-1, len(self.__trs) * self.get_font_height() * 2))

    # -----------------------------------------------------------------------

    def write_transcription(self, parser):
        """Write the transcription object with the given parser.

        :param parser: (sppasRW)

        """
        parser.write(self.__trs)

    # -----------------------------------------------------------------------

    def get_duration(self):
        """Return the duration of the transcription."""
        if self.__trs is not None:
            max_point = self.__trs.get_max_loc()
            if max_point is not None:
                midpoint = max_point.get_midpoint()
                radius = max_point.get_radius()
                if radius is None:
                    return midpoint
                else:
                    return midpoint + radius

        return 0.

    # -----------------------------------------------------------------------

    def set_visible_period(self, start, end):
        """Period to display (in seconds)."""
        for child in self.GetChildren():
            child.set_visible_period(start, end)

    # -----------------------------------------------------------------------

    def set_selection_period(self, start, end):
        raise NotImplementedError

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
                child.SetBorderColour(self.GetBackgroundColour())
                child.SetSelected(False)
            if child.get_tiername() == tier_name:
                child.SetBorderColour(wx.RED)  # border is visible only if selected
                child.SetSelected(True)

    # -----------------------------------------------------------------------

    def get_tier_list(self):
        """Return the list of tiers."""
        if self.__trs is not None:
            return self.__trs.get_tier_list()
        return list()

    # -----------------------------------------------------------------------

    def get_selected_localization(self):
        """Return begin and end time value (float) rounded to milliseconds."""
        for child in self.GetChildren():
            if child.IsSelected() is True:
                return child.get_selected_localization()

        return 0., 0.

    # -----------------------------------------------------------------------

    def get_selected_ann(self):
        """Return the index of the currently selected annotation or -1."""
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
        """An annotation was created. Create the corresponding control."""
        for child in self.GetChildren():
            if child.IsSelected() is True:
                child.Refresh()

    # -----------------------------------------------------------------------
    # Construct the GUI
    # -----------------------------------------------------------------------

    def show_tier_infos(self, value, tiername=None):
        """Show information about a tier instead or the annotations.

        :param value: (bool) True to show the information, False for the annotations.
        :param tiername: (str) Name of a tier or None for all tiers

        """
        if self.__trs is None:
            return
        for child in self.GetChildren():
            if tiername is None or tiername == child.get_tiername():
                child.show_infos(value)
                child.Refresh()

    # -----------------------------------------------------------------------

    def _create_content(self):
        sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(sizer)

    # -----------------------------------------------------------------------

    def notify(self, action, value=None):
        """Send a EVT_TRS event to the listener (if any)."""
        evt = TrsEvent(action=action, value=value)
        evt.SetEventObject(self)
        wx.PostEvent(self.GetParent(), evt)

    # -----------------------------------------------------------------------

    def _add_tier_to_panel(self, tier):
        tier_ctrl = sppasTierWindow(self, data=tier)
        tier_ctrl.SetBackgroundColour(self.GetBackgroundColour())
        tier_ctrl.SetHorizBorderWidth(1)
        tier_ctrl.SetBorderColour(self.GetBackgroundColour())  # border is visible only if selected
        tier_ctrl.SetMinSize(wx.Size(-1, self.get_font_height() * 2))
        tier_ctrl.Bind(wx.EVT_COMMAND_LEFT_CLICK, self._process_tier_selected)

        self.GetSizer().Add(tier_ctrl, 0, wx.EXPAND, 0)

    # -----------------------------------------------------------------------

    def _process_tier_selected(self, event):
        """Process a click on a tier or an annotation of a tier.

        :param event: (wx.Event)

        """
        # Which tier was clicked?
        tierctrl_click = event.GetEventObject()
        tier_click = event.GetObj()

        # Update selection: disable a previously selected tier
        for child in self.GetChildren():
            if child is not tierctrl_click and child.IsSelected():
                child.SetSelected(False)
                child.Refresh()

        self.notify(action="tier_selected", value=tier_click.get_name())

# ---------------------------------------------------------------------------


class TestPanel(sppasScrolledPanel):
    def __init__(self, parent):
        super(TestPanel, self).__init__(parent, name="TrsVista Panel")

        return
