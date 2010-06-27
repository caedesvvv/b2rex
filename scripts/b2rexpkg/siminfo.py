import sys
import urllib2
import xml.etree.ElementTree as ET

from .tools.restconnector import RestConnector


class GridInfo(RestConnector):
    def __init__(self):
        RestConnector.__init__(self)
        self._regions = {}
    def getGridInfo(self):
        self.gridinfo = self.httpObjGet("/get_grid_info")
        return self.gridinfo
    def getRegions(self):
        xmldata = self.httpXmlGet("/admin/regions/")
        for uuid in xmldata.findall('uuid'):
            region = self.httpObjGet("/admin/regions/"+uuid.text, "region_")
            self._regions[region['id']] = region
            map_url = self._url + "/index.php?method=regionImage"+region['id'].replace('-','')
            self._regions[region['id']]['map'] = map_url
        return self._regions

if __name__ == '__main__':
    base_url = "http://delirium:9000"
    gridinfo = GridInfo()
    gridinfo.connect(base_url)
    print gridinfo.getGridInfo()["gridnick"]
    regions = gridinfo.getRegions()
    for id in regions:
        region = regions[id]
        print " *", region["name"], region["x"], region["y"], id

