import wx
import wx.lib.newevent

MapClickEvent, EVT_MAP_CLICK = wx.lib.newevent.NewCommandEvent()

MapClickEvent = wx.NewEventType()
EVT_MAP_CLICK = wx.PyEventBinder(MapClickEvent, 0)

class MapMouseEvent(wx.PyEvent):
    eventType = MapClickEvent
    def __init__(self, point):
        wx.PyEvent.__init__(self, eventType=self.eventType) 
        self.mapPosition = point