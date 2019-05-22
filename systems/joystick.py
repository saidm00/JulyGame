
from pyglfw.libapi import *

from scripts.callbacks import *
from systems.system import System

LX, LY, RX, RY, LT, RT = range(6)
A, B, X, Y, LB, RB, SELECT, START, L_STICK, R_STICK, UP, RIGHT, DOWN, LEFT = range(14)
LT_BUTTON, RT_BUTTON = -2, -1


class Joystick(System):
    def __init__(self, engine):
        System.__init__(self, engine)
        self.callbacks = {UPDATE: self.update}

        # joystick_present = glfwJoystickPresent(GLFW_JOYSTICK_1)

        self.deadzone = .4

        self.joy_stopped = False

        self.rt_down = False
        self.lt_down = False
        self.button_states = [False for _ in range(14)]

    def update(self, dt):
        joy_axis = glfwGetJoystickAxes(GLFW_JOYSTICK_1)
        joy_buttons = glfwGetJoystickButtons(GLFW_JOYSTICK_1)

        ix = joy_axis[LX]
        if abs(ix) < self.deadzone:
            ix = 0
        iy = joy_axis[LY]
        if abs(iy) < self.deadzone:
            iy = 0

        stopped = (ix == 0 and iy == 0)

        if not stopped or not self.joy_stopped:
            self.joy_stopped = stopped
            self.engine.dispatch(JOY_STICK, (0, ix, iy, dt))

        self.engine.dispatch(JOY_STICK, (1, joy_axis[RX] * -6, joy_axis[RY] * -6, dt))

        for button, value in enumerate(joy_buttons):
            if value != self.button_states[button]:
                self.button_states[button] = value
                if value:
                    self.engine.dispatch(JOY_BUTTON_DOWN, [button])
                else:
                    self.engine.dispatch(JOY_BUTTON_UP, [button])

        rt_down = joy_axis[RT] > 0
        if rt_down != self.rt_down:
            self.rt_down = rt_down
            if self.rt_down:
                self.engine.dispatch(JOY_BUTTON_DOWN, [RT_BUTTON])
            else:
                self.engine.dispatch(JOY_BUTTON_UP, [RT_BUTTON])

        lt_down = joy_axis[LT] > 0
        if lt_down != self.lt_down:
            self.lt_down = lt_down
            if self.lt_down:
                self.engine.dispatch(JOY_BUTTON_DOWN, [LT_BUTTON])
            else:
                self.engine.dispatch(JOY_BUTTON_UP, [LT_BUTTON])


