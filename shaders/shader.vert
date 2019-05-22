#version 330

layout(location = 0) in vec3 position;
layout(location = 1) in vec3 normal;
layout(location = 2) in vec2 tex_coord;
layout(location = 3) in vec3 color;

uniform sampler2D tex;
uniform mat4 model;
uniform mat4 view;
uniform mat4 projection;

out vec3 _worldPos;
out vec3 normal0;
out vec3 color0;
out vec2 uv_vec0;

void main(void) {
    mat4 MVP = projection * view * model;
    gl_Position = MVP * vec4(position, 1.0);
    _worldPos = vec3(model * vec4(position, 1.0));
    normal0 = mat3(transpose(inverse(model))) * normal;
    color0 = color;
    uv_vec0 = tex_coord;
}