"""
A WxWidget implementation of map canvas for mapnik 

Yemi Kudaisi (yemikudaisi@gmail.com)
yemikudaisi.github.io

"""

import wx
from gui.mapcanvas import MapCanvas
import gui.maptools as toolbox
import events
from resources.provider import Provider as rp


class MapPanel(wx.Panel):

    def __init__(self, parent):
        wx.Panel.__init__(self, parent = parent, size=wx.Size(800,500))
        self.shapefile ="NIR.shp"
        panelSizer = wx.BoxSizer( wx.VERTICAL )
        self.canvas = MapCanvas(self)
        self.toolbar = self.buildToolbar()
        panelSizer.Add( self.toolbar, proportion=0, flag=wx.EXPAND )        
        panelSizer.Add( self.canvas,  proportion=1, flag=wx.EXPAND )
        panelSizer.Layout()
        self.SetSizer(panelSizer)
        self.canvas.Bind(events.EVT_MAP_TOOL_ACTIVATED, self.onActivateTool)
        self.canvas.Bind(events.EVT_MAP_TOOL_DEACTIVATED, self.onDeactivateTool)

    def onActivateTool(self, e):
        """Activate a tools by prepending 'is' and appending 'Tool'
        to the supplied flag name and setting the instance flag to false
        """
        pass

    def onDeactivateTool(self, event):
        """Deactivates a tools by prepending 'is' and appending 'Tool'
        to the supplied flag name and setting the instance flag to false
        """

        if(event.toolType is None):
            return      

        self.toggleOffActiveToolButton(event.toolType)

    def toggleOffActiveToolButton(self, toolType):
        tool = getattr(self, "tb" + toolType)
        self.toolbar.ToggleTool(id=tool.GetId(), toggle=False)

    def buildToolbar( self ) :
    
        toolbar = wx.ToolBar( self, -1 )
        
        zoomInID = wx.NewId()
        self.tbZoomInTool = toolbar.AddCheckTool( zoomInID, 
                                     bitmap=rp.GetIcon("zoom-in", wx.Size(16,16)))
        self.Bind(wx.EVT_TOOL, self.onZoomInTool, self.tbZoomInTool )
        
        zoomOutID = wx.NewId()
        self.tbZoomOutTool = toolbar.AddCheckTool( zoomOutID, 
                                     bitmap=rp.GetIcon("zoom-out", wx.Size(16,16)))
        self.Bind(wx.EVT_TOOL, self.onZoomOutTool, self.tbZoomOutTool)
            
        toolbar.AddSeparator()

        panID = wx.NewId()
        self.tbPanTool = toolbar.AddCheckTool( panID, 
                                     bitmap=rp.GetIcon("pan", wx.Size(16,16)))
        self.Bind(wx.EVT_TOOL, self.onPanTool, self.tbPanTool)

        toolbar.AddSeparator()

        zoomEnvelopeID = wx.NewId()
        self.tbZoomEnvelopeTool = toolbar.AddCheckTool( zoomEnvelopeID, 
                                     bitmap=rp.GetIcon("zoom-selection", wx.Size(16,16)))
        self.Bind(wx.EVT_TOOL, self.onZoomEnvelopeTool, self.tbZoomEnvelopeTool)

        zoomExtentID = wx.NewId()
        self.tbZoomExtentTool = toolbar.AddSimpleTool( zoomExtentID,
                                     bitmap=rp.GetIcon("zoom-region", wx.Size(16,16)))
        self.Bind(wx.EVT_TOOL, self.onZoomExtentTool, self.tbZoomExtentTool)
        
        toolbar.Realize()
        
        return toolbar

    def onZoomInTool(self,event):
        if self.canvas.activeTool == toolbox.types.ZOOM_IN_TOOL:
            self.canvas.setTool(toolbox.types.NONE)
            return

        self.canvas.setTool(toolbox.types.ZOOM_IN_TOOL)

    def onZoomOutTool(self,event):
        if self.canvas.activeTool == toolbox.types.ZOOM_OUT_TOOL:
            self.canvas.setTool(toolbox.types.NONE)
            return
        self.canvas.setTool(toolbox.types.ZOOM_OUT_TOOL)

    def onPanTool(self,event):
        if self.canvas.activeTool == toolbox.types.PAN_TOOL:
            self.canvas.setTool(toolbox.types.NONE)
            return
        self.canvas.activateTool(toolbox.types.PAN_TOOL)

    def onZoomEnvelopeTool(self,event):
        self.canvas.activateTool(toolbox.types.ZOOM_ENVELOPE_TOOL)

    def onZoomExtentTool(self,event):
        self.canvas.zoomExtent()




