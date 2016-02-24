import pyglet
from pyglet.gl import *
import stella

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

    def driver_open_display(self):
        # Enable alpha blending, required for image.blit.
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        window.width  = stella.Stella.FRAME_WIDTH 
        window.height = stella.Stella.FRAME_HEIGHT
        window.set_visible()

    def driver_update_display(self):
      self._draw_display()
      data = [x for line in self._display_lines[::-1] for colors in line for x in colors]
      rawdata = (GLubyte * len(data))(*data)
      rawimage = pyglet.image.ImageData(window.width, window.height, 'RGB', rawdata)
      rawimage.blit(0,0,0)

      window.switch_to()
      window.dispatch_events()
      window.dispatch_event('on_draw')
      window.flip()

    def driver_draw_display(self):
        pass
