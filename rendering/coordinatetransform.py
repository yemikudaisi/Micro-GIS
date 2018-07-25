from geometry.point import Point
class CoordinateTransform(object):
    """
    CoordinateTransform provides methods for converting coordinate pairs
    to and from a geographical coordinate system to screen or pixel 
    coordinates given a map extent and screen size.
    """
    def __init__(self,screenSize, mapExtent):
        self.extent = mapExtent
        self.sx = (float(screenSize.GetWidth()) / mapExtent.width())
        self.sy = (float(screenSize.GetHeight()) / mapExtent.height())

    def getSreenCoord(self,point):
        """Geo coordinates to Screen coordinates"""
        x0 = (point.x - self.extent.minx) * self.sx
        y0 = (self.extent.maxy - point.y) * self.sy
        return Point(x0,y0)

    def getGeoCoord(self,point):
        """Screen coordinates to Geo coordinates"""
        x0 = self.extent.minx + point.x / self.sx
        y0 = self.extent.maxy - point.y / self.sy
        return Point(x0,y0)