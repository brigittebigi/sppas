#!/usr/bin/env python

import wx
import wx.dataview as dv
import random
import logging

from sppas.src.ui.cfg import sppasAppConfig
from sppas.src.ui.phoenix.main_settings import WxAppSettings

musicdata = {
1 : ("Bad English", "The Price Of Love", "Rock"),
2 : ("DNA featuring Suzanne Vega", "Tom's Diner", "Rock"),
3 : ("George Michael", "Praying For Time", "Rock"),
4 : ("Gloria Estefan", "Here We Are", "Rock"),
5 : ("Linda Ronstadt", "Don't Know Much", "Rock"),
6 : ("Michael Bolton", "How Am I Supposed To Live Without You", "Blues"),
7 : ("Paul Young", "Oh Girl", "Rock"),
8 : ("Paula Abdul", "Opposites Attract", "Rock"),
9 : ("Richard Marx", "Should've Known Better", "Rock"),
10: ("Rod Stewart", "Forever Young", "Rock"),
11: ("Roxette", "Dangerous", "Rock"),
12: ("Sheena Easton", "The Lover In Me", "Rock"),
13: ("Sinead O'Connor", "Nothing Compares 2 U", "Rock"),
14: ("Stevie B.", "Because I Love You", "Rock"),
15: ("Taylor Dayne", "Love Will Lead You Back", "Rock"),
16: ("The Bangles", "Eternal Flame", "Rock"),
17: ("Wilson Phillips", "Release Me", "Rock"),
18: ("Billy Joel", "Blonde Over Blue", "Rock"),
19: ("Billy Joel", "Famous Last Words", "Rock"),
20: ("Janet Jackson", "State Of The World", "Rock"),
21: ("Janet Jackson", "The Knowledge", "Rock"),
22: ("Spyro Gyra", "End of Romanticism", "Jazz"),
23: ("Spyro Gyra", "Heliopolis", "Jazz"),
24: ("Spyro Gyra", "Jubilee", "Jazz"),
25: ("Spyro Gyra", "Little Linda", "Jazz"),
26: ("Spyro Gyra", "Morning Dance", "Jazz"),
27: ("Spyro Gyra", "Song for Lorraine", "Jazz"),
28: ("Yes", "Owner Of A Lonely Heart", "Rock"),
29: ("Yes", "Rhythm Of Love", "Rock"),
30: ("Billy Joel", "Lullabye (Goodnight, My Angel)", "Rock"),
31: ("Billy Joel", "The River Of Dreams", "Rock"),
32: ("Billy Joel", "Two Thousand Years", "Rock"),
33: ("Janet Jackson", "Alright", "Rock"),
34: ("Janet Jackson", "Black Cat", "Rock"),
35: ("Janet Jackson", "Come Back To Me", "Rock"),
36: ("Janet Jackson", "Escapade", "Rock"),
37: ("Janet Jackson", "Love Will Never Do (Without You)", "Rock"),
38: ("Janet Jackson", "Miss You Much", "Rock"),
39: ("Janet Jackson", "Rhythm Nation", "Rock"),
40: ("Cusco", "Dream Catcher", "New Age"),
41: ("Cusco", "Geronimos Laughter", "New Age"),
42: ("Cusco", "Ghost Dance", "New Age"),
43: ("Blue Man Group", "Drumbone", "New Age"),
44: ("Blue Man Group", "Endless Column", "New Age"),
45: ("Blue Man Group", "Klein Mandelbrot", "New Age"),
46: ("Kenny G", "Silhouette", "Jazz"),
47: ("Sade", "Smooth Operator", "Jazz"),
48: ("David Arkenstone", "Papillon (On The Wings Of The Butterfly)", "New Age"),
49: ("David Arkenstone", "Stepping Stars", "New Age"),
50: ("David Arkenstone", "Carnation Lily Lily Rose", "New Age"),
51: ("David Lanz", "Behind The Waterfall", "New Age"),
52: ("David Lanz", "Cristofori's Dream", "New Age"),
53: ("David Lanz", "Heartsounds", "New Age"),
54: ("David Lanz", "Leaves on the Seine", "New Age"),
}

# ----------------------------------------------------------------------


def makeBlank(self):
    # Just a little helper function to make an empty image for our
    # model to use.
    empty = wx.Bitmap(16,16,32)
    dc = wx.MemoryDC(empty)
    dc.SetBackground(wx.Brush((0,0,0,0)))
    dc.Clear()
    del dc
    return empty


# ----------------------------------------------------------------------
# We'll use instances of these classes to hold our music data. Items in the
# tree will get associated back to the corresponding Song or Genre object.

class Song(object):
    def __init__(self, id, artist, title, genre):
        self.id = id
        self.artist = artist
        self.title = title
        self.genre = genre
        self.like = False
        # get a random date value
        d = random.choice(range(27))+1
        m = random.choice(range(12))
        y = random.choice(range(1980, 2005))
        self.date = wx.DateTime().FromDMY(d, m, y)

    def __repr__(self):
        return 'Song: %s-%s' % (self.artist, self.title)


