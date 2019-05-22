import physics_objects


class Bullet:
    radius = .2
    timer = 0

    speed = 30
    gravity = 5

    def __init__(self, engine):
        self.engine = engine

        self.collider = physics_objects.DynamicCircle(0, 10, 0, self.radius * 2)
        self.collider.on_collision = self.on_collision
        self.collider.on_hit_top = self.on_collision
        self.collider.on_platform = self.on_collision

    def on_collision(self, other, *args):
        self.engine.game_manager.remove_object(self)

    def spawn(self, pos, vel, color, collision_filter):
        # self.color.rgb = color
        self.collider.filter = collision_filter

        self.collider.spawn(pos, vel)

        self.timer = 1

        self.engine.physics.bullets.append(self.collider)
        self.engine.renderer.scene.append(self)
        self.engine.game_manager.game_objects.append(self)

    def update(self, dt):
        # i = self.timer // .02

        self.collider.vel.y -= self.gravity * dt

        self.timer -= dt * .3
        if self.timer < 0:
            self.engine.game_manager.remove_object(self)

        # elif i != self.timer // .02:
        #     test_particle = self.engine.resource_manager.get_particle(self.pos.xyz, (0, 0, 0), 1)
        #     self.app.renderer.scene.add(test_particle.canvas)
        #     self.app.game_manager.game_objects.add(test_particle)

    def despawn(self):
        self.engine.renderer.scene.remove(self)
        self.engine.physics.bullets.remove(self.collider)
        self.engine.resource_manager.cache_bullet(self)

    def draw(self, renderer):
        renderer.push_matrix()

        renderer.translate(*self.collider.pos.xyz)

        renderer.update_matrix()
        renderer.draw_instance('models/projectiles/bullet', 'white')

        renderer.pop_matrix()
