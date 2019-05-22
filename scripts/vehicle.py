# todo: comment

import math
import glm

from scripts import physics_objects


class Vehicle:
    accel_force = -100.0
    turn_force = 5
    idle_turn_factor = .3
    max_speed = 30
    min_speed = -max_speed * .6
    max_angular_velocity = 4

    model_mat = glm.mat4(1.0)

    seats = [glm.vec4(0, -.1, -1.5, 1),
             glm.vec4(0, -.1, 1.5, 1)]
    occupied_seats = set()

    side_friction = 3
    friction_speed = 15
    stop_speed = .1

    a_damping = 2

    turned_on = False

    is_kinematic = False

    def __init__(self, engine, vehicle_id):
        self.engine = engine
        self.vehicle_id = vehicle_id

        self.collider = physics_objects.DynamicCircle(0, 0, 0, 2)
        self.engine.physics.dynamic.append(self.collider)

        self.throttle_up = 0
        self.throttle_down = 0
        self.ix = 0
        self.iy = 0

        self.angle = 0

    def spawn(self, pos):
        self.collider.pos = pos
        self.engine.renderer.scene.append(self)
        self.engine.game_manager.game_objects.append(self)
        self.engine.game_manager.vehicles.append(self)

    def get_pos(self):
        return self.collider.pos

    def get_vel(self):
        return self.collider.get_velocity()

    def move(self, input_vector, dt):
        pass

    def despawn(self):
        self.engine.renderer.scene.remove(self)
        self.engine.physics.dynamic.remove(self.collider)

    def turn_off(self):
        self.turned_on = False
        self.ix = self.iy = 0
        self.throttle_down = 0
        self.throttle_up = 0

    def update(self, dt):
        rot_mat = glm.rotate(glm.mat4(1.0), glm.radians(90 -self.angle), glm.vec3(0, 1, 0))

        local_vel = rot_mat * glm.vec4(self.collider.vel, 1)

        local_vel.x += self.ix * dt * 100
        local_vel.z += self.iy * dt * 100

        if self.ix:
            turn_input = abs(self.ix) ** 1.2 * cmp(-self.ix, 0)
            turn_force = abs(local_vel.x) * self.turn_force
            self.angle += turn_force * turn_input * dt

        local_vel.z *= 1 - self.side_friction * dt
        local_vel.x = min(self.max_speed, max(self.min_speed, local_vel.x))
        self.collider.vel = glm.vec3(glm.inverse(rot_mat) * local_vel).xyz

    def get_open_seat(self):
        for i in range(len(self.seats)):
            if i not in self.occupied_seats:
                self.occupied_seats.add(i)
                return i
            else:
                print 'seat {} is occupied'.format(i)
        return -1

    def get_seat_pos(self, i, f=1):
        return glm.vec3(*(self.model_mat * (self.seats[i] * glm.vec4(f, f, f, 1))).xyz)

    def left_trigger_down(self):
        self.throttle_down = 1
        self.turned_on = True

    def left_trigger_up(self):
        self.throttle_down = 0

    def right_trigger_down(self):
        self.throttle_up = 1
        self.turned_on = True

    def right_trigger_up(self):
        self.throttle_up = 0
