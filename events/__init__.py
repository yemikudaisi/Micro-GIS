import wx

MapMouseOverEvent, EVT_MAP_MOUSE_OVER = wx.lib.newevent.NewCommandEvent()
MapToolActivatedEvent, EVT_MAP_TOOL_ACTIVATED= wx.lib.newevent.NewCommandEvent()
MapToolDeactivatedEvent, EVT_MAP_TOOL_DEACTIVATED= wx.lib.newevent.NewCommandEvent()

MapMouseOverEvent = wx.NewEventType()
EVT_MAP_MOUSE_OVER = wx.PyEventBinder(MapMouseOverEvent, 0)

MapToolActivatedEvent = wx.NewEventType()
EVT_MAP_TOOL_ACTIVATED = wx.PyEventBinder(MapToolActivatedEvent, 0)

MapToolDeactivatedEvent = wx.NewEventType()
EVT_MAP_TOOL_DEACTIVATED = wx.PyEventBinder(MapToolDeactivatedEvent, 0)
