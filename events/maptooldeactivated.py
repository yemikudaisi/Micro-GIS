import wx
import wx.lib.newevent

from mapping.maptools import validateToolType

MapToolDeactivatedEventType, EVT_MAP_TOOL_DEACTIVATED= wx.lib.newevent.NewCommandEvent()

MapToolDeactivatedEventType = wx.NewEventType()
EVT_MAP_TOOL_DEACTIVATED = wx.PyEventBinder(MapToolDeactivatedEventType, 0)

class MapToolDeactivatedEvent(wx.PyEvent):
    eventType = MapToolDeactivatedEventType

    def __init__(self, toolType):
        validateToolType(toolType)
        wx.PyEvent.__init__(self, eventType=self.eventType) 
        self.__toolType = toolType

    @property
    def toolType(self):
        return self.__toolType