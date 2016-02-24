class Memory(object):
    STELLA_MASK  = 0xFE80
    STELLA_ADDR  = 0x0
    STACK_OFFSET = 0x100
    STACK_LENGTH = 0x100
    RIOT_MASK    = 0xDC80
    RIOT_ADDR    = 0x80
    ROM_MASK     = 0xD000
    ROM_ADDRLINE = 0x1000

    def __init__(self):
        pass

    def get_save_state(self):
        state = {}
        state['cartridge'] = self.cartridge.get_save_state()
        return state

    def set_cartridge(self, cartridge):
        self.cartridge = cartridge

    def set_save_state(self, state):
        self.cartridge.set_save_state(state['cartridge'])

    def set_stella(self, stella):
        self.stella = stella

    def set_riot(self, riot):
        self.riot = riot

    def write(self, address, data):
        if ((address & 0xFFEF) & self.STELLA_MASK) == self.STELLA_ADDR:
            self.stella.write(address & ~self.STELLA_MASK, data);
        elif ((address & self.RIOT_MASK) == self.RIOT_ADDR):
            self.riot.write(address & ~self.RIOT_MASK, data);
        elif (address >= self.STACK_OFFSET) and ((address < self.STACK_OFFSET + self.STACK_LENGTH)):
            self.riot.write(address, data);
        elif (address & self.ROM_ADDRLINE) == self.ROM_ADDRLINE:
        # Only address lines 1-13 are connected, higher bits ignored.
            return self.cartridge.write(address & ~self.ROM_MASK, data);
        else:
            print("Write:", hex(address))
            raise Exception("invalid_write_address" + address)

    def read(self, address):
      # Only address lines 1-13 are connected, higher bits ignored.
      if (address & self.ROM_ADDRLINE) == self.ROM_ADDRLINE:
          return self.cartridge.read(address & ~self.ROM_MASK)

      if (address & self.RIOT_MASK) == self.RIOT_ADDR:
          return self.riot.read(address & ~self.RIOT_MASK)

      if (address & self.STELLA_MASK) == self.STELLA_ADDR:
          return self.stella.read(address & ~self.STELLA_MASK)

      if (address >= self.STACK_OFFSET) and (address < self.STACK_OFFSET + self.STACK_LENGTH):
          return self.riot.read(address)

      return self.cartridge.read(address & ~self.ROM_MASK);

      print("Read:", hex(address))
      raise Exception("invalid_read_address" + address)

    def read16(self, address):
        return self.read(address) + (self.read(address + 1) << 8)

    def readSp(self, address):
        return self.read(address + self.STACK_LENGTH)

    def writeSp(self, address, data):
        self.write(address + self.STACK_LENGTH, data)
