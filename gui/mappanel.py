"""
A WxWidget implementation of map canvas for mapnik 

Yemi Kudaisi (yemikudaisi@gmail.com)
yemikudaisi.github.io

"""

import wx
import mapnik

from geometry.point import Point
from events.mapmouseoverevent import MapMouseOverEvent
from rendering.coordinatetransform import CoordinateTransform
from gui.maptools import ZoomTool, PanTool
from resources.resourceprovider import ResourceProvider as rp

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
        self.toolbar = self.buildToolbar()
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
        self.leftClickDown = False
        self.activeTool = None

        self.resetMousePositions()
    
    def bindEventHandlers(self):
        self.mapCanvas.Bind(wx.EVT_PAINT, self.onPaint)
        self.mapCanvas.Bind(wx.EVT_LEFT_DOWN, self.onLeftDown)
        self.mapCanvas.Bind(wx.EVT_LEFT_UP, self.onLeftUp)
        self.mapCanvas.Bind(wx.EVT_MOTION, self.onMouseOver)

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

    def buildToolbar( self ) :
    
        toolbar = wx.ToolBar( self, -1 )
        
        zoomInID = wx.NewId()
        self.tbZoomInTool = toolbar.AddCheckTool( zoomInID, 
                                     bitmap=rp.GetIcon("zoom-in"))
        self.Bind(wx.EVT_TOOL, self.onZoomInTool, self.tbZoomInTool )
        
        zoomOutID = wx.NewId()
        self.tbZoomOutTool = toolbar.AddCheckTool( zoomOutID, 
                                     bitmap=rp.GetIcon("zoom-out"))
        self.Bind(wx.EVT_TOOL, self.onZoomOutTool, self.tbZoomOutTool)
            
        toolbar.AddSeparator()

        panID = wx.NewId()
        self.tbPanTool = toolbar.AddCheckTool( panID, 
                                     bitmap=rp.GetIcon("pan"))
        self.Bind(wx.EVT_TOOL, self.onPanTool, self.tbPanTool)

        toolbar.AddSeparator()

        zoomEnvelopeID = wx.NewId()
        self.tbZoomEnvelopeTool = toolbar.AddCheckTool( zoomEnvelopeID, 
                                     bitmap=rp.GetIcon("zoom-selection"))
        self.Bind(wx.EVT_TOOL, self.onZoomEnvelopeTool, self.tbZoomEnvelopeTool)

        zoomExtentID = wx.NewId()
        self.tbZoomExtentTool = toolbar.AddCheckTool( zoomExtentID, 
                                     bitmap=rp.GetIcon("zoom-region"))
        self.Bind(wx.EVT_TOOL, self.onZoomExtentTool, self.tbZoomExtentTool)
        
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
        print "leftisdown"
        self.leftClickDown= True
        self.mousePosition = event.GetPosition()

    def onLeftUp(self, event):
        print "leftisup"
        self.leftClickDown = False
        self.mousePosition = event.GetPosition()
        self.selectTool()

    def resetMousePositions(self):
        self.mousePosition = None
        self.mouseDownPosition = None
        self.previousMouseDownPosition = None
    

    def onMouseOver(self, event):
        self.mouseDownPosition = event.GetPosition()
        if(self.leftClickDown):
            print "dragging"
            self.selectTool()
        transform = CoordinateTransform(self.mapCanvas.GetSize(), self.map.envelope())
        wx.PostEvent(self, MapMouseOverEvent(transform.getGeoCoord(self.mouseDownPosition)))
    
    def onZoomInTool(self,event):
        self.activateTool(FLAG_IS_ZOOM_IN_TOOL)

    def onZoomOutTool(self,event):
        self.activateTool(FLAG_IS_ZOOM_OUT_TOOL)
    
    def onPanTool(self,event):
        self.activateTool(FLAG_IS_PAN_TOOL)

    def onZoomEnvelopeTool(self,event):
        self.activateTool(FLAG_IS_ZOOM_ENVELOPE_TOOL)

    def onZoomExtentTool(self,event):
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
    
    def pan(self):
        tool = PanTool(self.map)
        transform = CoordinateTransform(self.mapCanvas.GetSize(), self.map.envelope())
        if(self.leftClickDown):
            print self.previousMouseDownPosition 
            if(self.previousMouseDownPosition is None):
                self.previousMouseDownPosition = self.mouseDownPosition
                return

            oldCenter = self.map.envelope().center()
            diff = self.previousMouseDownPosition - self.mouseDownPosition

            print str(oldCenter)
            print str(diff)
            newCenter = mapnik.Coord(oldCenter.x + diff.x, oldCenter.y + diff.y)
            tool.pan(newCenter)
            print "drag pan"
        else:
            tool.pan(self.mousePosition)
            self.resetMousePositions()

        self.paintMap()
 
    def selectTool(self):
        if(not self.isToolActive):
            return
        cases = {
            FLAG_IS_ZOOM_IN_TOOL: self.zoomIn,
            FLAG_IS_ZOOM_OUT_TOOL: self.zoomOut,
            FLAG_IS_PAN_TOOL : self.pan
        }
        func = cases.get(self.activeTool, lambda: "")
        print func()



