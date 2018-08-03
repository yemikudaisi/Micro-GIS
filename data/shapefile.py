import os

import mapnik

import utils
from data import DataSource


class ShapeFileDataSource(DataSource):

    def __init__(self, type, connectionString):
        DataSource.__init__(self, type, connectionString)

    def layer(self, layerName = ""):
        if "" == layerName:
            layerName = utils.File.getPathFileName(self.connectionString)  # get file name from path
            layerName = os.path.splitext(layerName)[0]  # file name without extension

        ds = mapnik.Shapefile(file=self.connectionString)
        layer = mapnik.Layer(str(layerName))
        layer.datasource = ds
        return layer
