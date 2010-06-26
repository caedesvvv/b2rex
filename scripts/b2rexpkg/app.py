import os
import b2rexpkg
from b2rexpkg.tools.selectable import SelectablePack, SelectableRegion

import Blender

from b2rexpkg.exporter import Exporter
from b2rexpkg.settings import ExportSettings

from ogredotscene import Screen, HorizontalLayout
from ogredotscene import BoundedValueModel
from ogredotscene import VerticalLayout, Action, QuitButton
from ogredotscene import StringButton, Label, Button, Box
from ogredotscene import Selectable, SelectableLabel

class RealextendExporterApplication(object):
    def __init__(self):
        self.buttons = {}
        self.screen = Screen()
        self.exporter = Exporter()
        self.exportSettings = ExportSettings()
        vLayout = VerticalLayout()
        buttonLayout = HorizontalLayout()
        self.buttonLayout = buttonLayout
        for button_name in ['Connect', 'Export', 'Quit']:
            self.addButton(button_name, buttonLayout)

        vLayout.addWidget(buttonLayout, 'buttonPanel')
        self.screen.addWidget(Box(vLayout, 'realXtend exporter'), "layout")
        self.addSettingsButton('pack', vLayout)
        self.addSettingsButton('path', vLayout)
        self.addSettingsButton('server_url', vLayout)
        self.region_uuid = ''
        self.addStatus("status")
        self.vLayout = vLayout
    def setRegion(self, region_uuid):
        self.region_uuid = region_uuid
        self.addStatus("Region set to " + region_uuid)
    def addStatus(self, text):
        self.screen.addWidget(Box(Label(text), 'status'), 'b2rex initialized')
    def addSettingsButton(self, button_name, layout):
        val = getattr(self.exportSettings, button_name)
        self.buttons[button_name] = StringButton(val,
                                    RealextendExporterApplication.ChangeSettingAction(self,
                                                                                     button_name),
                                                 button_name+": ", [200, 20],"extra")
        layout.addWidget(self.buttons[button_name], 'buttonPanelButton' + button_name)

    def addButton(self, button_name, layout):
        action = getattr(RealextendExporterApplication, button_name + 'Action')
        return layout.addWidget(Button(action(self),
                           button_name, [100, 20], button_name),
                           button_name + 'Button')

    def go(self):
        self.screen.activate()
        return
    def packTo(self, from_path, to_zip):
        import zipfile
        zfile = zipfile.ZipFile(to_zip, "w", zipfile.ZIP_DEFLATED)
        for dirpath, dirnames, filenames in os.walk(from_path):
            for name in filenames:
                file_path = os.path.join(dirpath,  name)
                zfile.write(file_path, file_path[len(from_path+"/"):])
        zfile.close()
    class ChangeSettingAction(Action):
        def __init__(self, app, name):
            self.app = app
            self.name = name
            return
        def execute(self):
            print "change setting"
            setattr(self.app.exportSettings, self.name,
                    self.app.buttons[self.name].string.val)
            return
    class QuitAction(Action):
        def __init__(self, exportSettings):
            self.settings = exportSettings.exportSettings
            return
        def execute(self):
            import Blender
            self.settings.save()
            Blender.Draw.Exit()
            return
    class ConnectAction(Action):
        def __init__(self, exportSettings):
            self.settings = exportSettings
            return
        def execute(self):
            base_url = self.settings.exportSettings.server_url
            print "connect!!", base_url
            self.settings.exporter.connect(str(base_url))
            regions = self.settings.exporter.gridinfo.getRegions()
            vLayout = VerticalLayout()
            gridinfo = self.settings.exporter.gridinfo
            griddata = gridinfo.getGridInfo()
            #for key in griddata:
                #    vLayout.addWidget(Label(key + ": " + griddata[key]), 'scene_key_'+key)
                #print key
            title = griddata['gridname'] + ' (' + griddata['mode'] + ')'
            vLayout.addWidget(Label(title), 'scene_key_title')
            self.settings.screen.addWidget(Box(vLayout, griddata['gridnick']), "layout2")
            pack = SelectablePack()
            for key, region in regions.iteritems():
                print "region:",key
                selectable = SelectableRegion(0, region["id"], self.settings,
                                              pack)
                label_text = region["name"] + " (" + str(region["x"]) + "," + str(region["y"]) + ")"
                vLayout.addWidget(SelectableLabel(selectable, region['name']),'region_'+key)
                #self.settings.exporter.test()
            self.settings.addButton("Upload", vLayout)
            self.settings.addButton("Clear", vLayout)
            self.settings.addStatus("Connected to " + griddata['gridnick'])
            Blender.Draw.Redraw(1)
            return
    class ExportAction(Action):
        def __init__(self, app):
            self.app = app
            return
        def execute(self):
            print "Export!!"
            import tempfile, shutil
            tempfile.gettempdir()
            base_url = self.app.exportSettings.server_url
            pack_name = self.app.exportSettings.pack
            export_dir = self.app.exportSettings.export_dir
            if not export_dir:
                export_dir = tempfile.tempdir
            destfolder = os.path.join(export_dir, 'b2rx_export')
            if not os.path.exists(destfolder):
                os.makedirs(destfolder)
            else:
                shutil.rmtree(destfolder)
                os.makedirs(destfolder)
            self.app.addStatus("Export")
            self.app.exporter.export(destfolder, pack_name)
            dest_file = "/tmp/world_pack.zip"
            self.app.packTo(destfolder, dest_file)
            self.app.addStatus("Exported to " + dest_file)
            Blender.Draw.Redraw(1)
            return
    class UploadAction(Action):
        def __init__(self, exportSettings):
            self.app = exportSettings
            return
        def execute(self):
            print "Upload!!"
            base_url = self.app.exportSettings.server_url
            pack_name = self.app.exportSettings.pack
            if not self.app.region_uuid:
                self.app.addStatus("No region selected ")
                return
            print self.app.exporter.sim.sceneUpload(self.app.region_uuid,
                                                               pack_name,
                                                               "/tmp/world_pack.zip")
            self.app.addStatus("Uploaded to " + base_url)
            print "Uploaded!!"
            Blender.Draw.Redraw(1)
            return
    class ClearAction(Action):
        def __init__(self, exportSettings):
            self.app = exportSettings
            return
        def execute(self):
            base_url = self.app.exportSettings.server_url
            pack_name = self.app.exportSettings.pack
            if not self.app.region_uuid:
                self.app.addStatus("No region selected ")
                return
            print self.app.exporter.sim.sceneClear(self.app.region_uuid,
                                                               pack_name)
            self.app.addStatus("Scene cleared " + self.app.region_uuid)
            Blender.Draw.Redraw(1)
            return

