from pyglfw.libapi import *

from scripts import (gui,
                     input_manager)


class Screen:
    def __init__(self, engine):
        self.engine = engine

        self.elements = {}

    def on_enter(self):
        pass

    def on_leave(self):
        pass

    def on_joy_stick(self, axis, dx, dy):
        pass

    def on_joy_button_down(self, button):
        pass

    def on_joy_button_up(self, button):
        pass

    def on_key_down(self, key):
        pass

    def on_key_up(self, key):
        pass

    def on_mouse_down(self, button, x, y):
        pass

    def on_mouse_up(self, button, x, y):
        pass

    def on_mouse_move(self, x, y, dx, dy):
        pass

    def on_size(self, w, h):
        pass

    def draw(self, renderer):
        for e in self.elements.itervalues():
            e.draw(renderer)

    def update(self, dt):
        pass


class GameScreen(Screen):
    def __init__(self, engine):
        self.engine = engine

        self.elements = {'game_display': gui.GameDisplay(self.engine),
                         'health': gui.StatBar(self.engine, 'button_down', (0, 1, 0), 0),
                         'fuel': gui.StatBar(self.engine, 'button_down', (0, 0, 1), 1)}

    def on_enter(self):
        self.engine.input_manager.toggle_mouse_lock(True)

    def on_leave(self):
        self.engine.input_manager.toggle_mouse_lock(False)

    def on_joy_stick(self, stick, dx, dy):
        if stick is 0:
            self.engine.game_manager.player.set_input(dx, dy)
        elif stick is 1:
            self.engine.renderer.camera.rotate(dx, dy)

    def on_joy_button_down(self, button):
        if button == input_manager.A:
            self.engine.game_manager.player.do_jump()
        elif button == input_manager.Y:
            self.engine.game_manager.player.drive()
        elif button == input_manager.LT_BUTTON:
            self.engine.game_manager.player.left_trigger_down()
        elif button == input_manager.RT_BUTTON:
            self.engine.game_manager.player.right_trigger_down()
        elif button == input_manager.START:
            self.engine.screen_manager.transition('menu')

    def on_joy_button_up(self, button):
        if button == input_manager.A:
            self.engine.game_manager.player.stop_jump()
        elif button == input_manager.LT_BUTTON:
            self.engine.game_manager.player.left_trigger_up()
        elif button == input_manager.RT_BUTTON:
            self.engine.game_manager.player.right_trigger_up()

    def on_key_down(self, key):
        if key is GLFW_KEY_D:
            self.engine.game_manager.player.add_input(1, 0)
        elif key is GLFW_KEY_A:
            self.engine.game_manager.player.add_input(-1, 0)
        elif key is GLFW_KEY_W:
            self.engine.game_manager.player.add_input(0, -1)
        elif key is GLFW_KEY_S:
            self.engine.game_manager.player.add_input(0, 1)
        elif key is GLFW_KEY_E:
            self.engine.game_manager.player.drive()
        elif key is GLFW_KEY_SPACE:
            self.engine.game_manager.player.do_jump()

    def on_key_up(self, key):
        if key is GLFW_KEY_D:
            self.engine.game_manager.player.add_input(-1, 0)
        elif key is GLFW_KEY_A:
            self.engine.game_manager.player.add_input(1, 0)
        elif key is GLFW_KEY_W:
            self.engine.game_manager.player.add_input(0, 1)
        elif key is GLFW_KEY_S:
            self.engine.game_manager.player.add_input(0, -1)
        elif key is GLFW_KEY_SPACE:
            self.engine.game_manager.player.stop_jump()

    def on_mouse_down(self, button, x, y):
        if button == 1:
            self.engine.game_manager.player.left_trigger_down()
        elif button == 0:
            self.engine.game_manager.player.right_trigger_down()

    def on_mouse_up(self, button, x, y):
        if button == 1:
            self.engine.game_manager.player.left_trigger_up()
        elif button == 0:
            self.engine.game_manager.player.right_trigger_up()

    def on_mouse_move(self, x, y, dx, dy):
        self.engine.renderer.camera.rotate(dx, dy)


class MenuScreen(Screen):
    def __init__(self, engine):
        self.engine = engine

        self.play_button = gui.Button(self.engine, (0, 0), (.2, .2),
                                      'button_down', 'button_normal',
                                      'button_over')

        self.elements = {'background': gui.Background(self.engine, 'download'),
                         'play_button': self.play_button}

    def on_mouse_move(self, x, y, dx, dy):
        self.play_button.collide_point(*self.engine.screen_manager.pixel_to_screen(x, y))

    def on_mouse_down(self, button, x, y):
        sx, sy = self.engine.screen_manager.pixel_to_screen(x, y)

        if self.play_button.collide_point(sx, sy):
            self.play_button.on_click(sx, sy)
            self.engine.screen_manager.transition('game')

    def on_mouse_up(self, button, x, y):
        sx, sy = self.engine.screen_manager.pixel_to_screen(x, y)

        if self.play_button.collide_point(sx, sy):
            self.play_button.on_release(sx, sy)
