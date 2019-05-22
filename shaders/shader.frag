#version 330

const int MAX_LIGHTS = 2;
const vec3 colorKey = vec3(0, 1, 0);

uniform sampler2D _tex;
uniform vec3 _cameraWorldPos;
uniform float _cameraFov;

uniform int _numLights;
uniform vec3[MAX_LIGHTS] _lightsPos;
uniform vec3[MAX_LIGHTS] _lightsColor;

in vec3 normal0;
in vec3 color0;

in vec3 _worldPos;
in vec2 uv_vec0;

struct PhongMaterial{
    vec3 Ia, Id, Is;
    float Ka, Kd, Ks, a;
};


vec3 phong( in vec3 N, in vec3 L, in vec3 V, in vec3 id, PhongMaterial mat) {
    vec3 R = reflect(L, N);
    mat.Ia = mat.Ka * mat.Ia;
    mat.Id *= id * max(dot(N, L), 0.0);
    mat.Is *= mat.Ks * pow(max(dot(R, V), 0.0), mat.a);
    return (mat.Ia + mat.Id + mat.Is) * id;
}


void main(void) {
    vec3 V = normalize(_cameraWorldPos - _worldPos);
    vec3 light_col = vec3(.6);
    vec3 L = vec3(0);

    vec3 diffuse = texture(_tex, uv_vec0).rgb;
    if (diffuse == colorKey) discard;

    PhongMaterial mat = PhongMaterial(vec3(.2, .2, .2), diffuse, vec3(1, 1, 1),
                                      0.5, 2.0, 1.5, 2.5);

    for (int i=0; i < _numLights && i < _lightsPos.length(); i++)
    {
        float dist = distance(_lightsPos[i], _worldPos) * .4;
        L = normalize(_lightsPos[i] - _worldPos);
        light_col += phong(normal0, L, V, _lightsColor[i], mat) / dist;
    }

//    if ((light_col.r + light_col.g + light_col.b) / 3.0 < .1) discard;

    gl_FragColor = vec4(light_col * diffuse, 1.0);

}