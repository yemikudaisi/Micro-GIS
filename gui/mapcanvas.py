"""
A WxWidget implementation of map canvas for mapnik

Yemi Kudaisi (yemikudaisi@gmail.com)
yemikudaisi.github.io

"""

import wx
import mapnik

import events
import gui.maptools as toolbox
import data
from geometry import Scale

from geometry.point import Point
from events.mapmouseover import MapMouseOverEvent
from rendering.coordinatetransform import CoordinateTransform

DEFAULT_MAP_BACKGROUND = mapnik.Color('#3c3F41')
DEFAULT_FILL_COLOR = mapnik.Color('#3c3F41')
DEFAULT_LINE_COLOR = mapnik.Color('#87939A')

class MapCanvas(wx.Panel):

    def __init__(self, parent):
        wx.Panel.__init__(self, parent=parent, size=wx.Size(800, 500))

        self.shapefile = "NIR.shp"
        self.isMapReady = False
        self.isToolActive = False
        self.leftClickDown = False
        self.activeTool = None
        self.mousePosition = wx.Point()
        self.mouseDownPosition = wx.Point()
        self.mouseStartPosition = wx.Point()
        self.previousMouseDownPosition = wx.Point()
        self.drawingOverlay = wx.Overlay()
        self.wasToolDragged = False

        self.createMap()
        self.bindEventHandlers()

    def createMap(self):
        """Create map"""

        self.map = mapnik.Map(self.GetSize().GetWidth(), self.GetSize().GetHeight());
        self.map.background = DEFAULT_MAP_BACKGROUND
        """self.addStyle('default', self.defaultPolygonStyle())
        ds = data.ShapeFileDataSource(data.sourceTypes.SHAPE_FILE, 'demo-data/NIR.shp')
        nigeria = ds.layer("Nigeria")
        nigeria.styles.append('default')
        self.addLayer(nigeria)"""
        if (not self.isMapReady):
            self.map.zoom_all()
        self.isMapReady = True;
        self.dispatchEvent(events.MapReadyEvent())

    def bindEventHandlers(self):
        """Bind events to handlers"""
        self.Bind(wx.EVT_PAINT, self.onPaint)
        self.Bind(wx.EVT_LEFT_DOWN, self.onLeftDown)
        self.Bind(wx.EVT_LEFT_UP, self.onLeftUp)
        self.Bind(wx.EVT_MOTION, self.onMouseOver)

    def dispatchEvent(self, event):
        """Dispatch an event through wxPython"""
        assert isinstance (event, wx.PyEvent)
        wx.PostEvent(self, event)

    def activateTool(self, toolName):
        """Activate a tools by prepending 'is' and appending 'Tool'
        to the supplied flag name and setting the instance flag to false
        """
        toolbox.validateToolType(toolName)
        self.deactivateTool(self.activeTool)
        self.activeTool = toolName
        self.isToolActive = True
        self.dispatchEvent(events.MapToolActivatedEvent(toolName))

    def deactivateTool(self, toolName):
        """Deactivates a tools by prepending 'is' and appending 'Tool'
        to the supplied flag name and setting the instance flag to false
        """

        self.resetMousePositions()
        toolbox.validateToolType(toolName)
        if (toolName is None):
            return
        toolbox.validateToolType(toolName)
        self.isToolActive = False
        self.activeTool = toolbox.types.NONE
        self.dispatchEvent(events.MapToolDeactivatedEvent(toolName))

    def addLayer(self, layer):
        """Adds a append layer to the map layer collection"""
        assert isinstance(layer, mapnik.Layer)
        self.map.layers.append(layer)
        self.dispatchEvent(events.MapLayersChangedEvent())

    def addStyle(self, styleName, style):
        """Appends a style to the map style collection"""
        assert isinstance(style, mapnik.Style)
        self.map.append_style(styleName, style)
        self.dispatchEvent(events.MapStylesChangedEvent())

    def defaultPolygonStyle(self):
        """Returns a default style for polyshape features"""
        s = mapnik.Style()
        r = mapnik.Rule()
        polygon_symbolizer = mapnik.PolygonSymbolizer()
        polygon_symbolizer.fill = DEFAULT_FILL_COLOR
        r.symbols.append(polygon_symbolizer)
        line_symbolizer = mapnik.LineSymbolizer()
        line_symbolizer.stroke = DEFAULT_LINE_COLOR
        line_symbolizer.stroke_width = 0.5
        r.symbols.append(line_symbolizer)
        s.rules.append(r)
        return s

    def createMapImage(self):
        """Creates a wx bitmap image from mapnik rendered map"""
        image = mapnik.Image(self.GetClientSize().GetWidth(), self.GetClientSize().GetHeight())
        mapnik.render(self.map, image)
        return wx.BitmapFromBufferRGBA(self.GetClientSize().GetWidth(),
                                       self.GetClientSize().GetHeight(), image.tostring())

    def paintMap(self):
        """Paints the map on the canvas"""
        if not self.isMapReady:
            self.createMap()
        else:
            self.map.resize(self.GetSize().GetWidth(), self.GetSize().GetHeight())

        dc = wx.PaintDC(self)
        memoryDC = wx.MemoryDC(self.createMapImage())
        # draw map to dc
        dc.Blit(0, 0, self.GetClientSize().GetWidth(), self.GetClientSize().GetHeight(), memoryDC, 0, 0)


    def onPaint(self, event):
        """
        Redraw the map everytime the panel is repainted
        """
        self.paintMap()

    def onLeftDown(self, event):
        self.CaptureMouse()
        self.mouseStartPosition = event.GetPosition()
        self.leftClickDown = True
        self.mousePosition = event.GetPosition()

    def onLeftUp(self, event):
        if self.HasCapture():
            self.ReleaseMouse()
        self.leftClickDown = False
        self.mousePosition = event.GetPosition()

        if (self.wasToolDragged):
            self.selectLeftUpTool()
        else:
            self.selectLeftUpTool()

        self.resetMousePositions()

    def onMouseOver(self, event):
        self.mousePosition= event.GetPosition()
        if (self.leftClickDown):
            self.mouseDownPosition = event.GetPosition()
            self.wasToolDragged = True
            self.selectLeftDragTool()
        transform = CoordinateTransform(self.GetSize(), self.map.envelope())
        wx.PostEvent(self, MapMouseOverEvent(transform.getGeoCoord(self.mousePosition)))

    def zoomIn(self):
        if self.wasToolDragged:
            return
        tool = toolbox.ZoomTool(self.map)
        transform = CoordinateTransform(self.GetSize(), self.map.envelope())
        tool.zoomToPoint(transform.getGeoCoord(self.mousePosition))
        self.paintMap()
        self.dispatchEvent(events.MapScaleChangedEvent(Scale(self.map.scale(), self.map.scale_denominator())))

    def zoomOut(self):
        if self.wasToolDragged:
            return
        tool = toolbox.ZoomTool(self.map)
        transform = CoordinateTransform(self.GetSize(), self.map.envelope())
        tool.zoomFromPoint(transform.getGeoCoord(self.mousePosition))
        self.paintMap()
        self.dispatchEvent(events.MapScaleChangedEvent(Scale(self.map.scale(), self.map.scale_denominator())))

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

        self.paintMap()
        self.dispatchEvent(events.MapScaleChangedEvent(Scale(self.map.scale(), self.map.scale_denominator())))

    def zoomExtent(self):
        self.setTool(toolbox.types.NONE)
        self.map.zoom_all()
        self.paintMap()
        self.dispatchEvent(events.MapScaleChangedEvent(Scale(self.map.scale(), self.map.scale_denominator())))

    def zoomEnvelope(self):
        if not self.leftClickDown:
            self.drawingOverlay.Reset()
            transform = CoordinateTransform(self.GetSize(), self.map.envelope())
            tool = toolbox.ZoomTool(self.map)
            topLeft = transform.getGeoCoord(self.mouseStartPosition)
            bottomRight = transform.getGeoCoord(self.mousePosition)
            minx = topLeft.x
            maxx = bottomRight.x
            miny = topLeft.y
            maxy = bottomRight.y
            box = mapnik.Box2d(minx,miny,maxx,maxy)
            self.map.zoom_to_box(box)
            self.paintMap()
            return

        rect = wx.RectPP(self.mouseStartPosition, self.mouseDownPosition)
        # Draw the rubber-band rectangle using an overlay so it
        # will manage keeping the rectangle and the former window
        # contents separate.
        dc = wx.ClientDC(self)
        odc = wx.DCOverlay(self.drawingOverlay, dc)
        odc.Clear()

        pen = wx.Pen("red", 1)
        brush = wx.Brush(wx.Colour(192, 192, 192, 128))
        if "wxMac" in wx.PlatformInfo:
            dc.SetPen(pen)
            dc.SetBrush(brush)
            dc.DrawRectangleRect(rect)
        else:
            # use a GC on Windows (and GTK?)
            # this crashed on the Mac
            ctx = wx.GraphicsContext_Create(dc)
            ctx.SetPen(pen)
            ctx.SetBrush(brush)
            ctx.DrawRectangle(*rect)

        del odc

    def selectLeftDragTool(self):
        if (not self.isToolActive):
            return
        cases = {
            toolbox.types.PAN_TOOL: self.pan,
            toolbox.types.ZOOM_ENVELOPE_TOOL: self.zoomEnvelope
        }
        func = cases.get(self.activeTool, lambda: "")
        func()

    def selectLeftUpTool(self):
        if (not self.isToolActive):
            return
        cases = {
            toolbox.types.ZOOM_IN_TOOL: self.zoomIn,
            toolbox.types.ZOOM_OUT_TOOL: self.zoomOut,
            toolbox.types.ZOOM_ENVELOPE_TOOL: self.zoomEnvelope
        }
        func = cases.get(self.activeTool, lambda: "")
        func()

    def setTool(self, tool):
        self.activateTool(tool)

    @property
    def mapScale(self):
        return Scale(self.map.scale(), self.map.scale_denominator())

    @property
    def mapLayers(self):
        return self.map.layers

    def resetMousePositions(self):
        self.mouseStartPosition = None
        self.mousePosition = None
        self.mouseDownPosition = None
        self.previousMouseDownPosition = None
        self.wasToolDragged = False

    def openMap(self, mapString):
        """Open a map from xml string"""
        assert isinstance(mapString, str)
        mapnik.load_map_from_string(self.map, mapString)
        self.map.zoom_all()
        self.paintMap()