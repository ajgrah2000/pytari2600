import pyglet
from pyglet.gl import *
from . import stella

window = pyglet.window.Window(visible=False, resizable=True)

class PygletColors(stella.Colors):
    def __init__(self):
        super(PygletColors, self).__init__()

    def set_color(self, r, g, b):
      r = r & 0xFF
      g = g & 0xFF
      b = b & 0xFF
      return b << 16 | g << 8 | r

class PygletStella(stella.Stella):
    """ GUI layer for stella.
    """
    def __init__(self, *args):
        # 'default_color' is used by stella init, need to set before super
        self.default_color = 0
        self._colors = PygletColors()
        super(PygletStella, self).__init__(*args)

        self.KEY_PRESS_ENUM = 0
        self.KEY_RELEASE_ENUM = 1

        # Map input keys/events
        self._map_input_events()

    def poll_events(self):
        pass

    def driver_open_display(self):
        # Enable alpha blending, required for image.blit.
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        window.width  = stella.Stella.BLIT_WIDTH 
        window.height = stella.Stella.BLIT_HEIGHT
        window.set_visible()
        pyglet.gl.glScalef(self.PIXEL_WIDTH, self.PIXEL_HEIGHT, 1.0)

        window.push_handlers(self.on_key_press)
        window.push_handlers(self.on_key_release)

    def driver_update_display(self):
        self._draw_display()
        data = [x for line in reversed(self._display_lines[:self.FRAME_HEIGHT:]) for x in line]
        rawdata = (GLuint * len(data))(*data)
        rawimage = pyglet.image.ImageData(self.FRAME_WIDTH, self.FRAME_HEIGHT, 'RGBA', rawdata)
        pyglet.gl.glTexParameteri(rawimage.get_texture().target, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        rawimage.blit(0,0,0)

        window.switch_to()
        window.dispatch_events()
        window.dispatch_event('on_draw')
        window.flip()

    def driver_draw_display(self):
        pass

    def on_key_press(self, symbol, modifiers):
        self.inputs.input_register_bits(self.KEY_PRESS_ENUM, symbol)

    def on_key_release(self, symbol, modifiers):
        self.inputs.input_register_bits(self.KEY_RELEASE_ENUM, symbol)

    def _map_input_events(self):
        self.inputs.EVENT_KEYDOWN     = self.KEY_PRESS_ENUM
        self.inputs.EVENT_KEYUP       = self.KEY_RELEASE_ENUM
                                        
        self.inputs.KEY_UP            = pyglet.window.key.UP
        self.inputs.KEY_DOWN          = pyglet.window.key.DOWN
        self.inputs.KEY_LEFT          = pyglet.window.key.LEFT
        self.inputs.KEY_RIGHT         = pyglet.window.key.RIGHT
        self.inputs.KEY_SELECT        = pyglet.window.key.S
        self.inputs.KEY_RESET         = pyglet.window.key.R
        self.inputs.KEY_P0_DIFICULTY  = pyglet.window.key._1
        self.inputs.KEY_P1_DIFICULTY  = pyglet.window.key._2
        self.inputs.KEY_BLACK_WHITE   = pyglet.window.key.C
        self.inputs.KEY_BUTTON        = pyglet.window.key.Z
        self.inputs.KEY_QUIT          = pyglet.window.key.Q
        self.inputs.KEY_SAVE_STATE    = pyglet.window.key.BRACKETLEFT
        self.inputs.KEY_RESTORE_STATE = pyglet.window.key.BRACKETRIGHT
