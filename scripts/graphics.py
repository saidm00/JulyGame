import numpy as np

import objloader
import mesh, texture


class Graphics(object):
    tex_format = 'bmptextures/{}.bmp'

    meshes = {}
    textures = {}

    def get_texture(self, filename, linear=True):
        if filename in self.textures:
            return self.textures[filename]
        else:
            t = texture.Texture(self.tex_format.format(filename), linear)
            self.textures[filename] = t
            return t

    def get_mesh(self, filename):
        if filename in self.meshes:
            return self.meshes[filename]
        else:
            obj = objloader.ObjFile('{}.obj'.format(filename))
            mesh_data = obj.objects.values()[0]

            m = mesh.Mesh((3, np.array(mesh_data.vertices, np.float32)),
                          (3, np.array(mesh_data.normals, np.float32)),
                          (2, np.array(mesh_data.tex_coords, np.float32)),
                          np.array(mesh_data.indices, np.int32))

            self.meshes[filename] = m
            return m
