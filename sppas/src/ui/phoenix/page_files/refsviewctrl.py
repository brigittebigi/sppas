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

    src.ui.phoenix.page_files.refstreectrl.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""

import wx
import wx.lib.newevent

from sppas.src.wkps import States, sppasWorkspace
from sppas.src.wkps import sppasAttribute, FileReference
from ..windows import sppasPanel
from ..windows import sppasScrolledPanel
from ..windows import sppasCollapsiblePanel
from ..windows import sppasSimpleText
from ..windows import sppasListCtrl
from ..main_events import DataChangedEvent

# ---------------------------------------------------------------------------
# Internal use of an event, when an item is clicked.

ItemClickedEvent, EVT_ITEM_CLICKED = wx.lib.newevent.NewEvent()
ItemClickedCommandEvent, EVT_ITEM_CLICKED_COMMAND = wx.lib.newevent.NewCommandEvent()

# ---------------------------------------------------------------------------


STATES_ICON_NAMES = {
    States().UNUSED: "choice_checkbox",
    States().CHECKED: "choice_checked",
    States().LOCKED: "locked",
    States().AT_LEAST_ONE_CHECKED: "choice_pos",
    States().AT_LEAST_ONE_LOCKED: "choice_neg"
}

# ---------------------------------------------------------------------------


