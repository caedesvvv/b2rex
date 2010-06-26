import ogremeshesexporter as meshexport
import ogredotscene as sceneexport
from ogrepkg.base import Log, View
from b2rex import OgreExporter

if __name__ == '__main__':
    global_path = "/tmp/export2"
    pack_name = "cube2"
    exporter = OgreExporter()
    exporter.export(global_path, pack_name)
