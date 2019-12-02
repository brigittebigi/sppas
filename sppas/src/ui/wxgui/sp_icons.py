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
# File: sp_icons.py
# ----------------------------------------------------------------------------

import os.path

# ---------------------------------------------------------------------------

THEME_DEFAULT = 'Default'

# ---------------------------------------------------------------------------
# Frames/Applications

APP_ICON         = os.path.join("applications", "sppas.png")
COMPONENTS_ICON  = os.path.join("applications", "components.png")
ANNOTATIONS_ICON = os.path.join("applications", "annotations.png")
PLUGINS_ICON     = os.path.join( "applications", "plugins.png" )

AUDIOROAMER_APP_ICON = os.path.join( "applications", "player.png")
DATAROAMER_APP_ICON  = os.path.join( "applications", "roamer.png")
IPUSCRIBE_APP_ICON   = os.path.join( "applications", "ipuscribe.png")
SPPASEDIT_APP_ICON   = os.path.join( "applications", "viewer.png")
STATISTICS_APP_ICON  = os.path.join( "applications", "stats.png")
DATAFILTER_APP_ICON  = os.path.join( "applications", "filter.png")


# ---------------------------------------------------------------------------
# Actions, for the toolbars and menus

MENU_EXIT_ICON     = os.path.join( "menu", "exit.png" )
MENU_BUG_ICON      = os.path.join( "menu", "bug.png" )
MENU_BACK_ICON     = os.path.join( "menu", "back.png" )
MENU_FEEDBACK_ICON = os.path.join( "menu", "feedback.png" )
MENU_CLOSE_ICON    = os.path.join( "menu", "close.png" )

ANNOTATE_ICON       = os.path.join( "actions", "annotate.png" )
ANNOTATE_CONFIG_ICON= os.path.join( "actions", "annotate-config.png" )
BACKWARD_ICON       = os.path.join( "actions", "backward.png" )
BUG_ICON            = os.path.join( "actions", "bug.png" )
FEEDBACK_ICON       = os.path.join( "actions", "feedback.png")
FORWARD_ICON        = os.path.join( "actions", "forward.png" )
HOME_ICON           = os.path.join( "actions", "home.png" )
NEXT_ICON           = os.path.join( "actions", "next.png")
PREVIOUS_ICON       = os.path.join( "actions", "previous.png")
RESTORE_ICON        = os.path.join( "actions", "restore.png")
SETTINGS_ICON       = os.path.join( "actions", "settings.png")
TAB_NEW_ICON        = os.path.join( "actions", "tab-new.png")
TAB_CLOSE_ICON      = os.path.join( "actions", "tab-close.png")
MESSAGE_ICON        = os.path.join( "actions", "message.png")
WEB_ICON            = os.path.join( "actions", "world.png")

PLUGIN_IMPORT_ICON = os.path.join( "actions", "plugin-import.png")
PLUGIN_REMOVE_ICON = os.path.join( "actions", "plugin-remove.png")

ABOUT_ICON          = os.path.join( "actions", "about.png" )
APPLY_ICON          = os.path.join( "actions", "apply.png" )
CANCEL_ICON         = os.path.join( "actions", "cancel.png" )
CLOSE_ICON          = os.path.join( "actions", "close.png" )
EXIT_ICON           = os.path.join( "actions", "exit.png" )
HELP_ICON           = os.path.join( "actions", "help.png" )
LOGOUT_ICON         = os.path.join( "actions", "logout.png" )
INFO_ICON           = os.path.join( "actions", "info.png" )
YES_ICON            = os.path.join( "actions", "yes.png")
NO_ICON             = os.path.join( "actions", "no.png")
OKAY_ICON           = os.path.join( "actions", "okay.png")

DLG_INFO_ICON       = os.path.join( "actions", "dialog-information.png")
DLG_WARN_ICON       = os.path.join( "actions", "dialog-warning.png")
DLG_ERR_ICON        = os.path.join( "actions", "dialog-error.png")
DLG_QUEST_ICON      = os.path.join( "actions", "dialog-question.png")

# ---------------------------------------------------------------------------
# Files

# toolbars and menus
ADD_FILE_ICON       = os.path.join( "files", "file-add.png" )
ADD_DIR_ICON        = os.path.join( "files", "folder-add.png" )
REMOVE_ICON         = os.path.join( "files", "remove.png" )
DELETE_ICON         = os.path.join( "files", "delete.png" )
EXPORT_AS_ICON      = os.path.join( "files", "export1.png" )
EXPORT_ICON         = os.path.join( "files", "export2.png" )

