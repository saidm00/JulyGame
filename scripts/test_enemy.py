import physics_objects
import glm

import random


class Enemy:
    damping = 5

    def __init__(self, engine):
        self.engine = engine

        self.collider = physics_objects.DynamicCircle(0, 0, 0, 5)
        self.collider.spawn(glm.vec3(random.random() * 200, 0, random.random() * 200*0), glm.vec3(0, 0, 0))
        self.engine.physics.dynamic.append(self.collider)

    def update(self, dt):
        damping = 1 - (self.damping * dt)
        self.collider.vel.x *= damping
        self.collider.vel.z *= damping

    def despawn(self):
        pass

    def draw(self, renderer):
        renderer.push_matrix()

        renderer.translate(*self.collider.pos.xyz)

        renderer.update_matrix()
        renderer.draw_instance('models/enemies/enemy', 'robot_texture')

        renderer.pop_matrix()
