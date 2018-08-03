import ntpath
import sys
import wx

def checkAttr(self, attrName):
    """ Checks if an attribute exist otherwise raise an error"""

    if not hasattr(self, attrName):
        raise AttributeError('module has no attribute ' + attrName)
        return False
    return True


def scaleBitmap(bitmap, size):
    image = wx.ImageFromBitmap(bitmap)
    image = image.Scale(size.GetWidth(), size.GetHeight(), wx.IMAGE_QUALITY_HIGH)
    result = wx.BitmapFromImage(image)
    return result

def enum(**named_values):
    # type: (object) -> object
    # type: (str) -> str
    """

    :str:
    """

    return type('Enum', (), named_values)


def accepts(*types, **kw):
    '''Function decorator. Checks decorated function's arguments are
    of the expected types.

    Parameters:
    types -- The expected types of the inputs to the decorated function.
             Must specify type for each parameter.
    kw    -- Optional specification of 'debug' level (this is the only valid
             keyword argument, no other should be given).
             debug = ( 0 | 1 | 2 )

    '''
    if not kw:
        # default level: MEDIUM
        debug = 1
    else:
        debug = kw['debug']
    try:
        def decorator(f):
            def newf(*args):
                if debug is 0:
                    return f(*args)
                assert len(args) == len(types)
                argtypes = tuple(map(type, args))
                if argtypes != types:
                    msg = info(f.__name__, types, argtypes, 0)
                    if debug is 1:
                        print >> sys.stderr, 'TypeWarning: ', msg
                    elif debug is 2:
                        raise TypeError, msg
                return f(*args)
            newf.__name__ = f.__name__
            return newf
        return decorator
    except KeyError, key:
        raise KeyError, key + "is not a valid keyword argument"
    except TypeError, msg:
        raise TypeError, msg


def returns(ret_type, **kw):
    '''Function decorator. Checks decorated function's return value
    is of the expected type.

    Parameters:
    ret_type -- The expected type of the decorated function's return value.
                Must specify type for each parameter.
    kw       -- Optional specification of 'debug' level (this is the only valid
                keyword argument, no other should be given).
                debug=(0 | 1 | 2)
    '''
    try:
        if not kw:
            # default level: MEDIUM
            debug = 1
        else:
            debug = kw['debug']
        def decorator(f):
            def newf(*args):
                result = f(*args)
                if debug is 0:
                    return result
                res_type = type(result)
                if res_type != ret_type:
                    msg = info(f.__name__, (ret_type,), (res_type,), 1)
                    if debug is 1:
                        print >> sys.stderr, 'TypeWarning: ', msg
                    elif debug is 2:
                        raise TypeError, msg
                return result
            newf.__name__ = f.__name__
            return newf
        return decorator
    except KeyError, key:
        raise KeyError, key + "is not a valid keyword argument"
    except TypeError, msg:
        raise TypeError, msg

def info(fname, expected, actual, flag):
    '''Convenience function returns nicely formatted error/warning msg.'''
    format = lambda types: ', '.join([str(t).split("'")[1] for t in types])
    expected, actual = format(expected), format(actual)
    msg = "'{}' method ".format( fname )\
          + ("accepts", "returns")[flag] + " ({}), but ".format(expected)\
          + ("was given", "result is")[flag] + " ({})".format(actual)
    return msg

class Log:
    def WriteText(self, text):
        if text[-1:] == '\n':
            text = text[:-1]
        wx.LogMessage(text)
    write = WriteText

class Gui:

    @staticmethod
    def openFileDialogPath(parent,title, wildcard):

        with wx.FileDialog(parent, title, wildcard=wildcard,
                           style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as fileDialog:

            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return ""
            return fileDialog.GetPath()

    @staticmethod
    def showMessageBoxYesNo(parent, question, caption='Yes or no?'):
        dlg = wx.MessageDialog(parent, question, caption, wx.YES_NO | wx.ICON_QUESTION)
        result = dlg.ShowModal() == wx.ID_YES
        dlg.Destroy()
        return result

    @staticmethod
    def showMessageBoxInfo(parent, message, caption='Insert program title'):
        dlg = wx.MessageDialog(parent, message, caption, wx.OK | wx.ICON_INFORMATION)
        dlg.ShowModal()
        dlg.Destroy()

    @staticmethod
    def showScrollMessageInfoText(parent, message, caption='Information !'):
        dlg = wx.ScrolledMessageDialog(parent, message, caption)
        dlg.ShowModal()

    @staticmethod
    def showMessageBoxWarn(parent, message, caption='Warning!'):
        dlg = wx.MessageDialog(parent, message, caption, wx.OK | wx.ICON_WARNING)
        dlg.ShowModal()
        dlg.Destroy()

class File:
    @staticmethod
    def getPathFileName(path):
        head, tail = ntpath.split(path)
        return tail or ntpath.basename(head)