import wx
import sys

from os import path
PROGRAM = path.abspath(__file__)
SPPAS = path.dirname(path.dirname(path.dirname(path.dirname(path.dirname(path.dirname(PROGRAM))))))
sys.path.append(SPPAS)

from sppas.src.ui import sppasLogSetup
from sppas.src.ui.phoenix.dialogs.settings import sppasSettingsDialog

from sppas.src.ui.phoenix import WxAppSettings
from sppas.src.ui.cfg import sppasAppConfig

# ---------------------------------------------------------------------------


class testApp(wx.App):
    """Create a test SPPAS Phoenix application.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2018  Brigitte Bigi

    """

    def __init__(self):
        """Wx Application initialization."""
        # Initialize the wx application
        wx.App.__init__(self,
                        redirect=False,
                        filename=None,
                        useBestVisual=True,
                        clearSigInt=True)
        self.cfg = sppasAppConfig()
        self.settings = WxAppSettings()

# ---------------------------------------------------------------------------


lgs = sppasLogSetup(0)
lgs.stream_handler()
app = testApp()

# demo = sppasDialog(None, title="sppasDialog")
# demo.CreateHeader("This is a BaseDialog...")
# demo.CreateActions([wx.CANCEL], [wx.OK])
# demo.LayoutComponents()
# demo.ShowModal()
# demo.Destroy()

# demo = sppasYesNoDialog("This is a question?")
# r = demo.ShowModal()
# if r == wx.ID_YES:
#     print("Click on Yes")
# elif r == wx.ID_NO:
#     print("Click on No")
# else:
#     print('Nothing clicked on. {:d}'.format(r))
# demo.Destroy()

# demo = sppasInformationDialog("This is an information!")
# demo.ShowModal()
# demo.Destroy()

# demo = sppasFeedbackDialog(None)
# response = demo.ShowModal()
# demo.Destroy()

# demo = sppasAboutDialog(None)
# response = demo.ShowModal()
# demo.Destroy()

demo = sppasSettingsDialog(None)
response = demo.ShowModal()
demo.Destroy()

app.SetTopWindow(demo)
app.MainLoop()
