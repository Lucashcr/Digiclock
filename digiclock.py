import glfw
from datetime import datetime as dt
import OpenGL.GL as gl
import glm
from ctypes import c_void_p
import logging

def get_current_time():
    current_time = dt.now()
    
    c_time = []
    for t in (current_time.hour, current_time.minute, current_time.second):
        c_time.append((t - t%10)//10)
        c_time.append(t%10)
    return c_time
    
    
def define_dot(position, size):
    dot = glm.array([
        glm.vec3([ 0,-1, 0]), 
        glm.vec3([ 1, 0, 0]), 
        glm.vec3([ 0, 1, 0]),
        glm.vec3([ 0,-1, 0]),
        glm.vec3([ 0, 1, 0]), 
        glm.vec3([-1, 0, 0])
    ])
    for i in range(dot.length):
        dot[i] *= size
        dot[i] += position
    VertexBuffer = gl.glGenBuffers(1)
    gl.glBindBuffer(gl.GL_ARRAY_BUFFER, VertexBuffer)
    gl.glBufferData(gl.GL_ARRAY_BUFFER, dot.nbytes, dot.ptr, gl.GL_STATIC_DRAW)
    return VertexBuffer, dot.length
def define_bar(position, size, length, angle):
    bar = glm.array([
        glm.vec3([ length/2,  -size, 0]), 
        glm.vec3([ length/2+size, 0, 0]), 
        glm.vec3([ length/2,   size, 0]),
        glm.vec3([ length/2,  -size, 0]),
        glm.vec3([ length/2,   size, 0]),
        glm.vec3([-length/2,   size, 0]), 
        glm.vec3([-length/2,   size, 0]), 
        glm.vec3([-length/2,  -size, 0]), 
        glm.vec3([ length/2,  -size, 0]), 
        glm.vec3([-length/2,  -size, 0]), 
        glm.vec3([-length/2,   size, 0]), 
        glm.vec3([-length/2-size, 0, 0])
    ])
    for i in range(bar.length):
        bar[i] = glm.rotateZ(bar[i], glm.radians(angle))
        bar[i] += position
    return bar
def define_number(number, op=0):
    bar_struct = (define_bar(glm.vec3([ 0,   0, 0]), 5, 70,  0),
                  define_bar(glm.vec3([ 0,  72, 0]), 5, 70,  0),
                  define_bar(glm.vec3([ 42, 36, 0]), 5, 60, 90),
                  define_bar(glm.vec3([ 42,-36, 0]), 5, 60, 90),
                  define_bar(glm.vec3([ 0, -72, 0]), 5, 70,  0),
                  define_bar(glm.vec3([-42,-36, 0]), 5, 60, 90),
                  define_bar(glm.vec3([-42, 36, 0]), 5, 60, 90))

    bars = None
    for bar in range(7): 
        if number[bar]:
            if bars == None:
                bars = bar_struct[bar]
            else:
                bars = bars.concat(bar_struct[bar])
    
    if op == 0:
        VertexBuffer = gl.glGenBuffers(1)
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, VertexBuffer)
        gl.glBufferData(gl.GL_ARRAY_BUFFER, bars.nbytes, bars.ptr, gl.GL_DYNAMIC_DRAW)
        return VertexBuffer, bars.length
    else:
        return bars


def draw_dot(VertexBuffer, n_of_vertices):
    gl.glEnableVertexAttribArray(0)
    gl.glBindBuffer(gl.GL_ARRAY_BUFFER, VertexBuffer)
    gl.glVertexAttribPointer(0, 3, gl.GL_FLOAT, gl.GL_FALSE, 0, c_void_p(0))
    
    gl.glDrawArrays(gl.GL_TRIANGLES, 0, 3*n_of_vertices)
    
    gl.glBindBuffer(gl.GL_ARRAY_BUFFER, 0)
    gl.glDisableVertexAttribArray(0)
def draw_number(number, position_x):
    for i in range(len(number)):
        number[i] += glm.vec3(position_x, 0, 0)
    
    VertexBuffer = gl.glGenBuffers(1)
    gl.glBindBuffer(gl.GL_ARRAY_BUFFER, VertexBuffer)
    gl.glBufferData(gl.GL_ARRAY_BUFFER, number.nbytes, number.ptr, gl.GL_STATIC_DRAW)
    
    gl.glEnableVertexAttribArray(0)
    gl.glBindBuffer(gl.GL_ARRAY_BUFFER, VertexBuffer)
    gl.glVertexAttribPointer(0, 3, gl.GL_FLOAT, gl.GL_FALSE, 0, c_void_p(0))
    
    gl.glDrawArrays(gl.GL_TRIANGLES, 0, 3*number.length)
    
    gl.glBindBuffer(gl.GL_ARRAY_BUFFER, 0)
    gl.glDisableVertexAttribArray(0)


