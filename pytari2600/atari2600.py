from .memory import memory
from .memory import riot
from .memory import cartridge
from .graphics import stella
from . import clocks
from . import inputs
import json

class Atari(object):
    def __init__(self, Graphics, audio, cpu):
        self.clocks   = clocks.Clock()
        self.pc_state = cpu.pc_state.PC_State()
        self.inputs   = inputs.Input()
        self.memory   = memory.Memory()
        self.riot     = riot.Riot(self.clocks, self.inputs)
        self.stella   = Graphics(self.clocks,  self.inputs, audio)
        self.core     = cpu.core.Core(self.clocks, self.memory, self.pc_state)

        self.core.initialise()

    def insert_cartridge(self, cart_name, cart_type):
        if cart_type == 'pb':
            new_cart = cartridge.PBCartridge(cart_name)
        elif cart_type == 'mnet':
            new_cart = cartridge.MNetworkCartridge(cart_name)
        elif cart_type == 'fe':
            new_cart = cartridge.GenericCartridge(cart_name, 8, 0x1000, 0xFFB, 0x080)
        elif cart_type == 'e':
            # Robotank, Decathelon
            new_cart = cartridge.FECartridge(cart_name, 2, 0x1000)
        elif cart_type == 'cbs':
            new_cart = cartridge.GenericCartridge(cart_name, 3, 0x1000, 0xFFA, 0x100)
        elif cart_type == 'super':
            new_cart = cartridge.GenericCartridge(cart_name, 4, 0x1000, 0xFF9, 0x080)
        elif cart_type == 'f4':
            new_cart = cartridge.GenericCartridge(cart_name, 8, 0x1000, 0xFFB, 0x000)
        elif cart_type == 'single_bank':
            new_cart = cartridge.SingleBankCartridge(cart_name, 0x1000)
        elif cart_type == 'default':
            new_cart = cartridge.GenericCartridge(cart_name, 8, 0x1000, 0xFF9, 0x0)
        else:
            # Same as 'default'
            new_cart = cartridge.GenericCartridge(cart_name, 4, 0x1000, 0xFF9, 0x0)
        self.memory.set_cartridge(new_cart)


    def get_save_state(self):
        state = {}
        # clock
        state['clocks'] = self.clocks.get_save_state()
        # Stella, riot, cart
        state['memory'] = self.memory.get_save_state()
        # pc state
        state['core']   = self.core.get_save_state()
        # input state
        state['inputs'] = self.inputs.get_save_state()
        # stella
        state['stella'] = self.stella.get_save_state()
        # riot
        state['riot']   = self.riot.get_save_state()
        return state

    def set_save_state(self, state):
        # clock
        self.clocks.set_save_state(state['clocks'])
        # Stella, riot, cart
        self.memory.set_save_state(state['memory'])
        # pc state
        self.core.set_save_state(  state['core'])
        # input state
        self.inputs.set_save_state(state['inputs'])
        # stella
        self.stella.set_save_state(state['stella'])
        # riot
        self.riot.set_save_state(  state['riot'])

    def power_on(self, stop_clock, no_delay=False, debug=False, replay_file=False, stella_record_file=None):

        # Allow recording of 'stella' interface.
        if stella_record_file:
            stella.StellaInstrumentRecord.instrumentStella(self.stella, stella_record_file)

        self.memory.set_riot(self.riot)
        self.memory.set_stella(self.stella)

        self.core.reset()

        step_func = self.core.step
        quit_func = self.inputs.get_quit

        if debug:
            if 0 == stop_clock:
                while 0 == quit_func():
                    print("clock:%s, %s"%((self.clocks.system_clock - self.stella._vsync_debug_output_clock)/3, str(self.core.pc_state)))
                    step_func()
            else:
                with open('debug.json', 'w') as fp:
                    clk = self.clocks
                    while clk.system_clock < stop_clock:

                        print("%s clock:%s, %s"%(self.clocks.system_clock, (self.clocks.system_clock - self.stella._vsync_debug_output_clock)/3, str(self.core.pc_state)))
                        step_func()
                        state = self.get_save_state()
                        json.dump(state, fp)
                        fp.write("\n");
        elif replay_file:
                state = self.get_save_state()

                while 0 == quit_func():
                    step_func()

                    # Save/restore state depending on key press.
                    if self.inputs.get_save_state_key():
                        state = self.get_save_state()
                        with open(replay_file, 'w') as fp:
                            json.dump(state, fp)
                    elif self.inputs.get_restore_state_key():
                        with open(replay_file, 'r') as fp:
                            state = json.load(fp)
                        self.set_save_state(state)

        else:
            if 0 == stop_clock:
                while 0 == quit_func():
                    step_func()
            else:
                clk = self.clocks
                while clk.system_clock < stop_clock:
                    step_func()

        print("Atari finished")