class Genre(object):
    def __init__(self, name):
        self.name = name
        self.songs = []

    def __repr__(self):
        return 'Genre: ' + self.name

# ----------------------------------------------------------------------

# This model acts as a bridge between the DataViewCtrl and the music data, and
# organizes it hierarchically as a collection of Genres, each of which is a
# collection of songs. We derive the class from PyDataViewCtrl, which knows
# how to reflect the C++ virtual methods to the Python methods in the derived
# class.

# This model provides these data columns:
#
#     0. Genre :  string
#     1. Artist:  string
#     2. Title:   string
#     3. id:      integer
#     4. Acquired: date
#     5. Liked:   bool
#


class MyTreeListModel(dv.PyDataViewModel):
    def __init__(self, data):
        dv.PyDataViewModel.__init__(self)
        self.data = data

        # The PyDataViewModel derives from both DataViewModel and from
        # DataViewItemObjectMapper, which has methods that help associate
        # data view items with Python objects. Normally a dictionary is used
        # so any Python object can be used as data nodes. If the data nodes
        # are weak-referencable then the objmapper can use a
        # WeakValueDictionary instead.
        self.UseWeakRefs(True)

    # Report how many columns this model provides data for.
    def GetColumnCount(self):
        return 6

    # Map the data column numbers to the data type
    def GetColumnType(self, col):
        mapper = { 0 : 'string',
                   1 : 'string',
                   2 : 'string',
                   3.: 'string', # the real value is an int, but the renderer should convert it okay
                   4 : 'datetime',
                   5 : 'bool',
                   }
        return mapper[col]

    def GetChildren(self, parent, children):
        # The view calls this method to find the children of any node in the
        # control. There is an implicit hidden root node, and the top level
        # item(s) should be reported as children of this node. A List view
        # simply provides all items as children of this hidden root. A Tree
        # view adds additional items as children of the other items, as needed,
        # to provide the tree hierachy.

        # If the parent item is invalid then it represents the hidden root
        # item, so we'll use the genre objects as its children and they will
        # end up being the collection of visible roots in our tree.
        if not parent:
            for genre in self.data:
                children.append(self.ObjectToItem(genre))
            return len(self.data)

        # Otherwise we'll fetch the python object associated with the parent
        # item and make DV items for each of its child objects.
        node = self.ItemToObject(parent)
        if isinstance(node, Genre):
            for song in node.songs:
                children.append(self.ObjectToItem(song))
            return len(node.songs)
        return 0

    def IsContainer(self, item):
        # Return True if the item has children, False otherwise.
        # The hidden root is a container
        if not item:
            return True
        # and in this model the genre objects are containers
        node = self.ItemToObject(item)
        if isinstance(node, Genre):
            return True
        # but everything else (the song objects) are not
        return False

    #def HasContainerColumns(self, item):
    #    return True

    def GetParent(self, item):
        # Return the item which is this item's parent.
        if not item:
            return dv.NullDataViewItem

        node = self.ItemToObject(item)
        if isinstance(node, Genre):
            return dv.NullDataViewItem
        elif isinstance(node, Song):
            for g in self.data:
                if g.name == node.genre:
                    return self.ObjectToItem(g)

    def GetValue(self, item, col):
        # Return the value to be displayed for this item and column. For this
        # example we'll just pull the values from the data objects we
        # associated with the items in GetChildren.

        # Fetch the data object for this item.
        node = self.ItemToObject(item)

        if isinstance(node, Genre):
            # We'll only use the first column for the Genre objects,
            # for the other columns lets just return empty values
            mapper = { 0 : node.name,
                       1 : "",
                       2 : "",
                       3 : "",
                       4 : wx.DateTime.FromTimeT(0),  # TODO: There should be some way to indicate a null value...
                       5 : False,
                       }
            return mapper[col]

        elif isinstance(node, Song):
            mapper = { 0 : node.genre,
                       1 : node.artist,
                       2 : node.title,
                       3 : node.id,
                       4 : node.date,
                       5 : node.like,
                       }
            return mapper[col]

        else:
            raise RuntimeError("unknown node type")

    def GetAttr(self, item, col, attr):
        node = self.ItemToObject(item)
        if isinstance(node, Genre):
            attr.SetColour('blue')
            attr.SetBold(True)
            return True
        return False

    def SetValue(self, value, item, col):
        # We're not allowing edits in column zero (see below) so we just need
        # to deal with Song objects and cols 1 - 5
        node = self.ItemToObject(item)
        if isinstance(node, Song):
            if col == 1:
                node.artist = value
            elif col == 2:
                node.title = value
            elif col == 3:
                node.id = value
            elif col == 4:
                node.date = value
            elif col == 5:
                node.like = value
        return True

# ----------------------------------------------------------------------


