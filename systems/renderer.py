from OpenGL.GL import *
import glm
import numpy as np

from scripts.components import *
from systems.joystick import *

# import random

from scripts import (frame_buffer,
                     camera,
                     shader,
                     graphics,
                     mesh)
from systems import system


class Renderer(system.System):

    def __init__(self, engine):
        system.System.__init__(self, engine)
        self.callbacks = {WINDOW_SIZE: self.on_size,
                          JOY_STICK: self.on_joystick,
                          ON_PAUSE: self.on_pause,
                          UPDATE: self.update}

        self.settings.update({'draw/buttons': True,
                              'draw/scene': True})

        self.paused = False

        size = .5
        verts = np.array((-size, -size, 0,
                          size, -size, 0,
                          size, size, 0,
                          -size, size, 0), dtype=np.float32)
        texcoords = np.array((0, 0,
                              1, 0,
                              1, 1,
                              0, 1), dtype=np.float32)
        indices = np.array((0, 1, 2, 0, 2, 3), dtype=np.uint32)

        self.mesh = mesh.Mesh((3, verts),
                              (2, texcoords),
                              indices)

        positions = []
        colors = []
        # for x in range(5):
        #     for z in range(5):
        #         positions.extend(((x - 2.5) * 10, 1, (z - 2.5) * 10))
        #         colors.extend([random.random() for _ in range(3)])

        positions.extend((0, 4, 20))
        colors.extend((0, 1, 0))

        self.size = glm.vec3(1, 1, 1)
        self.aspect = 1
        self.opacity = 1

        self.meshes = {}
        self.instances = {}

        self.light_positions = np.array(positions, dtype=np.float32)
        self.light_colors = np.array(colors, dtype=np.float32)

        self.scene = []
        self.stack = []
        self.model_mat = glm.mat4(1.0)

        # Initialize Game entities
        self.camera = camera.Camera(glm.vec3(0.0, 2.0, 5.0),
                                    glm.vec3(0.0, 1.0, 0.0),
                                    glm.vec3(0.0, 0.0, -1.0),
                                    0.0, 1.0, 1.0, 1000.0)

        self.shader = shader.Shader("./shaders/shader")
        self.instanced_shader = shader.Shader("./shaders/instanced_shader")
        self.gui_shader = shader.Shader("./shaders/gui")
        self.text_shader = shader.Shader("./shaders/text")

        proj_mat = glm.ortho(0, 1, 0, 1, 0, 10)

        self.bind(self.gui_shader)
        self.active_shader.set_mat4('proj', proj_mat)

        self.bind(self.shader)

        self.set_fov(glm.radians(75.0))

        self.fbo = frame_buffer.FrameBuffer()

        self.active_shader = self.shader

        self.update_lights()

        self.engine.graphics.get_texture('nana', False)
        self.engine.graphics.get_mesh('models/UI/plane')

    def on_joystick(self, stick_id, x, y, dt):
        if stick_id is 1:
            self.camera.rotate(0, y * dt)

    def bind(self, shader):
        self.active_shader = shader
        shader.bind()

    def set_opacity(self, opacity):
        self.opacity = opacity

    def set_color(self, *args):
        self.active_shader.set_vec3('color', *args)

    def set_texture(self, texture):
        glActiveTexture(GL_TEXTURE0 + texture)
        glBindTexture(GL_TEXTURE_2D, texture)
        self.active_shader.set_int('_tex', texture)

    def draw_instance(self, mesh_name, tex_name=None):
        if tex_name:
            key = '{} {}'.format(mesh_name, tex_name)
        else:
            key = mesh_name

        if key in self.instances:
            self.instances[key].append(self.model_mat)
        else:
            self.instances[key] = [self.model_mat]

    def push_matrix(self):
        self.stack.append(self.model_mat)

    def pop_matrix(self):
        if self.stack:
            self.model_mat = self.stack.pop()
        else:
            print 'STACK EMPTY'

    def rotate(self, angle, x, y, z, rads=False):
        if not rads:
            angle /= 57.3
        self.model_mat = glm.rotate(self.model_mat, angle, (x, y, z))

    def scale(self, *args):
        x = y = z = 0
        if len(args) == 1:
            x = y = z = args[0]
        if len(args) == 2:
            x, y = args
            z = 1
        elif len(args) == 3:
            x, y, z = args

        self.model_mat = glm.scale(self.model_mat, (x, y, z))

    def translate(self, x, y, z=0):
        self.model_mat = glm.translate(self.model_mat, (x, y, z))

    def update_matrix(self):
        self.active_shader.set_mat4('model', self.model_mat)

    def update_lights(self):
        self.bind(self.shader)
        self.shader.set_int('_numLights', len(self.light_positions) / 3)
        self.shader.set_vec3_array('_lightsPosition', self.light_positions)
        self.shader.set_vec3_array('_lightsColor', self.light_colors)

        self.bind(self.instanced_shader)
        self.instanced_shader.set_int('_numLights', len(self.light_positions) / 3)
        self.instanced_shader.set_vec3_array('_lightsPosition', self.light_positions)
        self.instanced_shader.set_vec3_array('_lightsColor', self.light_colors)

    def on_size(self, w, h):
        self.size.x = w
        self.size.y = h
        self.aspect = w / float(h)
        glViewport(0, 0, w, h)
        self.fbo.on_size(w, h)
        self.camera.aspect = self.aspect
        self.set_proj_mat()

    def set_fov(self, fov):
        self.camera.fovy = fov
        # glUniform1f(glGetUniformLocation(self.shader.program, "_cameraFov"), self.camera.fovy)
        self.set_proj_mat()

    def set_proj_mat(self):
        proj = self.camera.getProjection()
        self.bind(self.shader)
        self.shader.set_mat4('projection', proj)
        self.bind(self.instanced_shader)
        self.instanced_shader.set_mat4('projection', proj)

    def update(self, dt):
        if self.paused:
            return

        elif self.settings['enabled']:
            self.camera.update(dt)

            gui = []
            animated = []
            scene = []
            text = []

            for e in self.engine.entities:
                if has_components(e, (POS, CAM_OFFSET)):
                    self.camera.set_pos(*(e[POS] + e[CAM_OFFSET]))
                    if ANGLE in e:
                        self.camera.set_yaw(90 - e[ANGLE])

                if has_tag(e, GUI_TAG):
                    if TEXT in e:
                        text.append(e)
                    else:
                        gui.append(e)

                elif MESH in e:
                    scene.append(e)

                elif ANIMATOR in e:
                    animated.append(e)

            if self.settings['draw/scene']:
                self.draw_game(scene, animated)

            self.draw_gui(gui, text)

            if self.stack:
                print 'STACK NOT EMPTY'
                self.model_mat = glm.mat4(1.0)
                self.stack *= 0

    def draw_gui(self, gui, text):
        self.bind(self.gui_shader)

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        self.active_shader.set_float('opacity', self.opacity)

        for e in gui:
            if self.settings['draw/buttons'] or BUTTON not in e:
                self.push_matrix()

                if POS in e:
                    self.translate(*e[POS])

                if has_components(e, [TEX]):
                    self.set_texture(e[TEX])

                    if SIZE in e:
                        self.scale(*e[SIZE])

                elif FBO_TEX in e:
                    self.set_texture(self.fbo.texture)

                    if SIZE in e:
                        self.scale(*(e[SIZE]))

                self.update_matrix()
                self.mesh.draw()

                self.pop_matrix()

        self.bind(self.text_shader)

        proj_mat = glm.ortho(0, self.aspect, 0, 1, 0, 10)
        self.active_shader.set_mat4('proj', proj_mat)

        for e in text:
            tex, size = self.engine.graphics.get_rendered_text(e[TEXT])
            self.set_texture(tex)

            self.push_matrix()

            if COLOR in e:
                self.set_color(*e[COLOR])

            if POS in e:
                self.translate(e[POS].x * self.aspect, e[POS].y, e[POS].z)

            if SIZE in e:
                self.scale(*(e[SIZE] * size))

            self.update_matrix()
            self.mesh.draw()

            self.pop_matrix()

    def draw_game(self, scene, animated):
        self.fbo.bind()

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        view = self.camera.getView()

        self.bind(self.shader)
        self.shader.set_mat4('view', view)

        for e in scene:
            self.push_matrix()

            if POS in e:
                self.translate(*e[POS])

            if ANGLE in e:
                self.rotate(e[ANGLE], 0, 1, 0)

            if TEX in e:
                self.set_texture(e[TEX])

            self.update_matrix()
            e[MESH].draw()

            self.pop_matrix()

        for e in animated:
            self.push_matrix()

            if POS in e:
                self.translate(*e[POS])

            if ANGLE in e:
                self.rotate(e[ANGLE], 0, 1, 0)

            if TEX in e:
                self.set_texture(e[TEX])

            e[ANIMATOR].draw(self)

            self.pop_matrix()

        self.instances.clear()
        self.bind(self.instanced_shader)
        self.instanced_shader.set_mat4('view', view)
        for k, v in self.instances.iteritems():
            mesh_data = k.split(' ')
            if len(mesh_data) == 2:
                self.set_texture(self.engine.graphics.get_texture(mesh_data[1]))

            mesh = self.engine.graphics.get_mesh(mesh_data[0])
            # self.instanced_shader.set_mat4('model', v[0])

            for i in range(0, len(v), 254):
                mats = v[i:min(i + 254, len(v))]

                self.instanced_shader.set_mat4_array('modelTransforms', mats)
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

        self.fbo.unbind()

        self.bind(self.gui_shader)

    def on_stop(self):
        del self.shader
