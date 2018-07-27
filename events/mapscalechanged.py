import wx
import wx.lib.newevent

from geometry import Scale

MapScaleChangedEventType, EVT_MAP_SCALE_CHANGED= wx.lib.newevent.NewCommandEvent()
MapScaleChangedEventType = wx.NewEventType()
EVT_MAP_SCALE_CHANGED = wx.PyEventBinder(MapScaleChangedEventType, 0)


class MapScaleChangedEvent(wx.PyEvent):
    eventType = MapScaleChangedEventType

    def __init__(self, scale):
        assert isinstance(scale, Scale)
        wx.PyEvent.__init__(self, eventType=self.eventType) 
        self.__scale = scale

    @property
    def scale(self):
        return self.__scale