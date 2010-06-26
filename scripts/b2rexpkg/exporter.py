#!BPY

"""
Name: 'RealXtend Exporter'
Blender: 249
Group: 'Export'
Tooltip: 'Exports the current scene to RealXtend server'
"""

__author__ = ['Pablo Martin']
__version__ = '0.1'
__url__ = ['B2rex Sim, http://sim.lorea.org',
               'B2rex forum, http://sim.lorea.org/b2rex']
__bpydoc__ = "Please see the external documentation that comes with the script."

from b2rexpkg.siminfo import GridInfo
from b2rexpkg.simconnection import SimConnection
from b2rexpkg.ogre_exporter import OgreExporter

class Exporter(object):
    def __init__(self):
        # rest
        self.gridinfo = GridInfo()
        self.sim = SimConnection()
        self.ogre = OgreExporter()
    def connect(self, base_url):
        self.gridinfo.connect(base_url)
        print self.sim.connect(base_url)
    def test(self):
        print self.gridinfo.getGridInfo()["gridnick"]
        regions = self.gridinfo.getRegions()
        for id in regions:
            region = regions[id]
            print " *", region["name"], region["x"], region["y"], id

        # xmlrpc
        print self.sim.login("caedes", "caedes", "nemesis")
        print self.sim.sceneClear("d9d1b302-5049-452d-b176-3a9561189ca4",
                                         "cube")
        print self.sim.sceneUpload("d9d1b302-5049-452d-b176-3a9561189ca4",
                              "cube",
                              "/home/caedes/groupmembers.zip")
    def export(self, path, pack_name):
        self.ogre.export(path, pack_name)

