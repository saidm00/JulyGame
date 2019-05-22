#version 330

layout(location = 0) in vec3 position;
layout(location = 1) in vec2 tex_coord;

uniform mat4 proj;
uniform mat4 model;

out vec2 uv_vec;

void main(void) {
    gl_Position =  proj * model * vec4(position, 1.0);
    uv_vec = tex_coord;
}