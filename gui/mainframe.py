import wx
import wx.lib.agw.aui as aui
import sys, time, math, os, os.path

import mapnik

import data
from gui.settingspanel import SettingsPanel
from mapping import MapCanvas
import mapping.tools as toolbox
import events
import utils
from resources.provider import Provider as rp

try:
    from agw import customtreectrl as ct
except ImportError:  # if it's not there locally, try the wxPython lib.
    import wx.lib.agw.customtreectrl as ct

    STATUS_FIELD_MSG = 0
    STATUS_FIELD_COORD_LABEL = 1
    STATUS_FIELD_COORD_VALUE = 2
    STATUS_FIELD_SCALE_LABEL = 3
    STATUS_FIELD_SCALE_VALUE = 4
    STATUS_FIELD_PROJECTION = 5

    ID_ZOOM_IN_TOOL = wx.NewId()
    ID_ZOOM_OUT_TOOL = wx.NewId()
    ID_PAN_TOOL = wx.NewId()
    ID_ZOOM_ENVELOPE_TOOL = wx.NewId()
    ID_ZOOM_EXTENT_TOOL = wx.NewId()
    ID_ADD_SHAPE_LAYER_ACTION = wx.NewId()
    ID_REMOVE_LAYER_ACTION = wx.NewId()


