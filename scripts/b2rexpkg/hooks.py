"""
    Some ugly hooks to override behaviour from the ogre exporter.
"""

from collections import defaultdict

import ogredotscene
import ogremeshesexporter
from ogrepkg.base import PathName
import ogrepkg.meshexport
import ogrepkg.materialexport
import uuid
import Blender.Material

class UUIDExporter(object):
    def __init__(self):
        self.nodes = defaultdict(list)
    def add(self, section, obj_type, obj_name, obj_uuid):
        self.nodes[section].append(" <"+obj_type+" name='"+obj_name+"' uuid='"+str(obj_uuid)+"' />\n")
    def write(self, f):
        f.write("<uuids>\n")
        for obj_type in self.nodes:
            f.write("<%s>\n"%(obj_type,))
            for node in self.nodes[obj_type]:
                f.write(node)
            f.write("</%s>\n"%(obj_type,))
        f.write("</uuids>")


uuidexporter = None

def start():
    global uuidexporter
    uuidexporter = UUIDExporter()

def write(f):
    global uuidexporter
    uuidexporter.write(f)

obj_export = ogredotscene.ObjectExporter.export
mesh_export = ogremeshesexporter.MeshExporter.export
mat_export = ogrepkg.materialexport.DefaultMaterial.write
tex_export = ogrepkg.materialexport.MaterialManager.registerTextureImage

def reset_uuids(bobjs):
    for bobj in bobjs:
        if not 'opensim' in bobj.properties:
            bobj.properties['opensim'] = {}
        bobj.properties['opensim']['uuid'] = str(uuid.uuid4())

def my_obj_export(*args):
    obj = args[0]
    bobj = obj.getBlenderObject()
    name = bobj.getName()
    if not 'opensim' in bobj.properties:
        bobj.properties['opensim'] = {}
    if not 'uuid' in bobj.properties['opensim']:
        bobj.properties['opensim']['uuid'] = str(uuid.uuid4())
    uuid_str = bobj.properties['opensim']['uuid']
    uuidexporter.add('objects', 'object', name, uuid_str)
    print " * exporting obj", name, uuid_str, bobj
    sceneExporter = args[1]
    return obj_export(*args)

def my_tex_export(*args):
    materialmanager = args[0]
    bobj = args[1] # blender image
    path = bobj.filename
    texturePath = PathName(path)
    name = texturePath.basename()
    #name = bobj.getName()
    if not 'opensim' in bobj.properties:
        bobj.properties['opensim'] = {}
    if not 'uuid' in bobj.properties['opensim']:
        bobj.properties['opensim']['uuid'] = str(uuid.uuid4())
    uuid_str = bobj.properties['opensim']['uuid']
    uuidexporter.add('textures', 'texture', name, uuid_str)
    print " * exporting tex", name, uuid_str, bobj
    return tex_export(*args)


def my_mat_export(*args):
    obj = args[0]
    try:
	    bobj = obj.material
    except:
	    return mat_export(*args)
    name = obj._createName()
    if not bobj:
        uuid_str = str(uuid.uuid5(uuid.NAMESPACE_DNS, name))
        uuidexporter.add('materials', 'material', name, uuid_str)
        return mat_export(*args)
    if not 'opensim' in bobj.properties:
        bobj.properties['opensim'] = {}
    if not 'uuid' in bobj.properties['opensim']:
        bobj.properties['opensim']['uuid'] = str(uuid.uuid4())
    uuid_str = bobj.properties['opensim']['uuid']
    uuid_str = str(uuid.uuid5(uuid.UUID(uuid_str), name))
    uuidexporter.add('materials', 'material', name, uuid_str)
    print " * exporting material", name, uuid_str, bobj
    sceneExporter = args[1]
    return mat_export(*args)

def my_mesh_export(*args):
    obj = args[0]
    bobj = obj.getObject().getData(0, True)
    name = obj.getName()
    if not 'opensim' in bobj.properties:
        bobj.properties['opensim'] = {}
    if not 'uuid' in bobj.properties['opensim']:
        bobj.properties['opensim']['uuid'] = str(uuid.uuid4())
    uuid_str = bobj.properties['opensim']['uuid']
    uuidexporter.add('meshes' ,'mesh', name, uuid_str)
    print " * exporting mesh", name, uuid_str, bobj
    sceneExporter = args[1]
    return mesh_export(*args)

ogredotscene.ObjectExporter.export = my_obj_export
ogremeshesexporter.MeshExporter.export = my_mesh_export
ogrepkg.materialexport.DefaultMaterial.write = my_mat_export
ogrepkg.materialexport.MaterialManager.registerTextureImage = my_tex_export


