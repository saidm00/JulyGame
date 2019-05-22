from systems.system import System
from scripts.callbacks import *
from scripts.components import *


class Animation(System):
    def __init__(self, engine):
        System.__init__(self, engine)

        self.callbacks = {UPDATE: self.update,
                          ON_PAUSE: self.on_pause,
                          JOY_STICK: self.on_joystick}

    def on_joystick(self, stick_id, x, y, dt):
        if stick_id is 0:
            for e in self.engine.entities:
                if ANIMATOR in e:
                    e[ANIMATOR].in_y = y

    def update(self, dt):
        for e in self.engine.entities:
            if ANIMATOR in e:
                e[ANIMATOR].update(e, dt)
