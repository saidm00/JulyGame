#version 330

const vec3 colorKey = vec3(0, 1, 0);

uniform sampler2D _tex;
uniform vec3 color;
uniform float opacity;

in vec2 uv_vec;

void main(void) {
    vec3 diffuse = texture(_tex, uv_vec).rgb;
    if (diffuse == colorKey) discard;
    gl_FragColor = vec4(diffuse * color * opacity, 1.0);
}