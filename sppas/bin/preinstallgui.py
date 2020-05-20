#!/usr/bin/env python

import sys
import os
import time

try:
    import wx
except ImportError:
    msg = "WxPython is not installed on your system.\n"\
          "The Graphical User Interface of SPPAS Installer can't work."
    print("[ ERROR ] {:s}".format(msg))
    print("SPPAS exits with error status: -1")
    time.sleep(5)
    sys.exit(-1)

PROGRAM = os.path.abspath(__file__)
SPPAS = os.path.dirname(os.path.dirname(os.path.dirname(PROGRAM)))
sys.path.append(SPPAS)

from sppas import sg
from sppas.src.ui.phoenix.install_app import sppasInstallApp

# Create and run the wx application
app = sppasInstallApp()
status = app.run()
if status != 0:
    print("{:s} exits with error status: {:d}"
          "".format(sg.__name__, status))
sys.exit(status)
