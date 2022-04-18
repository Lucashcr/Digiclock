#version 330 core

layout (location = 0) in vec3 InPosition;

// uniform float Position_x;

// void main() {
//     gl_Position = vec4(InPosition + vec3(Position_x, 0.0f, 0.0f), 1.0f);
// }

void main() {
    gl_Position = vec4(vec3(0.0f), 1.0f);
}