def LoadShaders(vertex_shader_file, fragment_shader_file):
    logger = logging.getLogger(__name__)

    vertex_code = open(vertex_shader_file).readlines()
    assert vertex_code
    fragment_code = open(fragment_shader_file).readlines()
    assert fragment_code

    program = gl.glCreateProgram()
    vertex = gl.glCreateShader(gl.GL_VERTEX_SHADER)
    fragment = gl.glCreateShader(gl.GL_FRAGMENT_SHADER)

    # Set shaders source
    gl.glShaderSource(vertex, vertex_code)
    gl.glShaderSource(fragment, fragment_code)

    # Compile shaders
    gl.glCompileShader(vertex)
    if not gl.glGetShaderiv(vertex, gl.GL_COMPILE_STATUS):
        error = gl.glGetShaderInfoLog(vertex).decode()
        logger.error("Vertex shader compilation error: %s", error)

    gl.glCompileShader(fragment)
    if not gl.glGetShaderiv(fragment, gl.GL_COMPILE_STATUS):
        error = gl.glGetShaderInfoLog(fragment).decode()
        print(error)
        raise RuntimeError("Fragment shader compilation error")

    gl.glAttachShader(program, vertex)
    gl.glAttachShader(program, fragment)
    gl.glLinkProgram(program)

    if not gl.glGetProgramiv(program, gl.GL_LINK_STATUS):
        print(gl.glGetProgramInfoLog(program))
        raise RuntimeError('Linking error')

    gl.glDetachShader(program, vertex)
    gl.glDetachShader(program, fragment)

    gl.glDeleteShader(vertex)
    gl.glDeleteShader(fragment)

    return program


def main():
    # Inicialização do GLFW
    glfw.init()
    glfw.window_hint(glfw.RESIZABLE, glfw.FALSE)
    glfw.window_hint(glfw.SAMPLES, 4)
    width, height = 900, 200
    window = glfw.create_window(width, height, "DigiClock", None, None)
    glfw.make_context_current(window)
    
    # Definindo projeção ortogonal
    gl.glViewport(0, 0, width, height)
    gl.glMatrixMode(gl.GL_PROJECTION)
    gl.glLoadIdentity()
    gl.glOrtho(-width/2, width/2, -height/2, height/2, -1., 1.)
    
    # Definindo a estrutura dos números
    n_struct = ((0,1,1,1,1,1,1), # número 0
                (0,0,1,1,0,0,0), # número 1
                (1,1,1,0,1,1,0), # número 2
                (1,1,1,1,1,0,0), # número 3
                (1,0,1,1,0,0,1), # número 4
                (1,1,0,1,1,0,1), # número 5
                (1,1,0,1,1,1,1), # número 6
                (0,1,1,1,0,0,0), # número 7
                (1,1,1,1,1,1,1), # número 8
                (1,1,1,1,1,0,1)) # número 9
    
    # Definindo buffers de vértices e programa de shaders dos números
    number_positions = [-360, -240, -60, 60, 240, 360]
    numbers = []
    for i in range(10):
        numbers.append(define_number(n_struct[i]))
       
    Numbers_ProgramID = LoadShaders("./glsl/vertex_shader.glsl", 
                                    "./glsl/fragment_shader.glsl")
    
    # Definindo buffers de vértices dos pontos
    dot_inf1_buffer, dot_inf1_size = define_dot(glm.vec3([-150,-20, 0]), 10)
    dot_sup1_buffer, dot_sup1_size = define_dot(glm.vec3([-150, 20, 0]), 10)
    dot_inf2_buffer, dot_inf2_size = define_dot(glm.vec3([ 150,-20, 0]), 10)
    dot_sup2_buffer, dot_sup2_size = define_dot(glm.vec3([ 150, 20, 0]), 10)
    
    gl.glEnable(gl.GL_MULTISAMPLE)
    gl.glClearColor(0.1, 0.1, 0.1, 1.0)

    while not glfw.window_should_close(window):
        gl.glClear(gl.GL_COLOR_BUFFER_BIT)
    
        # Captura o valor da  hora corrente
        current_time = get_current_time()
        
        draw_dot(dot_sup1_buffer, dot_sup1_size)
        draw_dot(dot_inf1_buffer, dot_inf1_size)
        draw_dot(dot_sup2_buffer, dot_sup2_size)
        draw_dot(dot_inf2_buffer, dot_inf2_size)
        
        for i in range(6):
            draw_number(define_number(n_struct[current_time[i]], op=1), number_positions[i])
        
        glfw.swap_buffers(window)
        glfw.poll_events()
    glfw.destroy_window(window)

if __name__ == "__main__":
    main()