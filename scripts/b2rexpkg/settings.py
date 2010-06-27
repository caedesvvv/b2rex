import os

import Blender
from Blender import Registry

from ogredotscene import BoundedValueModel

#from ogredotscene import BoundedValueModel
class ExportSettings:
    """Global export settings.
    """
    def __init__(self):
        self.path = os.path.dirname(Blender.Get('filename'))
        self.pack = 'pack'
        self.server_url = 'http://delirium:9000'
        self.export_dir = ''
        self.load()
        """
        self.fileName = ''
        self.fixUpAxis = 0
        self.doProperties = 0
        self.scale = BoundedValueModel(0.0, 1e6, 1.0);
        self.load()
        """
        self.locX = BoundedValueModel(-10000.0, 10000.0, 128.0)
        self.locY = BoundedValueModel(-10000.0, 10000.0, 128.0)
        self.locZ = BoundedValueModel(-1000.0, 1000.0, 20.0)
        return
    def getLocX(self):
        return self.locX.getValue()
    def getLocY(self):
        return self.locY.getValue()
    def getLocZ(self):
        return self.locZ.getValue()
    def getScale(self):
        return self.scale.getValue()
    def load(self):
        """Load settings from registry, if available.
        """
        settingsDict = Registry.GetKey('b2rex', True)
        if settingsDict:
            if settingsDict.has_key('path'):
                self.path = settingsDict['path']
            if settingsDict.has_key('pack'):
                self.pack = settingsDict['pack']
            if settingsDict.has_key('server_url'):
                self.server_url = settingsDict['server_url']
            if settingsDict.has_key('export_dir'):
                self.export_dir = settingsDict['export_dir']
            if settingsDict.has_key('locX'):
                self.locX.setValue(float(settingsDict['locX']))
            if settingsDict.has_key('locY'):
                self.locY.setValue(float(settingsDict['locY']))
            if settingsDict.has_key('locZ'):
                self.locZ.setValue(float(settingsDict['locZ']))
    def save(self):
        """Save settings to registry.
        """
        settingsDict = {}
        settingsDict['path'] = self.path
        settingsDict['pack'] = self.pack
        settingsDict['server_url'] = self.server_url
        settingsDict['export_dir'] = self.export_dir
        settingsDict['locX'] = self.locX
        settingsDict['locY'] = self.locY
        settingsDict['locZ'] = self.locZ
        Registry.SetKey('b2rex', settingsDict, True) 
        return

