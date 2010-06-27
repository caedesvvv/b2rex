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

