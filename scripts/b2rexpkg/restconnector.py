import urllib2
import xml.etree.ElementTree as ET

class RestConnector(object):
    def __init__(self):
        self._url = None
    def connect(self, url):
        self._url = url
    def httpGet(self, relative_url):
        req = urllib2.Request(self._url + relative_url)
        req = urllib2.urlopen(req)
        return req.read()
    def httpXmlGet(self, relative_url):
        data = self.httpGet(relative_url)
        return ET.fromstring(data)
    def httpObjGet(self, relative_url, subst=""):
        xmldata = self.httpXmlGet(relative_url)
        return self.mapToDict(xmldata, subst)
    def mapToDict(self, xmldata, subst=""):
        obj = {}
        for prop in xmldata.getchildren():
            obj[prop.tag[len(subst):]] = prop.text
        return obj


