import glm


class Particle:
    def __init__(self, engine):
        self.engine = engine

        self.pos = glm.vec3()
        self.vel = glm.vec3()
        self.angle = 0
        self.timer = 1

        self.tex_name = None

    def spawn(self, pos, vel, tex):
        self.timer = 1
        self.pos = glm.vec3(*pos)
        self.vel = glm.vec3(*vel)
        self.tex_name = tex
        self.engine.renderer.scene.append(self)
        self.engine.game_manager.game_objects.append(self)

    def despawn(self):
        self.engine.resource_manager.cache_particle(self)
        self.engine.renderer.scene.remove(self)
        self.engine.game_manager.game_objects.remove(self)

    def update(self, dt):
        self.angle += 90 * dt
        self.vel.y -= 10 * dt
        self.pos += self.vel * dt
        self.timer -= dt
        if self.timer < 0:
            self.despawn()

    def draw(self, renderer):
        renderer.push_matrix()

        renderer.translate(*self.pos)
        renderer.rotate(-renderer.camera.yaw, 0, 1, 0)
        renderer.rotate(-renderer.camera.pitch, 1, 0, 0)
        renderer.rotate(self.angle, 0, 0, 1)

        renderer.update_matrix()
        # self.engine.graphics.get_mesh('models/UI/plane').draw()
        renderer.draw_instance('models/UI/plane', self.tex_name)

        renderer.pop_matrix()