NEW_FILE            = os.path.join( "files", "new.png")
SAVE_FILE           = os.path.join( "files", "save.png")
SAVE_ALL_FILE       = os.path.join( "files", "save_all.png")
SAVE_AS_FILE        = os.path.join( "files", "save_as.png")

# mime and tree view
TREE_ROOT           = os.path.join( "files", "tree.png")
TREE_FOLDER_CLOSE   = os.path.join( "files", "folder-close.png")
TREE_FOLDER_OPEN    = os.path.join( "files", "folder-open.png")
MIME_WAV            = os.path.join( "files", "mime_wav.png")
MIME_ASCII          = os.path.join( "files", "mime_text.png")
MIME_PITCHTIER      = os.path.join( "files", "mime_pitchtier.png")
MIME_TEXTGRID       = os.path.join( "files", "mime_textgrid.png")
MIME_TRS            = os.path.join( "files", "mime_trs.png")
MIME_EAF            = os.path.join( "files", "mime_eaf.png")
MIME_XRA            = os.path.join( "files", "mime_xra.png")
MIME_MRK            = os.path.join( "files", "mime_mrk.png")
MIME_SUBTITLES      = os.path.join( "files", "mime_subtitles.png")
MIME_ANVIL          = os.path.join( "files", "mime_anvil.png")
MIME_ANTX           = os.path.join( "files", "mime_antx.png")
MIME_XTRANS         = os.path.join( "files", "mime_xtrans.png")
MIME_AUP            = os.path.join( "files", "mime_aup.png")


# ---------------------------------------------------------------------------
# For the Settings

FONT_ICON               = os.path.join( "settings", "font.png")
BG_COLOR_ICON           = os.path.join( "settings", "fill-color.png")
FG_COLOR_ICON           = os.path.join( "settings", "text-color.png")


# ---------------------------------------------------------------------------
# Player

PLAYER_INFO             = os.path.join( "speech", "snd-info.png")
PLAYER_PLAY             = os.path.join( "speech", "snd-play.png")
PLAYER_REPLAY           = os.path.join( "speech", "snd-replay.png")
PLAYER_PAUSE            = os.path.join( "speech", "snd-pause.png")
PLAYER_STOP             = os.path.join( "speech", "snd-stop.png")
PLAYER_NEXT             = os.path.join( "speech", "snd-next.png")
PLAYER_REWIND           = os.path.join( "speech", "snd-previous.png")
PLAYER_EJECT            = os.path.join( "speech", "snd-eject.png")

PLAYER_INFO_DISABLED    = os.path.join( "speech", "snd-info-disabled.png")
PLAYER_PLAY_DISABLED    = os.path.join( "speech", "snd-play-disabled.png")
PLAYER_REPLAY_DISABLED  = os.path.join( "speech", "snd-replay-disabled.png")
PLAYER_PAUSE_DISABLED   = os.path.join( "speech", "snd-pause-disabled.png")
PLAYER_STOP_DISABLED    = os.path.join( "speech", "snd-stop-disabled.png")
PLAYER_NEXT_DISABLED    = os.path.join( "speech", "snd-next-disabled.png")
PLAYER_REWIND_DISABLED  = os.path.join( "speech", "snd-previous-disabled.png")
PLAYER_EJECT_DISABLED   = os.path.join( "speech", "snd-eject-disabled.png")


# ---------------------------------------------------------------------------
# DataRoamer

TIER_RENAME         = os.path.join( "tiers", "tier_rename.png")
TIER_DELETE         = os.path.join( "tiers", "tier_delete.png")
TIER_CUT            = os.path.join( "tiers", "tier_cut.png")
TIER_COPY           = os.path.join( "tiers", "tier_copy.png")
TIER_PASTE          = os.path.join( "tiers", "tier_paste.png")
TIER_DUPLICATE      = os.path.join( "tiers", "tier_duplicate.png")
TIER_MOVE_UP        = os.path.join( "tiers", "tier_up.png")
TIER_MOVE_DOWN      = os.path.join( "tiers", "tier_down.png")
TIER_PREVIEW        = os.path.join( "tiers", "tier_preview.png")
TIER_RADIUS         = os.path.join( "tiers", "tier_radius.png")

# ---------------------------------------------------------------------------
# IPUscribe

PAGE_FIRST_ICON = os.path.join( "others", "pagefirst.png")
PAGE_LAST_ICON  = os.path.join( "others", "pagelast.png")
PAGE_PREV_ICON  = os.path.join( "others", "pageprev.png")
PAGE_NEXT_ICON  = os.path.join( "others", "pagenext.png")


