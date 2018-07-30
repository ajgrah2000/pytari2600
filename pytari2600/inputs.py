import sys

class Input(object):
    def __init__(self):
        self.swcha = 0xFF
        self.swchb = 0x3F
        self.input7 = 0xFF
        self.paddle0 = 0x00
        self.quit = 0x0

        # Custom key inputs. 
        self._save_state = 0
        self._restore_state = 0

    def get_save_state(self):
        state = {}
        state['swcha']   = self.swcha
        state['swchb']   = self.swchb
        state['input7']  = self.input7
        state['paddle0'] = self.paddle0
        state['quit']    = self.quit
        return state

    def set_save_state(self, state):
        """ TODO: Get current key state, to avoid need to 'toggle' """
        self.swcha   = state['swcha']   
        self.swchb   = state['swchb']   
        self.input7  = state['input7']  
        self.paddle0 = state['paddle0'] 
        self.quit    = state['quit']    

    def refresh_inputs(self):
        pass

    def get_swcha(self):
        self.refresh_inputs()
        return self.swcha

    def get_swchb(self):
        self.refresh_inputs()
        return self.swchb

    def get_input7(self):
        self.refresh_inputs()
        return self.input7

    def get_paddle0(self):
        self.refresh_inputs()
        return self.paddle0

    def get_quit(self):
        self.refresh_inputs()
        return self.quit

    # Custom key events
    def get_save_state_key(self):
        return self._save_state

    def reset_save_state_key(self):
        self._save_state = 0x0

    def get_restore_state_key(self):
        return self._restore_state

    def reset_restore_state_key(self):
        self._restore_state = 0x0

    def input_register_bits(self, action, key):
        if action == self.EVENT_KEYDOWN:
            if key   == self.KEY_UP:
                self.swcha ^= 0x10
            elif key == self.KEY_DOWN:
                self.swcha ^= 0x20
            elif key == self.KEY_LEFT:
                self.swcha ^= 0x40
                self.paddle0 = 1
            elif key == self.KEY_RIGHT:
                self.swcha ^= 0x80
                self.paddle0 = -1
            elif key == self.KEY_SELECT:
                self.swchb ^= 0x1
            elif key == self.KEY_RESET:
                self.swchb ^= 0x2
            elif key == self.KEY_P0_DIFICULTY:
                self.swchb ^= 0x40
                print("P0 dificulty %s"%(("hard", "easy")[self.swchb & 0x40 != 0]))
            elif key == self.KEY_P1_DIFICULTY:
                self.swchb ^= 0x80
                print("P1 dificulty %s"%(("hard", "easy")[self.swchb & 0x80 != 0]))
            elif key == self.KEY_BLACK_WHITE: # toggle black and white
                self.swchb ^= 0x8
            elif key == self.KEY_BUTTON: # toggle black and white
                self.input7 &= 0x7F
            elif key == self.KEY_QUIT: # Dodgy quit
                self.quit = 0x1
                sys.exit()

            # Custom key events
            elif key   == self.KEY_SAVE_STATE:
                self._save_state = 0x1
            elif key   == self.KEY_RESTORE_STATE:
                self._restore_state = 0x1
        elif action == self.EVENT_KEYUP:
            if key   == self.KEY_UP:
                self.swcha |= 0x10
            elif key == self.KEY_DOWN:
                self.swcha |= 0x20
            elif key == self.KEY_LEFT:
                self.swcha |= 0x40
                self.paddle0 = 0
            elif key == self.KEY_RIGHT:
                self.swcha |= 0x80
                self.paddle0 = 0
            elif key == self.KEY_SELECT:
                self.swchb |= 0x1
            elif key == self.KEY_RESET:
                self.swchb |= 0x2
            elif key == self.KEY_BUTTON: # toggle black and white
                self.input7 |= 0x80

            # Custom key events
            elif key   == self.KEY_SAVE_STATE:
                self._save_state = 0x0
            elif key   == self.KEY_RESTORE_STATE:
                self._restore_state = 0x0
