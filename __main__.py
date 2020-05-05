#!/usr/bin/env python

import sys
import os
import time

try:
    import wx
except ImportError:
    msg = "WxPython is not installed on your system.\n"\
          "The Graphical User Interface of SPPAS can't work."
    print("[ ERROR ] {:s}".format(msg))
    print("SPPAS exits with error status: -1")
    time.sleep(5)
    sys.exit(-1)

sppasDir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, sppasDir)
from sppas.src.config import sg
from sppas.src.ui.phoenix.main_app import sppasApp

# Create and run the wx application
app = sppasApp()
status = app.run()
if status != 0:
    print("{:s} exits with error status: {:d}"
          "".format(sg.__name__, status))
sys.exit(status)
