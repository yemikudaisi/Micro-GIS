import wx
import mapnik
import gui

app = wx.App(0)

frame = gui.MainFrame(None)
app.SetTopWindow(frame)
frame.Show()
#frame.LoadMap()

app.MainLoop()