class TestPanel(wx.Panel):
    def __init__(self, parent, data=None, model=None):
        wx.Panel.__init__(self, parent, -1)

        # Create a dataview control
        self.dvc = dv.DataViewCtrl(self,
                                   style=wx.BORDER_THEME
                                   | dv.DV_ROW_LINES  # nice alternating bg colors
                                   | dv.DV_VERT_RULES
                                   | dv.DV_SINGLE
                                   )

        # Create an instance of our model...
        if model is None:
            self.model = MyTreeListModel(data)
            newModel = True  # it's a new instance so we need to decref it below
        else:
            self.model = model
            newModel = False

        # Tell the DVC to use the model
        self.dvc.AssociateModel(self.model)
        if newModel:
            self.model.DecRef()

        # Define the columns that we want in the view.  Notice the
        # parameter which tells the view which column in the data model to pull
        # values from for each view column.
        # here is an example of adding a column with full control over the renderer, etc.
        tr = dv.DataViewTextRenderer()
        c0 = dv.DataViewColumn("Genre",   # title
                               tr,        # renderer
                               0,         # data model column
                               width=80)
        self.dvc.AppendColumn(c0)
        c1 = self.dvc.AppendTextColumn("Artist",   1, width=170, mode=dv.DATAVIEW_CELL_EDITABLE)
        c2 = self.dvc.AppendTextColumn("Title",    2, width=260, mode=dv.DATAVIEW_CELL_EDITABLE)
        c3 = self.dvc.AppendDateColumn('Acquired', 4, width=100, mode=dv.DATAVIEW_CELL_ACTIVATABLE)
        c4 = self.dvc.AppendToggleColumn('Like',   5, width=40, mode=dv.DATAVIEW_CELL_ACTIVATABLE)

        # Notice how we pull the data from col 3, but this is the 6th column
        # added to the DVC. The order of the view columns is not dependent on
        # the order of the model columns at all.
        c5 = self.dvc.AppendTextColumn("id", 3, width=40,  mode=dv.DATAVIEW_CELL_EDITABLE)
        c5.Alignment = wx.ALIGN_RIGHT

        # Set some additional attributes for all the columns
        for c in self.dvc.Columns:
            c.Sortable = True
            c.Reorderable = True

        self.Sizer = wx.BoxSizer(wx.VERTICAL)
        self.Sizer.Add(self.dvc, 1, wx.EXPAND)

        b1 = wx.Button(self, label="New View", name="newView")
        self.Bind(wx.EVT_BUTTON, self.OnNewView, b1)
        b2 = wx.Button(self, label="Delete", name="delSelect")
        self.Bind(wx.EVT_BUTTON, self.OnDeleteSelected, b1)
        b3 = wx.Button(self, label="Cleared", name="cleared")
        self.Bind(wx.EVT_BUTTON, self.OnCleared, b1)

        btnsizer = wx.BoxSizer(wx.HORIZONTAL)
        self.Sizer.Add(b1, 0, wx.ALL, 5)
        self.Sizer.Add(b2, 0, wx.ALL, 5)
        self.Sizer.Add(b3, 0, wx.ALL, 5)

        self.Sizer.Add(btnsizer, 0, wx.ALL, 5)

    def OnNewView(self, evt):
        f = wx.Frame(None, title="New view, shared model", size=(600,400))
        TestPanel(f, model=self.model)
        b = f.FindWindow("newView")
        b.Disable()
        f.Show()

    def OnDeleteSelected(self, evt):
        pass

    def OnCleared(self, evt):
        self.model.Cleared()

# ----------------------------------------------------------------------------
# App to test
# ----------------------------------------------------------------------------


class TestApp(wx.App):

    def __init__(self):
        """Create a customized application."""
        # ensure the parent's __init__ is called with the args we want
        wx.App.__init__(self,
                        redirect=False,
                        filename=None,
                        useBestVisual=True,
                        clearSigInt=True)

        # create the frame
        frm = wx.Frame(None, title='Test frame', size=(800, 600))
        self.SetTopWindow(frm)

        # Fix language and translation
        self.locale = wx.Locale(wx.LANGUAGE_DEFAULT)
        self.__cfg = sppasAppConfig()
        self.settings = WxAppSettings()
        self.setup_debug_logging()

        # our data structure will be a collection of Genres, each of which is a
        # collection of Songs
        data = dict()
        for key in musicdata:
            val = musicdata[key]
            song = Song(str(key), val[0], val[1], val[2])
            genre = data.get(song.genre)
            if genre is None:
                genre = Genre(song.genre)
                data[song.genre] = genre
            genre.songs.append(song)
        data = data.values()

        # create a panel in the frame
        sizer = wx.BoxSizer()
        sizer.Add(TestPanel(frm, data), 1, wx.EXPAND, 0)
        frm.SetSizer(sizer)

        # show result
        frm.Show()

    @staticmethod
    def setup_debug_logging():
        logger = logging.getLogger()
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.DEBUG)
        logging.debug('Logging set to DEBUG level')

# ---------------------------------------------------------------------------


if __name__ == '__main__':
    app = TestApp()
    app.MainLoop()
