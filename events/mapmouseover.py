import wx
import wx.lib.newevent


MapMouseOverEventType, EVT_MAP_MOUSE_OVER = wx.lib.newevent.NewCommandEvent()

MapMouseOverEventType = wx.NewEventType()
EVT_MAP_MOUSE_OVER = wx.PyEventBinder(MapMouseOverEventType, 0)


class MapMouseOverEvent(wx.PyEvent):
    eventType = MapMouseOverEventType

    def __init__(self, point):
        wx.PyEvent.__init__(self, eventType=self.eventType) 
        self.mapPosition = point