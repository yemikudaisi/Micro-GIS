
def checkAttr(self, attrName):
    """ Checks if an attribute exist otherwise raise an error"""

    if not hasattr(self, attrName):
        raise AttributeError('module has no attribute ' + attrName)
        return False
    return True


def enum(**named_values):
    # type: (object) -> object
    # type: (str) -> str
    """

    :str:
    """

    return type('Enum', (), named_values)
