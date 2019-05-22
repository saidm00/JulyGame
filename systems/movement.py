import math

from systems.system import System
from scripts.callbacks import *
from scripts.components import *
from scripts import character

from joystick import *


class Movement(System):
    def __init__(self, engine):
        System.__init__(self, engine)

        self.callbacks = {JOY_STICK: self.on_joystick,
                          JOY_BUTTON_DOWN: self.on_joy_button_down,
                          UPDATE: self.update}
        self.settings = {'friction': True}

        self.left_x = 0
        self.left_y = 0

        self.right_x = 0
        self.right_y = 0

    def on_joystick(self, stick_id, x, y, dt):
        for e in self.engine.entities:
            if has_tag(e, PLAYER_TAG):
                if stick_id is 0:
                    if MOVE_SPEED in e:
                        if ANGLE in e:
                            rads = (90 - e[ANGLE]) / 57.3
                            cos = math.cos(rads)
                            sin = math.sin(rads)

                            dx = cos * x + sin * y
                            dy = sin * x - cos * y

                        else:
                            dx = x
                            dy = y

                        speed = e[MOVE_SPEED] * dt

                        e[VEL].x += dx * speed
                        e[VEL].z += dy * speed

                elif stick_id is 1:
                    if ANGLE in e:
                        e[ANGLE] += x * dt

                break

    def on_joy_button_down(self, button):
        if button is A:
            for e in self.engine.entities:
                if has_tag(e, PLAYER_TAG):
                    if has_components(e, (JUMP, VEL, POS)):
                        if e[POS].y == 0:
                            e[VEL].y += e[JUMP]
                            if STATE in e:
                                e[STATE] = character.JUMPING

    def update(self, dt):
        for e in self.engine.entities:
            if VEL in e:
                if DAMPING in e:
                    d = 1 - (e[DAMPING] * dt)
                    e[VEL].x *= d
                    e[VEL].z *= d

                if GRAVITY in e:
                    e[VEL].y -= e[GRAVITY] * dt

                if POS in e:
                    e[POS] += e[VEL]
                    if e[POS].y <= 0:
                        e[POS].y = 0
                        e[VEL].y = 0

                        if self.settings['friction']:
                            if FRICTION in e:
                                f = 1 - (e[FRICTION] * dt)
                                e[VEL].x *= f
                                e[VEL].z *= f

                        if has_components(e, (STATE, ANIMATOR)):
                            if isinstance(e[ANIMATOR], character.Character):
                                e[STATE] = character.WALK
