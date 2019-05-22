# todo: comment

import pymunk
import math

from kivy.graphics import *

import vehicle, util


class Car(vehicle.Vehicle):
    height = 4.5

    accel_force = -100.0
    turn_force = .02
    idle_turn_factor = .3
    max_speed = 40
    min_speed = -max_speed * .6
    max_angular_velocity = 15

    seats = [(0, .3, 0),
             (-2, 1.5, 0)]

    wheel_offset = 1.9

    side_friction = 3
    friction_speed = 10
    stop_speed = .1

    a_damping = .4

    timer = 0

    def __init__(self, app, vehicle_id):
        vehicle.Vehicle.__init__(self, app, vehicle_id)

        wheel_tex = 'wheel.png'

    def move(self, input_vector, dt):
        self.input_vector = list(input_vector)
        accel = self.throttle_down - self.throttle_up

        self.local_vel = pymunk.Vec2d(self.collision.body.velocity).rotated(-self.collision.body.angle)

        if self.local_vel.x:
            mag = self.local_vel.x
            if not accel:
                mag *= self.idle_turn_factor
            self.input_vector[0] *= mag
        else:
            self.input_vector[0] = 0

        self.collision.body.apply_impulse_at_local_point((accel * self.accel_force * dt, 0))
        # self.collision.body.apply_impulse_at_local_point((0, self.input_vector[0] * self.turn_force * dt),
        #                                                  (self.wheel_offset, 0))

    def animate(self, turn, accel, dt):
        target_angle = turn * accel

        da = accel * 1000 * dt
        for r in self.wheel_rots:
            r.angle += da

        da = (target_angle - self.fr_rot.angle) * .2

        self.fr_rot.angle += da
        self.fl_rot.angle += da

    def update(self, dt):
        if self.is_kinematic:
            da, dx, dy, dz = self.lerp_move()

            self.animate(da * 15, 1, dt)
        else:
            self.animate(self.input_vector[0], (self.throttle_down - self.throttle_up), dt)

            if not self.collision.standing:
                self.collision.dy -= 10 * dt
                self.collision.move_y(dt)

        vehicle.Vehicle.update(self, dt)

    def draw(self, renderer):
        self.rot = Rotate(0, 0, 1, 0)
        Translate(0, 1.5, 0)

        self.app.graphic_data.draw_instance('models/vehicles/car',
                                            self.canvas,
                                            texture='metal.png')

        axel_width = 2.5

        renderer.push_matrix()
        Translate(2, 0, 0)

        renderer.push_matrix()
        Translate(0, 0, -axel_width)

        self.fl_rot = Rotate(0, 0, 1, 0)
        self.wheel_rots.add(Rotate(0, 0, 0, 1))
        self.app.graphic_data.draw_instance('models/vehicles/wheel',
                                            self.canvas,
                                            wheel_tex)
        renderer.pop_matrix()

        renderer.push_matrix()
        Translate(0, 0, axel_width)
        self.fr_rot = Rotate(0, 0, 1, 0)
        self.wheel_rots.add(Rotate(0, 0, 0, 1))
        self.app.graphic_data.draw_instance('models/vehicles/wheel',
                                            self.canvas,
                                            wheel_tex)
        renderer.pop_matrix()
        renderer.pop_matrix()

        renderer.push_matrix()
        Translate(-2, 0, 0)
        self.wheel_rots.add(Rotate(0, 0, 0, 1))

        renderer.push_matrix()
        Translate(0, 0, -axel_width)
        self.app.graphic_data.draw_instance('models/vehicles/wheel',
                                            self.canvas,
                                            wheel_tex)
        Translate(0, 0, axel_width * 2)
        self.app.graphic_data.draw_instance('models/vehicles/wheel',
                                            self.canvas,
                                            wheel_tex)
        renderer.pop_matrix()
        renderer.pop_matrix()
