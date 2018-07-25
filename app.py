import wx
import mapnik
from gui.mainframe import MainFrame

app = wx.App(0)

frame = MainFrame(None)
app.SetTopWindow(frame)
frame.Show()
#frame.LoadMap()

app.MainLoop()