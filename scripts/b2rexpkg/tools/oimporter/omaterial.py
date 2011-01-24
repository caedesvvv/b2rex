class OgreMaterial(object):
    def __init__(self, material=None):
        self.textures = []
        self.layers = {}
        self.vertex_program = ""
        self.fragment_program = ""
        self.scene_blend = None
        self.depth_ignore = False
        self.two_side = False
        self.alpha = 1.0
        self.btex = None
        self.doambient = False # XXX when to do ambient?
        self.ambient = (1.0,1.0,1.0)
        self.specular = (0.0,0.0,0.0,12.0)
        self.name = "unnamed"
        if material:
            self.parse_material(material)
    def get_base_texture(self):
        if "baseMap" in self.layers:
            return self.layers["baseMap"]
        elif self.textures:
            return self.textures[0]
        return None
    def parse_material(self, material):
        self.textures = []
        material_data = material["data"]
        basemap = False
        currlayer = None
        for line in material_data.split("\n"):
            line = line.strip()
            if line.startswith("material"):
                self.name = line.split()[1]
            elif line.startswith("ambient "):
                self.ambient = map(lambda s: float(s), line.split()[1:])
            elif line.startswith("specular "):
                self.specular = map(lambda s: float(s), line.split()[1:])
            elif line.startswith("scene_blend "):
                self.scene_blend = line.split()[1]
            elif line.startswith("depth_write "):
                depth_write = line.split()[1]
                if depth_write == "off":
                    self.depth_ignore = True
            elif line.startswith("cull_software "):
                cull_software = line.split()[1]
                if cull_software == "none":
                    self.two_side = True
            elif line.startswith("vertex_program_ref"):
                self.vertex_program = line.split()[1]
            elif line.startswith("fragment_program_ref"):
                self.fragment_program = line.split()[1]
            elif line.startswith("texture_unit"):
                currlayer = line.split()[1]
                if "baseMap" in line:
                    basemap = True
                else:
                    basemap = False
                self.layers[currlayer] = None
            elif "texture " in line and currlayer:
                split_line = line.split(" ")
                if len(split_line) == 2:
                    tex = split_line[1].strip()
                    self.textures.append(tex)
                    self.layers[currlayer] = tex
                basemap = False


if __name__ == "__main__":
    ogremat = OgreMaterial()
    f = open("../../test/pack.material")
    material = {"data":f.read()}
    f.close()
    print ogremat
    ogremat.parse_material(material)
    for a in ogremat.__dict__:
        print " *", a, ogremat.__dict__[a]

