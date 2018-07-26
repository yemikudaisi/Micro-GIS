import wx
import wx.lib.newevent

MapMouseOverEvent, EVT_MAP_MOUSE_OVER = wx.lib.newevent.NewCommandEvent()

MapMouseOverEvent = wx.NewEventType()
EVT_MAP_MOUSE_OVER = wx.PyEventBinder(MapMouseOverEvent, 0)

class MapMouseOverEvent(wx.PyEvent):
    eventType = MapMouseOverEvent
    def __init__(self, point):
        wx.PyEvent.__init__(self, eventType=self.eventType) 
        self.mapPosition = point