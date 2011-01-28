import traceback

from b2rexpkg.settings import ExportSettings
from b2rexpkg.siminfo import GridInfo
from b2rexpkg.tools.selectable import SelectablePack, SelectableRegion

from ogredotscene import Screen, HorizontalLayout
from ogredotscene import NumberView, Widget, CheckBox
from ogredotscene import VerticalLayout, Action, QuitButton, Button
from ogredotscene import StringButton, Label, Button, Box
from ogredotscene import SelectableLabel

import Blender

ERROR = 0
OK = 1
IMMEDIATE = 2

class BaseApplication(object):
    def __init__(self, title="RealXtend"):
        self.screen = Screen()
        self.gridinfo = GridInfo()
        self.buttons = {}
        self.settings_visible = False
        self.exportSettings = ExportSettings()
        self.initGui(title)
        self.addStatus("b2rex started")

    def connect(self, base_url, username="", password=""):
        """
        Connect to an opensim instance
        """
        self.gridinfo.connect(base_url, username, password)
        #self.sim.connect(base_url)

    def initGui(self, title):
        """
        Initialize the interface system.
        """
        self.vLayout = VerticalLayout()
        self.buttonLayout = HorizontalLayout()
        self.addCallbackButton('Connect', self.buttonLayout, 'Connect to opensim server. Needed if you want to upload worlds directly.')
        #self.addButton('Export', self.buttonLayout, 'Export to disk')
        self.addButton('Quit', self.buttonLayout, 'Quit the exporter')
        self.vLayout.addWidget(self.buttonLayout, 'buttonPanel')
        self.screen.addWidget(Box(self.vLayout, title), "layout")

        settingsButton = CheckBox(self.ToggleSettingsAction(self),
			          self.settings_visible,
				  'Settings',
				  [100, 20],
				  tooltip='Show Settings')
        self.buttonLayout.addWidget(settingsButton, 'SettingsButton')

    def addSettingsButton(self, button_name, layout, tooltip=""):
        """
        Create a settings string button.
        """
        val = getattr(self.exportSettings, button_name)
        self.buttons[button_name] = StringButton(val,
                                                 self.ChangeSettingAction(self, button_name),
                                                 button_name+": ", [200, 20], tooltip)
        layout.addWidget(self.buttons[button_name], 'buttonPanelButton' + button_name)

    def showSettings(self):
        """
        Create the settings widgets.
        """
        self.settingsLayout = VerticalLayout()
        self.vLayout.addWidget(self.settingsLayout, 'settingsLayout')
        self.addSettingsButton('pack', self.settingsLayout, 'name for the main world files')
        self.addSettingsButton('path', self.settingsLayout, 'path to export to')
        self.addSettingsButton('server_url', self.settingsLayout, 'server login url')
        self.addSettingsButton('username', self.settingsLayout, 'server login username')
        self.addSettingsButton('password', self.settingsLayout, 'server login password')
        posControls = HorizontalLayout()
        uuidControls = HorizontalLayout()
        self.settingsLayout.addWidget(posControls, 'posControls')
        self.settingsLayout.addWidget(uuidControls, 'uuidControls')
        posControls.addWidget(NumberView('OffsetX:', self.exportSettings.locX, [100, 20], [Widget.INFINITY, 20], 
            tooltip='Additional offset on the x axis.'), 'locX')
        posControls.addWidget(NumberView('OffsetY:', self.exportSettings.locY, [100, 20], [Widget.INFINITY, 20], 
            tooltip='Additional offset on the y axis.'), 'locY')
        posControls.addWidget(NumberView('OffsetZ:', self.exportSettings.locZ, [100, 20], [Widget.INFINITY, 20], 
            tooltip='Additional offset on the z axis.'), 'locZ')
        for objtype in ['Objects', 'Meshes', 'Materials', 'Textures']:
            keyName = 'regen' + objtype
            settingToggle = CheckBox(self.ToggleSettingAction(self, objtype),
				          getattr(self.exportSettings, keyName),
					  'Regen ' + objtype,
					  [100, 20],
					  tooltip='Regenerate uuids for ' + objtype)
            uuidControls.addWidget(settingToggle, keyName)

    def addRegionsPanel(self, regions, griddata):
        """
        Show available regions
        """
        vLayout = VerticalLayout()
        self.regionLayout = vLayout
        title = griddata['gridname'] + ' (' + griddata['mode'] + ')'
        vLayout.addWidget(Label(title), 'scene_key_title')
        self.screen.addWidget(Box(vLayout, griddata['gridnick']), "layout2")
        pack = SelectablePack()
        for key, region in regions.iteritems():
             selectable = SelectableRegion(0, region["id"], self, pack)
             label_text = region["name"] + " (" + str(region["x"]) + "," + str(region["y"]) + ")"
             vLayout.addWidget(SelectableLabel(selectable, region['name']),'region_'+key)
        return griddata

    def onConnectAction(self):
        """
        Connect Action
        """
        base_url = self.exportSettings.server_url
        self.addStatus("Connecting to " + base_url, IMMEDIATE)
        self.connect(base_url, self.exportSettings.username,
                     self.exportSettings.password)
        self.region_uuid = ''
        self.regionLayout = None
        try:
            regions = self.gridinfo.getRegions()
            griddata = self.gridinfo.getGridInfo()
        except:
            self.addStatus("Error: couldnt connect to " + base_url, ERROR)
            traceback.print_exc()
            return
        self.addRegionsPanel(regions, griddata)
        # create the regions panel
        self.addStatus("Connected to " + griddata['gridnick'])

    def toggleSettings(self):
        """
        Toggle the settings widget.
        """
        if self.settings_visible:
            self.vLayout.removeWidget('settingsLayout')
            self.settings_visible = False
        else:
            self.showSettings()
            self.settings_visible = True

    def addCallbackButton(self, button_name, layout, tooltip=""):
        """
        Add a button to the interface. This function prelinks
        the button to a function in the class, called like
        "on" + button_name + "Action"
        """
        cb = getattr(self, 'on' + button_name.replace(" ", "") + 'Action')
        return layout.addWidget(Button(self.CallbackAction(cb),
                           button_name, [100, 20], tooltip),
                           button_name + 'Button')


    def addButton(self, button_name, layout, tooltip=""):
        """
        Add a button to the interface. This function prelinks
        the button to an action on this clss.
        """
        action = getattr(self, button_name + 'Action')
        return layout.addWidget(Button(action(self),
                           button_name, [100, 20], tooltip),
                           button_name + 'Button')

    def addStatus(self, text, level = OK):
        """
        Add status information.
        """
        self.screen.addWidget(Box(Label(text), 'status'), 'b2rex initialized')
        if level in [ERROR, IMMEDIATE]:
            # Force a redraw
            Blender.Draw.Draw()
        else:
            Blender.Draw.Redraw(1)

    def go(self):
        """
        Start the ogre interface system
        """
        self.screen.activate()

    class ToggleSettingAction(Action):
        """
        Toggle a boolean setting.
        """
        def __init__(self, app, objtype):
            self.app = app
            self.objtype = objtype 

        def execute(self):
            keyName = 'regen' + self.objtype
            setattr(self.app.exportSettings, keyName, not getattr(self.app.exportSettings, keyName))

    class ChangeSettingAction(Action):
        """
        Change a setting from the application.
        """
        def __init__(self, app, name):
            self.app = app
            self.name = name
        def execute(self):
            setattr(self.app.exportSettings, self.name,
                    self.app.buttons[self.name].string.val)
            self.app.exportSettings.save()

    class ToggleSettingsAction(Action):
        """
        Toggle the settings panel.
        """
        def __init__(self, app):
            self.app = app

        def execute(self):
            self.app.toggleSettings()

    class CallbackAction(Action):
        """
        Connect to the opensim server.
        """
        def __init__(self, cb):
            self.cb = cb

        def execute(self):
            try:
                self.cb()
	    except:
                traceback.print_exc()
                self.app.addStatus("Error: couldnt rum. Check your settings to see they are ok", ERROR)
                return False

    class QuitAction(Action):
        """
        Quit the application.
        """
        def __init__(self, app):
            self.settings = app.exportSettings
        def execute(self):
            import Blender
            self.settings.save()
            Blender.Draw.Exit()


