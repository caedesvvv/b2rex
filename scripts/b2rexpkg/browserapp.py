from .baseapp import BaseApplication
from .baseapp import HorizontalLayout, Box, Label
from .baseapp import IMMEDIATE

from b2rexpkg.simconnection import SimConnection
from b2rexpkg.importer import Importer

import Blender

class RealxtendBrowserApplication(BaseApplication):
    def __init__(self):
        BaseApplication.__init__(self, "RealXtend Browser")
        self.addStatus("b2rex started")

    def setRegion(self, regionuuid):
        self.region_uuid = regionuuid
        vLayout = HorizontalLayout()
        #self.regionLayout = vLayout
        #title = griddata['gridname'] + ' (' + griddata['mode'] + ')'
        #vLayout.addWidget(Label(title), 'scene_key_title')
        self.screen.addWidget(Box(vLayout, "Browser"), "browser")
        self.addCallbackButton('Next', vLayout, 'Next object.')
        self.addCallbackButton('Previous', vLayout, 'Previous object.')
        vLayout.addWidget(Label("press next to start"), "browser_info")
        self.setScene()
        self.browserLayout = vLayout
        self.browserInitialized = False

    def setScene(self):
        try:
            self.scene = Blender.Scene.Get("b2rexbrowser")
        except:
            self.scene = Blender.Scene.New("b2rexbrowser")
        self.scene.makeCurrent()

    def clearScene(self):
        for obj in list(self.scene.objects):
            self.scene.unlink(obj)

    def initializeBrowser(self):
        self.importer = Importer(self.gridinfo)
        con = SimConnection()
        con.connect(self.gridinfo._url)
        region_id = self.region_uuid
        scenedata = con._con.ogrescene_list({"RegionID":region_id})
        self.scenedata = scenedata['res']
        self.browserkeys = self.scenedata.keys()
        self.browserIdx = -1
        self.browserInitialized = True

    def loadGroup(self, name, group):
        self.setScene()
        self.clearScene()
        self.browserLayout.addWidget(Label(name), "browser_info")
        obj = self.importer.import_group(name, group, 10, load_materials=False)
        if obj:
           obj.setLocation(0.0,0.0,0.0)
           obj.select(True)

    def onNextAction(self):
        if not self.browserInitialized:
            self.initializeBrowser()
        self.browserIdx += 1 % len(self.browserkeys)
        name = self.browserkeys[self.browserIdx]
        group = self.scenedata[name]
        self.addStatus("loading next", IMMEDIATE)
        try:
            self.loadGroup(name, group)
            self.addStatus("loaded next")
        except Exception as e:
            self.addStatus("error loading next: "+str(e))

    def onPreviousAction(self):
        if not self.browserInitialized:
            self.initializeBrowser()
        self.browserIdx -= 1 % len(self.browserkeys)
        name = self.browserkeys[self.browserIdx]
        group = self.scenedata[name]
        self.addStatus("loading previous", IMMEDIATE)
        try:
            self.loadGroup(name, group)
            self.addStatus("loaded previous")
        except Exception as e:
            self.addStatus("error loading previous: "+str(e))


