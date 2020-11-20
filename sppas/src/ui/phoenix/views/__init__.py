# -*- coding: UTF-8 -*-

from .about import About
from .about import AboutPlugin
from .metaedit import MetaDataEdit

from .feedback import Feedback
from .settings import Settings
from .statsview import StatsView
from .tiersview import TiersView
from .audioroamer import AudioRoamer
from .textedit import sppasTextEditDialog, CloseEditEvent, EVT_CLOSE_EDIT

__all__ = (
    "MetaDataEdit",
    'Feedback',
    'About',
    'AboutPlugin',
    'Settings',
    "StatsView",
    "TiersView",
    "sppasTextEditDialog",
    "CloseEditEvent",
    "EVT_CLOSE_EDIT",
    "AudioRoamer"
)
