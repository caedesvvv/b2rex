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
                                          'passwd':passwd,
                                          'start':'home'})
	print r
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
    #a = con._con.search_for_region_by_name({"name":"Taiga"})
    #print con._con.user_alert({"name":"Taiga"})
    #print con._con.check({})
    scenedata = con._con.ogrescene_list({"RegionID":"0a1b14b9-ca02-481d-bf77-9cbeca1ab050"})
    for groupid, scenegroup in scenedata['res'].iteritems():
        print " *", groupid, scenegroup
        if "materials" in scenegroup:
            for mat in scenegroup['materials'].values():
                if isinstance(mat, xmlrpclib.Binary):
                    #                   print mat.decode()
                    print mat.data
    #a = con._con.admin_create_region({"password":"unknownrex",
    #                                  "region_name":"test2", "region_master_first":"caedes","region_master_last":"caedes","region_master_password":"caedes","external_address":"127.0.0.1","listen_ip":"127.0.0.1","listen_port":9002,"region_x":999,"region_y":1001})
    #con._con.admin_delete_region({"password":"unknownrex",
    #                              "region_name":a["region_name"]})
    #print con.sceneClear("d9d1b302-5049-452d-b176-3a9561189ca4", "cube")
    #print con.sceneUpload("d9d1b302-5049-452d-b176-3a9561189ca4", "cube",
    #                     "/home/caedes/groupmembers.zip")

