import wx.lib.newevent


class MediaEvents(object):
    # -----------------------------------------------------------------------
    # Event to be used by a media to ask parent perform an action.

    MediaActionEvent, EVT_MEDIA_ACTION = wx.lib.newevent.NewEvent()
    MediaActionCommandEvent, EVT_MEDIA_ACTION_COMMAND = wx.lib.newevent.NewCommandEvent()
