#version 330

const vec3 colorKey = vec3(0, 1, 0);

uniform sampler2D _tex;
uniform vec3 color = vec3(1);
uniform float opacity;

in vec2 uv_vec;

void main(void) {
    gl_FragColor = vec4(color, texture(_tex, uv_vec).a);
}