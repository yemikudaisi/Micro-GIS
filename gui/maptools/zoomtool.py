import mapnik

import geometry

"""
   Zoom tool class
"""

class ZoomTool:
    ZOOM_FACTOR = 1.2

    def __init__(self, map):
        assert isinstance(map, mapnik.Map)
        self.map = map

    def zoomBox(self, box):
        assert isinstance(box, mapnik.Box2d)
        self.map.zoom_to_box(box)
    def zoomIn(self):
        newe = self.map.envelope()
        newe.width((newe.width())/self.ZOOM_FACTOR)
        newe.height((newe.height())/self.ZOOM_FACTOR)
        self.map.zoom_to_box(newe)
    
    def zoomOut(self):
        newe = self.map.envelope()
        newe.width((newe.width())*self.ZOOM_FACTOR)
        newe.height((newe.height())*self.ZOOM_FACTOR)
        self.map.zoom_to_box(newe)

    def zoomToPoint(self, point):
        assert isinstance(point, geometry.Point)
        newe = self.map.envelope()
        newe.width((newe.width())/self.ZOOM_FACTOR)
        newe.height((newe.height())/self.ZOOM_FACTOR)
        newe.center(point.x,point.y)
        self.map.zoom_to_box(newe)
    
    def zoomFromPoint(self, point):
        assert isinstance(point, geometry.Point)
        newe = self.map.envelope()
        newe.width((newe.width())*self.ZOOM_FACTOR)
        newe.height((newe.height())*self.ZOOM_FACTOR)
        newe.center(point.x,point.y)
        self.map.zoom_to_box(newe)
    
    def addZoom(self, env):
        pass
