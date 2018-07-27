from abc import abstractmethod, abstractproperty

import data


class DataSource(object):
    def __init__(self, type, connectionString):
        data.validateSourceType(type)
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
        return self.__connectionString

    @connectionString.setter
    def connectionString(self, value):
        self.__connectionString = value
