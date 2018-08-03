import utils

types = utils.enum(
    NONE = None,
    ZOOM_IN_TOOL = "ZoomInTool",
    ZOOM_OUT_TOOL = "ZoomOutTool",
    ZOOM_ENVELOPE_TOOL = "ZoomEnvelopeTool",
    ZOOM_EXTENT_TOOL = "ZoomExtentTool",
    PAN_TOOL = "PanTool")

def validateToolType(type):
    if type not in (types.NONE,types.ZOOM_IN_TOOL, types.ZOOM_OUT_TOOL,types.ZOOM_ENVELOPE_TOOL,types.ZOOM_EXTENT_TOOL,types.PAN_TOOL):
        raise ValueError('map tool not valid')

import mapnik

class PanTool:
    def __init__(self, map):
        self.map = map

    def pan(self, point):
        self.map.pan(int(point.x),int(point.y))

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
        newe.width((newe.width()) / self.ZOOM_FACTOR)
        newe.height((newe.height()) / self.ZOOM_FACTOR)
        self.map.zoom_to_box(newe)

    def zoomOut(self):
        newe = self.map.envelope()
        newe.width((newe.width()) * self.ZOOM_FACTOR)
        newe.height((newe.height()) * self.ZOOM_FACTOR)
        self.map.zoom_to_box(newe)

    def zoomToPoint(self, point):
        assert isinstance(point, geometry.Point)
        newe = self.map.envelope()
        newe.width((newe.width()) / self.ZOOM_FACTOR)
        newe.height((newe.height()) / self.ZOOM_FACTOR)
        newe.center(point.x, point.y)
        self.map.zoom_to_box(newe)

    def zoomFromPoint(self, point):
        assert isinstance(point, geometry.Point)
        newe = self.map.envelope()
        newe.width((newe.width()) * self.ZOOM_FACTOR)
        newe.height((newe.height()) * self.ZOOM_FACTOR)
        newe.center(point.x, point.y)
        self.map.zoom_to_box(newe)

    def addZoom(self, env):
        pass
