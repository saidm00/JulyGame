import glm

import physics_objects


class Wall(object):
    def __init__(self, engine, pos):
        self.pos = glm.vec3(*pos)

        self.collider = physics_objects.Segment((self.pos.x - 8, self.pos.z + 0),
                                                (self.pos.x + 8, self.pos.z + 0),
                                                self.pos.y, 16)
        self.collider.radius = .2
        engine.physics.static.append(self.collider)
        engine.renderer.scene.append(self)

    def draw(self, renderer):
        renderer.push_matrix()

        renderer.translate(*self.pos)

        renderer.update_matrix()
        renderer.draw_instance('models/environment/wall', 'wood')

        renderer.pop_matrix()
