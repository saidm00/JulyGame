import glm

import physics_objects


class StairCase(object):
    def __init__(self, engine, pos, angle=0):
        self.pos = glm.vec3(*pos)
        self.angle = angle
        self.scale = 1

        self.texture = engine.graphics.get_texture('wood')
        self.mesh = engine.graphics.get_mesh('models/environment/staircase')

        self.collider = physics_objects.Box(self.pos, (4, 4 * self.scale, 8), angle)
        self.collider.radius = .2
        self.collider.get_height = self.get_height

        self.slope = self.collider.half_size.y / self.collider.half_size.z

        engine.physics.static.append(self.collider)
        engine.renderer.scene.append(self)

    def get_height(self, pos):
        # return self.collider.half_size.y
        return self.collider.half_size.y + glm.dot(self.pos.xz - pos, self.collider.forward) * -self.slope

    def draw(self, renderer):
        renderer.push_matrix()

        renderer.translate(*self.pos)
        renderer.rotate(self.angle, 0, 1, 0)
        renderer.scale(1, self.scale, 1)

        renderer.update_matrix()
        renderer.set_texture(self.texture)
        self.mesh.draw()

        renderer.pop_matrix()
