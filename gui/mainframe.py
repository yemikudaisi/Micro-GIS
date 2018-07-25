import wx
import wx.lib.agw.aui as aui
import mapnik
from events.mapmouseevent import EVT_MAP_CLICK
from gui.mappanel import MapPanel

class MainFrame(wx.Frame):

    def __init__(self, parent, id=-1, title="Simple GIS", pos=wx.DefaultPosition,
                 size=(800, 600), style=wx.DEFAULT_FRAME_STYLE):

        wx.Frame.__init__(self, parent, id, title, pos, size, style)

        self._mgr = aui.AuiManager()

        self._mgr.SetManagedWindow(self)

        # create several text controls
        treePanel = wx.Panel(self)
        self.treeLayers = wx.TreeCtrl(self, -1, style=wx.TR_HAS_BUTTONS|wx.TR_DEFAULT_STYLE|wx.SUNKEN_BORDER)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.treeLayers, 1, wx.EXPAND, 0)
        treePanel.SetAutoLayout(True)
        treePanel.SetSizer(sizer)
        sizer.Fit(treePanel)
        sizer.SetSizeHints(treePanel)
        treePanel.Layout()

        self.root = self.treeLayers.AddRoot('Something goes here')
        self.treeLayers.SetPyData(self.root, ('key', 'value'))
        os = self.treeLayers.AppendItem(self.root, 'Operating Systems')
        self.treeLayers.Expand(self.root)

        text2 = wx.TextCtrl(self, -1, "Pane 2 - sample text",
                            wx.DefaultPosition, wx.Size(200,150),
                            wx.NO_BORDER | wx.TE_MULTILINE)

        mapPanel = MapPanel(self)

        # add the panes to the manager
        #self._mgr.AddPane(treePanel, aui.AuiPaneInfo().Left().Caption("Layers"))
        self._mgr.AddPane(text2, aui.AuiPaneInfo().Left().Caption("Map Layers"))
        self._mgr.AddPane(mapPanel, aui.AuiPaneInfo().CenterPane())
        self.initComponents()
        # tell the manager to "commit" all the changes just made
        self._mgr.Update()


        mapPanel.Bind(EVT_MAP_CLICK, self.OnMapClick)
        self.Bind(wx.EVT_CLOSE, self.OnClose)

    
    def initComponents(self):
        tbMain = aui.AuiToolBar(self, -1, wx.DefaultPosition, wx.DefaultSize,agwStyle=aui.AUI_TB_DEFAULT_STYLE | aui.AUI_TB_OVERFLOW)
        tbMain.AddSimpleTool(31,"hello tool",wx.ArtProvider.GetBitmap(wx.ART_FILE_OPEN))
        tbMain.AddSimpleTool(31,"hello tool",wx.ArtProvider.GetBitmap(wx.ART_FILE_SAVE))
        tbMain.AddSimpleTool(31,"hello tool",wx.ArtProvider.GetBitmap(wx.ART_NEW))
        tbMain.AddSimpleTool(31,"hello tool",wx.ArtProvider.GetBitmap(wx.ART_QUESTION))
        tbMain.Realize()

        self._mgr.AddPane(tbMain, aui.AuiPaneInfo().Caption("Sample Vertical Toolbar").ToolbarPane().Top())

        self.CreateStatusBar()
        self.GetStatusBar().SetStatusText("Ready")

    def OnClose(self, event):
        # deinitialize the frame manager
        self._mgr.UnInit()
        event.Skip()
    
    def OnMapClick(self, event):
        # note: y represents latitude why x represent longitude
        self.GetStatusBar().SetStatusText("["+str(event.mapPosition.y)+","+str(event.mapPosition.x)+"]")

