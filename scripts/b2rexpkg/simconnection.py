"""
Manage user connections to opensim.
"""

import xmlrpclib

class SimConnection(object):
    def __init__(self):
        self.session_id = None
        self._con = None
        self.avatar_uuid = None

    def connect(self, url):
        """
        Connect to the xmlrpc server.
        """
        self._con = xmlrpclib.Server(url)

    def login(self, first, last, passwd):
        """
        Login with user credentials.
        """
        r = self._con.login_to_simulator({'first':first, 'last':last,
                                      'web_login_key':'unknownrex',
                                          'passwd':passwd})
        self.session_id = r['session_id']
        self.avatar_uuid = r['agent_id']
        return r

    def sceneUpload(self, region_uuid, pack_name, file_name):
        """
        Upload given scene to the server.
        """
        f = open(file_name, "r")
        r = self._con.ogrescene_upload({"AgentID": pack_name,
                                    "RegionID": region_uuid,
                                    "AvatarURL": xmlrpclib.Binary(f.read()),
                                    "PackName": pack_name})
        f.close()
        return r

    def sceneClear(self, region_uuid, pack_name):
        """
        Clear all objects from the given scene.
        """
        r = self._con.ogrescene_clear({"AgentID": pack_name,
                                   "RegionID": region_uuid,
                                   "PackName": pack_name})
        return r



if __name__ == "__main__":
    con = SimConnection()
    print con.connect("http://127.0.0.1:9000")
    print con.login("caedes", "caedes", "nemesis")
    print con.sceneClear("d9d1b302-5049-452d-b176-3a9561189ca4", "cube")
    print con.sceneUpload("d9d1b302-5049-452d-b176-3a9561189ca4", "cube",
                         "/home/caedes/groupmembers.zip")

