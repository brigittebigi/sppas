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

# Check if installation and feature configuration are matching...
try:
    import wx
    if cfg.feature_installed("wxpython") is False:
        # WxPython wasn't installed by the SPPAS setup.
        cfg.set_feature("wxpython", True)
except ImportError:
    if cfg.feature_installed("wxpython") is True:
        # Invalidate the feature because the package is not installed!
        cfg.set_feature("wxpython", False)

        class sppasWxError(object):
            def __init__(self, *args, **kwargs):
                raise sppasPackageFeatureError("wx", "wxpython")
    else:
        class sppasWxError(object):
            def __init__(self, *args, **kwargs):
                raise sppasEnableFeatureError("wxpython")

# The feature "wxpython" is enabled. Check the version!
if cfg.feature_installed("wxpython") is True:
    v = wx.version().split()[0][0]
    if v != '4':
        # Invalidate the feature because the package is not up-to-date
        cfg.set_feature("wxpython", False)

        class sppasWxError(object):
            def __init__(self, *args, **kwargs):
                raise sppasPackageUpdateFeatureError("wx", "wxpython")

# ---------------------------------------------------------------------------
# Either import classes or define them in cases wxpython is valid or not.
# ---------------------------------------------------------------------------


if cfg.feature_installed("wxpython") is True:
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
