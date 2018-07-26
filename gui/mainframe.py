import wx
import wx.lib.agw.aui as aui
from events import EVT_MAP_MOUSE_OVER
from gui.mappanel import MapPanel
from gui.settingspanel import SettingsPanel


class MainFrame(wx.Frame):
    __MSG_STATUS_FIELD = 0
    __COORD_STATUS_FIELD = 1
    __SCALE_LABEL_STATUS_FIELD = 2
    __SCALE_VALUE_STATUS_FIELD = 3
    __PROJ_STATUS_FIELD = 4

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

        #self.root = self.treeLayers.AddRoot('Something goes here')
        #self.treeLayers.SetPyData(self.root, ('key', 'value'))
        #os = self.treeLayers.AppendItem(self.root, 'Operating Systems')
        #self.treeLayers.Expand(self.root)

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
        self.SetMenuBar(self.buildMenu())

        mapPanel.Bind(EVT_MAP_MOUSE_OVER, self.OnMapClick)
        self.Bind(wx.EVT_CLOSE, self.OnClose)

        self.settings = [False, False, False]

    def onSettings(self, e):
        settings_dialog = SettingsPanel(self.settings, self)
        res = settings_dialog.ShowModal()
        if res == wx.ID_OK:
            self.settings = settings_dialog.GetSettings()

    
    def initComponents(self):
        tbMain = aui.AuiToolBar(self, -1, wx.DefaultPosition, wx.DefaultSize,agwStyle=aui.AUI_TB_DEFAULT_STYLE | aui.AUI_TB_OVERFLOW)
        tbMain.AddSimpleTool(31,"hello tool",wx.ArtProvider.GetBitmap(wx.ART_FILE_OPEN))
        tbMain.AddSimpleTool(31,"hello tool",wx.ArtProvider.GetBitmap(wx.ART_FILE_SAVE))
        tbMain.AddSimpleTool(31,"hello tool",wx.ArtProvider.GetBitmap(wx.ART_NEW))
        tbMain.AddSimpleTool(31,"hello tool",wx.ArtProvider.GetBitmap(wx.ART_QUESTION))
        tbMain.Realize()

        self._mgr.AddPane(tbMain, aui.AuiPaneInfo().Caption("Sample Vertical Toolbar").ToolbarPane().Top())
        self.initStatusBar()

    def initStatusBar(self):
        self.CreateStatusBar(5)
        self.GetStatusBar().SetStatusWidths([-1, 150,100,100,200])
        self.GetStatusBar().SetStatusText("Ready")
        self.GetStatusBar().SetStatusText("Scale: ", self.__SCALE_LABEL_STATUS_FIELD)

    def buildMenu(self):
        mb = wx.MenuBar()
        fileMenu = wx.Menu()
        fileMenu.Append(wx.ID_ANY, "Open")
        fileMenu.Append(wx.ID_ANY, "Exit")

        editMenu = wx.Menu()
        viewMenu = wx.Menu()
        windowMenu = wx.Menu()
        helpMenu = wx.Menu()

        mb.Append(fileMenu, "&File")
        mb.Append(editMenu, "&Edit")
        mb.Append(viewMenu, "&View")
        mb.Append(windowMenu, "&Window")
        mb.Append(helpMenu, "&Help")

        return mb

    def OnClose(self, event):
        # deinitialize the frame manager
        self._mgr.UnInit()
        event.Skip()
    
    def OnMapClick(self, event):
        # note: y represents latitude why x represent longitude
        lat = ("%.3f" % round(event.mapPosition.y, 3))
        long = ("%.3f" % round(event.mapPosition.x, 3))
        coord = "Coords: {lat},{long}".format(**locals())
        self.GetStatusBar().SetStatusText(coord, self.__COORD_STATUS_FIELD)

