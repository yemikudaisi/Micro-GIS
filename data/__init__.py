import utils
from datasource import DataSource
from shapefile import ShapeFileDataSource

sourceTypes = utils.enum(
    SHAPE_FILE="ZoomInTool",
    XML_FILE="ZoomOutTool")


def validateSourceType(type):
    if type not in (sourceTypes.SHAPE_FILE, sourceTypes.XML_FILE):
        raise ValueError('data source not valid')
