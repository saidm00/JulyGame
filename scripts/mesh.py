from OpenGL.GL import *

import numpy as np


class Mesh(object):
    def __init__(self, *args):
        self.vao = glGenVertexArrays(1)
        glBindVertexArray(self.vao)

        self.vbo = glGenBuffers(len(args))

        for i, attr in enumerate(args[:-1]):
            l, data = attr
            data = data.flatten()

            glBindBuffer(GL_ARRAY_BUFFER, self.vbo[i])
            glBufferData(GL_ARRAY_BUFFER, data.nbytes, data, GL_STATIC_DRAW)
            glEnableVertexAttribArray(i)
            glVertexAttribPointer(i, l, GL_FLOAT, GL_FALSE, 0, 0)

        indices = args[-1]
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.vbo[len(args)-1])
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, indices.nbytes, indices, GL_STATIC_DRAW)

        self.index_count = len(indices)

    def draw(self):
        glBindVertexArray(self.vao)
        glDrawElements(GL_TRIANGLES, self.index_count, GL_UNSIGNED_INT, 0)
        glBindVertexArray(0)