class RefsTreeView(sppasScrolledPanel):
    """A control to display data references in a tree-spreadsheet style.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      contact@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2019  Brigitte Bigi

    This class manages a sppasWorkspace() instance to add/delete/edit references and
    the wx objects to display it.

    """

    def __init__(self, parent, name=wx.PanelNameStr):
        """Constructor of the RefsTreeCtrl.

        :param parent: (wx.Window)
        :param name: (str)

        """
        super(RefsTreeView, self).__init__(parent, name=name)

        # The workspace to display
        self.__data = sppasWorkspace()

        # Each FilePath has its own CollapsiblePanel in the sizer
        self.__refps = dict()  # key=ref.id, value=FileRefCollapsiblePanel
        self._create_content()
        self._setup_events()

        # Look&feel
        self.SetBackgroundColour(wx.GetApp().settings.bg_color)
        self.SetForegroundColour(wx.GetApp().settings.fg_color)
        self.SetFont(wx.GetApp().settings.text_font)

    # ------------------------------------------------------------------------
    # Public methods
    # ------------------------------------------------------------------------

    def get_data(self):
        """Return the data."""
        return self.__data

    # ------------------------------------------------------------------------

    def set_data(self, data):
        """Set the data and update the corresponding wx objects."""
        self.__data = data
        self.__update()

    # ------------------------------------------------------------------------

    def GetCheckedRefs(self):
        """Return checked references."""
        return self.__data.get_reference_from_state(States().CHECKED)

    # ------------------------------------------------------------------------

    def HasCheckedRefs(self):
        """Return True if at least one reference is checked."""
        return len(self.__data.get_reference_from_state(States().CHECKED)) > 0

    # ------------------------------------------------------------------------

    def CreateRef(self, ref_name, ref_type):
        """Create a new reference and add it into the tree.

        :param ref_name: (str)
        :param ref_type: (str) On of the accepted type of references
        :raise: Exception

        """
        r = FileReference(ref_name)
        r.set_type(ref_type)
        self.__data.add_ref(r)  # can raise a ValueError
        self.__add_ref_panel(r)
        self.GetParent().SendSizeEvent()

    # ------------------------------------------------------------------------

    def AddRefs(self, entries):
        """Add a list of references into the model.

        :param entries: (str) List of references.

        """
        added_refs = list()
        for entry in entries:
            try:
                self.__data.add_ref(entry)
                self.__add_ref_panel(entry)
                added_refs.append(entry)
            except ValueError as e:
                wx.LogError(' ... reference {:s} not added: {:s}.'
                            ''.format(entry, str(e)))

        if len(added_refs) > 0:
            self.Layout()

        return len(added_refs)

    # ------------------------------------------------------------------------

    def RemoveCheckedRefs(self):
        """Remove all checked references."""
        nb_removed = self.__data.remove_refs(States().CHECKED)
        if nb_removed > 0:
            self.__data.update()
            self.__update()

        return nb_removed

    # ------------------------------------------------------------------------

    def RemoveAttribute(self, identifier):
        """Remove an attribute from the checked references.

        :param identifier: (str)
        :returns: Number of references in which the attribute were removed.

        """
        nb = 0
        for ref in self.__data.get_refs():
            if ref.state == States().CHECKED and identifier in ref:
                ref.pop(identifier)
                panel = self.__refps[ref.get_id()]
                panel.remove(identifier)
                nb += 1

        if nb > 0:
            self.Layout()

        return nb

    # ------------------------------------------------------------------------

    def EditAttribute(self, identifier, value, att_type, description):
        """Add or modify an attribute into the checked references.

        :param identifier: (str)
        :param value: (str)
        :param att_type: (str)
        :param description: (str)
        :returns: Number of references in which the attribute were added.

        """
        nb = 0
        if len(value.strip()) == 0:
            value = None
        if len(description.strip()) == 0:
            description = None
        for ref in self.__data.get_reference_from_state(States().CHECKED):
            att = ref.att(identifier)
            if att is None:
                # Create the attribute and add it
                att = sppasAttribute(identifier, value, att_type, description)
                ref.append(att)
                panel = self.__refps[ref.get_id()]
                panel.add(att)
            else:
                # Update the attribute
                att.set_value(value)
                att.set_value_type(att_type)
                att.set_description(description)
                panel = self.__refps[ref.get_id()]
                panel.update(att)

            nb += 1
            if ref.subjoined is None:
                ref.subjoined = dict()
            ref.subjoined['expand'] = True

        if nb > 0:
            self.Layout()

        return nb

    # ------------------------------------------------------------------------
    # Manage the data and their panels
    # ------------------------------------------------------------------------

    def __add_ref_panel(self, ref):
        """Create a child panel to display the content of a FileReference.

        :param ref: (FileReference)
        :return: FileRefCollapsiblePanel

        """
        p = FileRefCollapsiblePanel(self, ref)
        p.SetFocus()
        self.ScrollChildIntoView(p)
        self.Bind(wx.EVT_COLLAPSIBLEPANE_CHANGED, self.OnCollapseChanged, p)

        self.GetSizer().Add(p, 0, wx.EXPAND | wx.ALL, border=sppasPanel.fix_size(4))
        self.__refps[ref.get_id()] = p
        return p

    # ------------------------------------------------------------------------

    def __remove_ref_panel(self, identifier):
        """Remove a child panel that displays the content of a FileReference.

        :param identifier: (str)
        :return: FileRefCollapsiblePanel

        """
        if identifier in self.__refps:
            path_panel = self.__refps[identifier]
            path_panel.Destroy()
            del self.__refps[identifier]

    # ------------------------------------------------------------------------

    def __update(self):
        """Update the currently displayed wx objects to match the data."""
        # Remove paths of the panel if not in the data
        r = list()
        for refid in self.__refps:
            if refid not in self.__data.get_refs():
                r.append(refid)
        for refid in r:
            self.__remove_ref_panel(refid)

        # Add or update
        for ref in self.__data.get_refs():
            if ref.get_id() not in self.__refps:
                p = self.__add_ref_panel(ref)
                p.update(ref)
            else:
                self.__refps[ref.get_id()].update(ref)

        self.GetParent().SendSizeEvent()

    # ------------------------------------------------------------------------

    def _create_content(self):
        sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(sizer)
        self.Layout()
        self.SetupScrolling(scroll_x=True, scroll_y=True)
        self.SetAutoLayout(True)

    # -----------------------------------------------------------------------
    # Events management
    # -----------------------------------------------------------------------

    def Notify(self):
        evt = DataChangedEvent()
        evt.SetEventObject(self)
        wx.PostEvent(self.GetParent(), evt)

    # ------------------------------------------------------------------------

    def _setup_events(self):
        """Associate a handler function with the events.

        It means that when an event occurs then the process handler function
        will be called.

        """
        self.Bind(wx.EVT_SIZE, self.OnSize)

        # The user pressed a key of its keyboard
        # self.Bind(wx.EVT_KEY_DOWN, self._process_key_event)

        # The user clicked an item
        self.Bind(EVT_ITEM_CLICKED, self._process_item_clicked)

    # ------------------------------------------------------------------------

    def _process_item_clicked(self, event):
        """Process an action event: an item was clicked.

        The sender of the event is a Ref Collapsible Panel.

        :param event: (wx.Event)

        """
        # the object is a FileBase (path, root or file)
        object_id = event.id
        ref = self.__data.get_object(object_id)

        # change state of the item
        current_state = ref.get_state()
        new_state = States().UNUSED
        if current_state == States().UNUSED:
            new_state = States().CHECKED
        modified = self.__data.set_object_state(new_state, ref)

        # update the corresponding panel(s)
        if len(modified) > 0:
            for fs in modified:
                wx.LogDebug("New state {} for reference {:s}"
                            "".format(new_state, fs.get_id()))
                panel = self.__refps[ref.get_id()]
                if panel is not None:
                    panel.change_state(fs.get_state())
            self.Notify()

    # ------------------------------------------------------------------------

    def OnCollapseChanged(self, evt=None):
        """One of the roots was collapsed/expanded."""
        panel = evt.GetEventObject()
        self.Layout()
        for ref_id in self.__refps:
            if self.__refps[ref_id] == panel:
                ref = self.__data.get_object(ref_id)
                if ref.subjoined is None:
                    ref.subjoined = dict()
                ref.subjoined['expand'] = panel.IsExpanded()
                break
        self.GetParent().SendSizeEvent()
        self.ScrollChildIntoView(panel)

    # ------------------------------------------------------------------------

    def OnSize(self, event):
        """Handle the wx.EVT_SIZE event.

        :param event: a SizeEvent event to be processed.

        """
        # each time our size is changed, the child panel needs a resize.
        self.Layout()

