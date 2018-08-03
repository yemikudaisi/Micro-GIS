import mapnik
from canvas import MapCanvas

__ALL__ = ["maptools", "canvas"]


DEFAULT_MAP_BACKGROUND = mapnik.Color('#3c3F41')
DEFAULT_FILL_COLOR = mapnik.Color('#3c3F41')
DEFAULT_LINE_COLOR = mapnik.Color('#87939A')

DEFAULT_MAP_STYLE = "default"


def defaultPolygonStyle():
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