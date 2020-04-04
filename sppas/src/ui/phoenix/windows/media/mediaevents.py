import wx.lib.newevent


class MediaEvents(object):

    # -----------------------------------------------------------------------
    # Event to be used by a media to ask parent perform an action.

    MediaActionEvent, EVT_MEDIA_ACTION = wx.lib.newevent.NewEvent()
    MediaActionCommandEvent, EVT_MEDIA_ACTION_COMMAND = wx.lib.newevent.NewCommandEvent()

    # -----------------------------------------------------------------------
    # Event sent when the media is loaded, so when it's real size is known.
    # Not platform dependent: the event is sent whatever the backend used.
    MediaLoadedEvent, EVT_MEDIA_LOADED = wx.lib.newevent.NewEvent()
    MediaLoadedCommandEvent, EVT_MEDIA_LOADED_COMMAND = wx.lib.newevent.NewCommandEvent()

    # -----------------------------------------------------------------------
    # Event sent when the media failed to be loaded.
    # Not platform dependent: the event is sent whatever the backend used.
    MediaNotLoadedEvent, EVT_MEDIA_NOT_LOADED = wx.lib.newevent.NewEvent()
    MediaNotLoadedCommandEvent, EVT_MEDIA_NOT_LOADED_COMMAND = wx.lib.newevent.NewCommandEvent()
