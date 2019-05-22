#version 330

uniform sampler2D tex;
uniform float opacity;

void main(void) {
    gl_FragColor = vec4(texture(tex, gl_Position).rgb * opacity, 1.0);
}