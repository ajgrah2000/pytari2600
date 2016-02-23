
class Riot(object):

    CYCLES_TO_CLOCK = 3
    RAMSIZE         = 128
    NOT_RAMSELECT   = 0x200
    RIOT_ADDRMASK   = 0x7F
    RIOT_Swcha      = 0x00
    RIOT_Swchb      = 0x02
    TIMERADDR       = 0x04
    RIOT_Interrupt  = 0x05

    INT_ENABLE_MASK = 0x8

    RIOT_Tim1t      = 0x14
    RIOT_Tim8t      = 0x15
    RIOT_Tim64t     = 0x16
    RIOT_T1024t     = 0x17

    def __init__(self, clock, inputs):
        self.clock           = clock
        self.set_time        = clock.system_clock
        self.inputs          = inputs
        self.interval        = 1024
        self.expiration_time = 1000000

        self.ram = [0] * self.RAMSIZE

    def get_save_state(self):
        state = {}
        state['set_time']        = self.set_time
        state['interval']        = self.interval
        state['expiration_time'] = self.expiration_time
        state['ram']             = list(self.ram)
        return state

    def set_save_state(self, state):
        self.set_time        = state['set_time']
        self.interval        = state['interval']
        self.expiration_time = state['expiration_time']
        self.ram             = list(state['ram'])

    def read(self, addr):
        value = 0
    
        future_clock = self.clock.system_clock + 12
    
        if 0 == (addr & self.NOT_RAMSELECT):
            return self.ram[addr & self.RIOT_ADDRMASK]
    
        # Ignore interrupt enable address line.
        test = addr & self.RIOT_ADDRMASK & ~self.INT_ENABLE_MASK
        if test == self.RIOT_Swcha:
            value = self.inputs.swcha
    
        elif test == self.RIOT_Swchb:
            value = self.inputs.swchb
    
        elif test == self.RIOT_Tim1t or test == self.RIOT_Tim8t or test == self.RIOT_Tim64t or test == self.RIOT_T1024t or test == self.TIMERADDR:

            if self.expiration_time >= future_clock:
                # If expiration hasn't occured, return the time remaining. 
                value = (self.expiration_time - future_clock) / (self.interval * self.CYCLES_TO_CLOCK)
            else: # Calculate ticks past zero, may not be quite right
                # The interval was passed, value counts down from 255. 
                value = 0x100 - (((future_clock - self.expiration_time)/self.CYCLES_TO_CLOCK) & 0xFF)
        elif test == self.RIOT_Interrupt:
            if self.expiration_time >= future_clock:
                value = 0
            else:
                # Return the interrupt flag if time has expired. 
                value = 0x80
        else:
            print("Bad address:", addr)
    
        return value

    def write(self, addr, data):
        if 0 == (addr & self.NOT_RAMSELECT):
            self.ram[addr & self.RIOT_ADDRMASK] = data
        else:
            test = addr & self.RIOT_ADDRMASK
            if test == self.RIOT_Tim1t:
                self.interval = 1
                self.set_time = self.clock.system_clock

            elif test == self.RIOT_Tim8t:
                self.interval = 8
                self.set_time = self.clock.system_clock

            elif test == self.RIOT_Tim64t:
                self.interval = 64
                self.set_time = self.clock.system_clock

            elif test == self.RIOT_T1024t:
                self.interval = 1024
                self.set_time = self.clock.system_clock
            else:
                print("Nothing written:", addr)

            self.expiration_time = self.clock.system_clock + self.CYCLES_TO_CLOCK * data * self.interval
