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
import gui.maptools as toolbox
import utils
import data

class MapCanvas(wx.Panel):

    DEFAULT_MAP_BACKGROUND = mapnik.Color('steelblue')
    def __init__(self, parent):
        wx.Panel.__init__(self, parent=parent, size=wx.Size(800, 500))

        self.shapefile = "NIR.shp"
        self.isFirstPaint = True
        self.isMapReady = False
        self.isToolActive = False
        self.leftClickDown = False
        self.activeTool = None
        self.mousePosition = wx.Point()
        self.mouseDownPosition = wx.Point()
        self.previousMouseDownPosition = wx.Point()
        self.wasToolDragged = False

        self.bindEventHandlers()


    def bindEventHandlers(self):
        """Bind events to handlers"""
        self.Bind(wx.EVT_PAINT, self.onPaint)
        self.Bind(wx.EVT_LEFT_DOWN, self.onLeftDown)
        self.Bind(wx.EVT_LEFT_UP, self.onLeftUp)
        self.Bind(wx.EVT_MOTION, self.onMouseOver)

    def activateTool(self, toolName):
        """Activate a tools by prepending 'is' and appending 'Tool'
        to the supplied flag name and setting the instance flag to false
        """
        self.activeTool = toolNameName
        self.isToolActive = True

    def deactivateTool(self, flagName):
        """Deactivates a tools by prepending 'is' and appending 'Tool'
        to the supplied flag name and setting the instance flag to false
        """

        # if no tool is active see -> self.deactivateTool(self.activeTool)
        if (flagName is None):
            return

        # check if an instance attribute exists for the supplied flag
        if (utils.checkAttr(flagName)):
            self.isToolActive = False
            # set the flag for the active tool to false
            setattr(self, flagName, False)
            self.activeTool = None

    def createMap(self):
        """Create map"""

        self.map = mapnik.Map(self.GetSize().GetWidth(), self.GetSize().GetHeight());
        self.map.background = self.DEFAULT_MAP_BACKGROUND
        self.addStyle('My Style', self.defaultPolygonStyle())
        ds = data.ShapeFileDataSource(data.sourceTypes.SHAPE_FILE,'demo-data/NIR.shp')
        self.addLayer(ds.layer('Nigeria'))
        if (not self.isMapReady):
            self.map.zoom_all()
        self.isMapReady = True;

    def addLayer(self, layer):
        self.map.layers.append(layer)

    def addStyle(self, styleName, style):
        self.map.append_style(styleName, style)

    def defaultPolygonStyle(self):
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
        return s

    def createMapImage(self):
        """Draw map to Bitmap object"""
        # create a Image32 object
        image = mapnik.Image(self.GetClientSize().GetWidth(), self.GetClientSize().GetHeight())
        # render map to Image32 object
        mapnik.render(self.map, image)
        # load raw data from Image32 to bitmap
        self.bmp = wx.BitmapFromBufferRGBA(self.GetClientSize().GetWidth(),
                                           self.GetClientSize().GetHeight(), image.tostring())

    def updateMap(self):
        if (not self.isMapReady):
            self.createMap()
            self.isMapReady = True
        else:
            self.map.resize(self.GetSize().GetWidth(), self.GetSize().GetHeight())

        self.createMapImage()
        dc = wx.PaintDC(self)
        memoryDC = wx.MemoryDC(self.bmp)
        # draw map to dc
        dc.Blit(0, 0, self.GetClientSize().GetWidth(), self.GetClientSize().GetHeight(), memoryDC,
                0, 0)


    def scale_bitmap(self, bitmap, width, height):
        image = wx.ImageFromBitmap(bitmap)
        image = image.Scale(width, height, wx.IMAGE_QUALITY_HIGH)
        result = wx.BitmapFromImage(image)
        return result

    def onPaint(self, event):
        """
        Redraw the map everytime the panel is repainted
        """
        self.updateMap()

    def onLeftDown(self, event):
        self.leftClickDown = True
        self.mousePosition = event.GetPosition()

    def onLeftUp(self, event):
        self.leftClickDown = False
        self.mousePosition = event.GetPosition()

        if (self.wasToolDragged):
            pass
        else:
            self.selectTool()

        self.resetMousePositions()

    def resetMousePositions(self):
        self.mousePosition = None
        self.mouseDownPosition = None
        self.previousMouseDownPosition = None
        self.wasToolDragged = False

    def onMouseOver(self, event):
        self.mouseDownPosition = event.GetPosition()
        if (self.leftClickDown):
            self.wasToolDragged = True
            self.selectTool()
        transform = CoordinateTransform(self.GetSize(), self.map.envelope())
        wx.PostEvent(self, MapMouseOverEvent(transform.getGeoCoord(self.mouseDownPosition)))

    def onZoomInTool(self, event):
        self.activateTool(maptools.FLAG_IS_ZOOM_IN_TOOL)

    def onZoomOutTool(self, event):
        self.activateTool(FLAG_IS_ZOOM_OUT_TOOL)

    def onPanTool(self, event):
        self.activateTool(toolbox.FLAG_IS_PAN_TOOL)

    def onZoomEnvelopeTool(self, event):
        self.activateTool(FLAG_IS_ZOOM_ENVELOPE_TOOL)

    def onZoomExtentTool(self, event):
        self.deactivateTool(self.activeTool)
        self.toolbar.ToggleTool(id=event.GetEventObject().GetId(), toggle=False)
        self.map.zoom_all()
        self.updateMap()

    def zoomIn(self):
        tool = ZoomTool(self.map)
        transform = CoordinateTransform(self.GetSize(), self.map.envelope())
        tool.zoomToPoint(transform.getGeoCoord(self.mousePosition))
        self.updateMap()

    def zoomOut(self):
        tool = toolbox.ZoomTool(self.map)
        transform = CoordinateTransform(self.GetSize(), self.map.envelope())
        tool.zoomFromPoint(transform.getGeoCoord(self.mousePosition))
        self.updateMap()

    def pan(self):
        tool = toolbox.PanTool(self.map)
        transform = CoordinateTransform(self.GetSize(), self.map.envelope())
        if (self.leftClickDown):
            if (self.previousMouseDownPosition is None):
                self.previousMouseDownPosition = self.mouseDownPosition
                return

            oldCenter = self.map.envelope().center()
            screenDiff = self.mouseDownPosition - self.previousMouseDownPosition
            oldScreenCenter = transform.getSreenCoord(Point.fromMapnikCoord(oldCenter))
            newScreenCenter = oldScreenCenter - Point.fromWxPoint(screenDiff)  # subtracted to enable inverse control
            # todo: add map settings for inverse control
            tool.pan(newScreenCenter)
            self.previousMouseDownPosition = self.mouseDownPosition
        else:
            tool.pan(self.mousePosition)

        self.updateMap()

    def selectTool(self):
        # todo: Toggle tool availability if previously enabled/disabled and clicked (inline with the tools toggle button)
        if (not self.isToolActive):
            return
        cases = {
            toolbox.ZOOM_IN_TOOL: self.zoomIn,
            toolbox.ZOOM_OUT_TOOL: self.zoomOut,
            toolbox.PAN_TOOL: self.pan
        }
        func = cases.get(self.activeTool, lambda: "")
        func()

    def setTool(self, tool):
        self.activateTool()



