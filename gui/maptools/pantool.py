__all__ = ['PanTool']

class PanTool:
    def __init__(self, map):
        self.map = map

    def pan(self, point):
        self.map.pan(int(point.x),int(point.y))
