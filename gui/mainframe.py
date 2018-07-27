import wx
import wx.lib.agw.aui as aui
import events
from gui.mappanel import MapPanel
from gui.settingspanel import SettingsPanel
try:
    from agw import customtreectrl as ct
except ImportError: # if it's not there locally, try the wxPython lib.
    import wx.lib.agw.customtreectrl as ct



class MainFrame(wx.Frame):
    __MSG_STATUS_FIELD = 0
    __COORD_LABEL_STATUS_FIELD = 1
    __COORD_VALUE_STATUS_FIELD = 2
    __SCALE_LABEL_STATUS_FIELD = 3
    __SCALE_VALUE_STATUS_FIELD = 4
    __PROJ_STATUS_FIELD = 5

    def __init__(self, parent, id=-1, title="GIS Lite", pos=wx.DefaultPosition,
                 size=(800, 600), style=wx.DEFAULT_FRAME_STYLE):

        wx.Frame.__init__(self, parent, id, title, pos, size, style)

        self._mgr = aui.AuiManager()
        self._mgr.SetManagedWindow(self)
        self.mapPanel = MapPanel(self)
        self.initLayerTree()

        # add the panes to the manager
        self._mgr.AddPane(self.treeLayers, aui.AuiPaneInfo().Left().Caption("Layers"))
        self._mgr.AddPane(self.mapPanel, aui.AuiPaneInfo().CenterPane())
        self.initToolbars()
        # tell the manager to "commit" all the changes just made
        self._mgr.Update()

        self.SetMenuBar(self.buildMenu())
        self.mapPanel.canvas.Bind(events.EVT_MAP_MOUSE_OVER, self.onMapClick)
        self.mapPanel.canvas.Bind(events.EVT_MAP_SCALE_CHANGED, self.onMapScaleChanged)
        self.mapPanel.canvas.Bind(events.EVT_MAP_READY, self.onMapReady)
        self.mapPanel.canvas.Bind(events.EVT_MAP_LAYERS_CHANGED, self.onMapLayersChanged)
        self.Bind(wx.EVT_CLOSE, self.OnClose)

        self.settings = [False, False, False]

    def initLayerTree(self):
        self.treeLayers = ct.CustomTreeCtrl(self, -1, size=wx.Size(200,150), style=wx.TR_HAS_BUTTONS|wx.TR_DEFAULT_STYLE|wx.SUNKEN_BORDER)
        self.layersTreeRoot = self.treeLayers.AddRoot('Layers')
        self.treeLayers.SetPyData(self.layersTreeRoot, ('key', 'value'))
        self.treeLayers.Expand(self.layersTreeRoot)

    def onSettings(self, e):
        settings_dialog = SettingsPanel(self.settings, self)
        res = settings_dialog.ShowModal()
        if res == wx.ID_OK:
            self.settings = settings_dialog.GetSettings()

    
    def initToolbars(self):
        tbMain = aui.AuiToolBar(self, -1, wx.DefaultPosition, wx.DefaultSize,agwStyle=aui.AUI_TB_DEFAULT_STYLE | aui.AUI_TB_OVERFLOW)
        tbMain.SetToolBitmapSize(wx.Size(16, 16))
        tbMain.AddSimpleTool(wx.NewId(),"hello tool",wx.ArtProvider.GetBitmap(wx.ART_FILE_OPEN, size=wx.Size(16, 16)))
        tbMain.AddSimpleTool(wx.NewId(),"hello tool",wx.ArtProvider.GetBitmap(wx.ART_FILE_SAVE, size=wx.Size(16, 16)))
        tbMain.AddSimpleTool(wx.NewId(),"hello tool",wx.ArtProvider.GetBitmap(wx.ART_NEW, size=wx.Size(16, 16)))
        tbMain.AddSimpleTool(wx.NewId(),"hello tool",wx.ArtProvider.GetBitmap(wx.ART_QUESTION, size=wx.Size(16, 16)))
        tbMain.Realize()

        self._mgr.AddPane(tbMain, aui.AuiPaneInfo().Caption("Sample Vertical Toolbar").ToolbarPane().Top())
        self.initStatusBar()

    def initStatusBar(self):
        self.CreateStatusBar(6)
        self.GetStatusBar().SetStatusWidths([-1, 80,100,40,120,100])
        self.GetStatusBar().SetStatusText("Ready")
        self.GetStatusBar().SetStatusText("Coordinates: ", self.__COORD_LABEL_STATUS_FIELD)
        self.GetStatusBar().SetStatusText("Scale: ", self.__SCALE_LABEL_STATUS_FIELD)
        self.GetStatusBar().SetStatusText("WGS84", self.__PROJ_STATUS_FIELD)

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

    def onMapReady(self, event):
        self.GetStatusBar().SetStatusText(self.mapPanel.canvas.mapScale.representativeFraction, self.__SCALE_VALUE_STATUS_FIELD)

    def onMapClick(self, event):
        # note: y represents latitude why x represent longitude
        lat = ("%.3f" % round(event.mapPosition.y, 3))
        long = ("%.3f" % round(event.mapPosition.x, 3))
        coord = "{lat},{long}".format(**locals())
        self.GetStatusBar().SetStatusText(coord, self.__COORD_VALUE_STATUS_FIELD)

    def onMapScaleChanged(self, event):
        self.GetStatusBar().SetStatusText(event.scale.representativeFraction, self.__SCALE_VALUE_STATUS_FIELD)

    def onMapLayersChanged(self, e):
        self.updateLayerTree()

    def updateLayerTree(self):
        layers = self.mapPanel.canvas.mapLayers
        for l in layers:
            os = self.treeLayers.AppendItem(self.layersTreeRoot, l.name)
            self.treeLayers.Expand(self.layersTreeRoot)