class MainFrame(wx.Frame):

    def __init__(self, parent, id=-1, title="Micro GIS", pos=wx.DefaultPosition,
                 size=(1200, 600), style=wx.DEFAULT_FRAME_STYLE):

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

        self.canvas.Bind(events.EVT_MAP_MOUSE_DRAG, self.onMapMouseMotion)
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
            tool = self.tbMap.GetToolToggled(ID_ZOOM_IN_TOOL)
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
        self._mgr.AddPane(self.treeLayers, aui.AuiPaneInfo().Left().Caption("Layers").BestSize(180,150))

        self.propertiesPanel = wx.Panel(self)
        self.propertyPanel = PropertyPanel(self, utils.Log(), wx.Point(200, 150))
        self.layerPropertyPanel = LayerPropertyPanel(self, utils.Log(), wx.Point(200, 150))
        topsizer = wx.BoxSizer(wx.VERTICAL)
        topsizer.Add(self.layerPropertyPanel, 1, wx.EXPAND)
        self.propertiesPanel.SetSizer(topsizer)
        self.propertiesPanel.SetAutoLayout(True)
        self._mgr.AddPane(self.layerPropertyPanel, aui.AuiPaneInfo().Right().Caption("Properties").BestSize(180,150))
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
        self.tbMap.AddToggleTool(ID_ZOOM_IN_TOOL, rp.GetIcon("zoom-in", wx.Size(16, 16)),
                                 rp.GetIcon("zoom-in", wx.Size(16, 16)),
                                 short_help_string="Zoom In tool")
        self.tbMap.AddToggleTool(ID_ZOOM_OUT_TOOL, rp.GetIcon("zoom-out", wx.Size(16, 16)),
                                 rp.GetIcon("zoom-out", wx.Size(16, 16)),
                                 short_help_string="Zoom Out tool")
        self.tbMap.AddSeparator()
        self.tbMap.AddToggleTool(ID_PAN_TOOL, rp.GetIcon("pan", wx.Size(16, 16)), rp.GetIcon("pan", wx.Size(16, 16)),
                                 short_help_string="Pan tool tool")
        self.tbMap.AddToggleTool(ID_ZOOM_ENVELOPE_TOOL, rp.GetIcon("zoom-selection", wx.Size(16, 16)),
                                 rp.GetIcon("zoom-selection", wx.Size(16, 16)),
                                 short_help_string="Zoom to envelope tool")
        self.tbMap.AddSimpleTool(ID_ZOOM_EXTENT_TOOL, rp.GetIcon("zoom-region", wx.Size(16, 16)),
                                 rp.GetIcon("zoom-region", wx.Size(16, 16)), short_help_string="Zoom to extent tool")

        self.Bind(wx.EVT_TOOL, self.onZoomInTool, id=ID_ZOOM_IN_TOOL)
        self.Bind(wx.EVT_TOOL, self.onZoomOutTool, id=ID_ZOOM_OUT_TOOL)
        self.Bind(wx.EVT_TOOL, self.onPanTool, id=ID_PAN_TOOL)
        self.Bind(wx.EVT_TOOL, self.onZoomEnvelopeTool, id=ID_ZOOM_ENVELOPE_TOOL)
        self.Bind(wx.EVT_TOOL, self.onZoomExtentTool, id=ID_ZOOM_EXTENT_TOOL)

        self.tbMap.Realize()

        self._mgr.AddPane(tbMain, aui.AuiPaneInfo().Name("tbMain").Caption("Edit Toolbar").
                          ToolbarPane().Top().Row(1))
        self._mgr.AddPane(self.tbMap, aui.AuiPaneInfo().Name("tbMap").Caption("Map Toolbar").
                          ToolbarPane().Top().Row(1).Position(1))

    def initStatusBar(self):
        self.CreateStatusBar(6)
        self.GetStatusBar().SetStatusWidths([-1, 80, 100, 40, 120, 100])
        self.GetStatusBar().SetStatusText("Ready")
        self.GetStatusBar().SetStatusText("Coordinates: ", STATUS_FIELD_COORD_LABEL)
        self.GetStatusBar().SetStatusText("Scale: ", STATUS_FIELD_SCALE_LABEL)
        self.GetStatusBar().SetStatusText("WGS84", STATUS_FIELD_PROJECTION)

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

        layerMenu = wx.Menu()
        layerMenu.Append(ID_ADD_SHAPE_LAYER_ACTION, "Add Shape File Layer")
        layerMenu.Append(ID_REMOVE_LAYER_ACTION, "Remove Shape File Layer")
        self.Bind(wx.EVT_MENU, self.onAddShapeFileLayer, id=ID_ADD_SHAPE_LAYER_ACTION)
        self.Bind(wx.EVT_MENU, self.onRemoveLayer, id=ID_REMOVE_LAYER_ACTION)

        windowMenu = wx.Menu()
        helpMenu = wx.Menu()

        mb.Append(fileMenu, "&File")
        mb.Append(editMenu, "&Edit")
        mb.Append(viewMenu, "&View")
        mb.Append(layerMenu, "&Layer")
        mb.Append(windowMenu, "&Window")
        mb.Append(helpMenu, "&Help")

        return mb

    def OnClose(self, event):
        # deinitialize the frame manager
        self._mgr.UnInit()
        event.Skip()

    def onMapReady(self, event):
        self.GetStatusBar().SetStatusText(self.canvas.mapScale.representativeFraction, STATUS_FIELD_SCALE_VALUE)

    def onMapMouseMotion(self, event):
        # note: y represents latitude why x represent longitude
        lat = ("%.3f" % round(event.mapPosition.y, 3))
        long = ("%.3f" % round(event.mapPosition.x, 3))
        coord = "{lat},{long}".format(**locals())
        self.GetStatusBar().SetStatusText(coord, STATUS_FIELD_COORD_VALUE)

    def onMapScaleChanged(self, event):
        self.GetStatusBar().SetStatusText(event.scale.representativeFraction, STATUS_FIELD_SCALE_VALUE)

    def onMapLayersChanged(self, e):
        self.updateLayerTree()

    def updateLayerTree(self):
        self.treeLayers.DeleteChildren(self.layersTreeRoot)
        layers = reversed(self.canvas.mapLayers)  # reversed to appear logically laid in the tree
        for l in layers:
            item = self.treeLayers.AppendItem(self.layersTreeRoot, l.name)
            self.treeLayers.SetPyData(item, l)
            self.treeLayers.Expand(self.layersTreeRoot)

    def onZoomInTool(self, event):

        if self.canvas.activeTool == toolbox.types.ZOOM_IN_TOOL:
            self.canvas.setTool(toolbox.types.NONE)
            return

        self.canvas.setTool(toolbox.types.ZOOM_IN_TOOL)
        self.activateToolBarItem(ID_ZOOM_IN_TOOL)

    def onZoomOutTool(self, event):
        if self.canvas.activeTool == toolbox.types.ZOOM_OUT_TOOL:
            self.canvas.setTool(toolbox.types.NONE)
            return
        self.canvas.setTool(toolbox.types.ZOOM_OUT_TOOL)
        self.activateToolBarItem(ID_ZOOM_OUT_TOOL)

    def onPanTool(self, event):
        if self.canvas.activeTool == toolbox.types.PAN_TOOL:
            self.canvas.setTool(toolbox.types.NONE)
            return
        self.canvas.activateTool(toolbox.types.PAN_TOOL)
        self.activateToolBarItem(ID_PAN_TOOL)

    def onZoomEnvelopeTool(self, event):
        self.canvas.activateTool(toolbox.types.ZOOM_ENVELOPE_TOOL)
        self.activateToolBarItem(ID_ZOOM_ENVELOPE_TOOL)

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
        with wx.FileDialog(self, "Select a Map file", wildcard="xml files (*.xml)|*.xml",
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
                wx.LogError("Cannot open file '%s'." % pathname)

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


    def onExit(self, event):
        wx.CallAfter(self.Close)

    def onAddShapeFileLayer(self, event):
        path = utils.Gui.openFileDialogPath(self, "Select a shape file", "Shape files (*.shp)|*.shp")

        if "" != path:
            try:
                ds = data.ShapeFileDataSource(data.sourceTypes.SHAPE_FILE, path)
                layer = ds.layer()
                layer.styles.append('default')
                self.canvas.addMapLayer(layer)
            except IOError:
                wx.LogError("Unable to open file '%s'." % path)

    def onRemoveLayer(self, event):
        selectedItem = self.treeLayers.GetSelection()
        if isinstance(self.treeLayers.GetPyData(selectedItem), tuple) and self.treeLayers.GetPyData(selectedItem) :
            utils.Gui.showMessageBoxWarn(self, "Root layer cannot be removed", "Warning")
            return

        result = utils.Gui.showMessageBoxYesNo(self, "Are you sure you want to remove this layer ?", "Remove layer")
        if result:
            layer = self.treeLayers.GetPyData(selectedItem)
            self.canvas.removeMapLayer(layer)


#---------------------------------------------------------------------------

_ = wx.GetTranslation
import wx.propgrid as wxpg

default_object_content2 = """\
object.title = "Object Title"
object.index = 1
object.PI = %f
object.wxpython_rules = True
""" % (math.pi)

default_object_content1 = """\

#
# Note that the results of autofill will appear on the second page.

#
# Set number of iterations appropriately to test performance
iterations = 100

#
# Test result for 100,000 iterations on Athlon XP 2000+:
#
# Time spent per property: 0.054ms
# Memory allocated per property: ~350 bytes (includes Python object)
#

for i in range(0,iterations):
    setattr(object,'title%i'%i,"Object Title")
    setattr(object,'index%i'%i,1)
    setattr(object,'PI%i'%i,3.14)
    setattr(object,'wxpython_rules%i'%i,True)
"""


############################################################################
#
# CUSTOM PROPERTY SAMPLES
#
############################################################################


class ValueObject:
    def __init__(self):
        pass


class IntProperty2(wxpg.PyProperty):
    """\
    This is a simple re-implementation of wxIntProperty.
    """

    def __init__(self, label, name=wxpg.PG_LABEL_STRING, value=0):
        wxpg.PyProperty.__init__(self, label, name)
        self.SetValue(value)

    def GetClassName(self):
        """\
        This is not 100% necessary and in future is probably going to be
        automated to return class name.
        """
        return "IntProperty2"

    def GetEditor(self):
        return "TextCtrl"

    def ValueToString(self, value, flags):
        return str(value)

    def StringToValue(self, s, flags):
        """ If failed, return False or (False, None). If success, return tuple
            (True, newValue).
        """
        try:
            v = int(s)
            if self.GetValue() != v:
                return (True, v)
        except (ValueError, TypeError):
            if flags & wxpg.PG_REPORT_ERROR:
                wx.MessageBox("Cannot convert '%s' into a number." % s, "Error")
        return False

    def IntToValue(self, v, flags):
        """ If failed, return False or (False, None). If success, return tuple
            (True, newValue).
        """
        if (self.GetValue() != v):
            return (True, v)
        return False

    def ValidateValue(self, value, validationInfo):
        """ Let's limit the value to range -10000 and 10000.
        """
        # Just test this function to make sure validationInfo and
        # wxPGVFBFlags work properly.
        oldvfb__ = validationInfo.GetFailureBehavior()

        # Mark the cell if validaton failred
        validationInfo.SetFailureBehavior(wxpg.PG_VFB_MARK_CELL)

        if value < -10000 or value > 10000:
            return False

        return (True, value)


class SizeProperty(wxpg.PyProperty):
    """ Demonstrates a property with few children.
    """

    def __init__(self, label, name=wxpg.PG_LABEL_STRING, value=wx.Size(0, 0)):
        wxpg.PyProperty.__init__(self, label, name)

        value = self._ConvertValue(value)

        self.AddPrivateChild(wxpg.IntProperty("X", value=value.x))
        self.AddPrivateChild(wxpg.IntProperty("Y", value=value.y))

        self.m_value = value

    def GetClassName(self):
        return self.__class__.__name__

    def GetEditor(self):
        return "TextCtrl"

    def RefreshChildren(self):
        size = self.m_value
        self.Item(0).SetValue(size.x)
        self.Item(1).SetValue(size.y)

    def _ConvertValue(self, value):
        """ Utility convert arbitrary value to a real wx.Size.
        """
        from operator import isSequenceType
        if isinstance(value, wx.Point):
            value = wx.Size(value.x, value.y)
        elif isSequenceType(value):
            value = wx.Size(*value)
        return value

    def ChildChanged(self, thisValue, childIndex, childValue):
        # FIXME: This does not work yet. ChildChanged needs be fixed "for"
        #        wxPython in wxWidgets SVN trunk, and that has to wait for
        #        2.9.1, as wxPython 2.9.0 uses WX_2_9_0_BRANCH.
        size = self._ConvertValue(self.m_value)
        if childIndex == 0:
            size.x = childValue
        elif childIndex == 1:
            size.y = childValue
        else:
            raise AssertionError

        return size


class DirsProperty(wxpg.PyArrayStringProperty):
    """ Sample of a custom custom ArrayStringProperty.

        Because currently some of the C++ helpers from wxArrayStringProperty
        and wxProperytGrid are not available, our implementation has to quite
        a bit 'manually'. Which is not too bad since Python has excellent
        string and list manipulation facilities.
    """

    def __init__(self, label, name=wxpg.PG_LABEL_STRING, value=[]):
        wxpg.PyArrayStringProperty.__init__(self, label, name, value)

        # Set default delimiter
        self.SetAttribute("Delimiter", ',')

    def GetEditor(self):
        return "TextCtrlAndButton"

    def ValueToString(self, value, flags):
        return self.m_display

    def OnSetValue(self):
        self.GenerateValueAsString()

    def DoSetAttribute(self, name, value):
        # Proper way to call same method from super class
        retval = self.CallSuperMethod("DoSetAttribute", name, value)

        #
        # Must re-generate cached string when delimiter changes
        if name == "Delimiter":
            self.GenerateValueAsString(delim=value)

        return retval

    def GenerateValueAsString(self, delim=None):
        """ This function creates a cached version of displayed text
            (self.m_display).
        """
        if not delim:
            delim = self.GetAttribute("Delimiter")
            if not delim:
                delim = ','

        ls = self.GetValue()
        if delim == '"' or delim == "'":
            text = ' '.join(['%s%s%s' % (delim, a, delim) for a in ls])
        else:
            text = ', '.join(ls)
        self.m_display = text

    def StringToValue(self, text, argFlags):
        """ If failed, return False or (False, None). If success, return tuple
            (True, newValue).
        """
        delim = self.GetAttribute("Delimiter")
        if delim == '"' or delim == "'":
            # Proper way to call same method from super class
            return self.CallSuperMethod("StringToValue", text, 0)
        v = [a.strip() for a in text.split(delim)]
        return (True, v)

    def OnEvent(self, propgrid, primaryEditor, event):
        if event.GetEventType() == wx.wxEVT_COMMAND_BUTTON_CLICKED:
            dlg = wx.DirDialog(propgrid,
                               _("Select a directory to be added to "
                                 "the list:"))

            if dlg.ShowModal() == wx.ID_OK:
                new_path = dlg.GetPath()
                old_value = self.m_value
                if old_value:
                    new_value = list(old_value)
                    new_value.append(new_path)
                else:
                    new_value = [new_path]
                self.SetValueInEvent(new_value)
                retval = True
            else:
                retval = False

            dlg.Destroy()
            return retval

        return False


class PyObjectPropertyValue:
    """\
    Value type of our sample PyObjectProperty. We keep a simple dash-delimited
    list of string given as argument to constructor.
    """

    def __init__(self, s=None):
        try:
            self.ls = [a.strip() for a in s.split('-')]
        except:
            self.ls = []

    def __repr__(self):
        return ' - '.join(self.ls)


class PyObjectProperty(wxpg.PyProperty):
    """\
    Another simple example. This time our value is a PyObject.

    NOTE: We can't return an arbitrary python object in DoGetValue. It cannot
          be a simple type such as int, bool, double, or string, nor an array
          or wxObject based. Dictionary, None, or any user-specified Python
          class is allowed.
    """

    def __init__(self, label, name=wxpg.PG_LABEL_STRING, value=None):
        wxpg.PyProperty.__init__(self, label, name)
        self.SetValue(value)

    def GetClassName(self):
        return self.__class__.__name__

    def GetEditor(self):
        return "TextCtrl"

    def ValueToString(self, value, flags):
        return repr(value)

    def StringToValue(self, s, flags):
        """ If failed, return False or (False, None). If success, return tuple
            (True, newValue).
        """
        v = PyObjectPropertyValue(s)
        return (True, v)


class SampleMultiButtonEditor(wxpg.PyTextCtrlEditor):
    def __init__(self):
        wxpg.PyTextCtrlEditor.__init__(self)

    def CreateControls(self, propGrid, property, pos, sz):
        # Create and populate buttons-subwindow
        buttons = wxpg.PGMultiButton(propGrid, sz)

        # Add two regular buttons
        buttons.AddButton("...")
        buttons.AddButton("A")
        # Add a bitmap button
        buttons.AddBitmapButton(wx.ArtProvider.GetBitmap(wx.ART_FOLDER))

        # Create the 'primary' editor control (textctrl in this case)
        wnd = self.CallSuperMethod("CreateControls",
                                   propGrid,
                                   property,
                                   pos,
                                   buttons.GetPrimarySize())

        # Finally, move buttons-subwindow to correct position and make sure
        # returned wxPGWindowList contains our custom button list.
        buttons.Finalize(propGrid, pos);

        # We must maintain a reference to any editor objects we created
        # ourselves. Otherwise they might be freed prematurely. Also,
        # we need it in OnEvent() below, because in Python we cannot "cast"
        # result of wxPropertyGrid.GetEditorControlSecondary() into
        # PGMultiButton instance.
        self.buttons = buttons

        return (wnd, buttons)

    def OnEvent(self, propGrid, prop, ctrl, event):
        if event.GetEventType() == wx.wxEVT_COMMAND_BUTTON_CLICKED:
            buttons = self.buttons
            evtId = event.GetId()

            if evtId == buttons.GetButtonId(0):
                # Do something when the first button is pressed
                wx.LogDebug("First button pressed");
                return False  # Return false since value did not change
            if evtId == buttons.GetButtonId(1):
                # Do something when the second button is pressed
                wx.MessageBox("Second button pressed");
                return False  # Return false since value did not change
            if evtId == buttons.GetButtonId(2):
                # Do something when the third button is pressed
                wx.MessageBox("Third button pressed");
                return False  # Return false since value did not change

        return self.CallSuperMethod("OnEvent", propGrid, prop, ctrl, event)


class SingleChoiceDialogAdapter(wxpg.PyEditorDialogAdapter):
    """ This demonstrates use of wxpg.PyEditorDialogAdapter.
    """

    def __init__(self, choices):
        wxpg.PyEditorDialogAdapter.__init__(self)
        self.choices = choices

    def DoShowDialog(self, propGrid, property):
        s = wx.GetSingleChoice("Message", "Caption", self.choices)

        if s:
            self.SetValue(s)
            return True

        return False;


class SingleChoiceProperty(wxpg.PyStringProperty):
    def __init__(self, label, name=wxpg.PG_LABEL_STRING, value=''):
        wxpg.PyStringProperty.__init__(self, label, name, value)

        # Prepare choices
        dialog_choices = []
        dialog_choices.append("Cat");
        dialog_choices.append("Dog");
        dialog_choices.append("Gibbon");
        dialog_choices.append("Otter");

        self.dialog_choices = dialog_choices

    def GetEditor(self):
        # Set editor to have button
        return "TextCtrlAndButton"

    def GetEditorDialog(self):
        # Set what happens on button click
        return SingleChoiceDialogAdapter(self.dialog_choices)


class TrivialPropertyEditor(wxpg.PyEditor):
    """\
    This is a simple re-creation of TextCtrlWithButton. Note that it does
    not take advantage of wx.TextCtrl and wx.Button creation helper functions
    in wx.PropertyGrid.
    """

    def __init__(self):
        wxpg.PyEditor.__init__(self)

    def CreateControls(self, propgrid, property, pos, sz):
        """ Create the actual wxPython controls here for editing the
            property value.

            You must use propgrid.GetPanel() as parent for created controls.

            Return value is either single editor control or tuple of two
            editor controls, of which first is the primary one and second
            is usually a button.
        """
        try:
            x, y = pos
            w, h = sz
            h = 64 + 6

            # Make room for button
            bw = propgrid.GetRowHeight()
            w -= bw

            s = property.GetDisplayedString();

            tc = wx.TextCtrl(propgrid.GetPanel(), wxpg.PG_SUBID1, s,
                             (x, y), (w, h),
                             wx.TE_PROCESS_ENTER)
            btn = wx.Button(propgrid.GetPanel(), wxpg.PG_SUBID2, '...',
                            (x + w, y),
                            (bw, h), wx.WANTS_CHARS)
            return (tc, btn)
        except:
            import traceback
            print(traceback.print_exc())

    def UpdateControl(self, property, ctrl):
        ctrl.SetValue(property.GetDisplayedString())

    def DrawValue(self, dc, rect, property, text):
        if not property.IsValueUnspecified():
            dc.DrawText(property.GetDisplayedString(), rect.x + 5, rect.y)

    def OnEvent(self, propgrid, property, ctrl, event):
        """ Return True if modified editor value should be committed to
            the property. To just mark the property value modified, call
            propgrid.EditorsValueWasModified().
        """
        if not ctrl:
            return False

        evtType = event.GetEventType()

        if evtType == wx.wxEVT_COMMAND_TEXT_ENTER:
            if propgrid.IsEditorsValueModified():
                return True
        elif evtType == wx.wxEVT_COMMAND_TEXT_UPDATED:
            #
            # Pass this event outside wxPropertyGrid so that,
            # if necessary, program can tell when user is editing
            # a textctrl.
            event.Skip()
            event.SetId(propgrid.GetId())

            propgrid.EditorsValueWasModified()
            return False

        return False

    def GetValueFromControl(self, property, ctrl):
        """ Return tuple (wasSuccess, newValue), where wasSuccess is True if
            different value was acquired succesfully.
        """
        tc = ctrl
        textVal = tc.GetValue()

        if property.UsesAutoUnspecified() and not textVal:
            return (True, None)

        res, value = property.StringToValue(textVal,
                                            wxpg.PG_EDITABLE_VALUE)

        # Changing unspecified always causes event (returning
        # True here should be enough to trigger it).
        if not res and value is None:
            res = True

        return (res, value)

    def SetValueToUnspecified(self, property, ctrl):
        ctrl.Remove(0, len(ctrl.GetValue()))

    def SetControlStringValue(self, property, ctrl, text):
        ctrl.SetValue(text)

    def OnFocus(self, property, ctrl):
        ctrl.SetSelection(-1, -1)
        ctrl.SetFocus()


class LargeImagePickerCtrl(wx.Panel):
    """\
    Control created and used by LargeImageEditor.
    """

    def __init__(self):
        pre = wx.PrePanel()
        self.PostCreate(pre)

    def Create(self, parent, id_, pos, size, style=0):
        wx.Panel.Create(self, parent, id_, pos, size,
                        style | wx.BORDER_SIMPLE)
        img_spc = size[1]
        self.tc = wx.TextCtrl(self, -1, "", (img_spc, 0), (2048, size[1]),
                              wx.BORDER_NONE)
        self.SetBackgroundColour(wx.WHITE)
        self.SetBackgroundStyle(wx.BG_STYLE_CUSTOM)
        self.property = None
        self.bmp = None
        self.Bind(wx.EVT_PAINT, self.OnPaint)

    def OnPaint(self, event):
        dc = wx.BufferedPaintDC(self)

        whiteBrush = wx.Brush(wx.WHITE)
        dc.SetBackground(whiteBrush)
        dc.Clear()

        bmp = self.bmp
        if bmp:
            dc.DrawBitmap(bmp, 2, 2)
        else:
            dc.SetPen(wx.Pen(wx.BLACK))
            dc.SetBrush(whiteBrush)
            dc.DrawRectangle(2, 2, 64, 64)

    def RefreshThumbnail(self):
        """\
        We use here very simple image scaling code.
        """
        if not self.property:
            self.bmp = None
            return

        path = self.property.DoGetValue()

        if not os.path.isfile(path):
            self.bmp = None
            return

        image = wx.Image(path)
        image.Rescale(64, 64)
        self.bmp = wx.BitmapFromImage(image)

    def SetProperty(self, property):
        self.property = property
        self.tc.SetValue(property.GetDisplayedString())
        self.RefreshThumbnail()

    def SetValue(self, s):
        self.RefreshThumbnail()
        self.tc.SetValue(s)

    def GetLastPosition(self):
        return self.tc.GetLastPosition()


class LargeImageEditor(wxpg.PyEditor):
    """\
    Double-height text-editor with image in front.
    """

    def __init__(self):
        wxpg.PyEditor.__init__(self)

    def CreateControls(self, propgrid, property, pos, sz):
        try:
            x, y = pos
            w, h = sz
            h = 64 + 6

            # Make room for button
            bw = propgrid.GetRowHeight()
            w -= bw

            lipc = LargeImagePickerCtrl()
            if sys.platform.startswith('win'):
                lipc.Hide()
            lipc.Create(propgrid.GetPanel(), wxpg.PG_SUBID1, (x, y), (w, h))
            lipc.SetProperty(property)
            # Hmmm.. how to have two-stage creation without subclassing?
            # btn = wx.PreButton()
            # pre = wx.PreWindow()
            # self.PostCreate(pre)
            # if sys.platform == 'win32':
            #    btn.Hide()
            # btn.Create(propgrid, wxpg.PG_SUBID2, '...', (x2-bw,pos[1]),
            #           (bw,h), wx.WANTS_CHARS)
            btn = wx.Button(propgrid.GetPanel(), wxpg.PG_SUBID2, '...',
                            (x + w, y),
                            (bw, h), wx.WANTS_CHARS)
            return (lipc, btn)
        except:
            import traceback
            print(traceback.print_exc())

    def UpdateControl(self, property, ctrl):
        ctrl.SetValue(property.GetDisplayedString())

    def DrawValue(self, dc, rect, property, text):
        if not property.IsValueUnspecified():
            dc.DrawText(property.GetDisplayedString(), rect.x + 5, rect.y)

    def OnEvent(self, propgrid, property, ctrl, event):
        """ Return True if modified editor value should be committed to
            the property. To just mark the property value modified, call
            propgrid.EditorsValueWasModified().
        """
        if not ctrl:
            return False

        evtType = event.GetEventType()

        if evtType == wx.wxEVT_COMMAND_TEXT_ENTER:
            if propgrid.IsEditorsValueModified():
                return True
        elif evtType == wx.wxEVT_COMMAND_TEXT_UPDATED:
            #
            # Pass this event outside wxPropertyGrid so that,
            # if necessary, program can tell when user is editing
            # a textctrl.
            event.Skip()
            event.SetId(propgrid.GetId())

            propgrid.EditorsValueWasModified()
            return False

        return False

    def GetValueFromControl(self, property, ctrl):
        """ Return tuple (wasSuccess, newValue), where wasSuccess is True if
            different value was acquired succesfully.
        """
        tc = ctrl.tc
        textVal = tc.GetValue()

        if property.UsesAutoUnspecified() and not textVal:
            return (None, True)

        res, value = property.StringToValue(textVal,
                                            wxpg.PG_EDITABLE_VALUE)

        # Changing unspecified always causes event (returning
        # True here should be enough to trigger it).
        if not res and value is None:
            res = True

        return (res, value)

    def SetValueToUnspecified(self, property, ctrl):
        ctrl.tc.Remove(0, len(ctrl.tc.GetValue()))

    def SetControlStringValue(self, property, ctrl, txt):
        ctrl.SetValue(txt)

    def OnFocus(self, property, ctrl):
        ctrl.tc.SetSelection(-1, -1)
        ctrl.tc.SetFocus()

    def CanContainCustomImage(self):
        return True


class PropertyPanel(wx.Panel):

    def __init__(self, parent, log, size):
        wx.Panel.__init__(self, parent, wx.ID_ANY, size)
        self.log = log

        self.panel = panel = wx.Panel(self, wx.ID_ANY)
        topsizer = wx.BoxSizer(wx.VERTICAL)

        # Difference between using PropertyGridManager vs PropertyGrid is that
        # the manager supports multiple pages and a description box.
        self.pg = pg = wxpg.PropertyGridManager(panel,
                                                style=wxpg.PG_SPLITTER_AUTO_CENTER |
                                                      wxpg.PG_AUTO_SORT |
                                                      wxpg.PG_TOOLBAR)

        # Show help as tooltips
        pg.SetExtraStyle(wxpg.PG_EX_HELP_AS_TOOLTIPS)

        pg.Bind(wxpg.EVT_PG_CHANGED, self.OnPropGridChange)
        pg.Bind(wxpg.EVT_PG_PAGE_CHANGED, self.OnPropGridPageChange)
        pg.Bind(wxpg.EVT_PG_SELECTED, self.OnPropGridSelect)
        pg.Bind(wxpg.EVT_PG_RIGHT_CLICK, self.OnPropGridRightClick)

        #
        # Let's use some simple custom editor
        #
        # NOTE: Editor must be registered *before* adding a property that
        # uses it.
        if not getattr(sys, '_PropGridEditorsRegistered', False):
            pg.RegisterEditor(TrivialPropertyEditor)
            pg.RegisterEditor(SampleMultiButtonEditor)
            pg.RegisterEditor(LargeImageEditor)
            # ensure we only do it once
            sys._PropGridEditorsRegistered = True

        #
        # Add properties
        #

        pg.AddPage("Page 1 - Testing All")

        pg.Append(wxpg.PropertyCategory("1 - Basic Properties"))
        pg.Append(wxpg.StringProperty("String", value="Some Text"))
        pg.Append(wxpg.IntProperty("Int", value=100))
        pg.Append(wxpg.FloatProperty("Float", value=100.0))
        pg.Append(wxpg.BoolProperty("Bool", value=True))
        pg.Append(wxpg.BoolProperty("Bool_with_Checkbox", value=True))
        pg.SetPropertyAttribute("Bool_with_Checkbox", "UseCheckbox", True)

        pg.Append(wxpg.PropertyCategory("2 - More Properties"))
        pg.Append(wxpg.LongStringProperty("LongString",
                                          value="This is a\\nmulti-line string\\nwith\\ttabs\\nmixed\\tin."))
        pg.Append(wxpg.DirProperty("Dir", value="C:\\Windows"))
        pg.Append(wxpg.FileProperty("File", value="C:\\Windows\\system.ini"))
        pg.Append(wxpg.ArrayStringProperty("ArrayString", value=['A', 'B', 'C']))

        pg.Append(wxpg.EnumProperty("Enum", "Enum",
                                    ['wxPython Rules',
                                     'wxPython Rocks',
                                     'wxPython Is The Best'],
                                    [10, 11, 12],
                                    0))
        pg.Append(wxpg.EditEnumProperty("EditEnum", "EditEnumProperty",
                                        ['A', 'B', 'C'],
                                        [0, 1, 2],
                                        "Text Not in List"))

        pg.Append(wxpg.PropertyCategory("3 - Advanced Properties"))
        pg.Append(wxpg.FontProperty("Font", value=panel.GetFont()))
        pg.Append(wxpg.ColourProperty("Colour",
                                      value=panel.GetBackgroundColour()))
        pg.Append(wxpg.SystemColourProperty("SystemColour"))
        pg.Append(wxpg.ImageFileProperty("ImageFile"))
        pg.Append(wxpg.MultiChoiceProperty("MultiChoice",
                                           choices=['wxWidgets', 'QT', 'GTK+']))

        pg.Append(wxpg.PropertyCategory("4 - Additional Properties"))
        # pg.Append( wxpg.PointProperty("Point",value=panel.GetPosition()) )
        # pg.Append( SizeProperty("Size",value=panel.GetSize()) )
        # pg.Append( wxpg.FontDataProperty("FontData") )
        pg.Append(wxpg.IntProperty("IntWithSpin", value=256))
        pg.SetPropertyEditor("IntWithSpin", "SpinCtrl")

        pg.SetPropertyAttribute("File", wxpg.PG_FILE_SHOW_FULL_PATH, 0)
        pg.SetPropertyAttribute("File", wxpg.PG_FILE_INITIAL_PATH,
                                "C:\\Program Files\\Internet Explorer")

        pg.Append(wxpg.PropertyCategory("5 - Custom Properties and Editors"))
        pg.Append(IntProperty2("IntProperty2", value=1024))

        pg.Append(PyObjectProperty("PyObjectProperty"))

        pg.Append(DirsProperty("Dirs1", value=['C:/Lib', 'C:/Bin']))
        pg.Append(DirsProperty("Dirs2", value=['/lib', '/bin']))

        # Test another type of delimiter
        pg.SetPropertyAttribute("Dirs2", "Delimiter", '"')

        # SampleMultiButtonEditor
        pg.Append(wxpg.LongStringProperty("MultipleButtons"));
        pg.SetPropertyEditor("MultipleButtons", "SampleMultiButtonEditor");
        pg.Append(SingleChoiceProperty("SingleChoiceProperty"))

        # Custom editor samples
        prop = pg.Append(wxpg.StringProperty("StringWithCustomEditor",
                                             value="test value"))
        pg.SetPropertyEditor(prop, "TrivialPropertyEditor")

        pg.Append(wxpg.ImageFileProperty("ImageFileWithLargeEditor"))
        pg.SetPropertyEditor("ImageFileWithLargeEditor", "LargeImageEditor")

        # When page is added, it will become the target page for AutoFill
        # calls (and for other property insertion methods as well)
        pg.AddPage("Page 2 - Results of AutoFill will appear here")

        topsizer.Add(pg, 1, wx.EXPAND)
        panel.SetSizer(topsizer)
        topsizer.SetSizeHints(panel)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(panel, 1, wx.EXPAND)
        self.SetSizer(sizer)
        self.SetAutoLayout(True)

    def OnPropGridChange(self, event):
        p = event.GetProperty()
        if p:
            self.log.write('%s changed to "%s"\n' % (p.GetName(), p.GetValueAsString()))

    def OnPropGridSelect(self, event):
        p = event.GetProperty()
        if p:
            self.log.write('%s selected\n' % (event.GetProperty().GetName()))
        else:
            self.log.write('Nothing selected\n')

    def OnDeleteProperty(self, event):
        p = self.pg.GetSelectedProperty()
        if p:
            self.pg.DeleteProperty(p)
        else:
            wx.MessageBox("First select a property to delete")

    def OnReserved(self, event):
        pass

    def OnSetPropertyValues(self, event):
        try:
            d = self.pg.GetPropertyValues(inc_attributes=True)

            ss = []
            for k, v in d.iteritems():
                v = repr(v)
                if not v or v[0] != '<':
                    if k.startswith('@'):
                        ss.append('setattr(obj, "%s", %s)' % (k, v))
                    else:
                        ss.append('obj.%s = %s' % (k, v))

            dlg = MemoDialog(self,
                             "Enter Content for Object Used in SetPropertyValues",
                             '\n'.join(ss))  # default_object_content1

            if dlg.ShowModal() == wx.ID_OK:
                import datetime
                sandbox = {'obj': ValueObject(),
                           'wx': wx,
                           'datetime': datetime}
                exec dlg.tc.GetValue() in sandbox
                t_start = time.time()
                # print(sandbox['obj'].__dict__)
                self.pg.SetPropertyValues(sandbox['obj'])
                t_end = time.time()
                self.log.write('SetPropertyValues finished in %.0fms\n' %
                               ((t_end - t_start) * 1000.0))
        except:
            import traceback
            traceback.print_exc()

    def OnGetPropertyValues(self, event):
        try:
            t_start = time.time()
            d = self.pg.GetPropertyValues(inc_attributes=True)
            t_end = time.time()
            self.log.write('GetPropertyValues finished in %.0fms\n' %
                           ((t_end - t_start) * 1000.0))
            ss = ['%s: %s' % (k, repr(v)) for k, v in d.iteritems()]
            dlg = MemoDialog(self, "GetPropertyValues Result",
                             'Contents of resulting dictionary:\n\n' + '\n'.join(ss))
            dlg.ShowModal()
        except:
            import traceback
            traceback.print_exc()

    def OnGetPropertyValues2(self, event):
        try:
            t_start = time.time()
            d = self.pg.GetPropertyValues(as_strings=True)
            t_end = time.time()
            self.log.write('GetPropertyValues(as_strings=True) finished in %.0fms\n' %
                           ((t_end - t_start) * 1000.0))
            ss = ['%s: %s' % (k, repr(v)) for k, v in d.iteritems()]
            dlg = MemoDialog(self, "GetPropertyValues Result",
                             'Contents of resulting dictionary:\n\n' + '\n'.join(ss))
            dlg.ShowModal()
        except:
            import traceback
            traceback.print_exc()

    def OnAutoFill(self, event):
        try:
            dlg = MemoDialog(self, "Enter Content for Object Used for AutoFill", default_object_content1)
            if dlg.ShowModal() == wx.ID_OK:
                sandbox = {'object': ValueObject(), 'wx': wx}
                exec dlg.tc.GetValue() in sandbox
                t_start = time.time()
                self.pg.AutoFill(sandbox['object'])
                t_end = time.time()
                self.log.write('AutoFill finished in %.0fms\n' %
                               ((t_end - t_start) * 1000.0))
        except:
            import traceback
            traceback.print_exc()

    def OnPropGridRightClick(self, event):
        p = event.GetProperty()
        if p:
            self.log.write('%s right clicked\n' % (event.GetProperty().GetName()))
        else:
            self.log.write('Nothing right clicked\n')

    def OnPropGridPageChange(self, event):
        index = self.pg.GetSelectedPage()
        self.log.write('Page Changed to \'%s\'\n' % (self.pg.GetPageName(index)))


class LayerPropertyPanel(wx.Panel):

    def __init__(self, parent, log, size):
        wx.Panel.__init__(self, parent, wx.ID_ANY, size)
        self.log = log

        self.panel = panel = wx.Panel(self, wx.ID_ANY)
        topsizer = wx.BoxSizer(wx.VERTICAL)

        # Difference between using PropertyGridManager vs PropertyGrid is that
        # the manager supports multiple pages and a description box.
        self.pg = pg = wxpg.PropertyGridManager(panel,
                                                style=wxpg.PG_SPLITTER_AUTO_CENTER |
                                                      wxpg.PG_AUTO_SORT |
                                                      wxpg.PG_TOOLBAR)

        # Show help as tooltips
        pg.SetExtraStyle(wxpg.PG_EX_HELP_AS_TOOLTIPS)

        pg.Bind(wxpg.EVT_PG_CHANGED, self.OnPropGridChange)
        pg.Bind(wxpg.EVT_PG_PAGE_CHANGED, self.OnPropGridPageChange)
        pg.Bind(wxpg.EVT_PG_SELECTED, self.OnPropGridSelect)
        pg.Bind(wxpg.EVT_PG_RIGHT_CLICK, self.OnPropGridRightClick)

        pg.AddPage("Page 1 - Testing All")

        pg.Append(wxpg.PropertyCategory("1 - Basic Properties"))
        pg.Append(wxpg.StringProperty("String", value="Some Text"))
        pg.Append(wxpg.IntProperty("Int", value=100))

        topsizer.Add(pg, 1, wx.EXPAND)
        panel.SetSizer(topsizer)
        topsizer.SetSizeHints(panel)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(panel, 1, wx.EXPAND)
        self.SetSizer(sizer)
        self.SetAutoLayout(True)

    def OnPropGridChange(self, event):
        p = event.GetProperty()
        if p:
            self.log.write('%s changed to "%s"\n' % (p.GetName(), p.GetValueAsString()))

    def OnPropGridSelect(self, event):
        p = event.GetProperty()
        if p:
            self.log.write('%s selected\n' % (event.GetProperty().GetName()))
        else:
            self.log.write('Nothing selected\n')

    def OnDeleteProperty(self, event):
        p = self.pg.GetSelectedProperty()
        if p:
            self.pg.DeleteProperty(p)
        else:
            wx.MessageBox("First select a property to delete")

    def OnReserved(self, event):
        pass

    def OnSetPropertyValues(self, event):
        try:
            d = self.pg.GetPropertyValues(inc_attributes=True)

            ss = []
            for k, v in d.iteritems():
                v = repr(v)
                if not v or v[0] != '<':
                    if k.startswith('@'):
                        ss.append('setattr(obj, "%s", %s)' % (k, v))
                    else:
                        ss.append('obj.%s = %s' % (k, v))

            dlg = MemoDialog(self,
                             "Enter Content for Object Used in SetPropertyValues",
                             '\n'.join(ss))  # default_object_content1

            if dlg.ShowModal() == wx.ID_OK:
                import datetime
                sandbox = {'obj': ValueObject(),
                           'wx': wx,
                           'datetime': datetime}
                exec dlg.tc.GetValue() in sandbox
                t_start = time.time()
                # print(sandbox['obj'].__dict__)
                self.pg.SetPropertyValues(sandbox['obj'])
                t_end = time.time()
                self.log.write('SetPropertyValues finished in %.0fms\n' %
                               ((t_end - t_start) * 1000.0))
        except:
            import traceback
            traceback.print_exc()

    def OnGetPropertyValues(self, event):
        try:
            t_start = time.time()
            d = self.pg.GetPropertyValues(inc_attributes=True)
            t_end = time.time()
            self.log.write('GetPropertyValues finished in %.0fms\n' %
                           ((t_end - t_start) * 1000.0))
            ss = ['%s: %s' % (k, repr(v)) for k, v in d.iteritems()]
            dlg = MemoDialog(self, "GetPropertyValues Result",
                             'Contents of resulting dictionary:\n\n' + '\n'.join(ss))
            dlg.ShowModal()
        except:
            import traceback
            traceback.print_exc()

    def OnGetPropertyValues2(self, event):
        try:
            t_start = time.time()
            d = self.pg.GetPropertyValues(as_strings=True)
            t_end = time.time()
            self.log.write('GetPropertyValues(as_strings=True) finished in %.0fms\n' %
                           ((t_end - t_start) * 1000.0))
            ss = ['%s: %s' % (k, repr(v)) for k, v in d.iteritems()]
            dlg = MemoDialog(self, "GetPropertyValues Result",
                             'Contents of resulting dictionary:\n\n' + '\n'.join(ss))
            dlg.ShowModal()
        except:
            import traceback
            traceback.print_exc()

    def OnAutoFill(self, event):
        try:
            dlg = MemoDialog(self, "Enter Content for Object Used for AutoFill", default_object_content1)
            if dlg.ShowModal() == wx.ID_OK:
                sandbox = {'object': ValueObject(), 'wx': wx}
                exec dlg.tc.GetValue() in sandbox
                t_start = time.time()
                self.pg.AutoFill(sandbox['object'])
                t_end = time.time()
                self.log.write('AutoFill finished in %.0fms\n' %
                               ((t_end - t_start) * 1000.0))
        except:
            import traceback
            traceback.print_exc()

    def OnPropGridRightClick(self, event):
        p = event.GetProperty()
        if p:
            self.log.write('%s right clicked\n' % (event.GetProperty().GetName()))
        else:
            self.log.write('Nothing right clicked\n')

    def OnPropGridPageChange(self, event):
        index = self.pg.GetSelectedPage()
        self.log.write('Page Changed to \'%s\'\n' % (self.pg.GetPageName(index)))

# ---------------------------------------------------------------------------


class MemoDialog(wx.Dialog):
    """\
    Dialog for multi-line text editing.
    """

    def __init__(self, parent=None, title="", text="", pos=None, size=(500, 500)):
        wx.Dialog.__init__(self, parent, -1, title, style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)

        topsizer = wx.BoxSizer(wx.VERTICAL)

        tc = wx.TextCtrl(self, 11, text, style=wx.TE_MULTILINE)
        self.tc = tc
        topsizer.Add(tc, 1, wx.EXPAND | wx.ALL, 8)

        rowsizer = wx.BoxSizer(wx.HORIZONTAL)
        rowsizer.Add(wx.Button(self, wx.ID_OK, 'Ok'), 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTRE_VERTICAL, 8)
        rowsizer.Add((0, 0), 1, wx.ALIGN_RIGHT | wx.ALIGN_CENTRE_VERTICAL, 8)
        rowsizer.Add(wx.Button(self, wx.ID_CANCEL, 'Cancel'), 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTRE_VERTICAL, 8)
        topsizer.Add(rowsizer, 0, wx.EXPAND | wx.ALL, 8)

        self.SetSizer(topsizer)
        topsizer.Layout()

        self.SetSize(size)
        if not pos:
            self.CenterOnScreen()
        else:
            self.Move(pos)

#---------------------------------------------------------------------------