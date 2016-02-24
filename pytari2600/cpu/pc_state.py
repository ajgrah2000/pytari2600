
class PC_Register(object):
    def __init__(self):
        self.value = 0

    def get_save_state(self):
        return self.value

    def set_save_state(self, state):
        self.value = state

    def __add__(self, x):
        self.value = (self.value + x) & 0xFF
        return self

    def __sub__(self, x):
        self.value = (self.value - x) & 0xFF
        return self

    def __int__(self):
        return self.value

    def set_value(self, value):
        if isinstance(value, PC_Register):
            self.value = value.get_value()
        else:
            self.value = value & 0xFF

    def get_value(self):
        return self.value

    def __str__(self):
        return "%X"%(self.value)

class PC_StatusFlags(object):
    def __init__(self):
        self.value = 0

    def get_save_state(self):
        return self.value

    def set_save_state(self, state):
        self.value = state

    def set_N(self, value):
        self.value = (self.value & ~(1)) | (value & 1)

    def set_N(self, value):
        self.value = (self.value & ~(1 << 7)) | ((value & 1) << 7)

    def set_V(self, value):
        self.value = (self.value & ~(1 << 6)) | ((value & 1) << 6)

    def set_X1(self, value):
        self.value = (self.value & ~(1 << 5)) | ((value & 1) << 5)

    def set_B(self, value):
        self.value = (self.value & ~(1 << 4)) | ((value & 1) << 4)

    def set_D(self, value):
        self.value = (self.value & ~(1 << 3)) | ((value & 1) << 3)

    def set_I(self, value):
        self.value = (self.value & ~(1 << 2)) | ((value & 1) << 2)

    def set_Z(self, value):
        self.value = (self.value & ~(1 << 1)) | ((value & 1) << 1)

    def set_C(self, value):
        self.value = (self.value & ~(1 << 0)) | ((value & 1) << 0)

    def get_N(self):
        return (self.value >> 7) & 1

    def get_V(self):
        return (self.value >> 6) & 1

    def get_X1(self):
        return (self.value >> 5) & 1

    def get_B(self):
        return (self.value >> 4) & 1

    def get_D(self):
        return (self.value >> 3) & 1

    def get_I(self):
        return (self.value >> 2) & 1

    def get_Z(self):
        return (self.value >> 1) & 1

    def get_C(self):
        return (self.value >> 0) & 1

    def __str__(self):
#        return "P:%s (C:%s Z:%s I:%s D:%s B:%s X1:%s V:%s N:%s)"%(
#                self.value, self.get_C(),  self.get_Z(),  self.get_I(), self.get_D(), 
#                self.get_B(), self.get_X1(), self.get_V(), self.get_N())
        return "(C:%s Z:%s I:%s D:%s B:%s X1:%s V:%s N:%s)"%(
                self.get_C(),  self.get_Z(),  self.get_I(), self.get_D(), 
                self.get_B(), self.get_X1(), self.get_V(), self.get_N())

class PC_State(object):
    def __init__(self):
        self.A  = PC_Register()
        self.X  = PC_Register()
        self.Y  = PC_Register()
        self.PC = 0
        self.S  = PC_Register()
        self.CYCLES_TO_CLOCK = 3

        self.P = PC_StatusFlags()

    def get_save_state(self):
        state = {}
        state['A']  = self.A.get_save_state()
        state['X']  = self.X.get_save_state()
        state['Y']  = self.Y.get_save_state()
        state['PC'] = self.PC
        state['S']  = self.S.get_save_state()
        state['P']  = self.P.get_save_state()
        return state

    def set_save_state(self, state):
        self.A.set_save_state(state['A'])
        self.X.set_save_state(state['X'])
        self.Y.set_save_state(state['Y'])
        self.PC = state['PC']
        self.S.set_save_state(state['S'])
        self.P.set_save_state(state['P'])

    def __str__(self):
        return "PC:%X X:%X Y:%X A:%X %s"%(
                self.PC, 
                self.X, self.Y, self.A,
                self.P)

    def get_PCL(self):
        return self.PC & 0xFF

    def get_PCH(self):
        return (self.PC >> 8) & 0xFF

    def set_PCL(self, value):
        self.PC = self.PC & 0xFF00 | (value & 0xFF)

    def set_PCH(self, value):
        self.PC = self.PC &   0xFF | ((value & 0xFF) << 8)
