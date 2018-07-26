import wx

class ResourceProvider:

    @staticmethod
    def GetIcon(fileName):
        return wx.Bitmap("resources/icons/"+fileName+".png")