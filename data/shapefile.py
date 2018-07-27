import mapnik

from data import DataSource


class ShapeFileDataSource(DataSource):

    def __init__(self, type, connectionString):
        DataSource.__init__(self, type, connectionString)

    def layer(self, layerName):
        ds = mapnik.Shapefile(file=self.connectionString)
        layer = mapnik.Layer(layerName)
        layer.datasource = ds
        return layer
