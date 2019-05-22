import numpy as np

import objloader
import mesh


class Terrain:
    def __init__(self, engine):
        self.texture = engine.graphics.get_texture('dirt')
        self.mesh = engine.graphics.get_mesh('models/terrains/Level1')

    def draw(self, renderer):
        renderer.set_texture(self.texture)

        renderer.update_matrix()
        self.mesh.draw()


class Plane:
    def __init__(self, engine):
        self.texture = engine.graphics.get_texture('debug')
        self.mesh = engine.graphics.get_mesh('models/plane')

    def draw(self, renderer):
        renderer.push_matrix()

        renderer.translate(0, 10, 0)

        renderer.set_texture(self.texture)

        renderer.update_matrix()
        self.mesh.draw()

        renderer.pop_matrix()
