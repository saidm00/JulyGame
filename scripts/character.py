# todo: comment

import math
import glm

import util

WALK, JUMPING, DRIVING, DIE, WIN, GRAB = range(6)


class Character:
    state = -1
    anim_timer = 0

    arm_pitch = 0

    grab_arm_roll = 20
    grab_arm_angle = 130

    def __init__(self, engine):
        self.engine = engine

        self.texture = self.engine.graphics.get_texture('robot_texture')

        self.cylinder = engine.graphics.get_mesh('models/player/cylinder')

        self.body_mesh = engine.graphics.get_mesh('models/player/robot_body')
        self.head_mesh = engine.graphics.get_mesh('models/player/robot_head')
        self.arm_mesh = engine.graphics.get_mesh('models/player/robot_arm')
        self.leg_mesh = engine.graphics.get_mesh('models/player/robot_leg')
        self.jetpack_mesh = engine.graphics.get_mesh('models/player/jetpack')

        self.pos = glm.vec3(0, 0, 0)

        self.head_yaw = 0
        self.head_pitch = 45
        self.right_arm_rot = 90
        self.right_arm_roll = 0
        self.left_arm_rot = 90
        self.left_arm_roll = 0
        self.right_leg_rot = 0
        self.left_leg_rot = 0
        self.rot = 0

    def do_animation(self, player, dt):
        speed = 10 * dt

        if player.attacking:
            self.right_arm_roll = util.lerp_int(self.right_arm_roll, 0, speed)
            self.left_arm_roll = util.lerp_int(self.left_arm_roll, 0, speed)
            self.right_arm_rot = util.lerp_int(self.right_arm_rot, self.arm_pitch, speed * 2)
            self.left_arm_rot = util.lerp_int(self.left_arm_rot, self.arm_pitch, speed * 2)
            # self.right_arm_roll.angle = util.lerp_int(self.right_arm_roll.angle, 135, speed)
            # self.left_arm_roll.angle = util.lerp_int(self.left_arm_roll.angle, 60, speed)
            # self.right_arm_rot.angle = util.lerp_int(self.right_arm_rot.angle, -40, speed * 2)
            # self.left_arm_rot.angle = util.lerp_int(self.left_arm_rot.angle, 135, speed * 2)

        if player.state == DRIVING:
            self.right_leg_rot = 90
            self.left_leg_rot = 90

            if player.vehicle is not None:
                self.rot = player.vehicle.angle

        elif player.state == WALK:
            vel = player.get_velocity()
            self.anim_timer += dt * vel
            arm_swing = 5 * vel
            swing_time = 7

            swing_pos = util.loop_time(self.anim_timer, swing_time)

            self.right_leg_rot = arm_swing * swing_pos
            self.left_leg_rot = -arm_swing * swing_pos

            if not player.attacking:
                self.right_arm_roll = util.lerp_int(self.right_arm_roll, -5, speed)
                self.left_arm_roll = util.lerp_int(self.left_arm_roll, 5, speed)
                self.right_arm_rot = util.lerp_int(self.right_arm_rot,
                                                   -arm_swing * util.loop_time(self.anim_timer,
                                                                               swing_time),
                                                   speed)
                self.left_arm_rot = util.lerp_int(self.left_arm_rot,
                                                  arm_swing * util.loop_time(self.anim_timer,
                                                                             swing_time),
                                                  speed)

        elif player.state == JUMPING:
            lean = player.in_y * 50

            self.right_leg_rot = util.lerp_int(self.right_leg_rot, lean, speed)
            self.left_leg_rot = util.lerp_int(self.left_leg_rot, lean, speed)

            if not player.attacking:
                self.right_arm_roll = util.lerp_int(self.right_arm_roll, -20, speed)
                self.left_arm_roll = util.lerp_int(self.left_arm_roll, 20, speed)
                self.right_arm_rot = util.lerp_int(self.right_arm_rot, lean, speed)
                self.left_arm_rot = util.lerp_int(self.left_arm_rot, lean, speed)

        elif player.state == DIE:
            speed = dt * 10

            self.right_leg_rot = util.lerp_int(self.right_leg_rot, 90, speed)
            self.left_leg_rot = util.lerp_int(self.left_leg_rot, 90, speed)
            self.right_arm_rot = util.lerp_int(self.right_arm_rot, 0, speed)
            self.left_arm_rot = util.lerp_int(self.left_arm_rot, 0, speed)

            self.pos.y = player.collider.pos.y - 1.5

        elif player.state == WIN:
            speed = dt * 3

            self.right_leg_rot = util.lerp_int(self.right_leg_rot, -20, speed)
            self.left_leg_rot = util.lerp_int(self.left_leg_rot, 20, speed)
            self.right_arm_rot = util.lerp_int(self.right_arm_rot, 130, speed)
            self.left_arm_rot = util.lerp_int(self.left_arm_rot, 0, speed)
            self.right_arm_roll = util.lerp_int(self.right_arm_roll, 0, speed)
            self.left_arm_roll = util.lerp_int(self.left_arm_roll, 30, speed)

        elif player.state == GRAB:
            speed = dt * 30

            self.right_leg_rot = util.lerp_int(self.right_leg_rot, 25, speed)
            self.left_leg_rot = util.lerp_int(self.left_leg_rot, 25, speed)
            self.right_arm_rot = util.lerp_int(self.right_arm_rot, self.grab_arm_angle, speed)
            self.left_arm_rot = util.lerp_int(self.left_arm_rot, self.grab_arm_angle, speed)
            self.right_arm_roll = util.lerp_int(self.right_arm_roll, -self.grab_arm_roll, speed)
            self.left_arm_roll = util.lerp_int(self.left_arm_roll, self.grab_arm_roll, speed)

    def get_hand_pos(self, index, distance=-1.5):
        rads = self.rot / 57.3
        sin = math.cos(rads)
        cos = math.sin(rads)

        arm_rads = self.right_arm_rot / 57.3

        local_x = 1.2 * index
        local_z = math.sin(arm_rads) * distance
        local_y = math.cos(arm_rads) * distance

        x = self.pos.x + (cos * local_x + -sin * local_z)
        y = self.pos.y + local_y + 3.5
        z = self.pos.z + (sin * local_x + cos * local_z)

        return x, y, z, -sin * local_z, local_y, cos * local_z

    def draw(self, renderer):

        renderer.set_texture(self.texture)

        renderer.push_matrix()

        renderer.translate(*self.pos.xyz)

        # renderer.update_matrix()
        # self.cylinder.draw()

        renderer.push_matrix()

        renderer.translate(0, 3.75, 0)
        renderer.rotate(self.head_yaw, 0, 1, 0)
        renderer.rotate(self.head_pitch, 1, 0, 0)

        renderer.update_matrix()
        self.head_mesh.draw()

        renderer.pop_matrix()

        renderer.rotate(self.rot, 0, 1, 0)
        renderer.update_matrix()
        self.body_mesh.draw()

        renderer.push_matrix()
        renderer.translate(0, 3.25, 1.25)
        renderer.rotate(self.right_arm_rot, 0, 0, 1)
        renderer.rotate(self.right_arm_roll, 1, 0, 0)

        renderer.update_matrix()
        self.arm_mesh.draw()

        renderer.pop_matrix()

        renderer.push_matrix()
        renderer.translate(0, 3.25, -1.25)
        renderer.rotate(self.left_arm_rot, 0, 0, 1)
        renderer.rotate(self.left_arm_roll, 1, 0, 0)

        renderer.update_matrix()
        self.arm_mesh.draw()

        renderer.pop_matrix()

        renderer.push_matrix()
        renderer.translate(0, 1.75, .4)
        renderer.rotate(self.right_leg_rot, 0, 0, 1)

        renderer.update_matrix()
        self.leg_mesh.draw()

        renderer.pop_matrix()

        renderer.push_matrix()
        renderer.translate(0, 1.75, -.4)
        renderer.rotate(self.left_leg_rot, 0, 0, 1)

        renderer.update_matrix()
        self.leg_mesh.draw()

        renderer.pop_matrix()

        renderer.push_matrix()

        renderer.translate(-.5, 3, 0)
        renderer.scale(.75)

        renderer.update_matrix()
        self.jetpack_mesh.draw()

        # Color(1, 0, 0, 1)
        # Rotate(270, 0, 1, 0)
        # Translate(-.8, .55, .5)
        # Scale(.8, .8, 1)
        # self.scale = Scale()
        #
        # self.app.graphic_data.draw_mesh('models/UI/health_bar',
        #                                 self.canvas)
        renderer.pop_matrix()
        renderer.pop_matrix()
