# todo: comment


from scripts import physics_objects


class Door:
    size = (1, 4)
    height = 7

    swing_angle = 135 / 57.3

    def __init__(self, engine, pos, angle):
        self.engine = engine

        self.texture = self.engine.graphics.get_texture('door')
        self.mesh = self.engine.graphics.get_mesh('models/environment/door')

        self.collider = physics_objects.DoorCollider(*pos, rest_angle=angle)

    def spawn(self):
        self.engine.physics.doors.append(self.collider)
        self.engine.renderer.scene.append(self)
        # self.engine.game_manager.game_objects.append(self)

    def despawn(self):
        self.engine.physics.dynamic.remove(self.collider)
        self.engine.renderer.scene.remove(self)

    def draw(self, renderer):
        renderer.set_texture(self.texture)

        renderer.push_matrix()

        renderer.translate(*self.collider.pos)
        renderer.rotate(self.collider.angle + 180, 0, 1, 0)

        renderer.update_matrix()
        self.mesh.draw()

        renderer.pop_matrix()
