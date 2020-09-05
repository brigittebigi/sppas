#!/usr/bin/env python
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

    __main__.py
    ~~~~~~~~~~~~~~~

    In Python, '__main__' is the name of the scope in which top-level code
    executes. Within SPPAS, it allows to launch the Graphical User Interface.

To launch the GUI, this main file allows the followings 3 possibilities:

>>> python3 -m sppas
>>> python3 sppas
>>> python3 sppas/__main__.py

In case of error, it will create a log file with the error message and
display it.

"""

import sys
import os
import webbrowser

if __package__ is None or len(__package__) == 0:
    dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.insert(0, dir)
    __package__ = "sppas"

from sppas.src.config import cfg
from sppas.src.config import sppasLogFile
from sppas.src.exceptions import sppasEnableFeatureError
from sppas.src.exceptions import sppasPackageFeatureError
from sppas.src.exceptions import sppasPackageUpdateFeatureError
from sppas.src.ui.phoenix import sppasApp

status = -1
msg = ""

if sys.version_info < (3, 6):
    msg = "The version of Python is not the right one. "\
          "This GUI of SPPAS requires at least version 3.6."
else:
    try:
        # Create and run the wx application
        app = sppasApp()
        status = app.run()
    except sppasEnableFeatureError as e:
        # wxpython feature is not enabled
        status = e.status
        msg = str(e)
    except sppasPackageFeatureError as e:
        # wxpython is enabled but wx can't be imported
        status = e.status
        msg = str(e)
    except sppasPackageUpdateFeatureError as e:
        # wxpython is enabled but the version is not the right one
        status = e.status
        msg = str(e)
    except Exception as e:
        # any other error...
        msg = str(e)

if status != 0:
    report = sppasLogFile(pattern="run")
    with open(report.get_filename(), "w") as f:
        f.write(report.get_header())
        f.write(msg)
        f.write("\n")
        f.write("\n")
        f.write("SPPAS application exited with error status: {:d}.".format(status))
    webbrowser.open(url=report.get_filename())

cfg.save()
sys.exit(status)
