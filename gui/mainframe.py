import wx
import wx.lib.agw.aui as aui

import mapnik

from gui.settingspanel import SettingsPanel
from gui.mapcanvas import MapCanvas
import gui.maptools as toolbox
import events
from resources.provider import Provider as rp

try:
    from agw import customtreectrl as ct
except ImportError:  # if it's not there locally, try the wxPython lib.
    import wx.lib.agw.customtreectrl as ct

    MSG_STATUS_FIELD = 0
    COORD_LABEL_STATUS_FIELD = 1
    COORD_VALUE_STATUS_FIELD = 2
    SCALE_LABEL_STATUS_FIELD = 3
    SCALE_VALUE_STATUS_FIELD = 4
    PROJ_STATUS_FIELD = 5

    ID_zoomInTool = wx.NewId()
    ID_zoomOutTool = wx.NewId()
    ID_panTool = wx.NewId()
    ID_zoomEnvelopeTool = wx.NewId()
    ID_zoomExtentTool = wx.NewId()


class MainFrame(wx.Frame):

    def __init__(self, parent, id=-1, title="GIS Lite", pos=wx.DefaultPosition,
                 size=(800, 600), style=wx.DEFAULT_FRAME_STYLE):

        wx.Frame.__init__(self, parent, id, title, pos, size, style)

        self._mgr = aui.AuiManager()
        self._mgr.SetManagedWindow(self)
        self.initLayerTree()
        self.canvas = MapCanvas(self)

        self.initToolbars()
        self.initStatusBar()
        self.SetMenuBar(self.buildMenu())
        self.initPanes()
        self.activeToolBarItem = None
        # tell the manager to "commit" all the changes just made
        self._mgr.Update()

        self.canvas.Bind(events.EVT_MAP_MOUSE_OVER, self.onMapClick)
        self.canvas.Bind(events.EVT_MAP_SCALE_CHANGED, self.onMapScaleChanged)
        self.canvas.Bind(events.EVT_MAP_READY, self.onMapReady)
        self.canvas.Bind(events.EVT_MAP_LAYERS_CHANGED, self.onMapLayersChanged)

        self.canvas.Bind(events.EVT_MAP_TOOL_ACTIVATED, self.onMapToolActivated)
        self.canvas.Bind(events.EVT_MAP_TOOL_DEACTIVATED, self.onMapToolDeactivate)
        self.Bind(wx.EVT_CLOSE, self.OnClose)

        self.settings = [False, False, False]

    def onMapToolActivated(self, e):
        """Handles map event when a tool is activated"""
        pass

    def onMapToolDeactivate(self, event):
        """Handles map event when a tool is deactivated"""

        if event.toolType is None:
            return

    def toggleOffActiveToolButton(self, toolType):
        if toolbox == toolbox.types.ZOOM_IN_TOOL:
            tool = self.tbMap.GetToolToggled(ID_zoomInTool)
        if toolbox == toolbox.types.ZOOM_OUT_TOOL:
            pass
        if toolbox == toolbox.types.ZOOM_ENVELOPE_TOOL:
            pass
        if toolbox == toolbox.types.ZOOM_EXTENT_TOOL:
            pass
        if toolbox == toolbox.types.PAN_TOOL:
            pass

    def initLayerTree(self):
        self.treeLayers = ct.CustomTreeCtrl(self, -1, size=wx.Size(200, 150),
                                            style=wx.TR_HAS_BUTTONS | wx.TR_DEFAULT_STYLE | wx.SUNKEN_BORDER)
        self.layersTreeRoot = self.treeLayers.AddRoot('Layers')
        self.treeLayers.SetPyData(self.layersTreeRoot, ('key', 'value'))
        self.treeLayers.Expand(self.layersTreeRoot)

    def onSettings(self, e):
        settings_dialog = SettingsPanel(self.settings, self)
        res = settings_dialog.ShowModal()
        if res == wx.ID_OK:
            self.settings = settings_dialog.GetSettings()

    def initPanes(self):
        # add the panes to the manager
        self._mgr.AddPane(self.treeLayers, aui.AuiPaneInfo().Left().Caption("Layers"))
        self._mgr.AddPane(self.canvas, aui.AuiPaneInfo().CenterPane())

    def initToolbars(self):
        tbMain = aui.AuiToolBar(self, -1, wx.DefaultPosition, wx.DefaultSize,
                                agwStyle=aui.AUI_TB_DEFAULT_STYLE | aui.AUI_TB_OVERFLOW)
        tbMain.SetToolBitmapSize(wx.Size(16, 16))

        tbMain.AddSimpleTool(wx.ID_NEW, "hello tool", wx.ArtProvider.GetBitmap(wx.ART_NEW, size=wx.Size(16, 16)))
        tbMain.AddSimpleTool(wx.ID_OPEN, "hello tool", wx.ArtProvider.GetBitmap(wx.ART_FILE_OPEN, size=wx.Size(16, 16)))
        tbMain.AddSimpleTool(wx.ID_SAVE, "hello tool", wx.ArtProvider.GetBitmap(wx.ART_FILE_SAVE, size=wx.Size(16, 16)))

        self.Bind(wx.EVT_TOOL, self.onMapOpen, id=wx.ID_OPEN)
        self.Bind(wx.EVT_TOOL, self.onMapSave, id=wx.ID_SAVE)
        self.Bind(wx.EVT_TOOL, self.onExit, id=wx.ID_EXIT)

        tbMain.Realize()

        self.tbMap = aui.AuiToolBar(self, -1, wx.DefaultPosition, wx.DefaultSize,
                                    agwStyle=aui.AUI_TB_DEFAULT_STYLE | aui.AUI_TB_OVERFLOW)
        self.tbMap.SetToolBitmapSize(wx.Size(16, 16))
        self.tbMap.AddToggleTool(ID_zoomInTool, rp.GetIcon("zoom-in", wx.Size(16, 16)),
                                 rp.GetIcon("zoom-in", wx.Size(16, 16)),
                                 short_help_string="Zoom In tool")
        self.tbMap.AddToggleTool(ID_zoomOutTool, rp.GetIcon("zoom-out", wx.Size(16, 16)),
                                 rp.GetIcon("zoom-out", wx.Size(16, 16)),
                                 short_help_string="Zoom Out tool")
        self.tbMap.AddSeparator()
        self.tbMap.AddToggleTool(ID_panTool, rp.GetIcon("pan", wx.Size(16, 16)), rp.GetIcon("pan", wx.Size(16, 16)),
                                 short_help_string="Pan tool tool")
        self.tbMap.AddToggleTool(ID_zoomEnvelopeTool, rp.GetIcon("zoom-selection", wx.Size(16, 16)),
                                 rp.GetIcon("zoom-selection", wx.Size(16, 16)),
                                 short_help_string="Zoom to envelope tool")
        self.tbMap.AddSimpleTool(ID_zoomExtentTool, rp.GetIcon("zoom-region", wx.Size(16, 16)),
                                 rp.GetIcon("zoom-region", wx.Size(16, 16)), short_help_string="Zoom to extent tool")

        self.Bind(wx.EVT_TOOL, self.onZoomInTool, id=ID_zoomInTool)
        self.Bind(wx.EVT_TOOL, self.onZoomOutTool, id=ID_zoomOutTool)
        self.Bind(wx.EVT_TOOL, self.onPanTool, id=ID_panTool)
        self.Bind(wx.EVT_TOOL, self.onZoomEnvelopeTool, id=ID_zoomEnvelopeTool)
        self.Bind(wx.EVT_TOOL, self.onZoomExtentTool, id=ID_zoomExtentTool)

        self.tbMap.Realize()

        self._mgr.AddPane(tbMain, aui.AuiPaneInfo().Name("tbMain").Caption("Edit Toolbar").
                          ToolbarPane().Top().Row(1))
        self._mgr.AddPane(self.tbMap, aui.AuiPaneInfo().Name("tbMap").Caption("Map Toolbar").
                          ToolbarPane().Top().Row(1).Position(1))

    def initStatusBar(self):
        self.CreateStatusBar(6)
        self.GetStatusBar().SetStatusWidths([-1, 80, 100, 40, 120, 100])
        self.GetStatusBar().SetStatusText("Ready")
        self.GetStatusBar().SetStatusText("Coordinates: ", COORD_LABEL_STATUS_FIELD)
        self.GetStatusBar().SetStatusText("Scale: ", SCALE_LABEL_STATUS_FIELD)
        self.GetStatusBar().SetStatusText("WGS84", PROJ_STATUS_FIELD)

    def buildMenu(self):
        mb = wx.MenuBar()
        fileMenu = wx.Menu()
        fileMenu.Append(wx.ID_OPEN, "Open")
        fileMenu.Append(wx.ID_SAVE, "Save Map")
        fileMenu.Append(wx.ID_EXIT, "Exit")

        self.Bind(wx.EVT_MENU, self.onMapOpen, id=wx.ID_OPEN)
        self.Bind(wx.EVT_MENU, self.onMapSave, id=wx.ID_SAVE)
        self.Bind(wx.EVT_MENU, self.onExit, id=wx.ID_EXIT)

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
        self.GetStatusBar().SetStatusText(self.canvas.mapScale.representativeFraction, SCALE_VALUE_STATUS_FIELD)

    def onMapClick(self, event):
        # note: y represents latitude why x represent longitude
        lat = ("%.3f" % round(event.mapPosition.y, 3))
        long = ("%.3f" % round(event.mapPosition.x, 3))
        coord = "{lat},{long}".format(**locals())
        self.GetStatusBar().SetStatusText(coord, COORD_VALUE_STATUS_FIELD)

    def onMapScaleChanged(self, event):
        self.GetStatusBar().SetStatusText(event.scale.representativeFraction, SCALE_VALUE_STATUS_FIELD)

    def onMapLayersChanged(self, e):
        self.updateLayerTree()

    def updateLayerTree(self):
        layers = self.canvas.mapLayers
        for l in layers:
            os = self.treeLayers.AppendItem(self.layersTreeRoot, l.name)
            self.treeLayers.Expand(self.layersTreeRoot)

    def onZoomInTool(self, event):

        if self.canvas.activeTool == toolbox.types.ZOOM_IN_TOOL:
            self.canvas.setTool(toolbox.types.NONE)
            return

        self.canvas.setTool(toolbox.types.ZOOM_IN_TOOL)
        self.activateToolBarItem(ID_zoomInTool)

    def onZoomOutTool(self, event):
        if self.canvas.activeTool == toolbox.types.ZOOM_OUT_TOOL:
            self.canvas.setTool(toolbox.types.NONE)
            return
        self.canvas.setTool(toolbox.types.ZOOM_OUT_TOOL)
        self.activateToolBarItem(ID_zoomOutTool)

    def onPanTool(self, event):
        if self.canvas.activeTool == toolbox.types.PAN_TOOL:
            self.canvas.setTool(toolbox.types.NONE)
            return
        self.canvas.activateTool(toolbox.types.PAN_TOOL)
        self.activateToolBarItem(ID_panTool)

    def onZoomEnvelopeTool(self, event):
        self.canvas.activateTool(toolbox.types.ZOOM_ENVELOPE_TOOL)
        self.activateToolBarItem(ID_zoomEnvelopeTool)

    def onZoomExtentTool(self, event):
        self.canvas.zoomExtent()

    def activateToolBarItem(self, id):
        self.deactivateToolBarItem()
        self.activeToolBarItem = self.tbMap.FindTool(id)
        self.activeToolBarItem.SetState(aui.AUI_BUTTON_STATE_CHECKED)

    def deactivateToolBarItem(self):
        if self.activeToolBarItem:
            self.activeToolBarItem.SetState(aui.AUI_BUTTON_STATE_NORMAL)
            self.activeToolBarItem = None

    def onMapOpen(self, event):
        self.contentNotSaved = False  # todo: Implement save dialog for open and exit
        if self.contentNotSaved:
            if wx.MessageBox("Current content has not been saved! Proceed?", "Please confirm",
                             wx.ICON_QUESTION | wx.YES_NO, self) == wx.NO:
                return

            # otherwise ask the user what new file to open
        with wx.FileDialog(self, "Save Map file", wildcard="xml files (*.xml)|*.xml",
                           style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as fileDialog:

            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return
            pathname = fileDialog.GetPath()

            try:
                with open(pathname, 'r') as file:
                    data = file.read()
                    print data
                    self.canvas.openMap(data)

            except IOError:
                wx.LogError("Cannot open file '%s'." % newfile)

    def onMapSave(self, event):
        with wx.FileDialog(self, "Save Map file", wildcard="xml files (*.xml)|*.xml",
                           style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT) as fileDialog:

            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return

            pathname = fileDialog.GetPath()

            try:
                mapnik.save_map(self.canvas.map, str(pathname)+".xml")
            except IOError:
                wx.LogError("Cannot save file '%s'." % pathname)


    def onExit(self):
        wx.CallAfter(self.Close)
