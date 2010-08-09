import Blender

from ogrepkg.materialexport import GameEngineMaterial, clamp, DefaultMaterial
from ogrepkg.base import PathName, indent


class RexMaterialExporter(GameEngineMaterial):
	def __init__(self, manager, blenderMesh, blenderFace, colouredAmbient):
		GameEngineMaterial.__init__(self, manager, blenderMesh, blenderFace, colouredAmbient)
		self.mesh = blenderMesh
		self.face = blenderFace
		self.colouredAmbient = colouredAmbient
		# check if a Blender material is assigned
		try:
			blenderMaterial = self.mesh.materials[self.face.mat]
		except:
			blenderMaterial = None
		self.fp_parms = {}
		self.vp_parms = {}
		self.alpha = 1.0
		self.shadows = False # doesnt work with rex for now..
		self.material = blenderMaterial
		DefaultMaterial.__init__(self, manager, self._createName())
		self._parseMaterial(blenderMaterial)
		return

	def getAutodetect(self):
		mat = self.material
		if not mat:
			return True
		if not 'opensim' in mat.properties:
			return True
		if not 'autodetect' in mat.properties['opensim']:
			return True
		return mat.properties['opensim']['autodetect']

	def toggleAutodetect(self):
		mat = self.material
		if not 'opensim' in mat.properties:
			mat.properties['opensim'] = {}
		if not 'autodetect' in mat.properties['opensim']:
			mat.properties['opensim']['autodetect'] = False
		else:
			mat.properties['opensim']['autodetect'] = not mat.properties['opensim']['autodetect']
		if mat.properties['opensim']['autodetect'] and 'shader' in mat.properties['opensim']:
			del mat.properties['opensim']['shader']
		self._parseShader(mat)

	def setShader(self, shader):
		mat = self.material
		if not 'opensim' in mat.properties:
			mat.properties['opensim'] = {}
		mat.properties['opensim']['shader'] = shader
	def getShader(self):
		mat = self.material
		if not 'opensim' in mat.properties or not 'shader' in mat.properties['opensim']:
			return ""
		return mat.properties['opensim']['shader']

	def _parseMaterial(self, mat):
		# alpha
		if mat:
			self.alpha = mat.getAlpha()
		self._parseShader(mat)

	def _parseShader(self, mat):
		fp_parms = {}
		vp_parms = {}
		textures = self.getTextureLayers(mat)
		nortex = textures['nor']
		disptex = textures['disp']
		spectex = textures['spec']
		ambtex = textures['amb']
		reftex = textures['ref']
		if textures['disp'] and textures['spec'] and textures['nor']:
			shader = "rex/DiffSpecmapNormalParallax"
			fp_parms['specularPower'] = 0.8
		elif textures['nor'] and textures['amb']:
			shader = "rex/DiffNormalLightmap"
		elif nortex and nortex.tex and nortex.tex.getImage():
			if spectex:
				shader = "rex/DiffSpecmapNormal"
				fp_parms['specularPower'] = 0.8
			else:
				shader = "rex/DiffNormal"
		elif reftex and spectex:
			shader = "rex/DiffSpecmapRefl"
			fp_parms['specularPower'] = 0.8
		elif reftex:
			fp_parms['opacity'] = alpha
			shader = "rex/DiffReflAlpha"
		else:
			shader = "rex/Diff"
		if 'opensim' in mat.properties and 'shader' in mat.properties['opensim'] and 'autodetect' in mat.properties['opensim'] and not mat.properties['opensim']['autodetect']:
			shader = mat.properties['opensim']['shader']

		self.shader = shader
		self.fp_parms = fp_parms

	def _writeShaderPrograms(self, f):
		shader = self.shader
		fp_parms = self.fp_parms
		vp_parms = self.vp_parms
		f.write(indent(3)+"vertex_program_ref " + shader + "VP\n")
		f.write(indent(3)+"{\n")
		for par, value in vp_parms.iteritems():
			par_type = "float"
			f.write(indent(4)+"param_named %s %s %s\n"%(par, par_type, value))
		f.write(indent(3)+"}\n")
		f.write(indent(3)+"fragment_program_ref " + shader + "FP\n")
		f.write(indent(3)+"{\n")
		for par, value in fp_parms.iteritems():
			par_type = "float"
			f.write(indent(4)+"param_named %s %s %s\n"%(par, par_type, value))
		f.write(indent(3)+"}\n")

	def writeTechniques(self, f):
		mat = self.material
		if (not(mat)
			and not(self.mesh.vertexColors)
			and not(self.mesh.vertexUV or self.mesh.faceUV)):
			# default material
			DefaultMaterial.writeTechniques(self, f)
		else:
			self.writeRexTechniques(f, mat)

	def _writePassContents(self, f, mat):
		f.write(indent(3)+"iteration once\n")

		# shader programs
		self._writeShaderPrograms(f)

		# material colors
		self._writeMaterialParameters(f, mat)

		# texture units
		self._writeTextureUnits(f, mat)

	def _writeMaterialParameters(self, f, mat):
		# alpha
		if self.alpha < 1.0:
			f.write(indent(3)+"scene_blend alpha_blend\n")
			f.write(indent(3)+"depth_write off\n")

		# ambient
		# (not used in Blender's game engine)
		if mat:
			if (not(mat.mode & Blender.Material.Modes["TEXFACE"])
				and not(mat.mode & Blender.Material.Modes["VCOL_PAINT"])
				and (self.colouredAmbient)):
				ambientRGBList = mat.rgbCol
			else:
				ambientRGBList = [1.0, 1.0, 1.0]
			# ambient <- amb * ambient RGB
			ambR = clamp(mat.amb * ambientRGBList[0])
			ambG = clamp(mat.amb * ambientRGBList[1])
			ambB = clamp(mat.amb * ambientRGBList[2])
			f.write(indent(3)+"ambient %f %f %f\n" % (ambR, ambG, ambB))
		# diffuse
		# (Blender's game engine uses vertex colours
		#  instead of diffuse colour.
		#
		#  diffuse is defined as
		#  (mat->r, mat->g, mat->b)*(mat->emit + mat->ref)
		#  but it's not used.)
		if self.mesh.vertexColors and False:
			# we ignore this possibility for now...
			# Blender does not handle "texface" mesh with vertex colours
			f.write(indent(3)+"diffuse vertexcolour\n")
		elif mat:
			if (not(mat.mode & Blender.Material.Modes["TEXFACE"])
				and not(mat.mode & Blender.Material.Modes["VCOL_PAINT"])):
				# diffuse <- rgbCol
				diffR = clamp(mat.rgbCol[0])
				diffG = clamp(mat.rgbCol[1])
				diffB = clamp(mat.rgbCol[2])
				f.write(indent(3)+"diffuse %f %f %f\n" % (diffR, diffG, diffB))
			elif (mat.mode & Blender.Material.Modes["VCOL_PAINT"]):
				f.write(indent(3)+"diffuse vertexcolour\n")

			# specular <- spec * specCol, hard/4.0
			specR = clamp(mat.spec * mat.specCol[0])
			specG = clamp(mat.spec * mat.specCol[1])
			specB = clamp(mat.spec * mat.specCol[2])
			specShine = mat.hard/4.0
			f.write(indent(3)+"specular %f %f %f %f\n" % (specR, specG, specB, specShine))
			# emissive
			# (not used in Blender's game engine)
			if(not(mat.mode & Blender.Material.Modes["TEXFACE"])
				and not(mat.mode & Blender.Material.Modes["VCOL_PAINT"])):
				# emissive <-emit * rgbCol
				emR = clamp(mat.emit * mat.rgbCol[0])
				emG = clamp(mat.emit * mat.rgbCol[1])
				emB = clamp(mat.emit * mat.rgbCol[2])
				##f.write(indent(3)+"emissive %f %f %f\n" % (emR, emG, emB))

	def _writeTextureUnits(self, f, mat):
		textures = self.getTextureLayers(mat)
		spectex = textures['spec']
		nortex = textures['nor']
		reftex = textures['ref']
		ambtex = textures['amb']
		disptex = textures['disp']
		shader = self.shader
		# texture units
		if self.mesh.faceUV:
			# mesh has texture values, resp. tface data
			# scene_blend <- transp
			if (self.face.transp == Blender.Mesh.FaceTranspModes["ALPHA"]):
				f.write(indent(3)+"scene_blend alpha_blend \n")
			elif (self.face.transp == Blender.NMesh.FaceTranspModes["ADD"]):
				f.write(indent(3)+"scene_blend add\n")
			# cull_hardware/cull_software
			if (self.face.mode & Blender.Mesh.FaceModes['TWOSIDE']):
				f.write(indent(3) + "cull_hardware none\n")
				f.write(indent(3) + "cull_software none\n")
			# shading
			# (Blender's game engine is initialized with glShadeModel(GL_FLAT))
			##f.write(indent(3) + "shading flat\n")
			# texture
			if (self.face.mode & Blender.Mesh.FaceModes['TEX']) and (self.face.image):
				# 0-diffuse
				f.write(indent(3)+"texture_unit baseMap\n")
				f.write(indent(3)+"{\n")
				f.write(indent(4)+"texture %s\n" % self.manager.registerTextureImage(self.face.image))
				f.write(indent(3)+"}\n") # texture_unit
				# 1-specular
				if spectex:
					self._exportTextureUnit(f, "specularMap", spectex)
				# 2-normal
				if len(self.mesh.materials):
					tex = self.findMapToTexture(mat, 'NOR')
					if tex and tex.tex and tex.tex.getImage():
						self._exportTextureUnit(f, "normalMap", tex)
				# 3-lightMap
				if ambtex:
					self._exportTextureUnit(f, "lightMap", ambtex)

				# 4-shadow
				if self.shadows:
					f.write(indent(3)+"texture_unit shadowMap\n")
					f.write(indent(3)+"{\n")
					f.write(indent(4)+"content_type shadow\n")
					f.write(indent(3)+"}\n") # texture_unit

				# 5-luminanceMap
				# 6-opacityMap
				if textures['alpha']:
					self._exportTextureUnit(f, "opacityMap", textures['alpha'])
				# 7-reflectionMap
				if reftex:
					self._exportTextureUnit(f, "reflectionMap", reftex)

				# 3-heightMap
				if disptex:
					self._exportTextureUnit(f, "heightMap", disptex)


	def writeRexTechniques(self, f, mat):
		# default material
		# SOLID, white, no specular
		f.write(indent(1)+"technique\n")
		f.write(indent(1)+"{\n")
		f.write(indent(2)+"pass\n")
		f.write(indent(2)+"{\n")
		self._writePassContents(f, mat)
		f.write(indent(2)+"}\n") # pass
		f.write(indent(1)+"}\n") # technique
		return

	def getTextureLayers(self, mat):
		textures = {}
		if mat:
			for tex in ['SPEC', 'NOR', 'REF', 'AMB', 'DISP', 'ALPHA']:
				textures[tex.lower()] = self.findMapToTexture(mat, tex)
		return textures

	def _exportTextureUnit(self, f, name, btex):
		f.write(indent(3)+"texture_unit " + name + "\n")
		f.write(indent(3)+"{\n")
		if btex.tex and btex.tex.getImage():
			f.write(indent(4)+"texture %s\n" % self.manager.registerTextureImage(btex.tex.getImage()))
		f.write(indent(3)+"}\n") # texture_unit

	def findMapToTexture(self, meshmat, mapto):
		if not meshmat and len(self.mesh.materials):
			meshmat = self.mesh.materials[0]
		if meshmat:
			image = None
			textures = meshmat.getTextures()
			for tex in textures:
				if tex and tex.mapto & Blender.Texture.MapTo[mapto]:
					return tex
			return image

	# private, might need to override later..
	def _createName(self):
		"""Create unique material name.
		
		   The name consists of several parts:
		   <OL>
		   <LI>rendering material name/</LI>
		   <LI>blend mode (ALPHA, ADD, SOLID)</LI>
		   <LI>/TEX</LI>
		   <LI>/texture file name</LI>
		   <LI>/VertCol</LI>
		   <LI>/TWOSIDE></LI>
		   </OL>
		"""
		return GameEngineMaterial._createName(self)

