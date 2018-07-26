from data import DataSource
import mapnik

class ShapeFileDataSource(DataSource):

    def __init__(self, type, connectionString):
        DataSource.__init__(self, type, connectionString)

    @property
    def layer(self, layerName):
        # demo-data/NIR.shp
        ds = mapnik.Shapefile(file=super(ShapeFileDataSource, self).connectionString)
        layer = mapnik.Layer(layerName)
        layer.datasource = ds
        return layer
