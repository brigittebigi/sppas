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

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2018  Brigitte Bigi

*****************************************************************************
plugins: access and manage external programs.
*****************************************************************************

This package includes classes to manage external program to plug into SPPAS.

:Example:

>>> # Create a plugin manager (it will explore the installed plugins).
>>> manager = sppasPluginsManager()
>>> # Install a plugin
>>> plugin_id = manager.install(plugin_zip_filename,
>>>                             plugin_destination_folder_name)
>>> # Get a plugin
>>> p = manager.get_plugin(plugin_id)
>>> # Apply a plugin on a list of files
>>> message = manager.run_plugin(plugin_id, [some_filename1, some_filename2])
>>> print(message)
>>> # Delete an installed plugin
>>> manager.delete(plugin_id)

Requires the following other packages:

* config
* utils
* files
* structs

"""

from .manager import sppasPluginsManager
from .plugin import sppasPluginParam
from .process import sppasPluginProcess

__all__ = (
    "sppasPluginsManager",
    "sppasPluginParam",
    "sppasPluginProcess"
)
