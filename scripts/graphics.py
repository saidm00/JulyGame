import numpy as np

import objloader
from mesh import *
from texture import *


class Graphics(object):
    tex_format = 'bmptextures/{}.bmp'

    meshes = {}
    textures = {}

    def get_texture(self, filename, linear=True):
        if filename in self.textures:
            return self.textures[filename]
        else:
            t = Texture(self.tex_format.format(filename), linear)
            self.textures[filename] = t
            return t

    def get_mesh(self, filename):
        if filename in self.meshes:
            return self.meshes[filename]
        else:
            obj = objloader.ObjFile('{}.obj'.format(filename))
            mesh_data = obj.objects.values()[0]

            vertices = np.array(mesh_data.vertices, dtype=np.float32).flatten()
            normals = np.array(mesh_data.normals, dtype=np.float32).flatten()
            texcoords = np.array(mesh_data.tex_coords, dtype=np.float32).flatten()
            indices = np.array(mesh_data.indices, dtype=np.int32).flatten()

            m = Mesh(vertices, normals, texcoords, indices)

            self.meshes[filename] = m
            return m
