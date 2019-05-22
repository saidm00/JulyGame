from pyglfw.libapi import *

import glm

from scripts import screen


class ScreenManager(object):
    fade_speed = 2

    def __init__(self, engine):
        self.engine = engine

        self.screens = {'game': screen.GameScreen(self.engine),
                        'menu': screen.MenuScreen(self.engine)}

        self.current = None
        self.screen = None

        self.size = glm.vec2(1, 1)

        self.next_screen = None

        self.fading = False
        self.fade_timer = 1
        self.engine.renderer.set_opacity(1)

        self.set_screen('menu')

    def pixel_to_screen(self, x, y):
        return (x * 2 / self.size.x) - 1, (y * 2 / self.size.y) - 1

    def on_joy_stick(self, axis, dx, dy):
        if self.screen:
            self.screen.on_joy_stick(axis, dx, dy)

    def on_joy_button_down(self, button):
        if self.screen:
            self.screen.on_joy_button_down(button)

    def on_joy_button_up(self, button):
        if self.screen:
            self.screen.on_joy_button_up(button)

    def on_key_down(self, key):
        if key is GLFW_KEY_ESCAPE:
            glfwSetWindowShouldClose(self.engine.renderer.window, True)
        else:
            if self.screen:
                self.screen.on_key_down(key)

    def on_key_up(self, key):
        if self.screen:
            self.screen.on_key_up(key)

    def on_mouse_down(self, button, x, y):
        if self.screen:
            self.screen.on_mouse_down(button, x, y)

    def on_mouse_up(self, button, x, y):
        if self.screen:
            self.screen.on_mouse_up(button, x, y)

    def on_mouse_move(self, x, y, dx, dy):
        if self.screen:
            self.screen.on_mouse_move(x, y, dx, dy)

    def on_size(self, w, h):
        self.size.x = w
        self.size.y = h

    def transition(self, screen_name):
        if screen_name in self.screens:
            self.next_screen = screen_name
            self.fade_timer = 1
            self.fading = True

    def set_screen(self, screen_name):
        if screen_name in self.screens:
            self.fade_timer = 0
            if self.screen:
                self.screen.on_leave()
            self.screen = self.screens[screen_name]
            self.screen.on_enter()
            self.current = self.next_screen

    def get_element(self, name):
        return self.screen.elements.get(name, None)

    def draw(self, renderer):
        if self.screen:
            self.screen.draw(renderer)

    def update(self, dt):
        if self.fading:
            if self.next_screen is self.current:
                self.fade_timer += dt * self.fade_speed
                if self.fade_timer > 1:
                    self.fade_timer = 1
                    self.fading = False

            else:
                self.fade_timer -= dt * self.fade_speed
                if self.fade_timer < 0:
                    self.set_screen(self.next_screen)

            self.engine.renderer.set_opacity(self.fade_timer)

        if self.screen:
            self.screen.update(dt)
