from pyglfw.libapi import *
from OpenGL.GL import *
import glm
import numpy as np
import gc

import random

from scripts import (frame_buffer,
                     camera,
                     shader)


class Renderer(object):
    wireframe = False

    def __init__(self, engine):
        self.engine = engine

        positions = []
        colors = []
        for x in range(5):
            for z in range(5):
                positions.extend(((x - 2.5) * 10, 1, (z - 2.5) * 10))
                colors.extend([random.random() for _ in range(3)])

        positions.extend((0, 4, 20))
        colors.extend((0, 1, 0))

        self.w = 0
        self.h = 0

        self.opacity = 1

        self.meshes = {}
        self.instances = {}

        self.light_positions = np.array(positions, dtype=np.float32)
        self.light_colors = np.array(colors, dtype=np.float32)

        self.scene = []
        self.stack = []
        self.model_mat = glm.mat4(1.0)

        self.init_gl()

        self.active_shader = self.shader

        self.update_lights()

        self.engine.graphics.get_texture('nana', False)
        self.engine.graphics.get_mesh('models/UI/plane')

    def bind(self, shader):
        self.active_shader = shader
        shader.bind()

    def set_opacity(self, opacity):
        self.opacity = opacity

    def set_color(self, *args):
        self.active_shader.set_vec3('color', *args)

    def set_texture(self, texture):
        glActiveTexture(GL_TEXTURE0 + texture.tex_id)
        glBindTexture(GL_TEXTURE_2D, texture.tex_id)
        self.active_shader.set_int('_tex', texture.tex_id)

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
        self.w = w
        self.h = h
        self.fbo.on_size(w, h)
        glViewport(0, 0, w, h)
        self.camera.aspect = w / float(h)
        self.set_proj_mat()
        self.engine.screen_manager.on_size(w, h)

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

    def init_gl(self, size=(800, 600)):
        if not glfwInit():
            print("glfw initialization failed!")
            return -1

        major, minor, rev = glfwGetVersion()
        print("GLFW {}.{}.{}".format(major, minor, rev))

        glfwWindowHint(GLFW_CLIENT_API, GLFW_OPENGL_API)
        glfwWindowHint(GLFW_CONTEXT_VERSION_MAJOR, 3)
        glfwWindowHint(GLFW_CONTEXT_VERSION_MINOR, 3)
        glfwWindowHint(GLFW_OPENGL_DEBUG_CONTEXT, True)


        if size is None:
            monitor = glfwGetPrimaryMonitor()
            mode = glfwGetVideoMode(monitor)
            size = mode.width, mode.height

            glfwWindowHint(GLFW_RED_BITS, mode.redBits)
            glfwWindowHint(GLFW_GREEN_BITS, mode.greenBits)
            glfwWindowHint(GLFW_BLUE_BITS, mode.blueBits)
            glfwWindowHint(GLFW_ALPHA_BITS, 8)
            glfwWindowHint(GLFW_DEPTH_BITS, 32)
            glfwWindowHint(GLFW_REFRESH_RATE, mode.refreshRate)

            self.window = glfwCreateWindow(size[0], size[1], b'My Title', monitor, None)
        else:
            self.window = glfwCreateWindow(size[0], size[1], b'My Title', None, None)

        glfwMakeContextCurrent(self.window)
        self.size = size

        print('OpenGL {}'.format(glGetString(GL_VERSION)))

        glfwSetWindowSizeCallback(self.window, on_window_size)
        glfwSetWindowUserPointer(self.window, self)

        glfwSwapInterval(0)

        glEnable(GL_DEBUG_OUTPUT)
        glDebugMessageCallback(GLDEBUGPROC(MessageCallback), None)

        glEnable(GL_DEPTH_TEST)
        glEnable(GL_CULL_FACE)
        glCullFace(GL_BACK)

        if self.wireframe:
            glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
        glClearColor(0.6, 0.6, 0.9, 1.0)

        # Initialize Game entities
        self.camera = camera.Camera(glm.vec3(0.0, 2.0, 5.0),
                                    glm.vec3(0.0, 1.0, 0.0),
                                    glm.vec3(0.0, 0.0, -1.0),
                                    0.0, 1.0, 1.0, 1000.0)

        self.shader = shader.Shader("./shaders/shader")
        self.instanced_shader = shader.Shader("./shaders/instanced_shader")
        self.gui_shader = shader.Shader("./shaders/gui")
        # self.post_shader = shader.Shader("./shaders/post")
        self.bind(self.shader)

        self.set_fov(glm.radians(75.0))

        glfwSwapInterval(0)
        glfwSetWindowPos(self.window, 600, 300)

        self.fbo = frame_buffer.FrameBuffer(*size)

    def update(self, dt):
        if glfwWindowShouldClose(self.window):
            self.engine.running = False
        else:
            self.camera.update(dt)

            self.bind(self.gui_shader)

            glClear(GL_DEPTH_BUFFER_BIT)

            self.gui_shader.set_float('opacity', self.opacity)

            self.engine.screen_manager.draw(self)

            if self.stack:
                print 'STACK NOT EMPTY'
                self.model_mat = glm.mat4(1.0)
                self.stack *= 0

            glfwSwapBuffers(self.window)
            glfwPollEvents()

    def on_stop(self):
        del self.shader

        glfwDestroyWindow(self.window)
        glfwTerminate()

@GLDEBUGPROC
def MessageCallback(source, msg_type, msg_id, severity, length, message, userParam):
    print("GL CALLBACK: {} type = {}, severity = {}, message = {}".format(source, msg_type, severity,
                                                                          message.decode("utf-8")))


@GLFWwindowsizefun
def on_window_size(window, w, h):
    glfwGetWindowUserPointer(window).on_size(w, h)
