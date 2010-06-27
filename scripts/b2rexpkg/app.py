"""
Main b2rex application class
"""

import os
import traceback
import b2rexpkg
from b2rexpkg.tools.selectable import SelectablePack, SelectableRegion

import Blender

from b2rexpkg.exporter import Exporter
from b2rexpkg.settings import ExportSettings

from ogredotscene import Screen, HorizontalLayout
from ogredotscene import NumberView, Widget, CheckBox
from ogredotscene import VerticalLayout, Action, QuitButton
from ogredotscene import StringButton, Label, Button, Box
from ogredotscene import Selectable, SelectableLabel

ERROR = 0
OK = 1
IMMEDIATE = 2

class RealxtendExporterApplication(object):
    def __init__(self):
        self.buttons = {}
        self.screen = Screen()
        self.exporter = Exporter()
        self.exportSettings = ExportSettings()
	self.settings_visible = False
        self.region_uuid = ''
	self.regionLayout = None
	self.initGui()
        self.addStatus("b2rex started")

    def initGui(self):
        """
        Initialize the interface system.
        """
        self.vLayout = VerticalLayout()
        self.buttonLayout = HorizontalLayout()
        self.addButton('Connect', self.buttonLayout, 'Connect to opensim server. Needed if you want to upload worlds directly.')
        self.addButton('Export', self.buttonLayout, 'Export to disk')
        self.addButton('Quit', self.buttonLayout, 'Quit the exporter')
        settingsButton = CheckBox(RealxtendExporterApplication.ToggleSettingsAction(self),
			          self.settings_visible,
				  'Settings',
				  [100, 20],
				  tooltip='Show Settings')
        self.buttonLayout.addWidget(settingsButton, 'SettingsButton')
        self.vLayout.addWidget(self.buttonLayout, 'buttonPanel')
        self.screen.addWidget(Box(self.vLayout, 'realXtend exporter'), "layout")

    def showSettings(self):
        """
        Create the settings widgets.
        """
        self.settingsLayout = VerticalLayout()
        self.vLayout.addWidget(self.settingsLayout, 'settingsLayout')
        self.addSettingsButton('pack', self.settingsLayout, 'name for the main world files')
        self.addSettingsButton('path', self.settingsLayout, 'path to export to')
        self.addSettingsButton('server_url', self.settingsLayout, 'server login url')
        posControls = HorizontalLayout()
        self.settingsLayout.addWidget(posControls, 'posControls')
        posControls.addWidget(NumberView('OffsetX:', self.exportSettings.locX, [100, 20], [Widget.INFINITY, 20], 
            tooltip='Additional offset on the x axis.'), 'locX')
        posControls.addWidget(NumberView('OffsetY:', self.exportSettings.locY, [100, 20], [Widget.INFINITY, 20], 
            tooltip='Additional offset on the y axis.'), 'locY')
        posControls.addWidget(NumberView('OffsetZ:', self.exportSettings.locZ, [100, 20], [Widget.INFINITY, 20], 
            tooltip='Additional offset on the z axis.'), 'locZ')

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

    def setRegion(self, region_uuid):
        """
        Set the selected region.
        """
        if not self.region_uuid:
            # setting for the first time
            hLayout = HorizontalLayout()
            self.regionLayout.addWidget(hLayout, "regionButtons")
            self.addButton("ExportUpload", hLayout, 'Export scene and upload to opensim region')
            self.addButton("Upload", hLayout, 'Upload previously exported scene')
            self.addButton("Clear", hLayout, 'Clear the selected region in the opensim server')
        self.region_uuid = region_uuid
        self.addStatus("Region set to " + region_uuid)

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

    def addSettingsButton(self, button_name, layout, tooltip=""):
        """
        Create a settings string button.
        """
        val = getattr(self.exportSettings, button_name)
        self.buttons[button_name] = StringButton(val,
                                    RealxtendExporterApplication.ChangeSettingAction(self,
                                                                                     button_name),
                                                 button_name+": ", [200, 20], tooltip)
        layout.addWidget(self.buttons[button_name], 'buttonPanelButton' + button_name)

    def addButton(self, button_name, layout, tooltip=""):
        """
        Add a button to the interface. This function prelinks
        the button to an action on this clss.
        """
        action = getattr(RealxtendExporterApplication, button_name + 'Action')
        return layout.addWidget(Button(action(self),
                           button_name, [100, 20], tooltip),
                           button_name + 'Button')

    def go(self):
        """
        Start the ogre interface system
        """
        self.screen.activate()

    def packTo(self, from_path, to_zip):
        """
        Pack a directory to a file.
        """
        import zipfile
        zfile = zipfile.ZipFile(to_zip, "w", zipfile.ZIP_DEFLATED)
        for dirpath, dirnames, filenames in os.walk(from_path):
            for name in filenames:
                file_path = os.path.join(dirpath,  name)
                zfile.write(file_path, file_path[len(from_path+"/"):])
        zfile.close()

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

    class ConnectAction(Action):
        """
        Connect to the opensim server.
        """
        def __init__(self, app):
            self.app = app
        def execute(self):
            try:
                self.connect()
	    except:
                traceback.print_exc()
                self.app.addStatus("Error: couldnt connect. Check your settings to see they are ok", ERROR)
                return False
        def connect(self):
            base_url = self.app.exportSettings.server_url
            self.app.addStatus("Connecting to " + base_url, IMMEDIATE)
            self.app.exporter.connect(base_url)
            self.app.region_uuid = ''
	    self.app.regionLayout = None
            try:
                regions = self.app.exporter.gridinfo.getRegions()
            except:
                self.app.addStatus("Error: couldnt connect to " + base_url, ERROR)
                return
            vLayout = VerticalLayout()
	    self.app.regionLayout = vLayout
            gridinfo = self.app.exporter.gridinfo
            griddata = gridinfo.getGridInfo()
            #for key in griddata:
                #    vLayout.addWidget(Label(key + ": " + griddata[key]), 'scene_key_'+key)
                #print key
            title = griddata['gridname'] + ' (' + griddata['mode'] + ')'
            vLayout.addWidget(Label(title), 'scene_key_title')
            self.app.screen.addWidget(Box(vLayout, griddata['gridnick']), "layout2")
            pack = SelectablePack()
            for key, region in regions.iteritems():
                selectable = SelectableRegion(0, region["id"], self.app,
                                              pack)
                label_text = region["name"] + " (" + str(region["x"]) + "," + str(region["y"]) + ")"
                vLayout.addWidget(SelectableLabel(selectable, region['name']),'region_'+key)
            self.app.addStatus("Connected to " + griddata['gridnick'])
            return

    class ToggleSettingsAction(Action):
        """
        Toggle the settings panel.
        """
        def __init__(self, app):
            self.app = app
        def execute(self):
            self.app.toggleSettings()

    class ExportUploadAction(Action):
        """
        Export and upload selected objects.
        """
        def __init__(self, app):
            self.app = app
        def execute(self):
            exportAction = RealxtendExporterApplication.ExportAction(self.app)
            uploadAction = RealxtendExporterApplication.UploadAction(self.app)
            if not exportAction.execute() == False:
                Blender.Draw.Draw()
                uploadAction.execute()

    class ExportAction(Action):
        """
        Export selected objects.
        """
        def __init__(self, app):
            self.app = app
            return
        def execute(self):
            try:
                self.export()
            except:
                traceback.print_exc()
                self.app.addStatus("Error: couldnt export", ERROR)
                return False
        def export(self):
            import tempfile, shutil
            tempfile.gettempdir()
            base_url = self.app.exportSettings.server_url
            path = self.app.exportSettings.path
            pack_name = self.app.exportSettings.pack
            export_dir = path
            self.app.addStatus("Exporting to " + path, IMMEDIATE)
            if not export_dir:
                export_dir = tempfile.tempdir
            destfolder = os.path.join(export_dir, 'b2rx_export')
            if not os.path.exists(destfolder):
                os.makedirs(destfolder)
            else:
                shutil.rmtree(destfolder)
                os.makedirs(destfolder)
            x = self.app.exportSettings.locX.getValue()
            y = self.app.exportSettings.locY.getValue()
            z = self.app.exportSettings.locZ.getValue()
            self.app.exporter.export(destfolder, pack_name, [x, y, z])
            dest_file = os.path.join(export_dir, "world_pack.zip")
            self.app.packTo(destfolder, dest_file)
            self.app.addStatus("Exported to " + dest_file)
            return

    class UploadAction(Action):
        """
        Upload a previously exported world.
        """
        def __init__(self, exportSettings):
            self.app = exportSettings
        def execute(self):
            try:
                self.upload()
            except:
                traceback.print_exc()
                self.app.addStatus("Error: couldnt upload", ERROR)
                return False
        def upload(self):
            base_url = self.app.exportSettings.server_url
            pack_name = self.app.exportSettings.pack
            if not self.app.region_uuid:
                self.app.addStatus("Error: No region selected ", ERROR)
                return
            self.app.addStatus("Uploading to " + base_url, IMMEDIATE)
            res = self.app.exporter.sim.sceneUpload(self.app.region_uuid,
                                                               pack_name,
                                                               "/tmp/world_pack.zip")
	    if res.has_key('success') and res['success'] == True:
                self.app.addStatus("Uploaded to " + base_url)
            else:
                self.app.addStatus("Error: Something went wrong uploading", ERROR)

    class ClearAction(Action):
        """
        Clear the selected scene.
        """
        def __init__(self, app):
            self.app = app
        def execute(self):
            try:
                self.clear()
            except:
                traceback.print_exc()
                self.app.addStatus("Error: couldnt clear", ERROR)
                return False
        def clear(self):
            base_url = self.app.exportSettings.server_url
            pack_name = self.app.exportSettings.pack
            if not self.app.region_uuid:
                self.app.addStatus("No region selected ")
                return
            self.app.exporter.sim.sceneClear(self.app.region_uuid,
                                                               pack_name)
            self.app.addStatus("Scene cleared " + self.app.region_uuid)

