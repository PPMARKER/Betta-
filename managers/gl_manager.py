import moderngl
import pygame
import numpy as np
import glm
from core.constants import SCREEN_WIDTH, SCREEN_HEIGHT
from animations.fish_animation import FISH_VERTEX_SHADER, FISH_FRAGMENT_SHADER

class GLManager:
    _instance = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = GLManager()
        return cls._instance

    def __init__(self):
        self.ctx = moderngl.create_context()
        self.ctx.enable(moderngl.BLEND)
        self.ctx.blend_func = moderngl.SRC_ALPHA, moderngl.ONE_MINUS_SRC_ALPHA

        # Standard Quad
        self.quad_buffer = self.ctx.buffer(np.array([
            0.0, 0.0, 0.0, 0.0,
            0.0, 1.0, 0.0, 1.0,
            1.0, 0.0, 1.0, 0.0,
            1.0, 1.0, 1.0, 1.0,
        ], dtype='f4'))

        # Base shader
        self.prog_base = self.ctx.program(
            vertex_shader="""
                #version 330
                in vec2 in_vert;
                in vec2 in_texcoord;
                out vec2 v_texcoord;
                uniform mat4 u_proj;
                uniform mat4 u_model;
                void main() {
                    gl_Position = u_proj * u_model * vec4(in_vert, 0.0, 1.0);
                    v_texcoord = in_texcoord;
                }
            """,
            fragment_shader="""
                #version 330
                uniform sampler2D u_texture;
                uniform vec4 u_color;
                in vec2 v_texcoord;
                out vec4 f_color;
                void main() {
                    vec4 tex_color = texture(u_texture, v_texcoord);
                    f_color = tex_color * u_color;
                }
            """
        )

        # Fish shader from animation folder
        self.prog_fish = self.ctx.program(
            vertex_shader=FISH_VERTEX_SHADER,
            fragment_shader=FISH_FRAGMENT_SHADER
        )

        self.vao_base = self.ctx.vertex_array(self.prog_base, [
            (self.quad_buffer, '2f 2f', 'in_vert', 'in_texcoord'),
        ], mode=moderngl.TRIANGLE_STRIP)

        self.vao_fish = self.ctx.vertex_array(self.prog_fish, [
            (self.quad_buffer, '2f 2f', 'in_vert', 'in_texcoord'),
        ], mode=moderngl.TRIANGLE_STRIP)

        self.projection = glm.ortho(0, SCREEN_WIDTH, SCREEN_HEIGHT, 0, -1, 1)
        self.textures = {}
        self.time = 0

    def update_time(self, dt):
        self.time += dt

    def get_texture(self, surface):
        if surface in self.textures:
            return self.textures[surface]

        rgb_data = pygame.image.tostring(surface, 'RGBA')
        tex = self.ctx.texture(surface.get_size(), 4, rgb_data)
        tex.filter = (moderngl.LINEAR, moderngl.LINEAR)
        self.textures[surface] = tex
        return tex

    def draw_texture(self, surface, x, y, width=None, height=None, color=(1,1,1,1), angle=0, flip_x=False, flip_y=False, blend_mode='alpha'):
        tex = self.get_texture(surface)

        # Update texture content for dynamic surfaces
        rgb_data = pygame.image.tostring(surface, 'RGBA')
        tex.write(rgb_data)

        if blend_mode == 'additive':
            self.ctx.blend_func = moderngl.SRC_ALPHA, moderngl.ONE
        else:
            self.ctx.blend_func = moderngl.SRC_ALPHA, moderngl.ONE_MINUS_SRC_ALPHA

        self._render_quad(self.prog_base, self.vao_base, tex, x, y, width, height, color, angle, flip_x, flip_y)
        self.ctx.blend_func = moderngl.SRC_ALPHA, moderngl.ONE_MINUS_SRC_ALPHA

    def draw_fish(self, surface, x, y, width, height, color=(1,1,1,1), angle=0, flip_x=False, speed=10.0, amplitude=0.08):
        tex = self.get_texture(surface)
        self.prog_fish['u_time'].value = self.time
        self.prog_fish['u_speed'].value = speed
        self.prog_fish['u_amplitude'].value = amplitude
        self.prog_fish['u_flip_x'].value = flip_x
        self._render_quad(self.prog_fish, self.vao_fish, tex, x, y, width, height, color, angle, flip_x, False)

    def _render_quad(self, prog, vao, tex, x, y, width, height, color, angle, flip_x, flip_y):
        if width is None: width = tex.width
        if height is None: height = tex.height

        model = glm.mat4(1.0)
        model = glm.translate(model, glm.vec3(x, y, 0))

        if angle != 0:
            model = glm.translate(model, glm.vec3(width/2, height/2, 0))
            model = glm.rotate(model, glm.radians(angle), glm.vec3(0, 0, 1))
            model = glm.translate(model, glm.vec3(-width/2, -height/2, 0))

        if flip_x or flip_y:
            model = glm.translate(model, glm.vec3(width/2 if flip_x else 0, height/2 if flip_y else 0, 0))
            model = glm.scale(model, glm.vec3(-1 if flip_x else 1, -1 if flip_y else 1, 1))
            model = glm.translate(model, glm.vec3(-width/2 if flip_x else 0, -height/2 if flip_y else 0, 0))

        model = glm.scale(model, glm.vec3(width, height, 1))

        tex.use(0)
        prog['u_proj'].write(self.projection)
        prog['u_model'].write(model)
        prog['u_color'].value = color
        vao.render()

    def clear(self, color=(0, 0, 0, 1)):
        self.ctx.clear(*color)

gl_manager = None

def init_gl():
    global gl_manager
    gl_manager = GLManager.get_instance()
