import wx.lib.newevent
import wx

MapStylesChangedEventType, EVT_MAP_STYLES_CHANGED= wx.lib.newevent.NewCommandEvent()
MapStylesChangedEventType = wx.NewEventType()
EVT_MAP_STYLE_CHANGED = wx.PyEventBinder(MapStylesChangedEventType, 0)


class MapStylesChangedEvent(wx.PyEvent):
    eventType = MapStylesChangedEventType

    def __init__(self):
        wx.PyEvent.__init__(self, eventType=self.eventType)
