import time
import gc
import sys

from scripts import (renderer,
                     input_manager,
                     game_manager,
                     graphics,
                     physics,
                     resource_manager,
                     screen_manager)


class Engine(object):
    framerate = 1 / 60.0

    def __init__(self):
        self.resource_manager = resource_manager.ResourceManager(self)
        self.physics = physics.Physics(self)
        self.graphics = graphics.Graphics()
        self.renderer = renderer.Renderer(self)
        self.input_manager = input_manager.InputManager(self)
        self.game_manager = game_manager.GameManager(self)
        self.screen_manager = screen_manager.ScreenManager(self)
        self.game_manager.load()

        self.running = True
        self.last_time = 0

        gc.disable()
        sys.setcheckinterval(1000)

    def run(self):
        self.renderer.on_size(800, 600)
        last_frame = time.time()
        while self.running:

            current_frame = time.time()
            dt = current_frame - last_frame
            if dt >= self.framerate:
                if dt > .1:
                    dt = .1
                self.input_manager.update(dt)
                self.physics.update(dt)
                self.game_manager.update(dt)
                self.renderer.update(dt)
                self.screen_manager.update(dt)
                last_frame = current_frame

                gc.collect()

        self.renderer.on_stop()