# ---------------------------------------------------------------------------
# SppasEdit

BROOM_ICON = os.path.join( "others", "broom.png")  # Search frame

RULER_RED   = os.path.join( "timenav", "indicator_down-red.png")
RULER_GREEN = os.path.join( "timenav", "indicator_down-green.png")
RULER_BLUE  = os.path.join( "timenav", "indicator_down-blue.png")

TIER_CHECK                = os.path.join( "tiers", "tier_check.png")
TIER_INFO                 = os.path.join( "tiers", "tier_info.png")
TIER_SEARCH               = os.path.join( "tiers", "tier_search.png")
TIER_CHECK_DISABLED       = os.path.join( "tiers", "tier_check_disabled.png")
TIER_INFO_DISABLED        = os.path.join( "tiers", "tier_info_disabled.png")
TIER_SEARCH_DISABLED      = os.path.join( "tiers", "tier_search_disabled.png")

NAV_GO_START_ICON         = os.path.join( "timenav", "nav_go_first.png")
NAV_GO_PREVIOUS_ICON      = os.path.join( "timenav", "nav_go_previous.png")
NAV_GO_NEXT_ICON          = os.path.join( "timenav", "nav_go_next.png")
NAV_GO_END_ICON           = os.path.join( "timenav", "nav_go_last.png")
NAV_FIT_SELECTION_ICON    = os.path.join( "timenav", "nav_fit_selection.png")
NAV_PERIOD_ZOOM_ICON      = os.path.join( "timenav", "nav_hzoom.png")
NAV_PERIOD_ZOOM_IN_ICON   = os.path.join( "timenav", "nav_hzoom_in.png")
NAV_PERIOD_ZOOM_OUT_ICON  = os.path.join( "timenav", "nav_hzoom_out.png")
NAV_VIEW_ZOOM_IN_ICON     = os.path.join( "timenav", "nav_vzoom_in.png")
NAV_VIEW_ZOOM_OUT_ICON    = os.path.join( "timenav", "nav_vzoom_out.png")

SND_INFO                  = os.path.join( "speech", "snd-info.png")
SND_INFO_DISABLED         = os.path.join( "speech", "snd-info-disabled.png")


# ---------------------------------------------------------------------------
# DataFilter

FILTER_ADD_LABEL    = os.path.join( "others", "list-add-label.png")
FILTER_ADD_DURATION = os.path.join( "others", "list-add-duration.png")
FILTER_ADD_TIME     = os.path.join( "others", "list-add-time.png")
FILTER_REMOVE       = os.path.join( "others", "list-clear.png")
FILTER_CHECK        = os.path.join( "others", "list-check.png")
FILTER_UNCHECK      = os.path.join( "others", "list-uncheck.png")
FILTER_UNLABELLED   = os.path.join( "others", "broom.png")
FILTER_SINGLE       = os.path.join( "actions", "filter.png")
FILTER_RELATION     = os.path.join( "actions", "filter-relation.png")

# ---------------------------------------------------------------------------
# Statistics

SPREADSHEETS     = os.path.join( "others", "spreadsheet.png")
USERCHECK        = os.path.join( "others", "usercheck.png")
TIMEANALYSIS     = os.path.join( "others", "timeanalysis.png")

# ---------------------------------------------------------------------------
# Various

# For the CustomCheckBox
ACTIVATED_ICON      = os.path.join( "others", "on.png")
DISABLED_ICON       = os.path.join( "others", "off.png")
CHECKED_ICON        = os.path.join( "others", "check.png")
UNCHECKED_ICON      = os.path.join( "others", "uncheck.png")
RADIOCHECKED_ICON   = os.path.join( "others", "radiocheck.png")
RADIOUNCHECKED_ICON = os.path.join( "others", "radiouncheck.png")

# For the Notebook
EMPTY_ICON          = os.path.join( "others", "empty.png")
NON_EMPTY_ICON      = os.path.join( "others", "non-empty.png")

# For the Feedback form
MAIL_DEFAULT_ICON     = os.path.join( "actions", "maildefault.png")
MAIL_GMAIL_ICON       = os.path.join( "actions", "mailgoogle.png")
MAIL_OTHER_ICON       = os.path.join( "actions", "mailother.png")

# Main frame
LINK_ICON   = os.path.join( "others", "link.png")
UNLINK_ICON = os.path.join( "others", "link-break.png")

# Procedure utcome report
REPORT_ICON = os.path.join( "others", "report.png")

# ---------------------------------------------------------------------------
