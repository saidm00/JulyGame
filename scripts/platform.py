# todo: comment

import physics_objects


class Platform:
    radius = 3
    height = 6

    standing = False

    def __init__(self, engine, pos):
        self.engine = engine
        self.engine.renderer.scene.append(self)
        self.engine.game_manager.game_objects.append(self)

        self.pos = pos

    def update(self, dt):
        pass

    def draw(self, renderer):
        pass

    def despawn(self):
        self.engine.renderer.scene.remove(self)


class Hedge(Platform):
    def __init__(self, engine, pos):
        Platform.__init__(self, engine, pos)

        self.collider = physics_objects.Circle(pos[0], pos[1],
                                               pos[2], 6)
        self.collider.set_radius(2.6)
        engine.physics.static.append(self.collider)

    def draw(self, renderer):

        renderer.push_matrix()

        renderer.translate(*self.pos)
        renderer.scale(3, 2, 3)

        renderer.update_matrix()
        renderer.draw_instance('models/platforms/barrel', 'metal')

        renderer.pop_matrix()




