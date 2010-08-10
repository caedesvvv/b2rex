"""
Class holding all export modules.
"""

import os
import b2rexpkg
from b2rexpkg.siminfo import GridInfo
from b2rexpkg.simconnection import SimConnection
from b2rexpkg.ogre_exporter import OgreExporter
from b2rexpkg.hooks import reset_uuids
import Blender

class Exporter(object):
    def __init__(self):
        # rest
        self.gridinfo = GridInfo()
        self.sim = SimConnection()
        self.ogre = OgreExporter()

    def connect(self, base_url):
        """
        Connect to an opensim instance
        """
        self.gridinfo.connect(base_url)
        print self.sim.connect(base_url)

    def test(self):
        """
        Api tests
        """
        print self.gridinfo.getGridInfo()["gridnick"]
        regions = self.gridinfo.getRegions()
        for id in regions:
            region = regions[id]
            print " *", region["name"], region["x"], region["y"], id

        # xmlrpc
        print self.sim.login("caedes", "caedes", "pass")
        print self.sim.sceneClear("d9d1b302-5049-452d-b176-3a9561189ca4",
                                         "cube")
        print self.sim.sceneUpload("d9d1b302-5049-452d-b176-3a9561189ca4",
                              "cube",
                              "/home/caedes/groupmembers.zip")

    def export(self, path, pack_name, offset, exportSettings):
        """
        Export the scene to a zipfile.
        """
        b2rexpkg.start()
	if exportSettings.regenMaterials:
            reset_uuids(Blender.Material.Get())
	if exportSettings.regenObjects:
            reset_uuids(Blender.Object.Get())
	if exportSettings.regenTextures:
            reset_uuids(Blender.Texture.Get())
	if exportSettings.regenMeshes:
            reset_uuids(Blender.Mesh.Get())
        self.ogre.export(path, pack_name, offset)
        f = open(os.path.join(path, pack_name + ".uuids"), 'w')
        b2rexpkg.write(f)
        f.close()

