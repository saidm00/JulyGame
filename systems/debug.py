from systems.system import System
from scripts.callbacks import *

from systems import joystick
from scripts.gui_entities import *


class Debug(System):
    def __init__(self, engine):
        System.__init__(self, engine)

        self.callbacks = {JOY_BUTTON_DOWN: self.on_joy_button_down}

        self.current_system = None
        self.path = []
        self.index = 0

        self.title = text((.8, .95, -.1), .002,
                          '', (0, 0, 1))
        self.engine.entities.append(self.title)
        self.entities = []

    def get_systems(self):
        return sorted([s for s in self.engine.systems if s is not self])

    def populate(self):
        self.clear()
        if self.current_system:
            self.title[TEXT] = str(self.current_system)

            settings, directories = self.current_system.get_settings(self.path)

            y = 0
            for key, value in settings:
                y += 1
                self.entities.append(text((.8, .9 - y * .05, -.1), .0015,
                                          '{} - {}'.format(key, value), (1, 1, 1)))

            y += .5
            for key in directories:
                y += 1
                self.entities.append(text((.8, .9 - y * .05, -.1), .0015,
                                          key, (1, 1, 1)))

        else:
            self.title[TEXT] = 'SYSTEMS'

            for y, s in enumerate(self.get_systems()):
                self.entities.append(text((.8, .9 - y * .05, -.1), .0015, str(s)))

        self.index = 0
        self.set_color(0, (1, 0, 0))
        self.engine.entities.extend(self.entities)

    def clear(self):
        self.title[TEXT] = ''
        for e in self.entities:
            self.engine.entities.remove(e)
        self.entities *= 0

    def set_color(self, i, color=(1, 1, 1)):
        self.entities[i][COLOR] = color

    def move_vertical(self, direction):
        self.set_color(self.index)

        self.index += direction
        if self.index < 0:
            self.index = 0
        elif self.index >= len(self.entities):
            self.index = len(self.entities) - 1

        self.set_color(self.index, (1, 0, 0))

    def on_joy_button_down(self, button):
        if button is joystick.LEFT:
            if self.path:
                self.path.pop()
                self.populate()

            elif self.current_system:
                self.current_system = None
                self.populate()

            else:
                self.clear()

        elif button is joystick.UP:
            if self.entities:
                self.move_vertical(-1)

        elif button is joystick.DOWN:
            if self.entities:
                self.move_vertical(1)

        elif button is joystick.RIGHT:
            if self.current_system:
                settings, directories = self.current_system.get_settings(self.path)
                if self.index < len(settings):
                    setting, value = settings[self.index]
                    name = '/'.join(self.path + [setting])

                    self.current_system.settings[name] = not value
                    self.entities[self.index][TEXT] = '{} - {}'.format(setting, not value)
                else:
                    i = len(settings) - self.index
                    self.path.append(directories[i])
                    self.populate()

            elif self.entities:
                self.current_system = self.get_systems()[self.index]
                self.populate()

            else:
                self.current_system = None
                self.populate()
