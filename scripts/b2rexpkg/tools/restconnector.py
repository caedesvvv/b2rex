"""
 Converts xml messages coming from opensim rest into python structs.
"""

import urllib2
import base64
import binascii
import xml.etree.ElementTree as ET

class RestConnector(object):
    def __init__(self):
        self._url = None
    def connect(self, url, username="", password=""):
        self._url = url
        self._username = username
        self._password = password
        self._connect()
    def _connect(self):
        username = self._username
        password = self._password
        if username and password:
            passman = urllib2.HTTPPasswordMgrWithDefaultRealm()
            passman.add_password(None, self._url, username, password)
            self.authhandler = urllib2.HTTPBasicAuthHandler(passman)
            self.passman = passman
            self.opener = urllib2.build_opener(self.authhandler)
        else:
            self.opener = urllib2.build_opener()
    def httpGet(self, relative_url):
        self._connect()
        req = urllib2.Request(self._url + relative_url)
        req = self.opener.open(req)
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
        for prop, val in xmldata.items():
            obj[prop] = val
        if xmldata.text:
            #obj["data"] = binascii.a2b_base64(xmldata.text)
            obj["data"] = base64.decodestring(xmldata.text)
            #obj["data"] = base64.b64decode(xmldata.text)
        return obj


