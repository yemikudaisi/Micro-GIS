import wx
import wx.lib.newevent

from events import MapMouseOverEvent


class MapMouseOverEvent(wx.PyEvent):
    eventType = MapMouseOverEvent
    def __init__(self, point):
        wx.PyEvent.__init__(self, eventType=self.eventType) 
        self.mapPosition = point