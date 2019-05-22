import glm

import math


class Camera(object):
    min_pitch = -45
    max_pitch = 80

    pitch_speed = 7
    yaw_speed = 7
    move_speed = 10

    target_pitch = 0
    target_yaw = 0
    target_pos = glm.vec3()

    def __init__(self, eye, up, center, fovy, aspect, near, far):
        self.fovy = fovy
        self.aspect = aspect
        self.near = near
        self.far = far

        self.pos = glm.vec3(0, -6, 0)
        self.offset = glm.vec3(0, 0, -15)
        self.pitch = 0
        self.yaw = 0

    def get_forward_xz(self):
        rads = -glm.radians(self.yaw)
        return math.cos(rads), math.sin(rads)

    def set_pos(self, x, y, z):
        self.target_pos = glm.vec3(-x, -y, -z)

    def rotate(self, yaw, pitch):
        self.target_yaw += yaw
        self.target_pitch += pitch
        if self.target_pitch < self.min_pitch:
            self.target_pitch = self.min_pitch
        elif self.target_pitch > self.max_pitch:
            self.target_pitch = self.max_pitch

    def getView(self):
        m = glm.mat4(1.0)
        m = glm.translate(m, self.offset)
        m = glm.rotate(m, glm.radians(self.pitch), (1, 0, 0))
        m = glm.rotate(m, glm.radians(self.yaw), (0, 1, 0))
        m = glm.translate(m, self.pos)

        return m

        # return glm.translate(glm.lookAt(self.eye, self.eye + self.center, self.up), -self.eye)

    def getProjection(self):
        return glm.perspective(self.fovy, self.aspect, self.near, self.far)

    def update(self, dt):
        self.pos += (self.target_pos - self.pos) * self.move_speed * dt
        self.pitch += (self.target_pitch - self.pitch) * self.pitch_speed * dt
        self.yaw += (self.target_yaw - self.yaw) * self.yaw_speed * dt