# ---------------------------------------------------------------------------


class FileRefCollapsiblePanel(sppasCollapsiblePanel):
    """A panel to display the ref as a list of att.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      contact@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2019  Brigitte Bigi

    """

    COLUMNS = ['idt', 'type', 'value', 'descr']

    def __init__(self, parent, ref, name="ref-panel"):
        super(FileRefCollapsiblePanel, self).__init__(
            parent, label=ref.get_id(), name=name)

        self._create_content(ref)
        self._setup_events()

        # Attributes are displayed in a listctrl. For convenience, their ids are
        # stored into a list.
        self.__refid = ref.get_id()
        self.__atts = list()

        # Look&feel
        self.SetBackgroundColour(self.GetParent().GetBackgroundColour())
        self.SetForegroundColour(wx.GetApp().settings.fg_color)
        self.SetFont(wx.GetApp().settings.text_font)

        # Fill in the controls with the data
        self.update(ref)

    # -----------------------------------------------------------------------
    # Public methods
    # -----------------------------------------------------------------------

    def SetForegroundColour(self, color):
        """Override."""
        reftypectrl = self.FindWindow("textctrl_type")
        wx.Window.SetForegroundColour(self, color)
        for c in self.GetChildren():
            if c != reftypectrl:
                c.SetForegroundColour(color)
        reftypectrl.SetForegroundColour(wx.Colour(128, 128, 250, 196))

    # -----------------------------------------------------------------------

    def SetFont(self, font):
        """Override."""
        f = wx.Font(font.GetPointSize(),
                    font.GetFamily(),
                    wx.FONTSTYLE_ITALIC,
                    wx.FONTWEIGHT_NORMAL,
                    font.GetUnderlined(),
                    font.GetFaceName())
        sppasCollapsiblePanel.SetFont(self, f)
        self.GetPane().SetFont(font)

        # The change of font implies to re-draw all proportional objects
        self.__set_pane_size()
        self.Layout()

    # ----------------------------------------------------------------------

    def add(self, att):
        """Add an attribute in the listctrl child panel.

        :param att: (sppasAttribute)

        """
        if att.get_id() in self.__atts:
            return False

        self.__add_att(att)
        return True

    # ----------------------------------------------------------------------

    def remove(self, identifier):
        """Remove an attribute of the listctrl child panel.

        :param identifier: (str)
        :return: (bool)

        """
        if identifier not in self.__atts:
            return False

        self.__remove_att(identifier)
        return True

    # ------------------------------------------------------------------------

    def change_state(self, state):
        """Update the state of the ref.

        :param state: (State/int)

        """
        icon_name = STATES_ICON_NAMES[state]
        self.FindButton("choice_checkbox").SetImage(icon_name)
        self.FindButton("choice_checkbox").Refresh()

    # ------------------------------------------------------------------------

    def update(self, fs):
        """Update each att of a given ref or update the given att.

        :param fs: (FileReference or sppasAttribute)

        """
        if isinstance(fs, FileReference):
            if fs.get_id() != self.__refid:
                return

            # Remove files of the panel if not in the data
            for attid in self.__atts:
                if attid not in fs:
                    self.__remove_att(attid)

            # Update existing attributes and add if missing
            for att in fs:
                if att.get_id() not in self.__atts:
                    self.add(att)
                else:
                    self.__update_att(att)

            reftypetext = self.FindWindow("textctrl_type")
            reftypetext.SetValue(fs.get_type())
            self.change_state(fs.get_state())

        elif isinstance(fs, sppasAttribute):
            self.__update_att(fs)

        self.Layout()

    # -----------------------------------------------------------------------

    def SetBackgroundColour(self, color):
        """Calculate a lightness or darkness background color."""
        r, g, b = color.Red(), color.Green(), color.Blue()
        delta = 10
        if (r + g + b) > 384:
            color = wx.Colour(r, g, b, 50).ChangeLightness(100 - delta)
        else:
            color = wx.Colour(r, g, b, 50).ChangeLightness(100 + delta)

        wx.Window.SetBackgroundColour(self, color)
        for c in self.GetChildren():
            c.SetBackgroundColour(color)

    # ------------------------------------------------------------------------
    # Construct the GUI
    # ------------------------------------------------------------------------

    def _create_content(self, fr):
        child_panel = sppasPanel(self)
        child_sizer = wx.BoxSizer(wx.VERTICAL)
        type_text = self.__create_reftypetext(child_panel)
        list_ctrl = self.__create_listctrl(child_panel)
        child_sizer.Add(type_text, 0, wx.EXPAND | wx.TOP | wx.BOTTOM, 2)
        child_sizer.Add(list_ctrl, 1, wx.EXPAND | wx.TOP | wx.BOTTOM, 2)
        child_panel.SetSizer(child_sizer)
        self.SetPane(child_panel)

        collapse = False
        if fr.subjoined is not None:
            if "expand" in fr.subjoined:
                collapse = not fr.subjoined["expand"]

        self.Collapse(collapse)
        self.AddButton("choice_checkbox")

    @property
    def _attlist(self):
        return self.FindWindow("atts_listctrl")

    # ------------------------------------------------------------------------

    def __create_reftypetext(self, parent):
        """Create a text control to display the type of this reference."""
        type_text = sppasSimpleText(parent, "", name="textctrl_type")
        type_text.SetSize(wx.Size(-1, self.GetButtonHeight()))
        return type_text

    # ------------------------------------------------------------------------

    def __create_listctrl(self, parent):
        """Create a listctrl to display attributes."""
        style = wx.BORDER_NONE | wx.LC_REPORT | wx.LC_NO_HEADER | wx.LC_SINGLE_SEL | wx.LC_HRULES
        lst = sppasListCtrl(parent, style=style, name="atts_listctrl")

        lst.AppendColumn("identifier",
                         format=wx.LIST_FORMAT_LEFT,
                         width=sppasScrolledPanel.fix_size(80))
        lst.AppendColumn("type",
                         format=wx.LIST_FORMAT_LEFT,
                         width=sppasScrolledPanel.fix_size(30))
        lst.AppendColumn("value",
                         format=wx.LIST_FORMAT_LEFT,
                         width=sppasScrolledPanel.fix_size(80))
        lst.AppendColumn("description",
                         format=wx.LIST_FORMAT_LEFT,
                         width=sppasScrolledPanel.fix_size(100))

        return lst

    # ------------------------------------------------------------------------

    def __set_pane_size(self):
        """Fix the size of the child panel."""
        # The listctrl can have an horizontal scrollbar
        bar = 14

        n = self._attlist.GetItemCount()
        h = int(self.GetFont().GetPixelSize()[1] * 2.)
        self._attlist.SetMinSize(wx.Size(-1, (n * h) + bar))
        self._attlist.SetMaxSize(wx.Size(-1, ((n * h) + bar) * 2))

    # ------------------------------------------------------------------------
    # Management the list of files
    # ------------------------------------------------------------------------

    def __add_att(self, att):
        """Append an attribute into the listctrl."""
        index = self._attlist.InsertItem(self._attlist.GetItemCount(), 0)
        self.__atts.append(att.get_id())

        self.__update_att(att)
        self.__set_pane_size()
        self.Layout()

    # ------------------------------------------------------------------------

    def __remove_att(self, identifier):
        """Remove an attribute of the listctrl."""
        idx = self.__atts.index(identifier)
        self._attlist.DeleteItem(idx)

        self.__atts.pop(idx)
        self.__set_pane_size()
        self.Layout()

    # ------------------------------------------------------------------------

    def __update_att(self, att):
        """Update information of an attribute."""
        if att.get_id() in self.__atts:
            index = self.__atts.index(att.get_id())
            self._attlist.SetItem(index, FileRefCollapsiblePanel.COLUMNS.index("idt"), att.get_id())
            self._attlist.SetItem(index, FileRefCollapsiblePanel.COLUMNS.index("type"), att.get_value_type())
            self._attlist.SetItem(index, FileRefCollapsiblePanel.COLUMNS.index("value"), att.get_value())
            self._attlist.SetItem(index, FileRefCollapsiblePanel.COLUMNS.index("descr"), att.get_description())

    # ------------------------------------------------------------------------
    # Management of the events
    # ------------------------------------------------------------------------

    def _setup_events(self):
        """Associate a handler function with the events.

        It means that when an event occurs then the process handler function
        will be called.

        """
        self.FindButton("choice_checkbox").Bind(wx.EVT_BUTTON, self.OnCkeckedRef)
        self._attlist.Bind(wx.EVT_LIST_ITEM_SELECTED, self._on_att_selected)

    # ------------------------------------------------------------------------

    def notify(self, identifier):
        """The parent has to be informed of a change of content."""
        evt = ItemClickedEvent(id=identifier)
        evt.SetEventObject(self)
        wx.PostEvent(self.GetParent(), evt)

    # ------------------------------------------------------------------------

    def OnCkeckedRef(self, evt):
        self.notify(self.__refid)

    # ------------------------------------------------------------------------

    def _on_att_selected(self, evt):
        """Disable selection."""
        item = evt.GetItem()
        item_index = item.GetId()
        self._attlist.Select(item_index, on=False)

