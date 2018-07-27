import wx
import wx.lib.newevent
import gui.maptools as toolbox

MapToolActivatedEventType, EVT_MAP_TOOL_ACTIVATED= wx.lib.newevent.NewCommandEvent()
MapToolActivatedEventType = wx.NewEventType()
EVT_MAP_TOOL_ACTIVATED = wx.PyEventBinder(MapToolActivatedEventType, 0)

class MapToolActivatedEvent(wx.PyEvent):
    eventType = MapToolActivatedEventType

    def __init__(self, toolType):
        toolbox.validateToolType(toolType)
        wx.PyEvent.__init__(self, eventType=self.eventType)
        self.__toolType = toolType

    @property
    def toolType(self):
        return self.__toolType