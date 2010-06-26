import os

import Blender
from Blender import Registry

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
        self.rotX = BoundedValueModel(-1000.0, 1000.0, 0.0)
        self.rotY = BoundedValueModel(-1000.0, 1000.0, 0.0)
        self.rotZ = BoundedValueModel(-1000.0, 1000.0, 0.0)
        self.scale = BoundedValueModel(0.0, 1e6, 1.0);
        self.load()
        """
        return
    def getRotX(self):
        return self.rotX.getValue()
    def getRotY(self):
        return self.rotY.getValue()
    def getRotZ(self):
        return self.rotZ.getValue()
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
            a = """
            if settingsDict.has_key('fileName'):
                self.fileName = settingsDict['fileName']
            if settingsDict.has_key('fixUpAxis'):
                self.fixUpAxis = settingsDict['fixUpAxis']
            if settingsDict.has_key('doProperties'):
                self.doProperties = settingsDict['doProperties']
# float(integer) for compatibility
            if settingsDict.has_key('rotX'):
                self.rotX.setValue(float(settingsDict['rotX']))
            if settingsDict.has_key('rotY'):
                self.rotY.setValue(float(settingsDict['rotY']))
            if settingsDict.has_key('rotZ'):
                self.rotZ.setValue(float(settingsDict['rotZ']))
            if settingsDict.has_key('scale'):
                self.scale.setValue(settingsDict['scale'])
            """
    def save(self):
        """Save settings to registry.
        """
        settingsDict = {}
        settingsDict['path'] = self.path
        settingsDict['pack'] = self.pack
        settingsDict['server_url'] = self.server_url
        settingsDict['export_dir'] = self.export_dir
        Registry.SetKey('b2rex', settingsDict, True) 
        return

