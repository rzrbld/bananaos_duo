precision mediump float;
uniform sampler2D u_texture;
uniform vec2 u_texture_size;
varying vec2 v_texcoord;
void main() {
    vec2 pixel = floor(v_texcoord * u_texture_size);
    gl_FragColor = SWIZ(texture2D(u_texture, (pixel + 0.5) / u_texture_size));
}
