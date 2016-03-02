class Addressing(object):
    def __init__(self, pc_state, memory, size, time, additional_page_delay_time=0):
        self.pc_state         = pc_state
        self.memory           = memory
        self._size            = size
        self._time            = time * self.pc_state.CYCLES_TO_CLOCK
        self._page_time       = (time +additional_page_delay_time) * self.pc_state.CYCLES_TO_CLOCK
        self._last_page_delay = False

    def clone(self):
        """ Allow the Address instances to be cloned, to accomodate customisations. """
        return self.__class__(self.pc_state, self.memory)

    def address(self, check_page_delay):
        pass

    def get_addressing_time(self):
        if self._last_page_delay:
            return self._page_time
        else:
            return self._time

    def get_addressing_size(self):
        return self._size

    def has_page_clock_delay(self, a, b):
        page_delay = False
        #  If pages don't match, add a cycle.
        if (a & 0xF00) != (b & 0xF00):
            page_delay = True

        return page_delay

class AddressIZX(Addressing):
    def __init__(self, pc_state, memory):
        super(AddressIZX, self).__init__(pc_state, memory, 1, 4)

    def address(self, check_page_delay):
        """IZX"""
        self.fixed = self.memory.read(self.pc_state.PC + 1)
        self.address = self.address_decode
        return self.address(check_page_delay)

    def address_decode(self, check_page_delay):
        tmp8  = self.fixed + self.pc_state.X.get_value() & 0xFFFF
        return self.memory.read16(tmp8)

class AddressZPX(Addressing):
    def __init__(self, pc_state, memory):
        super(AddressZPX, self).__init__(pc_state, memory, 1, 2)

    def address(self, check_page_delay):
        """ZPX"""
        self.fixed = self.memory.read(self.pc_state.PC + 1)
        self.address = self.address_decode
        return self.address(check_page_delay)

    def address_decode(self, check_page_delay):
        return (self.fixed + self.pc_state.X.get_value()) & 0xFF

class AddressZPY(Addressing):
    def __init__(self, pc_state, memory):
        super(AddressZPY, self).__init__(pc_state, memory, 1, 2)

    def address(self, check_page_delay):
        """ZPY"""
        self.fixed = self.memory.read(self.pc_state.PC + 1)
        self.address = self.address_decode
        return  self.address(check_page_delay)

    def address_decode(self, check_page_delay):
        return  (self.fixed + self.pc_state.Y.get_value()) & 0xFF

class AddressZP(Addressing):
    def __init__(self, pc_state, memory):
        super(AddressZP, self).__init__(pc_state, memory, 1, 1)

    def address(self, check_page_delay):
        """ZP"""
        self.fixed = self.memory.read(self.pc_state.PC + 1)
        self.address = self.address_decode
        return self.address(check_page_delay)

    def address_decode(self, check_page_delay):
        """ZP"""
        return self.fixed

class AddressIMM(Addressing):
    def __init__(self, pc_state, memory):
        super(AddressIMM, self).__init__(pc_state, memory, 1, 0)

    def address(self, check_page_delay):
        """IMM"""
        return self.pc_state.PC + 1

class AddressIZY(Addressing):
    def __init__(self, pc_state, memory):
        super(AddressIZY, self).__init__(pc_state, memory, 1, 3)

    def address(self, check_page_delay):
        """IZY"""
        self.fixed = self.memory.read(self.pc_state.PC + 1)
        self.address = self.address_decode
        return self.address(check_page_delay)

    def address_decode(self, check_page_delay):
        return self.memory.read16(self.fixed) + self.pc_state.Y.get_value() & 0xFFFF

class AddressAbs(Addressing):
    def __init__(self, pc_state, memory):
        super(AddressAbs, self).__init__(pc_state, memory, 2, 2)

    def address(self, check_page_delay):
        """Abs"""
        self.fixed= self.memory.read16(self.pc_state.PC + 1)
        self.address = self.address_decode
        return self.address(check_page_delay)

    def address_decode(self, check_page_delay):
        return self.fixed

class AddressIndirect(Addressing):
    def __init__(self, pc_state, memory):
        super(AddressIndirect, self).__init__(pc_state, memory, 2, 4)

    def address(self, check_page_delay):
        """Ind"""
        self.fixed = self.memory.read16(self.pc_state.PC + 1)
        self.address = self.address_decode
        return self.address(check_page_delay)

    def address_decode(self, check_page_delay):
        return self.memory.read16(self.fixed)

class AddressAby(Addressing):
    def __init__(self, pc_state, memory):
        super(AddressAby, self).__init__(pc_state, memory, 2, 2, 1)

    def address(self, check_page_delay):
        """Aby"""
        self.fixed = self.memory.read16(self.pc_state.PC + 1)
        self.address = self.address_decode
        return self.address(check_page_delay)

    def address_decode(self, check_page_delay):
        tmp16 = self.fixed + self.pc_state.Y.get_value() & 0xFFFF

        if (check_page_delay):
            self._last_page_delay = self.has_page_clock_delay(self.fixed, tmp16)

        return tmp16

class AddressAbx(Addressing):
    def __init__(self, pc_state, memory):
        super(AddressAbx, self).__init__(pc_state, memory, 2, 2, 1)

    def address(self, check_page_delay):
        """Abx"""
        self.fixed = self.memory.read16(self.pc_state.PC + 1)
        self.address = self.address_decode
        return self.address(check_page_delay)

    def address_decode(self, check_page_delay):
        tmp16 = self.fixed + self.pc_state.X.get_value() & 0xFFFF

        if (check_page_delay):
            self._last_page_delay = self.has_page_clock_delay(self.fixed, tmp16)

        return tmp16

class AddressAccumulator(Addressing):
    def __init__(self, pc_state, memory):
        super(AddressAccumulator, self).__init__(pc_state, memory, 0, 0)

    def address(self, check_page_delay):
        """Acc"""
        return 0
