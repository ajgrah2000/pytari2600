import cyglfw3 as glfw
from OpenGL import GL as gl
from . import stella

if not glfw.Init():
    exit()

# Not sure if this is the best spot for the window.
window = glfw.CreateWindow(stella.Stella.BLIT_WIDTH, stella.Stella.BLIT_HEIGHT, "Cyglfw Stella")

class CyglfwColors(stella.Colors):
    def __init__(self):
        super(CyglfwColors, self).__init__()

    def set_color(self, r, g, b):
      return [r,g,b]

class CyglfwStella(stella.Stella):
    """ GUI layer for stella.
    """
    def __init__(self, *args):
        # 'default_color' is used by stella init, need to set before super
        self.default_color = [0,0,0]
        self._colors = CyglfwColors()
        super(CyglfwStella, self).__init__(*args)

        # Map input keys/events
        self._map_input_events()

    def set_palette(self, palette_type):
        self._colors.set_palette(palette_type)

    def poll_events(self):
        pass

    def driver_open_display(self):
        if not window:
            glfw.Terminate()
            exit()

        glfw.MakeContextCurrent(window)

        glfw.SetKeyCallback(window, self.cyglfw_key_callback)

    def driver_update_display(self):
      self._draw_display()
      data = [x for line in self._display_lines[::-1] for colors in line for x in colors]

      rawdata = (gl.GLubyte * len(data))(*data)
      gl.glDrawPixels(stella.Stella.FRAME_WIDTH, stella.Stella.FRAME_HEIGHT, gl.GL_RGB, gl.GL_UNSIGNED_BYTE, rawdata)
      gl.glPixelZoom(self.PIXEL_WIDTH, self.PIXEL_HEIGHT)

      if not glfw.WindowShouldClose(window):
          glfw.SwapBuffers(window)

          glfw.PollEvents()

    def driver_draw_display(self):
        pass

    def cyglfw_key_callback(self, window, key, scancode, action, mods):
        self.inputs.input_register_bits(action, key)

        # TODO: find a better way to quit/stop pygame.
        #glfw.Terminate()
        #sys.exit()

    def _map_input_events(self):
        self.inputs.EVENT_KEYDOWN     = glfw.PRESS
        self.inputs.EVENT_KEYUP       = glfw.RELEASE
                                        
        self.inputs.KEY_UP            = glfw.KEY_UP
        self.inputs.KEY_DOWN          = glfw.KEY_DOWN
        self.inputs.KEY_LEFT          = glfw.KEY_LEFT
        self.inputs.KEY_RIGHT         = glfw.KEY_RIGHT
        self.inputs.KEY_SELECT        = glfw.KEY_S
        self.inputs.KEY_RESET         = glfw.KEY_R
        self.inputs.KEY_P0_DIFICULTY  = glfw.KEY_1
        self.inputs.KEY_P1_DIFICULTY  = glfw.KEY_2
        self.inputs.KEY_BLACK_WHITE   = glfw.KEY_C
        self.inputs.KEY_BUTTON        = glfw.KEY_Z
        self.inputs.KEY_QUIT          = glfw.KEY_Q
        self.inputs.KEY_SAVE_STATE    = glfw.KEY_LEFT_BRACKET
        self.inputs.KEY_RESTORE_STATE = glfw.KEY_RIGHT_BRACKET

