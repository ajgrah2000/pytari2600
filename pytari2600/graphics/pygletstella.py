import pyglet
from pyglet.gl import *
from . import stella

window = pyglet.window.Window(visible=False, resizable=True)

class PygletColors(stella.Colors):
    def __init__(self):
        super(PygletColors, self).__init__()

    def set_color(self, r, g, b):
      return [r,g,b]

class PygletStella(stella.Stella):
    """ GUI layer for stella.
    """
    def __init__(self, *args):
        # 'default_color' is used by stella init, need to set before super
        self.default_color = [0,0,0]
        self._colors = PygletColors()
        super(PygletStella, self).__init__(*args)

    def poll_events(self):
        pass

    def driver_open_display(self):
        # Enable alpha blending, required for image.blit.
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        window.width  = stella.Stella.BLIT_WIDTH 
        window.height = stella.Stella.BLIT_HEIGHT
        window.set_visible()
        pyglet.gl.glScalef(self.PIXEL_WIDTH, self.PIXEL_HEIGHT, 1.0)

    def driver_update_display(self):
        self._draw_display()
        data = [x for line in reversed(self._display_lines[:self.FRAME_HEIGHT:]) for colors in line for x in colors]
        rawdata = (GLubyte * len(data))(*data)
        rawimage = pyglet.image.ImageData(self.FRAME_WIDTH, self.FRAME_HEIGHT, 'RGB', rawdata)
        pyglet.gl.glTexParameteri(rawimage.get_texture().target, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        rawimage.blit(0,0,0)

        window.switch_to()
        window.dispatch_events()
        window.dispatch_event('on_draw')
        window.flip()

    def driver_draw_display(self):
        pass
