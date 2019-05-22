import math
import glm

from scripts import (physics_objects,
                     character,
                     util)


class Player:
    walk_speed = 80 * 1.5
    sprint_speed = 110 * 1.5
    speed = walk_speed

    damping = 4

    grab_range = .6
    hang_height = 4

    turn_speed = 5

    base_jump_force = 10
    jump_force = 20
    jump_time = .4
    gravity = 25

    vehicle = None
    seat_index = -1

    attacking = False
    attack_timer = 0
    arm_index = 1

    state = -1
    state_timer = 0

    damage_speed = 40
    fall_damage = 2

    health = 100
    max_health = 100.0
    fuel = 0
    max_fuel = 2
    jetpack_enabled = False
    sprint = 0
    max_sprint = 2

    def __init__(self, engine):
        self.engine = engine

        self.graphics = character.Character(self.engine)
        self.collider = physics_objects.DynamicCircle(0, 10, 0, 5, self)
        self.collider.set_radius(1)
        self.collider.collision_filter = physics_objects.PLAYER
        self.collider.on_platform = self.on_platform
        self.collider.on_platform_remove = self.on_platform_remove
        self.collider.on_hit_top = self.on_hit_top
        self.collider.on_collision = self.on_collision

        self.engine.physics.dynamic.append(self.collider)

        self.in_x = 0
        self.in_y = 0

        self.set_state(character.JUMPING)
        self.state_timer = 0

    def start_attack(self):
        self.attacking = True

    def stop_attack(self):
        self.attacking = False

    def drive(self):
        if self.state is not character.DIE:
            if self.state is character.DRIVING:
                self.collider.pos = self.vehicle.get_seat_pos(self.seat_index, 2)
                # self.collider.pos = self.graphics.pos
                self.engine.physics.dynamic.append(self.collider)
                self.collider.vel = glm.vec3(*self.vehicle.collider.vel)

                if self.seat_index is 0:
                    self.vehicle.accel = 0
                    self.vehicle.turn = 0
                    self.vehicle.turn_off()

                self.vehicle.occupied_seats.remove(self.seat_index)

                self.vehicle = None
                self.set_state(character.JUMPING)
            else:
                for vehicle in self.engine.game_manager.vehicles:
                    if glm.distance(self.graphics.pos, vehicle.collider.pos) < 7:
                        self.seat_index = vehicle.get_open_seat()
                        if self.seat_index >= 0:
                            self.vehicle = vehicle
                            self.set_state(character.DRIVING)
                            break

    def on_collision(self, other, hit_point, normal_vector, radius):
        if self.state not in (character.DIE, character.WALK):
            if other.collision_type == physics_objects.STATIC:
                top = other.get_top(self.collider.pos.xz)
                if self.collider.get_top(None) > top - self.grab_range:
                    self.collider.sleeping = True
                    self.collider.pos.y = top - self.hang_height
                    self.graphics.pos.y = self.collider.pos.y
                    self.collider.vel *= 0
                    self.collider.force *= 0

                    if radius == -1:
                        self.graphics.grab_arm_angle = 130
                        self.graphics.grab_arm_roll = 20

                    else:
                        self.graphics.grab_arm_angle = 110
                        self.graphics.grab_arm_roll = -30

                    self.graphics.rot = math.atan2(normal_vector.y, -normal_vector.x) * 57.3
                    # self.graphics.pos = self.collider.pos

                    self.set_state(character.GRAB)

    def on_platform(self, other):
        if self.state is not character.DIE:
            over_speed = self.collider.vel.y + self.damage_speed
            if over_speed < 0:
                self.add_health(-((-over_speed * self.fall_damage) ** 1.3))
            if self.health > 0:
                self.set_state(character.WALK)

    def on_platform_remove(self):
        if self.state is not character.DIE:
            self.set_state(character.JUMPING)
            self.state_timer = 0

    def on_hit_top(self, other):
        if self.state is character.GRAB:
            self.set_state(character.JUMPING)
        self.state_timer = 0

    def get_velocity(self):
        return self.collider.get_velocity()

    def add_input(self, dx, dy):
        self.set_input(cmp(self.in_x + dx, 0),
                       cmp(self.in_y + dy, 0))

    def set_input(self, x, y):
        self.in_x = x
        self.in_y = y

    def set_state(self, state):
        if state is character.DRIVING:
            self.engine.physics.dynamic.remove(self.collider)
            self.collider.colliding.clear()
            self.engine.renderer.camera.offset.z = -25
        else:
            if self.state is character.DRIVING:
                self.engine.renderer.camera.offset.z = -10

            if state is character.WALK:
                self.collider.vel[1] = 0

            elif state is character.JUMPING:
                self.state_timer = self.jump_time
                self.collider.platform = None

            elif state is character.GRAB:
                self.engine.renderer.camera.set_pos(self.graphics.pos.x,
                                                    self.graphics.pos.y + 6,
                                                    self.graphics.pos.z)

        self.state = state

    def move(self, speed, dt):
        cos, sin = self.engine.renderer.camera.get_forward_xz()

        global_in_x = cos * self.in_x + sin * self.in_y
        global_in_z = -sin * self.in_x + cos * self.in_y

        mag_sqrd = global_in_x ** 2 + global_in_z ** 2

        if mag_sqrd > 1:
            s = speed / (mag_sqrd ** .5)
        else:
            s = speed

        self.collider.sleeping = False
        self.collider.force.x += global_in_x * s * dt
        self.collider.force.z += global_in_z * s * dt

        damping = 1 - self.damping * dt
        self.collider.vel.x *= damping
        self.collider.vel.z *= damping

    def do_jump(self):
        if self.state is not character.DIE:
            if self.state is character.WALK:
                self.jetpack_enabled = False
                self.collider.vel.y = self.base_jump_force
                self.set_state(character.JUMPING)

            elif self.state is character.GRAB:
                self.collider.vel.y = self.base_jump_force

                rads = self.graphics.rot / 57.3

                cos = math.cos(rads)
                sin = math.sin(rads)

                self.collider.vel.x = -cos * 20
                self.collider.vel.z = sin * 20
                self.set_state(character.JUMPING)

            elif self.state is character.JUMPING and self.fuel > 0:
                self.jetpack_enabled = True
                self.collider.vel.y = self.base_jump_force

    def stop_jump(self):
        if self.state is character.JUMPING:
            self.jetpack_enabled = False
            self.state_timer = 0

    def update(self, dt):
        if self.state is character.DIE:
            pos = self.graphics.pos
            self.engine.renderer.camera.set_pos(pos.x,
                                                pos.y + 4,
                                                pos.z)
            if self.collider.platform:
                self.collider.vel *= 1 - (10 * dt)
        else:
            self.graphics.head_yaw = -self.engine.renderer.camera.yaw
            self.graphics.head_pitch = -self.engine.renderer.camera.pitch

            if self.state is character.DRIVING:
                self.vehicle.ix = self.in_x
                self.vehicle.iy = self.in_y
                # self.engine.renderer.camera.target_yaw = 90 - self.graphics.rot
                self.graphics.pos = self.vehicle.get_seat_pos(self.seat_index)
                self.engine.renderer.camera.set_pos(self.graphics.pos.x,
                                                    self.graphics.pos.y + 7,
                                                    self.graphics.pos.z)
            elif self.state is character.GRAB:
                pass
            else:
                self.move(self.speed, dt)

                if self.state is character.JUMPING:
                    if self.state_timer > 0 or self.jetpack_enabled:
                        self.state_timer -= dt
                        self.collider.force.y += self.jump_force * dt

                        if self.jetpack_enabled:
                            self.add_fuel(-dt)

                            self.engine.resource_manager.spawn_particle(self.collider.pos.xyz,
                                                                        self.collider.vel.xyz,
                                                                        'nana')

                    else:
                        self.collider.force.y -= self.gravity * dt

                if self.attacking:
                    cam_height = 8

                    self.attack_timer -= dt * 5
                    if self.attack_timer < 0:
                        self.attack_timer = 1
                        self.arm_index *= -1
                        x, y, z, dx, dy, dz = self.graphics.get_hand_pos(self.arm_index, -2.5)
                        self.engine.resource_manager.spawn_bullet(glm.vec3(x, y, z),
                                                                  self.collider.vel * .25 + glm.vec3(dx, dy, dz) * 30,
                                                                  (0, 0, 1))
                else:
                    cam_height = 6

                pos = self.graphics.pos
                self.engine.renderer.camera.set_pos(pos.x,
                                                    pos.y + cam_height,
                                                    pos.z)

                self.graphics.pos = glm.vec3(*self.collider.pos)

                target_angle = 90 - self.engine.renderer.camera.yaw
                da = util.angle_diff(self.graphics.rot, target_angle)
                turn_speed = self.turn_speed * dt
                if abs(da) > turn_speed:
                    self.graphics.rot += da * turn_speed
                else:
                    self.graphics.rot = target_angle

                self.graphics.arm_pitch = 90 - self.engine.renderer.camera.pitch

        self.graphics.do_animation(self, dt)

    def right_trigger_down(self):
        if self.state == character.DRIVING and self.seat_index is 0:
            self.vehicle.right_trigger_down()
        else:
            self.start_attack()

    def right_trigger_up(self):
        if self.state == character.DRIVING and self.seat_index is 0:
            self.vehicle.right_trigger_up()
        else:
            self.stop_attack()

    def left_trigger_down(self):
        if self.state == character.DRIVING and self.seat_index is 0:
            self.vehicle.left_trigger_down()

    def left_trigger_up(self):
        if self.state == character.DRIVING and self.seat_index is 0:
            self.vehicle.left_trigger_up()

    def add_fuel(self, amt=None):
        if amt is None:
            self.fuel = self.max_fuel
        elif amt < 0:
            self.fuel += amt
            if self.fuel < 0:
                self.fuel = 0
                self.jetpack_enabled = False
        else:
            self.fuel += amt
            if self.fuel > self.max_fuel:
                self.fuel = self.max_fuel

    def add_health(self, amt=None):
        if amt is None:
            self.health = self.max_health
        else:
            self.health += amt
            if amt < 0:
                if self.health < 0:
                    self.health = 0
                    self.set_state(character.DIE)
            elif self.health > self.max_health:
                self.health = self.max_health

        health = self.engine.screen_manager.get_element('health')
        health.target_value = self.health / self.max_health