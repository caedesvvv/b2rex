"""
Main b2rex application class
"""

import os
import tempfile, shutil
import traceback
import b2rexpkg

import Blender

from b2rexpkg.exporter import Exporter
from b2rexpkg.importer import Importer
from b2rexpkg.settings import ExportSettings

from ogredotscene import Screen, HorizontalLayout
from ogredotscene import NumberView, Widget, CheckBox
from ogredotscene import VerticalLayout, Action, QuitButton
from ogredotscene import StringButton, Label, Button, Box

ERROR = 0
OK = 1
IMMEDIATE = 2

from baseapp import BaseApplication

class RealxtendExporterApplication(Exporter, Importer, BaseApplication):
    def __init__(self):
        self.region_uuid = ''
        self.regionLayout = None
        Exporter.__init__(self)
        Importer.__init__(self, self.gridinfo)
        BaseApplication.__init__(self)
        self.addStatus("b2rex started")

    def initGui(self, title=None):
        """
        Initialize the interface system.
        """
        if not title:
            title = 'realXtend exporter'
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
            settingToggle = CheckBox(RealxtendExporterApplication.ToggleSettingAction(self, objtype),
				          getattr(self.exportSettings, keyName),
					  'Regen ' + objtype,
					  [100, 20],
					  tooltip='Regenerate uuids for ' + objtype)
            uuidControls.addWidget(settingToggle, keyName)
 
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
            self.addButton("Check", hLayout, 'Check blend file against region contents')
            self.addButton("Sync", hLayout, 'Sync blend file objects from region')
            self.addButton("Import", hLayout, 'Import all objects from current region')
        self.region_uuid = region_uuid
        self.addStatus("Region set to " + region_uuid)
        self.regionInfoLayout = VerticalLayout()
        self.regionLayout.addWidget(self.regionInfoLayout, "regionInfoLayout")
        self.regionInfoLayout.addWidget(Label(" \n"),
                                        "regionInfoSpace")
        self.regionInfoLayout.addWidget(Label("\n"+region_uuid), "regionInfo")

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

    def checkAction(self):
        text = self.check_region(self.region_uuid)
        self.regionInfoLayout = VerticalLayout()
        self.regionLayout.addWidget(self.regionInfoLayout, "regionInfoLayout")
        for idx, line in enumerate(text):
            self.regionInfoLayout.addWidget(Label(line),
                                        "regionInfoSpace"+str(idx))
        Blender.Draw.Draw()

    def syncAction(self):
        text = self.sync_region(self.region_uuid)
        Blender.Draw.Draw()

    def importAction(self):
        text = self.import_region(self.region_uuid)
        Blender.Draw.Draw()

    def clearAction(self):
        """
        Clear Action
        """
        base_url = self.exportSettings.server_url
        pack_name = self.exportSettings.pack
        if not self.region_uuid:
            self.addStatus("No region selected ")
            return
        self.sim.sceneClear(self.region_uuid, pack_name)
        self.addStatus("Scene cleared " + self.region_uuid)

    def uploadAction(self):
        """
        Upload Action
        """
        base_url = self.exportSettings.server_url
        pack_name = self.exportSettings.pack
        if not self.region_uuid:
            self.addStatus("Error: No region selected ", ERROR)
            return
        self.addStatus("Uploading to " + base_url, IMMEDIATE)
        export_dir = self.getExportDir()
        res = self.sim.sceneUpload(self.region_uuid,
                                                           pack_name,
                                   os.path.join(export_dir, "world_pack.zip"))
        if res.has_key('success') and res['success'] == True:
            self.addStatus("Uploaded to " + base_url)
        else:
            self.addStatus("Error: Something went wrong uploading", ERROR)

    def connectAction(self):
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

    def exportAction(self):
        """
        Export Action
        """
        tempfile.gettempdir()
        base_url = self.exportSettings.server_url
        pack_name = self.exportSettings.pack
        export_dir = self.getExportDir()

        self.addStatus("Exporting to " + export_dir, IMMEDIATE)

        destfolder = os.path.join(export_dir, 'b2rx_export')
        if not os.path.exists(destfolder):
            os.makedirs(destfolder)
        else:
            shutil.rmtree(destfolder)
            os.makedirs(destfolder)

        x = self.exportSettings.locX.getValue()
        y = self.exportSettings.locY.getValue()
        z = self.exportSettings.locZ.getValue()

        self.export(destfolder, pack_name, [x, y, z], self.exportSettings)
        dest_file = os.path.join(export_dir, "world_pack.zip")
        self.packTo(destfolder, dest_file)

        self.addStatus("Exported to " + dest_file)

    def getExportDir(self):
        export_dir = self.exportSettings.path
        if not export_dir:
            export_dir = tempfile.tempdir
        return export_dir

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
                self.app.exportAction()
            except:
                traceback.print_exc()
                self.app.addStatus("Error: couldnt export", ERROR)
                return False

    class UploadAction(Action):
        """
        Upload a previously exported world.
        """
        def __init__(self, exportSettings):
            self.app = exportSettings

        def execute(self):
            try:
                self.app.uploadAction()
            except:
                traceback.print_exc()
                self.app.addStatus("Error: couldnt upload", ERROR)
                return False

    class ClearAction(Action):
        """
        Clear the selected scene.
        """
        def __init__(self, app):
            self.app = app

        def execute(self):
            try:
                self.app.clearAction()
            except:
                traceback.print_exc()
                self.app.addStatus("Error: couldnt clear", ERROR)
                return False
    class CheckAction(Action):
        """
        Check the selected scene.
        """
        def __init__(self, app):
            self.app = app

        def execute(self):
            try:
                self.app.checkAction()
            except:
                traceback.print_exc()
                self.app.addStatus("Error: couldnt check", ERROR)
                return False
    class SyncAction(Action):
        """
        Check the selected scene.
        """
        def __init__(self, app):
            self.app = app

        def execute(self):
            try:
                self.app.syncAction()
            except:
                traceback.print_exc()
                self.app.addStatus("Error: couldnt sync", ERROR)
                return False
    class ImportAction(Action):
        """
        Check the selected scene.
        """
        def __init__(self, app):
            self.app = app

        def execute(self):
            try:
                self.app.importAction()
            except:
                traceback.print_exc()
                self.app.addStatus("Error: couldnt import", ERROR)
                return False

