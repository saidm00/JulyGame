import numpy as np
import glm

from OpenGL.GL import *

from scripts import mesh


class Rectangle(object):
    verts = np.array((-1, -1, 0,
                      1, -1, 0,
                      1, 1, 0,
                      -1, 1, 0), dtype=np.float32)
    tex_coords = np.array((0, 0,
                           1, 0,
                           1, 1,
                           0, 1), dtype=np.float32)
    indices = np.array((0, 1, 2, 0, 2, 3), dtype=np.uint32)

    def __init__(self):
        self.mesh = mesh.Mesh((3, self.verts),
                              (2, self.tex_coords),
                              self.indices)

    def collide_point(self, x, y):
        return False

    def on_click(self, x, y):
        pass

    def on_release(self, x, y):
        pass

    def draw(self, renderer):
        self.mesh.draw()


class Text(Rectangle):
    def __init__(self, engine, text=''):
        Rectangle.__init__(self, engine)
        self.text = text

    def draw(self, renderer):
        pass


class GameDisplay(Rectangle):
    def __init__(self, engine):
        Rectangle.__init__(self)

        self.texture = engine.renderer.fbo.texture

    def draw_game(self, renderer):
        renderer.fbo.bind()

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        view = renderer.camera.getView()

        renderer.instances.clear()

        renderer.bind(renderer.shader)
        renderer.shader.set_mat4('view', view)
        for o in renderer.scene:
            o.draw(renderer)

        renderer.bind(renderer.instanced_shader)
        renderer.instanced_shader.set_mat4('view', view)
        for k, v in renderer.instances.iteritems():
            mesh_data = k.split(' ')
            if len(mesh_data) == 2:
                renderer.set_texture(renderer.engine.graphics.get_texture(mesh_data[1]))

            mesh = renderer.engine.graphics.get_mesh(mesh_data[0])
            # self.instanced_shader.set_mat4('model', v[0])

            for i in range(0, len(v), 254):
                mats = v[i:min(i + 254, len(v))]

                renderer.instanced_shader.set_mat4_array('modelTransforms', mats)
                glBindVertexArray(mesh.vao)
                glDrawElementsInstanced(GL_TRIANGLES, mesh.index_count, GL_UNSIGNED_INT, None,
                                        len(mats))
                glBindVertexArray(0)

        # self.bind(self.post_shader)

        # glBindFramebuffer(GL_READ_FRAMEBUFFER, self.fbo.fbo)
        # glBindFramebuffer(GL_DRAW_FRAMEBUFFER, 0)
        #
        # glBlitFramebuffer(0, 0, self.fbo.w, self.fbo.h,  # src rect
        #                   0, 0, self.w, self.h,  # dst rect
        #                   GL_COLOR_BUFFER_BIT,  # buffer mask
        #                   GL_LINEAR)

        renderer.fbo.unbind()

        renderer.bind(renderer.gui_shader)

    def draw(self, renderer):
        self.draw_game(renderer)

        glActiveTexture(GL_TEXTURE0 + self.texture)
        glBindTexture(GL_TEXTURE_2D, self.texture)
        renderer.gui_shader.set_int('_tex', self.texture)

        renderer.push_matrix()
        renderer.translate(0, 0, .1)

        renderer.update_matrix()
        renderer.set_color(1, 1, 1)
        self.mesh.draw()

        renderer.pop_matrix()


class StatBar(Rectangle):
    width = .25
    height = .1
    spacing = .05

    def __init__(self, engine, tex_name, color, i):
        Rectangle.__init__(self)
        self.engine = engine
        self.pos = glm.vec2(-1 + self.spacing, 1 - ((self.height + self.spacing) * (i + 1)))
        self.size = glm.vec2(self.width, self.height * .5)
        self.size.x = 0

        self.target_value = 1

        self.color = color

        self.tex = engine.graphics.get_texture(tex_name)

    def draw(self, renderer):
        self.size.x += (self.target_value * self.width - self.size.x) * .1
        renderer.push_matrix()

        renderer.translate(*self.pos)
        renderer.scale(*self.size)
        renderer.translate(1, 0)

        renderer.update_matrix()
        renderer.set_color(*self.color)
        renderer.set_texture(self.tex)
        self.mesh.draw()

        renderer.pop_matrix()


class Background(Rectangle):
    def __init__(self, engine, tex_name):
        Rectangle.__init__(self)
        self.tex = engine.graphics.get_texture(tex_name, False)

    def draw(self, renderer):
        renderer.set_texture(self.tex)
        renderer.update_matrix()
        renderer.set_color(1, 1, 1)
        self.mesh.draw()


class Button(Rectangle):
    def __init__(self, engine, pos, size, down_tex, normal_tex, over_tex):
        Rectangle.__init__(self)

        self.down_tex = engine.graphics.get_texture(down_tex, False)
        self.normal_tex = engine.graphics.get_texture(normal_tex, False)
        self.over_tex = engine.graphics.get_texture(over_tex, False)

        self.pos = glm.vec2(*pos)
        self.size = glm.vec2(*size)

        self.texture = self.normal_tex

    def collide_point(self, x, y):
        if abs(x - self.pos.x) < self.size.x:
            if abs(y - self.pos.y) < self.size.y:
                self.texture = self.over_tex
                return True
        if self.texture is self.over_tex:
            self.texture = self.normal_tex

    def on_click(self, x, y):
        self.texture = self.down_tex

    def on_release(self, x, y):
        self.texture = self.over_tex

    def draw(self, renderer):
        renderer.push_matrix()

        renderer.translate(*self.pos)
        renderer.scale(*self.size)

        renderer.update_matrix()
        renderer.set_texture(self.texture)
        self.mesh.draw()

        renderer.pop_matrix()