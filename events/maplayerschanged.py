import wx.lib.newevent
import wx

MapLayersChangedEventType, EVT_MAP_LAYERS_CHANGED= wx.lib.newevent.NewCommandEvent()
MapLayersChangedEventType = wx.NewEventType()
EVT_MAP_LAYERS_CHANGED = wx.PyEventBinder(MapLayersChangedEventType, 0)


class MapLayersChangedEvent(wx.PyEvent):
    eventType = MapLayersChangedEventType

    def __init__(self):
        wx.PyEvent.__init__(self, eventType=self.eventType)
        pass