import managers.gl_manager as gl_mod
import pygame
import cv2
import numpy as np
import os
import moderngl
from core.constants import SCREEN_WIDTH, SCREEN_HEIGHT

class LightManager:
    def __init__(self):
        self.width = SCREEN_WIDTH
        self.height = SCREEN_HEIGHT
        
        # Shader for Light Effect
        ctx = gl_mod.gl_manager.ctx
        self.prog_light = ctx.program(
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
                uniform sampler2D u_mask;
                uniform float u_time;
                uniform vec3 u_color;
                in vec2 v_texcoord;
                out vec4 f_color;

                void main() {
                    vec4 mask_rgba = texture(u_mask, v_texcoord);
                    // If mask is white (r > 0.5), we draw light
                    if (mask_rgba.r < 0.5) discard;

                    // Light source position (top-right)
                    vec2 source = vec2(1.1, -0.1);
                    vec2 dir = v_texcoord - source;
                    float dist = length(dir);
                    float angle = atan(dir.y, dir.x);

                    // Shimmering rays
                    float ray = sin(angle * 10.0 + u_time * 0.7) * 0.4 +
                                sin(angle * 18.0 - u_time * 1.1) * 0.3 +
                                sin(angle * 35.0 + u_time * 2.2) * 0.3;
                    
                    ray = (ray + 1.0) / 2.0;
                    ray = pow(ray, 1.5);

                    // Distance fade
                    float fade = clamp(1.2 - dist / 1.3, 0.0, 1.0);
                    
                    float alpha = ray * fade * 0.3; // Max alpha reduced for better blending

                    f_color = vec4(u_color * alpha, alpha); // Premultiplied for additive
                }
            """
        )
        
        self.vao_light = ctx.vertex_array(self.prog_light, [
            (gl_mod.gl_manager.quad_buffer, '2f 2f', 'in_vert', 'in_texcoord'),
        ], mode=moderngl.TRIANGLE_STRIP)

        # Pre-create mask texture
        self.mask_tex = self._create_mask_texture()

    def _create_mask_texture(self):
        """Detect the water area and return as a ModernGL Texture."""
        path = os.path.join("asset", "Tank", "Tank.png")
        mask_rgb = None
        if os.path.exists(path):
            img = cv2.imread(path, cv2.IMREAD_UNCHANGED)
            if img is not None and img.shape[2] == 4:
                mask = (img[:, :, 3] < 128).astype(np.uint8) * 255
                kernel = np.ones((5, 5), np.uint8)
                mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
                mask_rgb = cv2.cvtColor(mask, cv2.COLOR_GRAY2RGB)
                w, h = img.shape[1], img.shape[0]
        
        if mask_rgb is None:
            mask_rgb = np.zeros((self.height, self.width, 3), dtype=np.uint8)
            cv2.rectangle(mask_rgb, (0, int(self.height*0.1)), (self.width, int(self.height*0.85)), (255,255,255), -1)
            w, h = self.width, self.height
        
        ctx = gl_mod.gl_manager.ctx
        tex = ctx.texture((w, h), 3, mask_rgb.tobytes())
        tex.filter = (moderngl.LINEAR, moderngl.LINEAR)
        return tex

    def update(self):
        pass

    def draw(self, _surface):
        import glm as pyglm
        ctx = gl_mod.gl_manager.ctx
        ctx.enable(moderngl.BLEND)
        ctx.blend_func = moderngl.ONE, moderngl.ONE # True additive blending

        self.mask_tex.use(0)
        self.prog_light['u_mask'].value = 0
        self.prog_light['u_time'].value = gl_mod.gl_manager.time
        self.prog_light['u_color'].value = (210/255.0, 240/255.0, 255/255.0)
        self.prog_light['u_proj'].write(gl_mod.gl_manager.projection)
        
        # Identity model matrix for full-screen quad
        model = pyglm.mat4(1.0)
        model = pyglm.scale(model, pyglm.vec3(self.width, self.height, 1))
        self.prog_light['u_model'].write(model)
        
        self.vao_light.render()
        
        # Reset blend func
        ctx.blend_func = moderngl.SRC_ALPHA, moderngl.ONE_MINUS_SRC_ALPHA
