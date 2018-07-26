class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y
    
    def x(self):
        return x

    def y(self):
        return y

    @staticmethod
    def fromMapnikCoord(coord):
        return Point(coord.x, coord.y)

    @staticmethod
    def fromWxPoint(size):
        return Point(size.x, size.y)
    
    def __str__(self):
        return "Point(x=" + str(self.x) + ", y=" + str(self.y)+")"

    def __add__(self, other):
        return Point((self.x + other.x),(self.y + other.y))

    def __sub__(self, other):
        return Point((self.x - other.x),(self.y - other.y))