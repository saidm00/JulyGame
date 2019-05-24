from OpenGL.GL import *
from OpenGL.arrays import *


class Mesh:
    def __init__(self, vertices, normals, texcoords, indices):
        self.vao = glGenVertexArrays(1)
        glBindVertexArray(self.vao)

        self.vertexBuffers = glGenBuffers(4)

        glBindBuffer(GL_ARRAY_BUFFER, self.vertexBuffers[0])
        glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 0, ctypes.cast(0, ctypes.c_void_p))

        glBindBuffer(GL_ARRAY_BUFFER, self.vertexBuffers[1])
        glBufferData(GL_ARRAY_BUFFER, normals.nbytes, normals, GL_STATIC_DRAW)
        glEnableVertexAttribArray(1)
        glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 0, ctypes.cast(0, ctypes.c_void_p))

        glBindBuffer(GL_ARRAY_BUFFER, self.vertexBuffers[2])
        glBufferData(GL_ARRAY_BUFFER, texcoords.nbytes, texcoords, GL_STATIC_DRAW)
        glEnableVertexAttribArray(2)
        glVertexAttribPointer(2, 2, GL_FLOAT, GL_FALSE, 0, ctypes.cast(0, ctypes.c_void_p))

        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.vertexBuffers[3])
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, indices.nbytes, indices, GL_STATIC_DRAW)
        self.indexCount = indices.size

        glBindVertexArray(0)

    def draw(self):
        glBindVertexArray(self.vao)
        glDrawElements(GL_TRIANGLES, self.indexCount, GL_UNSIGNED_INT, ctypes.cast(0, ctypes.c_void_p))
        glBindVertexArray(0)