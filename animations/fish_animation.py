FISH_VERTEX_SHADER = """
#version 330
in vec2 in_vert;
in vec2 in_texcoord;
out vec2 v_texcoord;
uniform mat4 u_proj;
uniform mat4 u_model;
uniform float u_time;
uniform float u_speed;
uniform float u_amplitude;
uniform bool u_flip_x;

void main() {
    vec2 pos = in_vert;

    // Tail wagging animation
    float x_factor = in_texcoord.x;
    if (u_flip_x) x_factor = 1.0 - x_factor;

    float wave = sin(u_time * u_speed - x_factor * 5.0) * u_amplitude * x_factor;
    pos.y += wave;

    gl_Position = u_proj * u_model * vec4(pos, 0.0, 1.0);
    v_texcoord = in_texcoord;
}
"""

FISH_FRAGMENT_SHADER = """
#version 330
uniform sampler2D u_texture;
uniform vec4 u_color;
in vec2 v_texcoord;
out vec4 f_color;
void main() {
    vec4 tex_color = texture(u_texture, v_texcoord);
    if (tex_color.a < 0.05) discard;
    f_color = tex_color * u_color;
}
"""
