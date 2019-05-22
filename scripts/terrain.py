import glm

import numpy as np
from glm import simplex

# from PIL import Image

import mesh
import physics_objects


class Terrain(object):
    def __init__(self, engine, sx, sy, length, height, seed):
        self.size = glm.vec3(sx * length, height, sy * length)
        self.tex_size = glm.vec2(sx, sy)

        self.texture = engine.graphics.get_texture('dirt')

        self.collider = physics_objects.Box((0, 0, 0),
                                            self.size)
        self.collider.get_height = self.get_height

        engine.physics.static.append(self.collider)

        self.positions = np.empty((sx * sy, 3), np.float32)
        normals = np.empty((sx * sy, 3), np.float32)
        texcoords = np.empty((sx * sy, 2), np.float32)
        colors = np.empty((sx * sy, 3), np.float32)
        indices = np.empty(6 * (sx - 1) * (sy - 1), np.uint32)

        # self.image = Image.new('L', (sx, sy), 'black')

        h = hash(seed)
        sample = glm.vec2(h, hash(h))

        # Generate vertex positions
        for x in range(0, sx):
            for y in range(0, sy):
                pos = glm.vec3(x / float(sx), 0.0, y / float(sy))

                for i in range(0, 4):
                    pos.y += pow(1.0, -i) * noise2(pos.x + sample.x,
                                                   pos.z + sample.y, i + 1)

                pos.y /= 4.0
                pos.y = 0.5 * pos.y + 0.5
                pos.y *= abs(pos.x-.5) + abs(pos.z-.5)
                # self.image.putpixel((x, y), int(pos.y * 255))

                # pos.y = pos.x

                self.positions[y * sx + x] = list(pos)
                texcoords[y * sx + x] = [pos.x, pos.z]

        # image.close()

        # Specify indices and normals
        i = 0
        for x in range(0, sx - 1):
            for y in range(0, sy - 1):
                indices[i] = y * sx + x
                indices[i + 1] = (y + 1) * sx + x
                indices[i + 2] = y * sx + x + 1

                v0 = self.positions[indices[i]]
                v1 = self.positions[indices[i + 1]]
                v2 = self.positions[indices[i + 2]]

                normal = np.cross(v1 - v0, v2 - v0)
                normal /= np.linalg.norm(normal)

                normals[indices[i]] = normal
                normals[indices[i + 1]] = normal
                normals[indices[i + 2]] = normal

                i += 3

                indices[i] = y * sx + (x + 1)
                indices[i + 1] = (y + 1) * sx + x
                indices[i + 2] = (y + 1) * sx + (x + 1)

                v0 = self.positions[indices[i]]
                v1 = self.positions[indices[i + 1]]
                v2 = self.positions[indices[i + 2]]

                normal = np.cross(v1 - v0, v2 - v0)
                normal /= np.linalg.norm(normal)

                normals[indices[i]] = normal
                normals[indices[i + 1]] = normal
                normals[indices[i + 2]] = normal

                i += 3

        GRASS = glm.vec3(0.35, 0.65, 0.25)
        SNOW = glm.vec3(0.925, 0.93, 0.95)

        for x in range(0, sx):
            for y in range(0, sy):
                i = y * sx + x
                p = self.positions[i]
                normal = glm.vec3(float(normals[i, 0]), float(normals[i, 1]), float(normals[i, 2]))
                angle = max(glm.dot(normal, glm.vec3(0.0, 1.0, 0.0)), 0.0)
                h = float(p[1])
                color = glm.mix(GRASS, SNOW * h, pow(angle, 10.0))
                colors[i] = [color.x, color.y, color.z]

        self.mesh = mesh.Mesh(self.positions, normals,
                              texcoords,
                              colors, indices)

    def get_position(self, pos):
        return self.positions[int(pos.y) * int(self.tex_size.x) + int(pos.x)]

    def get_height(self, pos):
        # print pos
        pixel = self.world_to_grid(pos)
        height = self.get_position(pixel)
        # print height[1]
        return height[1] * self.size.y

    def world_to_grid(self, pos):
        return glm.clamp((pos + self.size.xz * .5) / self.size.xz, 0.0, .99) * self.tex_size

    def draw(self, renderer):
        renderer.push_matrix()

        renderer.scale(*self.size)
        renderer.translate(-.5, 0, -.5)

        renderer.update_matrix()
        renderer.set_texture(self.texture)
        self.mesh.draw()

        renderer.pop_matrix()
