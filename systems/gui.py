from scripts.callbacks import *

from systems.system import System

from scripts.gui_entities import *


class GUI(System):
    def __init__(self, engine):
        System.__init__(self, engine)

        self.callbacks = {MOUSE_DOWN: self.on_mouse_down,
                          MOUSE_UP: self.on_mouse_up,
                          MOUSE_MOVE: self.on_mouse_move,
                          SET_SCREEN: self.set_screen,
                          WINDOW_SIZE: self.on_size}

        self.settings.update({'buttons/mouseover': True})

        self.next_screen = None
        self.screen = None
        self.button_normal = self.engine.graphics.get_texture('button_normal')
        self.screens = {'menu': [background(self.engine.graphics.get_texture('download')),
                                 button((.5, .5, -2), (.1, .1),
                                        self.button_normal, (SET_SCREEN, ['game'])),
                                 text((.5, .5, -1), .002, 'play')],
                        'game': [game_screen(),
                                 button((.2, .2, 0), (.1, .1),
                                        self.button_normal, (SET_SCREEN, ['menu'])),
                                 ]}

        self.set_screen('menu')
        self.w = 1
        self.h = 1

    def set_screen(self, screen):
        self.next_screen = screen
        if self.screen:
            for e in self.screens[self.screen]:
                self.engine.entities.remove(e)
        self.screen = screen
        for e in self.screens[self.screen]:
            self.engine.entities.append(e)

    def on_size(self, w, h):
        self.w = w
        self.h = h

    def pixel_to_screen(self, x, y):
        return ((x / float(self.w)), (y / float(self.h)))

    def collide_point(self, e, x, y):
        if abs(x - e[POS].x) < e[SIZE].x * .5:
            if abs(y - e[POS].y) < e[SIZE].y * .5:
                return True

    def get_colliding_button(self, x, y):
        sx, sy = self.pixel_to_screen(x, y)
        for e in self.engine.entities:
            if has_components(e, [POS, SIZE, BUTTON]):
                if self.collide_point(e, sx, sy):
                    return e
        return None

    def on_mouse_move(self, x, y, dx, dy):
        if self.settings['buttons/mouseover']:
            sx, sy = self.pixel_to_screen(x, y)

            for e in self.engine.entities:
                if has_components(e, [POS, SIZE, BUTTON, STATE, TEX]):
                    if self.collide_point(e, sx, sy):
                        if e[STATE] == BUTTON_NORMAL:
                            e[STATE] = BUTTON_OVER
                            e[TEX] = self.engine.graphics.get_texture('button_over')
                    else:
                        e[STATE] = BUTTON_NORMAL
                        e[TEX] = self.engine.graphics.get_texture('button_normal')

    def on_mouse_down(self, b, x, y):
        e = self.get_colliding_button(x, y)
        if e is not None:
            if has_components(e, [STATE]):
                e[STATE] = BUTTON_DOWN
                e[TEX] = self.engine.graphics.get_texture('button_down')

    def on_mouse_up(self, b, x, y):
        e = self.get_colliding_button(x, y)
        if e is not None:
            if has_components(e, [STATE]):
                e[STATE] = BUTTON_OVER
                e[TEX] = self.engine.graphics.get_texture('button_over')
            self.engine.dispatch(*e[BUTTON])

    def update(self, dt):
        pass
