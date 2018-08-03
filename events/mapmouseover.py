import wx
import wx.lib.newevent


MapMouseDragEventType, EVT_MAP_MOUSE_DRAG = wx.lib.newevent.NewCommandEvent()

MapMouseDragEventType = wx.NewEventType()
EVT_MAP_MOUSE_DRAG = wx.PyEventBinder(MapMouseDragEventType, 0)


class MapMouseOverEvent(wx.PyEvent):
    eventType = MapMouseDragEventType

    def __init__(self, point):
        wx.PyEvent.__init__(self, eventType=self.eventType) 
        self.mapPosition = point