# todo: comment

import math
import pymunk

import character, dynamic_object, util, network_manager, marker


class Player:
    walk_speed = .8
    sprint_speed = 1.1
    speed = walk_speed
    turn_speed = 5
    base_jump_force = 10
    jump_force = 20
    jump_time = .4
    gravity = 25

    radius = 1
    height = 4.5

    attack_timer = 0
    state_timer = 0
    state = -1

    damage_speed = 40
    fall_damage = 2
    arm_index = 1

    slow_motion_time = 0
    powerup_time = 0

    net_pos = [0, 0, 0]
    net_angle = 0

    target_angle = 0
    attacking = False
    vehicle = None
    seat_index = 0
    input_vector = [0, 0]

    max_health = 100.0
    damage_timer = 0
    health = max_health

    sprinting = False
    stamina = 0
    max_stamina = 2.0

    chip_count = 0
    max_chips = 10.0

    grid_pos = None

    def __init__(self, app):
        self.app = app

        self.collision = dynamic_object.DynamicObject(self.app, self)
        self.collision.ledge_hop = 10
        self.collision.spawn_collider(pymunk.Circle(None, self.radius),
                                      0, self.height)

        self.collision.collider.damage_object = self

        self.graphics = character.Character(self.app)

        self.collision.spawn((0, 0, 0))

        self.set_state(character.JUMPING)

    def hit_collider(self, col, point_set):
        if self.state == character.JUMPING:
            top = col.y + col.height
            min_y = top - self.height
            max_y = top - self.height * .5
            y_pos = self.collision.collider.y

            if min_y < y_pos < max_y:
                if not hasattr(col, 'no_grab'):
                    self.graphics.rot.angle = math.atan2(-point_set.normal.y, point_set.normal.x) * 57.3
                    self.graphics.pos.y = top - (self.height - .5)
                    self.collision.collider.y = self.graphics.pos.y
                    self.collision.body.velocity *= 0
                    self.set_state(character.GRAB)

                    if util.is_elevator(col):
                        self.collision.dy = col.parent.dy
                    else:
                        self.collision.dy = 0

    def get_velocity(self):
        return self.collision.get_velocity()

    def spawn(self, pos):
        self.app.renderer.cam_pitch.angle = 0
        self.app.renderer.cam_yaw.angle = 0

        self.graphics.pos.xyz = pos
        self.stop_powerup()

        self.health = self.max_health
        self.app.gui_manager.set_health(self.health, self.max_health)

        self.chip_count = 0
        self.app.gui_manager.set_chips(self.chip_count, self.max_chips)

        self.graphics.scale.x = 1

        if self.state == character.DRIVING:
            if self.vehicle:
                self.vehicle.occupied_seats.remove(self.seat_index)
            self.vehicle = None
            self.collision.spawn(pos)
        else:
            self.collision.set_pos(pos)

        self.set_state(character.JUMPING)
        self.collision.dy = 0
        self.state_timer = 0

    def set_standing(self, c, shape=True):
        if shape and hasattr(c, 'on_stand'):
            c.on_stand()
        if self.collision.dy > 0:
            return True
        else:
            if self.state != character.WIN:
                over_speed = self.collision.dy + self.damage_speed
                if over_speed < 0:
                    self.damage((-over_speed * self.fall_damage) ** 1.3)
                if self.health > 0:
                    self.set_state(character.WALK)

    def removed_standing(self):
        if self.state == character.WALK:
            self.set_state(character.JUMPING)
            self.state_timer = 0

    def drive(self):
        if self.state == character.DRIVING:
            self.collision.spawn(self.graphics.pos.xyz)
            self.collision.body.velocity = self.vehicle.collision.body.velocity
            self.collision.dy = self.vehicle.collision.dy

            if self.seat_index is 0:
                self.vehicle.accel = 0
                self.vehicle.turn = 0
                self.vehicle.turn_off()
                self.app.network_manager.send_message(network_manager.DRIVE_VEHICLE,
                                                      self.vehicle.vehicle_id,
                                                      self.seat_index, 0,
                                                      *self.vehicle.get_vel())
            else:
                self.app.network_manager.send_message(network_manager.DRIVE_VEHICLE,
                                                      self.vehicle.vehicle_id,
                                                      self.seat_index, 0)

            self.vehicle.occupied_seats.remove(self.seat_index)

            self.vehicle = None
            self.set_state(character.JUMPING)
        else:
            for vehicle in self.app.game_manager.vehicles:
                if util.sqr_distance_between(self.graphics.pos.xyz, vehicle.pos.xyz) < 50:
                    self.seat_index = vehicle.get_open_seat()
                    if self.seat_index >= 0:
                        self.vehicle = vehicle
                        self.app.network_manager.send_message(network_manager.DRIVE_VEHICLE,
                                                              self.vehicle.vehicle_id,
                                                              self.seat_index, 1)
                        self.set_state(character.DRIVING)
                        break

    def do_jump(self):
        if self.state == character.GRAB:
            rads = self.graphics.rot.angle / 57.3

            cos = math.cos(rads)
            sin = math.sin(rads)

            self.collision.body.apply_impulse_at_local_point((-cos * 10, sin * 10))
            self.collision.dy = self.base_jump_force
            self.set_state(character.JUMPING)
        elif (self.state == character.JUMPING and self.powerup_time > 0) or self.state == character.WALK:
            self.collision.dy = self.base_jump_force
            self.set_state(character.JUMPING)

    def add_markers(self, amt):
        self.chip_count += amt
        if self.chip_count > self.max_chips:
            self.chip_count = self.max_chips

        self.app.gui_manager.set_chips(self.chip_count, self.max_chips)

    def drop_marker(self):
        # self.app.pathfinder.set_weights_to_target(self.graphics.pos.xyz)

        if self.chip_count > 0:
            self.chip_count -= 1

            pos = (int(self.graphics.pos.x),
                   int(self.graphics.pos.y + 2),
                   int(self.graphics.pos.z))

            marker.Marker(self.app).spawn(pos)

            self.app.network_manager.send_message(network_manager.CHIPS, *pos)

            self.app.gui_manager.set_chips(self.chip_count, self.max_chips)

    def stop_jump(self):
        if self.state == character.JUMPING:
            self.state_timer = 0

    def start_attack(self):
        if self.state in (character.WALK, character.JUMPING):
            self.app.network_manager.send_message(network_manager.SET_ATTACK, 1)
            self.attacking = True
            self.attack_timer = 1

    def stop_attack(self):
        self.app.network_manager.send_message(network_manager.SET_ATTACK, 0)
        self.attacking = False

    def start_slow_motion(self):
        self.slow_motion_time = 1
        self.app.time_scale = .5

    def stop_slow_motion(self):
        self.slow_motion_time = 0
        self.app.time_scale = 1

    def on_sprint(self):
        self.stamina = self.max_stamina
        if self.stamina > 0:
            self.sprinting = True
            self.speed = self.sprint_speed

    def stop_sprint(self):
        self.sprinting = False
        self.speed = self.walk_speed

    def set_state(self, state):
        if state == character.DRIVING:
            self.attacking = False
            self.app.renderer.cam_offset.z = -15
            self.state = state
            self.collision.despawn()
        else:
            self.app.renderer.cam_offset.z = -6

            if state == character.WALK:
                self.collision.dy = 0

            elif state == character.JUMPING:
                self.state_timer = self.jump_time
                self.collision.standing = None
            elif state == character.WIN:
                if self.state == character.DRIVING:
                    self.drive()

        self.state = state
        self.app.network_manager.send_message(network_manager.SET_STATE, self.state)

    def start_powerup(self):
        self.powerup_time = 1
        self.graphics.color.rgb = (0, 0, 1)
        self.app.gui_manager.set_powerup(self.powerup_time)

    def stop_powerup(self):
        self.powerup_time = 0
        self.app.gui_manager.set_powerup(0)
        self.graphics.color.rgb = 1, 1, 1

    def set_axis(self, axis):
        self.input_vector = axis

    def despawn(self):
        pass

    def get_health(self):
        self.health = self.max_health
        self.app.gui_manager.set_health(self.health, self.max_health)
        self.graphics.scale.x = self.health / self.max_health

    def damage(self, amt):
        if self.state not in (character.WIN, character.DIE):
            if self.state == character.GRAB:
                self.set_state(character.JUMPING)
            self.damage_timer = 1
            self.health -= amt
            if self.health <= 0:
                self.health = 0
                self.set_state(character.DIE)
                self.app.level_manager.set_level(-2)
            self.app.gui_manager.set_health(self.health, self.max_health)
            self.graphics.scale.x = self.health / self.max_health

    def update(self, dt):
        if self.state in (character.DIE, character.WIN):
            self.collision.dy -= self.gravity * dt
            if not self.collision.standing:
                self.collision.move_y(dt)
            self.collision.update(dt)

            self.graphics.pos.xyz = self.collision.get_pos()

            self.app.renderer.set_cam_pos((-self.graphics.pos.x,
                                           -(self.graphics.pos.y + 3),
                                           -self.graphics.pos.z))

        else:
            if self.state == character.DRIVING:
                if self.seat_index == 0:
                    self.vehicle.move(self.input_vector, dt)
                    self.app.renderer.target_yaw = 90 - self.vehicle.rot.angle

                seat_pos = self.vehicle.get_seat_pos(self.seat_index)

                self.graphics.pos.x = self.vehicle.pos.x + seat_pos[0]
                self.graphics.pos.y = self.vehicle.pos.y + seat_pos[1]
                self.graphics.pos.z = self.vehicle.pos.z + seat_pos[2]

                self.app.renderer.set_cam_pos((-self.graphics.pos.x,
                                               -(self.graphics.pos.y + 10),
                                               -self.graphics.pos.z))
            elif self.state == character.GRAB:
                if self.collision.move_y(dt):
                    self.set_state(character.WALK)

                self.graphics.pos.xyz = self.collision.get_pos()
                self.app.renderer.set_cam_pos((-self.graphics.pos.x,
                                               -(self.graphics.pos.y + 7),
                                               -self.graphics.pos.z))
            else:
                self.move(self.input_vector, self.speed, dt)

                if self.sprinting:
                    self.stamina -= dt
                    if self.stamina < 0:
                        self.stamina = 0
                        self.stop_sprint()
                    self.app.gui_manager.set_stamina(self.stamina, self.max_stamina)

                if self.state == character.JUMPING:
                    if self.state_timer <= 0:
                        self.collision.dy -= self.gravity * dt
                        if self.collision.move_y(dt) and self.state != character.DIE:
                            self.set_state(character.WALK)
                    else:
                        self.state_timer -= dt
                        if self.powerup_time > 0:
                            self.collision.dy += self.jump_force * dt * 1.2
                            self.powerup_time -= dt
                            if self.powerup_time < 0:
                                self.stop_powerup()
                            else:
                                self.app.gui_manager.set_powerup(self.powerup_time)

                            rads = (self.graphics.rot.angle - 90) / 57.3
                            x = self.graphics.pos.x + math.sin(rads) * 2 + util.random_value(.3)
                            z = self.graphics.pos.z + math.cos(rads) * 2 + util.random_value(.3)

                            pos = (x, self.graphics.pos.y + 2, z)
                            vel = (util.random_value(4), -4, util.random_value(4))

                            test_particle = self.app.resource_manager.get_particle(pos, vel, 0)
                            self.app.renderer.scene.add(test_particle.canvas)
                            self.app.game_manager.game_objects.add(test_particle)
                        else:
                            self.collision.dy += self.jump_force * dt

                        self.collision.move_y(dt)

                if self.attacking:
                    cam_height = 8
                else:
                    cam_height = 6
                self.app.renderer.set_cam_pos((-self.graphics.pos.x,
                                               -(self.graphics.pos.y + cam_height),
                                               -self.graphics.pos.z))

                self.collision.update(dt)

                new_pos = [i + (j-i) * .2 for i, j in zip(self.graphics.pos.xyz,
                                                          self.collision.get_pos())]

                self.graphics.pos.xyz = new_pos

                if self.damage_timer > 0:
                    self.damage_timer -= dt * 2

                    if self.damage_timer > 0:
                        i = 1 - self.damage_timer

                        self.graphics.set_color((1, i, i))
                    else:
                        self.graphics.set_color((1, 1, 1))

            self.graphics.head_pitch.angle = -self.app.renderer.cam_pitch.angle
            self.graphics.head_yaw.angle = -self.app.renderer.cam_yaw.angle

            diff = sum([abs(i - j) for i, j in zip(self.net_pos, self.graphics.pos.xyz)])
            if diff > .5:
                self.net_pos = self.graphics.pos.xyz
                pos = [round(i, 2) for i in self.graphics.pos.xyz]

                if self.state == character.DRIVING:
                    self.app.network_manager.send_message(network_manager.SYNC_VEHICLE,
                                                          self.vehicle.vehicle_id,
                                                          self.vehicle.collision.body.angle,
                                                          *self.vehicle.get_pos())
                else:
                    self.app.network_manager.send_message(network_manager.SET_POS,
                                                          pos[0], pos[1], pos[2],
                                                          int(self.get_velocity()))

            if abs(self.graphics.rot.angle - self.net_angle) > 10:
                self.net_angle = int(self.graphics.rot.angle)
                if self.state == character.DRIVING:
                    self.app.network_manager.send_message(network_manager.SYNC_VEHICLE,
                                                          self.vehicle.vehicle_id,
                                                          round(self.vehicle.collision.body.angle, 1),
                                                          *self.vehicle.get_pos())
                else:
                    self.app.network_manager.send_message(network_manager.SET_ANGLE,
                                                          self.net_angle)

            if self.attacking:
                self.attack_timer -= dt * 5
                if self.attack_timer < 0:
                    self.attack_timer = 1
                    self.arm_index *= -1
                    x, y, z, dx, dy, dz = self.graphics.get_hand_pos(self.arm_index, -2)
                    self.app.resource_manager.spawn_bullet((x, y, z), (dx, dy, dz), 20, (0, 0, 1))

                    self.app.network_manager.send_message(network_manager.BULLET,
                                                          int(self.graphics.right_arm_rot.angle),
                                                          self.arm_index)

        if self.slow_motion_time > 0:
            self.slow_motion_time -= dt * .1
            if self.slow_motion_time < 0:
                self.stop_slow_motion()

        self.graphics.arm_pitch = 90 - self.app.renderer.cam_pitch.angle
        self.graphics.do_animation(self, dt)

        self.grid_pos = self.app.pathfinder.pos_to_grid(self.graphics.pos.xyz)

    def move(self, direction, speed, dt):
        if any(direction):
            ix, iy = direction

            rads = self.app.renderer.cam_yaw.angle / 57.3
            cos = math.cos(rads)
            sin = math.sin(rads)

            dx = cos * ix + -sin * iy
            dy = sin * ix + cos * iy

            mag_sqrd = dx ** 2 + dy ** 2

            if mag_sqrd > 1:
                s = speed / (mag_sqrd ** .5)
            else:
                s = speed

            self.collision.body.apply_impulse_at_local_point((dx * s, dy * s))

        if any(self.collision.body.velocity):
            target_angle = 90 - self.app.renderer.cam_yaw.angle
            da = util.angle_diff(self.graphics.rot.angle, target_angle)
            turn_speed = self.turn_speed * dt
            if abs(da) > turn_speed:
                self.graphics.rot.angle += da * turn_speed
            else:
                self.graphics.rot.angle = target_angle

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
