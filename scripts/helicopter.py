# todo: comment

import glm

import vehicle, util


class Helicopter(vehicle.Vehicle):
    height = 5.5

    accel_force = 100.0
    vertical_force = 5
    turn_force = 50
    idle_turn_factor = .3
    max_speed = 20
    min_speed = -max_speed * .5
    max_angular_velocity = 2

    max_y_vel = 10

    wheel_offset = 1

    seats = [glm.vec4(0, -.1, -1.5, 1),
             glm.vec4(0, -.1, 1.5, 1)]

    side_friction = 3
    friction_speed = 15
    stop_speed = .1

    a_damping = .4

    prop_vel = 0

    pitch = 0
    roll = 0
    prop_rot = 0

    def __init__(self, *args):
        vehicle.Vehicle.__init__(self, *args)

        self.collider.height = 7
        self.collider.radius = 3

        self.texture = self.engine.graphics.get_texture('metal')
        self.mesh = self.engine.graphics.get_mesh('models/vehicles/helicopter')
        self.prop_mesh = self.engine.graphics.get_mesh('models/vehicles/propellers')

    def animate(self, ix, iy, accel, platform, dt):
        if self.turned_on:
            target_vel = accel * 200 + 700
            self.prop_vel += cmp(target_vel, self.prop_vel) * 500 * dt

            self.prop_rot += self.prop_vel * dt

        elif self.prop_vel > 0:
            self.prop_vel -= 200 * dt
            if self.prop_vel < 0:
                self.prop_vel = 0
            else:
                self.prop_rot += self.prop_vel * dt

        if platform:
            if self.collider.vel.y > 0:
                self.collider.platform = None
            else:
                self.collider.vel *= 1 - (10 * dt)
            self.pitch = 0
            self.roll = 0
        else:
            self.pitch += (iy * 20 - self.pitch) * .01
            self.roll += (ix * 20 - self.roll) * .01

    def update(self, dt):
        # print (self.throttle_up - self.throttle_down - .2)
        accel = self.throttle_up - self.throttle_down

        if not self.collider.platform:
            accel -= .2

        if accel:
            self.collider.sleeping = False
            self.collider.force.y += accel * self.vertical_force

        self.animate(self.ix, self.iy,
                     (self.throttle_up - self.throttle_down),
                     self.collider.platform,
                     dt)

        if not self.collider.platform and 0 in self.occupied_seats:
            if abs(self.collider.vel.y) > self.max_y_vel:
                self.collider.vel.y = cmp(self.collider.vel.y, 0) * self.max_y_vel

            rot_mat = glm.rotate(glm.mat4(1.0), glm.radians(90 - self.angle), glm.vec3(0, 1, 0))

            local_vel = rot_mat * glm.vec4(self.collider.vel, 1)

            local_vel.x += self.ix * self.accel_force * dt
            local_vel.z += self.iy * self.turn_force * dt

            turn_input = util.angle_diff(self.angle, 90-self.engine.renderer.camera.yaw) * .1
            turn_force = self.turn_force * turn_input
            self.angle += turn_force * dt

            local_vel.z *= 1 - self.side_friction * dt
            local_vel.x = min(self.max_speed, max(self.min_speed, local_vel.x))
            self.collider.vel = glm.vec3(glm.inverse(rot_mat) * local_vel).xyz

    def draw(self, renderer):
        renderer.set_texture(self.texture)

        renderer.push_matrix()

        renderer.translate(*self.collider.pos)
        renderer.rotate(self.angle, 0, 1, 0)
        renderer.rotate(self.pitch, 0, 0, 1)
        renderer.rotate(self.roll, 1, 0, 0)

        renderer.update_matrix()
        self.model_mat = renderer.model_mat
        self.mesh.draw()

        renderer.rotate(self.prop_rot, 0, 1, 0)

        renderer.translate(0, 6.5, 0)

        renderer.update_matrix()
        self.prop_mesh.draw()

        renderer.pop_matrix()
