"""
A WxWidget implementation of map canvas for mapnik 

Yemi Kudaisi (yemikudaisi@gmail.com)
yemikudaisi.github.io

"""

import wx
import mapnik

from geometry.point import Point
from events.mapmouseevent import MapMouseEvent
from rendering.coordinatetransform import CoordinateTransform
from gui.tools.zoomintool import ZoomTool

FLAG_IS_ZOOM_IN_TOOL = "isZoomInTool"
FLAG_IS_ZOOM_OUT_TOOL = "isZoomOutTool"
FLAG_IS_ZOOM_ENVELOPE_TOOL = "isZoomEnvelopeTool"
FLAG_IS_ZOOM_EXETENT_TOOL = "isZoomExtentTool"
FLAG_IS_PAN_TOOL = "isPanTool"

class MapPanel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent = parent, size=wx.Size(800,500))
        self.shapefile ="NIR.shp"
        panelSizer = wx.BoxSizer( wx.VERTICAL )
        self.mapCanvas = wx.Panel(self)
        self.toolbar = self.CreateIconToolbar()
        panelSizer.Add( self.toolbar, proportion=0, flag=wx.EXPAND )        
        panelSizer.Add( self.mapCanvas,  proportion=1, flag=wx.EXPAND )
        panelSizer.Layout()
        self.SetSizer(panelSizer)

        self.initFlags()
        self.bindEventHandlers()
    
    def initFlags(self):
        self.isFirstPaint = True
        self.isMapReady = False
        self.isToolActive = False
        self.isZoomInTool = False
        self.isZoomOutTool = False
        self.isZoomEnvelopeTool = False
        self.isZoomExtentTool = False
        self.isPanTool = False

        self.activeTool = None
    
    def bindEventHandlers(self):
        self.mapCanvas.Bind(wx.EVT_PAINT, self.onPaint)
        self.mapCanvas.Bind(wx.EVT_LEFT_DOWN, self.onLeftDown)

    def activateTool(self, flagName):
        """Activate a tools by prepending 'is' and appending 'Tool'
        to the supplied flag name and setting the instance flag to false
        """
        self.deactivateTool(self.activeTool)
        if(self.checkAttr(flagName)):        
            self.isToolActive = True
            setattr(self, flagName, True)
            self.activeTool = flagName

    def deactivateTool(self, flagName):
        """Deactivates a tools by prepending 'is' and appending 'Tool'
        to the supplied flag name and setting the instance flag to false
        """
          
        #if no tool is active see -> self.deactivateTool(self.activeTool)
        if(flagName is None):
            return      

        #toggle off the button for the active tool
        tool = getattr(self, "tb"+flagName[2:])
        self.toolbar.ToggleTool(id=tool.GetId(),toggle=False)

        #check if an instance attribute exists for the supplied flag
        if(self.checkAttr(flagName)):
            self.isToolActive = False
            #set the flag for the active tool to false
            setattr(self, flagName, False)
            self.activeTool = None
        
    def checkAttr(self, attrName):
        """ Checks if an attribute exist otherwise raise an error"""
        if not hasattr(self, attrName):
            raise AttributeError('module has no attribute '+flagName)
            return False
        return True

    def createMap(self):
        """Create mapnik object

        """
        print "createMap"

        self.map = mapnik.Map(self.mapCanvas.GetSize().GetWidth(), self.mapCanvas.GetSize().GetHeight());
        self.map.background = mapnik.Color('steelblue')
        s = mapnik.Style()
        r = mapnik.Rule()
        polygon_symbolizer = mapnik.PolygonSymbolizer()
        polygon_symbolizer.fill = mapnik.Color('#929857')
        r.symbols.append(polygon_symbolizer)

        line_symbolizer = mapnik.LineSymbolizer()
        line_symbolizer.stroke = mapnik.Color('#000000')
        line_symbolizer.stroke_width = 0.5

        r.symbols.append(line_symbolizer)
        s.rules.append(r)
        self.map.append_style('My Style',s)
        ds = mapnik.Shapefile(file='demo-data/NIR.shp')
        layer = mapnik.Layer('world')
        layer.datasource = ds
        layer.styles.append('My Style')
        self.map.layers.append(layer)
        if (self.isFirstPaint):
            self.map.zoom_all()
            self.isFirstPaint = False
        self.isMapReady = True;

    def createMapImage(self):
        """Draw map to Bitmap object"""
        print "createMapImage"
        # create a Image32 object
        image = mapnik.Image(self.mapCanvas.GetClientSize().GetWidth(), self.mapCanvas.GetClientSize().GetHeight())
        # render map to Image32 object
        mapnik.render(self.map, image)
        # load raw data from Image32 to bitmap
        self.bmp = wx.BitmapFromBufferRGBA(self.mapCanvas.GetClientSize().GetWidth(), self.mapCanvas.GetClientSize().GetHeight(), image.tostring())

    def paintMap(self):
        if(not self.isMapReady):
            self.createMap()
            self.isMapReady = True
        else:
            self.map.resize(self.mapCanvas.GetSize().GetWidth(), self.mapCanvas.GetSize().GetHeight())

        self.createMapImage()
        dc = wx.PaintDC(self.mapCanvas)
        memoryDC = wx.MemoryDC(self.bmp)
        # draw map to dc
        dc.Blit(0, 0, self.mapCanvas.GetClientSize().GetWidth(), self.mapCanvas.GetClientSize().GetHeight(), memoryDC, 0, 0)

    def CreateIconToolbar( self ) :
    
        toolbar = wx.ToolBar( self, -1 )
        
        zoomInID = wx.NewId()
        bitmap = wx.Bitmap("icons/zoom-in.png")
        self.tbZoomInTool = toolbar.AddCheckTool( zoomInID, 
                                     bitmap=bitmap)
        self.Bind(wx.EVT_TOOL, self.onZoomIn, self.tbZoomInTool )
        
        zoomOutID = wx.NewId()        
        bitmap = wx.Bitmap("icons/zoom-out.png")
        self.tbZoomOutTool = toolbar.AddCheckTool( zoomOutID, 
                                     bitmap=bitmap)
        self.Bind(wx.EVT_TOOL, self.onZoomOut, self.tbZoomOutTool)
            
        toolbar.AddSeparator()

        zoomEnvelopeID = wx.NewId()        
        bitmap = wx.Bitmap("icons/zoom-selection.png")
        self.tbZoomEnvelopeTool = toolbar.AddCheckTool( zoomOutID, 
                                     bitmap=bitmap)
        self.Bind(wx.EVT_TOOL, self.onZoomEnvelope, self.tbZoomEnvelopeTool)

        zoomExtentID = wx.NewId()        
        bitmap = wx.Bitmap("icons/zoom-region.png")
        self.tbZoomExtentTool = toolbar.AddCheckTool( zoomOutID, 
                                     bitmap=bitmap)
        self.Bind(wx.EVT_TOOL, self.onZoomExtent, self.tbZoomExtentTool)
        
        toolbar.Realize()
        
        return toolbar

    def scale_bitmap(self,bitmap, width, height):
        image = wx.ImageFromBitmap(bitmap)
        image = image.Scale(width, height, wx.IMAGE_QUALITY_HIGH)
        result = wx.BitmapFromImage(image)
        return result

    def onPaint(self, event):
        """
        Redraw the map everytime the panel is repainted
        """
        self.paintMap()

    def onLeftDown(self, event):
        print "left down"
        self.mousePosition = event.GetPosition()
        if(self.isToolActive):
            self.selectTool()

    def onMouseOver(self, event):
        print "onMouseOver"
        ctrl_pos = event.GetPosition()
        obj = event.GetEventObject()
        transform = CoordinateTransform(self.mapCanvas.GetSize(), self.map.envelope())
        print str(transform.getGeoCoord(ctrl_pos))
        event.Skip()
        wx.PostEvent(obj.GetEventHandler(), MapMouseEvent(transform.getGeoCoord(ctrl_pos)))
    
    def onZoomIn(self,event):
        """Zoom into the map's current extent"""
        self.activateTool(FLAG_IS_ZOOM_IN_TOOL)

    def onZoomOut(self,event):
        """Zoom out of the map's current extent"""
        self.activateTool(FLAG_IS_ZOOM_OUT_TOOL)

    def onZoomEnvelope(self,event):
        """Zoom out of the map's current extent"""
        self.activateTool(FLAG_IS_ZOOM_ENVELOPE_TOOL)

    def onZoomExtent(self,event):
        self.deactivateTool(self.activeTool)
        self.toolbar.ToggleTool(id=event.GetEventObject().GetId(),toggle=False)
        self.map.zoom_all()
        self.paintMap()

    def zoomIn(self):
        tool = ZoomTool(self.map)
        transform = CoordinateTransform(self.mapCanvas.GetSize(), self.map.envelope())
        tool.zoomToPoint(transform.getGeoCoord(self.mousePosition))
        self.paintMap()
    
    def zoomOut(self):
        tool = ZoomTool(self.map)
        transform = CoordinateTransform(self.mapCanvas.GetSize(), self.map.envelope())
        tool.zoomFromPoint(transform.getGeoCoord(self.mousePosition))
        self.paintMap()
 
    def selectTool(self):
        print "selectTool"
        cases = {
            FLAG_IS_ZOOM_IN_TOOL: self.zoomIn,
            FLAG_IS_ZOOM_OUT_TOOL: self.zoomOut
        }
        func = cases.get(self.activeTool, lambda: "")
        print func()



