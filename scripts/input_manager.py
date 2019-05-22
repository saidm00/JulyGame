from pyglfw.libapi import *

LX, LY, RX, RY, LT, RT = range(6)
A, B, X, Y, LB, RB, SELECT, START, L_STICK, R_STICK, UP, RIGHT, DOWN, LEFT = range(14)
LT_BUTTON, RT_BUTTON = -2, -1


# JOYSTICK = 1


class InputManager:
    def __init__(self, engine):
        self.engine = engine

        window = self.engine.renderer.window
        glfwSetKeyCallback(window, on_key)
        glfwSetMouseButtonCallback(window, on_mouse_button)
        glfwSetCursorEnterCallback(window, on_cursor_enter)
        glfwSetCursorPosCallback(window, on_cursor_pos)
        glfwSetScrollCallback(window, on_scroll)

        joystick_present = glfwJoystickPresent(GLFW_JOYSTICK_1)

        # glfwSetDropCallback(window, on_file_drop)

        self.deadzone = .2

        self.reset_cursor = True
        self.last_x = 0
        self.last_y = 0
        self.lock_cursor = False

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
            self.engine.screen_manager.on_joy_stick(0, ix, -iy)

        self.engine.screen_manager.on_joy_stick(1, joy_axis[RX] * 6, -joy_axis[RY] * 6)

        for button, value in enumerate(joy_buttons):
            if value != self.button_states[button]:
                self.button_states[button] = value
                if value:
                    self.engine.screen_manager.on_joy_button_down(button)
                else:
                    self.engine.screen_manager.on_joy_button_up(button)

        rt_down = joy_axis[RT] > 0
        if rt_down != self.rt_down:
            self.rt_down = rt_down
            if self.rt_down:
                self.engine.screen_manager.on_joy_button_down(RT_BUTTON)
            else:
                self.engine.screen_manager.on_joy_button_up(RT_BUTTON)

        lt_down = joy_axis[LT] > 0
        if lt_down != self.lt_down:
            self.lt_down = lt_down
            if self.lt_down:
                self.engine.screen_manager.on_joy_button_down(LT_BUTTON)
            else:
                self.engine.screen_manager.on_joy_button_up(LT_BUTTON)

    def on_scroll(self, dx, dy):
        pass

    def on_key_down(self, key):
        self.engine.screen_manager.on_key_down(key)

    def on_key_up(self, key):
        self.engine.screen_manager.on_key_up(key)

    def on_mouse_down(self, button):
        self.engine.screen_manager.on_mouse_down(button, self.last_x, self.last_y)

    def on_mouse_up(self, button):
        self.engine.screen_manager.on_mouse_up(button, self.last_x, self.last_y)

    def on_cursor_enter(self, entered):
        print entered

    def on_cursor_pos(self, x, y):
        if self.reset_cursor:
            self.reset_cursor = False
            dx = dy = 0
        else:
            dx = x - self.last_x
            dy = y - self.last_y
        self.last_x = x
        self.last_y = y

        self.engine.screen_manager.on_mouse_move(x, y, dx, dy)

    def toggle_mouse_lock(self, value=None):
        if value is None:
            self.lock_cursor = not self.lock_cursor
        else:
            self.lock_cursor = value

        if self.lock_cursor:
            glfwSetInputMode(self.engine.renderer.window, GLFW_CURSOR, GLFW_CURSOR_DISABLED)
        else:
            glfwSetInputMode(self.engine.renderer.window, GLFW_CURSOR, GLFW_CURSOR_NORMAL)
        self.reset_cursor = True


@GLFWkeyfun
def on_key(window, key, scancode, action, mods):
    if action is 1:
        renderer = glfwGetWindowUserPointer(window)
        renderer.engine.input_manager.on_key_down(key)

    elif action is 0:
        renderer = glfwGetWindowUserPointer(window)
        renderer.engine.input_manager.on_key_up(key)


@GLFWmousebuttonfun
def on_mouse_button(window, button, action, mods):
    if action is 1:
        renderer = glfwGetWindowUserPointer(window)
        renderer.engine.input_manager.on_mouse_down(button)

    elif action is 0:
        renderer = glfwGetWindowUserPointer(window)
        renderer.engine.input_manager.on_mouse_up(button)


@GLFWcursorenterfun
def on_cursor_enter(window, entered):
    renderer = glfwGetWindowUserPointer(window)
    renderer.engine.input_manager.on_cursor_enter(entered)


@GLFWcursorposfun
def on_cursor_pos(window, x, y):
    renderer = glfwGetWindowUserPointer(window)
    renderer.engine.input_manager.on_cursor_pos(x, y)


@GLFWscrollfun
def on_scroll(window, dx, dy):
    renderer = glfwGetWindowUserPointer(window)
    renderer.engine.input_manager.on_scroll(dx, dy)

# @GLFWdropfun
# def on_scroll(window, count, paths):
#     renderer = glfwGetWindowUserPointer(window)
#     renderer.engine.input_manager.on_scroll(dx, dy)

# def on_joystick_conn(joy, event):
#     if event == GLFW_CONNECTED:
#         print 'connected joystick'
#
#     elif event == GLFW_DISCONNECTED:
#         print 'disconnected joystick'
