from abc import abstractmethod, abstractproperty
from data import ShapeFileDataSource, XmlFileDataSource
import utils

sourceTypes = utils.enum(
    SHAPE_FILE="ZoomInTool",
    XML_FILE="ZoomOutTool")

def validateSourceType(type):
    if type not in (sourceTypes.SHAPE_FILE, sourceTypes.XML_FILE):
        raise ValueError('data source not valid')

class DataSource(object):
    def __init__(self, type, connectionString):
        validateSourceType(type)
        self.__type = type  # type: str
        self.__connectionString = connectionString  # type: str

    @abstractmethod
    def layer(self, layerName):
        """Creates a mapnik layer from the data source with given name"""
        pass

    @property
    def type(self):
        return self.__type

    @type.setter
    def type(self, value):
        self.__type = value

    @property
    def connectionString(self):
        return

    @connectionString.setter
    def connectionString(self, value):
        self.__connectionString = value
