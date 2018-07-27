import wx
import wx.lib.newevent


MapReadyEventType, EVT_MAP_READY = wx.lib.newevent.NewCommandEvent()

MapReadyEventType = wx.NewEventType()
EVT_MAP_READY = wx.PyEventBinder(MapReadyEventType, 0)


class MapReadyEvent(wx.PyEvent):
    eventType = MapReadyEventType

    def __init__(self):
        wx.PyEvent.__init__(self, eventType=self.eventType)