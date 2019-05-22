from PIL import Image
from OpenGL.GL import *
import numpy as np


class Texture(object):
    def __init__(self, filename, linear=True):
        self.tex_id = glGenTextures(1)

        image = Image.open(filename)
        image = image.transpose(Image.FLIP_TOP_BOTTOM)
        # image.transpose(Image.FLIP_LEFT_RIGHT)

        self.w = image.width
        self.h = image.height

        data = np.array(list(image.getdata()), np.uint8)
        # data = image.getdata()

        glPixelStorei(GL_UNPACK_ALIGNMENT, 1)
        glBindTexture(GL_TEXTURE_2D, self.tex_id)

        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB8,
                     self.w, self.h, 0, GL_RGB,
                     GL_UNSIGNED_BYTE, data)

        image.close()

        glGenerateMipmap(GL_TEXTURE_2D)

        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)

        if linear:
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        else:
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_NEAREST)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
