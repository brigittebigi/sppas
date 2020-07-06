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

    ui.phoenix.__init__.py
    ~~~~~~~~~~~~~~~~~~~~~~

"""

from sppas.src.config import cfg
from sppas.src.exceptions import sppasEnableFeatureError
from sppas.src.exceptions import sppasPackageFeatureError
from sppas.src.exceptions import sppasPackageUpdateFeatureError


# The feature "wxpython" is enabled. Check if really correct!
if cfg.dep_installed("wxpython") is True:
    v = '0'
    try:
        import wx
    except ImportError:
        # Invalidate the feature because the package is not installed
        cfg.set_dep("wxpython", False)
    else:
        v = wx.version().split()[0][0]
        if v != '4':
            # Invalidate the feature because the package is not up-to-date
            cfg.set_dep("wxpython", False)

    class sppasWxError(object):
        def __init__(self, *args, **kwargs):
            if v != '4':
                raise sppasPackageUpdateFeatureError("wx", "wxpython")
            else:
                raise sppasPackageFeatureError("wx", "wxpython")

else:
    # The feature "wxpython" is not enabled or unknown.
    cfg.set_dep("wxpython", False)

    class sppasWxError(object):
        def __init__(self, *args, **kwargs):
            raise sppasEnableFeatureError("wxpython")


# ---------------------------------------------------------------------------
# Either import classes or define them in cases wxpython is valid or not.
# ---------------------------------------------------------------------------


if cfg.dep_installed("wxpython") is True:
    from .install_app import sppasInstallApp
    from .main_app import sppasApp

else:

    class sppasInstallApp(sppasWxError):
        pass


    class sppasApp(sppasWxError):
        pass


__all__ = (
    'sppasInstallApp',
    'sppasApp'
)
