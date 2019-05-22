
from scripts import (bullet,
                     particle,
                     physics_objects)


class ResourceManager:
    def __init__(self, engine):
        self.engine = engine

        self.bullet_cache = []
        self.particle_cache = []
    #
    # def get_particle(self, pos, vel, tex):
    #     if self.particle_cache:
    #         p = self.particle_cache.pop()
    #     else:
    #         p = particle.Particle(self.app)
    #
    #     p.spawn(pos, vel, self.app.graphic_data.get_texture(tex))
    #     return p
    #
    # def cache_particle(self, p):
    #     self.particle_cache.add(p)

    def spawn_bullet(self, pos, vel, color, collision_filter=physics_objects.DEFAULT):
        if self.bullet_cache:
            b = self.bullet_cache.pop()
        else:
            b = bullet.Bullet(self.engine)
        b.spawn(pos, vel, color, collision_filter)

    def cache_bullet(self, b):
        self.bullet_cache.append(b)

    def spawn_particle(self, pos, vel, tex):
        if self.particle_cache:
            p = self.particle_cache.pop()
        else:
            p = particle.Particle(self.engine)
        p.spawn(pos, vel, tex)

    def cache_particle(self, p):
        self.particle_cache.append(p)
