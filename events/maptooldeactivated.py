import wx
import wx.lib.newevent
from events import MapToolDeactivatedEvent
import gui.maptools as toolbox


class MapToolDeactivatedEvent(wx.PyEvent):
    eventType = MapToolDeactivatedEvent

    def __init__(self, toolType):
        toolbox.validateToolType(toolType)
        wx.PyEvent.__init__(self, eventType=self.eventType) 
        self.__toolType = toolType

    @property
    def type(self):
        return self.__toolType