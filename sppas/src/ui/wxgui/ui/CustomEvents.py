#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# ---------------------------------------------------------------------------
#            ___   __    __    __    ___
#           /     |  \  |  \  |  \  /              Automatic
#           \__   |__/  |__/  |___| \__             Annotation
#              \  |     |     |   |    \             of
#           ___/  |     |     |   | ___/              Speech
#
#
#                           http://www.sppas.org/
#
# ---------------------------------------------------------------------------
#            Laboratoire Parole et Langage, Aix-en-Provence, France
#                   Copyright (C) 2011-2016  Brigitte Bigi
#
#                   This banner notice must not be removed
# ---------------------------------------------------------------------------
# Use of this software is governed by the GNU Public License, version 3.
#
# SPPAS is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# SPPAS is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with SPPAS. If not, see <http://www.gnu.org/licenses/>.
#
# ---------------------------------------------------------------------------
# File: CustomEvents.py
# ----------------------------------------------------------------------------

__docformat__ = """epytext"""
__authors__   = """Brigitte Bigi"""
__copyright__ = """Copyright (C) 2011-2015  Brigitte Bigi"""


# ----------------------------------------------------------------------------
# Imports
# ----------------------------------------------------------------------------

import wx
import wx.lib.newevent as newevent


# ----------------------------------------------------------------------------
# Events related to the Main Frame
# ----------------------------------------------------------------------------

# Notebook: ask to add an empty page
# No expected parameter
NotebookNewPageEvent, spEVT_NOTEBOOK_NEW_PAGE = newevent.NewEvent()
NotebookNewPageCommandEvent, spEVT_NOTEBOOK_NEW_PAGE_COMMAND = newevent.NewCommandEvent()

# Notebook: ask to close a page
# No parameter is expected (the currently selected page is closed)
NotebookClosePageEvent, spEVT_NOTEBOOK_CLOSE_PAGE = newevent.NewEvent()
NotebookClosePageCommandEvent, spEVT_NOTEBOOK_CLOSE_PAGE_COMMAND = newevent.NewCommandEvent()


# Settings
SettingsEvent, spEVT_SETTINGS = newevent.NewEvent()
SettingsCommandEvent, spEVT_SETTINGS_COMMAND = newevent.NewCommandEvent()


# One file is removed/added.
# Expected parameters are:
# - "filename" String
# - "status"   True/False
FileWanderEvent, spEVT_FILE_WANDER = newevent.NewEvent()
FileWanderCommandEvent, spEVT_FILE_WANDER_COMMAND = newevent.NewCommandEvent()


# A file has to be checked/unchecked in the file manager
# Expected parameters are:
# - "filename" String
# - "status"   True/False
FileCheckEvent, spEVT_FILE_CHECK = newevent.NewEvent()
FileCheckCommandEvent, spEVT_FILE_CHECK_COMMAND = newevent.NewCommandEvent()


# A file has been modified
# Expected parameters are:
# - "filename" String
# - "status"   True/False
FileDirtyEvent, spEVT_FILE_DIRTY = newevent.NewEvent()
FileDirtyCommandEvent, spEVT_FILE_DIRTY_COMMAND = newevent.NewCommandEvent()


# ----------------------------------------------------------------------------
# Events for anz_panels
# ----------------------------------------------------------------------------

PanelSelectedEvent, spEVT_PANEL_SELECTED = newevent.NewEvent()
PanelSelectedCommandEvent, spEVT_PANEL_SELECTED_COMMAND = newevent.NewCommandEvent()


# Generic event to mention that an object was selected
# Expected parameters are:
# object : the selected object
# string : any string
ObjectSelectedEvent, spEVT_OBJECT_SELECTED =newevent.NewEvent()
ObjectSelectedCommandEvent, spEVT_OBJECT_SELECTED_COMMAND = newevent.NewCommandEvent()

# ----------------------------------------------------------------------------
