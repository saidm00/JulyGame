import glm
from scripts.components import *
from scripts.callbacks import *

BUTTON_DOWN, BUTTON_NORMAL, BUTTON_OVER = range(3)


def button(pos, size, texture, cb=(QUIT, ())):
    return {TAG: GUI_TAG,
            BUTTON: cb,
            POS: glm.vec3(pos),
            SIZE: glm.vec2(size),
            STATE: BUTTON_NORMAL,
            TEX: texture}


def background(texture):
    return {TAG: GUI_TAG,
            POS: glm.vec3(.5, .5, -9),
            TEX: texture}


def game_screen():
    return {TAG: GUI_TAG,
            POS: glm.vec3(.5, .5, -9),
            FBO_TEX: 0}


def text(pos, size, string, color=(1, 1, 1)):
    return {TAG: GUI_TAG,
            POS: glm.vec3(pos),
            SIZE: glm.vec2(size),
            COLOR: color,
            TEXT: string}
