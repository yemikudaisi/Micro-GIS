import wx
import wx.lib.newevent
import gui.maptools as toolbox
from events import MapToolActivatedEvent


class MapToolActivatedEvent(wx.PyEvent):
    eventType = MapToolActivatedEvent

    def __init__(self, toolType):
        toolbox.validateToolType(toolType)
        wx.PyEvent.__init__(self, eventType=self.eventType)
        self.__toolType = toolType

    @property
    def type(self):
        return self.__toolTypepoint