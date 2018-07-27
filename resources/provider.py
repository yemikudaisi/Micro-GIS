import wx
import utils

class Provider:

    @staticmethod
    def GetIcon(fileName, size=None):
        if size is not None:
            assert isinstance(size, wx.Size)
            return utils.scaleBitmap(wx.Bitmap("resources/icons/" + fileName + ".png"), size)
        return wx.Bitmap("resources/icons/"+fileName+".png")