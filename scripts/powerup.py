import glm

IDLE, DIE = range(2)


class Powerup:
    state = -1
    timer = 1

    mesh_name = 'models/items/powerup'
    tex_name = 'apple'

    def __init__(self, engine, item_id, pos):
        self.engine = engine
        self.item_id = item_id

        self.texture = self.engine.graphics.get_texture(self.tex_name)
        self.mesh = self.engine.graphics.get_mesh(self.mesh_name)

        self.pos = glm.vec3(*pos)
        self.angle = 0
        self.scale = 1

        self.set_state(IDLE)

    def spawn(self):
        self.engine.game_manager.powerups.append(self)
        self.engine.renderer.scene.append(self)

    def despawn(self):
        self.engine.renderer.scene.remove(self)

    def on_collect(self):
        pass

    def set_state(self, state):
        if state == DIE:
            self.timer = 1
        self.state = state

    def update(self, dt):
        if self.state is IDLE:
            self.angle += 30 * dt
            p_col = self.engine.game_manager.player.collider
            if glm.distance(self.pos.xz, p_col.pos.xz) < 2:
                if p_col.pos.y <= self.pos.y < p_col.pos.y + p_col.height:
                    self.set_state(DIE)

        elif self.state is DIE:
            self.timer -= dt
            if self.timer > 0:
                self.scale = self.timer
            else:
                self.despawn()
                self.engine.game_manager.powerups.remove(self)
                self.on_collect()

    def draw(self, renderer):
        renderer.push_matrix()

        renderer.translate(*self.pos)
        renderer.rotate(self.angle, 0, 1, 0)

        if self.state is DIE:
            renderer.scale(self.scale)

        renderer.update_matrix()
        renderer.set_texture(self.texture)
        self.mesh.draw()

        renderer.pop_matrix()


class Health(Powerup):
    mesh_name = 'models/items/health'
    tex_name = 'apple'

    def on_collect(self):
        self.engine.game_manager.player.add_health()


class Fuel(Powerup):
    mesh_name = 'models/items/powerup'
    tex_name = 'apple'

    def on_collect(self):
        self.engine.game_manager.player.add_fuel()


class SlowTime(Powerup):
    mesh_name = 'models/items/clock'
    tex_name = 'clock'

    def on_collect(self):
        self.engine.game_manager.player.start_slow_motion()


class Chips(Powerup):
    mesh_name = 'models/items/chips'
    tex_name = 'chips'

    def on_collect(self):
        self.engine.game_manager.player.add_markers(5)