# ----------------------------------------------------------------------------
# Panel tested by test_glob.py
# ----------------------------------------------------------------------------


class TestPanel(RefsTreeView):

    def __init__(self, parent):
        super(TestPanel, self).__init__(parent)
        data = sppasWorkspace()
        micros = FileReference('microphone')
        att1 = sppasAttribute('mic1', 'Bird UM1', None, '最初のインタビューで使えていましたマイク')
        micros.append(att1)
        micros.add('mic2', 'AKG D5')
        data.add_ref(micros)
        self.set_data(data)

        self.CreateRef("TestCreateRef", "STANDALONE")

        r1 = FileReference('SpeakerAB')
        r1.set_type('SPEAKER')
        r1.append(sppasAttribute('initials', 'AB'))
        r1.append(sppasAttribute('L1', 'French'))
        r1.append(sppasAttribute('XXXXX', 'INVISIBLE'))
        r1.set_state(States().CHECKED)
        r2 = FileReference('SpeakerCM')
        r2.set_type('SPEAKER')
        r2.append(sppasAttribute('initials', 'CM'))
        r2.append(sppasAttribute('XXXXX', 'VISIBLE'))

        self.AddRefs([r1, r2, r2])

        self.RemoveAttribute("XXXXX")

        r3 = FileReference('Dialog1')
        r3.set_type('INTERACTION')
        r3.set_state(States().CHECKED)

        self.AddRefs([r3])
        self.EditAttribute('spk-left', 'AB', 'str', 'Speaker at left')
        self.EditAttribute('spk-right', 'CM', 'str', 'Speaker at right')
        self.EditAttribute('when', '2003', 'int', 'Year of recording')

        # should not be seen
        r3.append(
        sppasAttribute('where', 'Aix-en-Provence', descr='Place of recording'))

