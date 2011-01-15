import user
import os
import json

class PasswordManager(object):
    def __init__(self, realm):
        self.config = {}
        realm = "."+realm
        appdir = os.path.join(user.home, realm)
        if not os.path.exists(appdir):
            os.makedirs(appdir)
        self.appfile = os.path.join(appdir, "config")
        print "CONFIG:",self.appfile
        if os.path.exists(self.appfile):
            self.load_config()
    def load_config(self):
        f = open(self.appfile, "r")
        data = f.read()
        f.close()
        self.config = json.loads(data)

    def save_config(self):
        if self.config:
            f = open(self.appfile, "w")
            data = f.write(json.dumps(self.config))
            f.close()

    def get_credentials(self, url):
        if url in self.config:
            return self.config[url]
        return ("", "")
    def set_credentials(self, url, username, password):
        self.config[url] = (username, password)
        self.save_config()

