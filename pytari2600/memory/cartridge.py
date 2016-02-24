"""
    Implementations of different cartridge types.
"""

class PBCartridge(object):
    MAXBANKS = 8
    BANKSIZE = 0x0400

    def __init__(self, file_name):

        self.max_banks = PBCartridge.MAXBANKS
        self.bank_size = PBCartridge.BANKSIZE

        self._slice = [0]*4
        self._slice[0] = 4
        self._slice[1] = 5
        self._slice[2] = 6
        self._slice[3] = 7

        self.num_banks = 0
        self.current_bank = 0

        self._file_name = file_name
        self._load_cartridge(file_name)

    def get_save_state(self):
        state = {}
        state['current_bank'] = self.current_bank 
        state['file_name']    = self._file_name 
        state['slices']       = list(self._slice)
        return state

    def set_save_state(self, state):
        self.current_bank = state['current_bank'] 
        self._file_name   = state['file_name']
        self._slice       = list(state['slices'])

    def get_absolute_address(self, address):
        absolute = self.bank_size * self._slice[(address & 0xC00) >> 10] + (address & 0x3FF)
        return absolute

    def write(self, address, data):
        address = address & 0xFFF

        if 0xFE0 == (address & 0xFF8):
            self._slice[0] = address & 0x7

        elif 0xFE8 == (address & 0xFF8):
            self._slice[1] = address & 0x7

        elif 0xFF0 == (address & 0xFF8):
            self._slice[2] = address & 0x7

    def read(self, address):
        """
           0xFF6 == address: Last bank - 3
           0xFF7 == address: Last bank - 2
           0xFF8 == address: Last bank - 1
           0xFF9 == address: Last bank
        """
        address = address & 0xFFF
        if 0xFE0 == (address & 0xFF8):
            self._slice[0] = address & 0x7

        elif 0xFE8 == (address & 0xFF8):
            self._slice[1] = address & 0x7

        elif 0xFF0 == (address & 0xFF8):
            self._slice[2] = address & 0x7

        return self.cartridge_banks[self._slice[(address & 0xC00) >> 10]][address & 0x3FF]

    def _load_cartridge(self, filename):
        bytes_read = 0
        total_bytes_read = 0

        self.max_cartridge = [[]] * self.max_banks

        print("Opening: ", filename)
        with open(filename, 'rb') as rom_file:

            full = rom_file.read()
            for bank in self._chunks(full, self.bank_size):

                bytes_read = len(bank)

                if (bytes_read != 0):
                    self.max_cartridge[self.num_banks] = bytearray(bank)
                    self.num_banks += 1

                total_bytes_read += bytes_read

        if (bytes_read > 0) and (bytes_read < self.bank_size):
            print("Warning: Short Cartridge")

        self.cartridge_banks = [[]] * self.num_banks

        for i in range(self.num_banks):
            self.cartridge_banks[i] = self.max_cartridge[i]

        # Set default bank to the last bank.
        self.current_bank = 0

        print("PBCartridge read:")
        print(" banks =", self.num_banks)
        print(" bytes =", total_bytes_read)

    def _chunks(self, l, n):
        for i in range(0, len(l), n):
            yield l[i:i+n]

class MNetworkCartridge(object):
    MAXBANKS = 8
    BANKSIZE = 0x0800
    RAMSIZE  = 0x0800

    def __init__(self, file_name):
        self.max_banks = MNetworkCartridge.MAXBANKS
        self.bank_size = MNetworkCartridge.BANKSIZE
        self.ram_size  = MNetworkCartridge.RAMSIZE

        self.num_banks = 0
        self.bank_select = 0
        self.ram_select = 0

        self.ram = []

        self._file_name = file_name

        self._load_cartridge(file_name)

    def get_save_state(self):
        state = {}
        state['ram']          = list(self.ram)
        state['current_bank'] = self.current_bank 
        state['ram_select']   = self.ram_select 
        state['file_name']    = self._file_name 
        return state

    def set_save_state(self, state):
        self.ram          = list(state['ram'])
        self.current_bank = state['current_bank']
        self.ram_select   = state['ram_select']
        self._file_name   = state['file_name']

    def get_absolute_address(self, address):
        bank = self.bank_select
        if ((address & 0xF00) >= 0xA00):
            bank = 7
        return bank * self.bank_size + (address & 0x7FF)

    def write(self, address, data):
        address = address & 0xFFF
        if 0xFE0 == (address & 0xFF8):
            # Bank select 0 to 7 
            self.bank_select = address & 0x7
        elif 0xFE8 == (address & 0xFF8):
            # 256k Ram select. 
            self.ram_select = address & 0x3

        if (self.bank_select == 7 and 0x000 == (address & 0x800)):
            self.ram[address & 0x3FF] = data
        elif 0x800 == (address & 0xF00):
            # Selectable 256Kb RAM. write on 1800-18FF
            self.ram[(address & 0x7FF) | 0x400 | (self.ram_select << 8)] = data
        else:
            print("Invalid write address %x"%(address))

    def read(self, address):
        address = address & 0xFFF
        if (0xFE0 == (address & 0xFF8)):
            self.bank_select = address & 0x7
        elif (0xFE8 == (address & 0xFF8)):
            self.ram_select = address & 0x3

        if ((self.bank_select == 7) and (0x400 == (address & 0xC00))):
            # Return reads from ram.
            byte = self.ram[address & 0x3FF]
        elif (0x000 == (address & 0x800)):
            # Return cartridge select.
            byte = self.cartridge_banks[self.bank_select][address & 0x7FF]
        elif (0x900 == (address & 0xF00)):
            # Selectable 256Kb RAM. write on 1800-18FF
            byte = self.ram[(address & 0x7FF) | 0x400 | (self.ram_select << 8)]
        elif ((address & 0xF00) >= 0xA00):
            # Return fixed cartridge location.
            byte = self.cartridge_banks[7][address & 0x7FF]
        else:
            print("Invalid address %x"%(address))
            byte = 0

        return byte

    def _load_cartridge(self, filename):
        bytes_read = 0
        total_bytes_read = 0

        self.max_cartridge = [[]] * self.max_banks

        print("Opening: ", filename)

        self.ram = [] * self.RAMSIZE
        with open(filename, 'rb') as rom_file:
            full = rom_file.read()
            for bank in self._chunks(full, self.bank_size):

                bytes_read = len(bank)
                if bytes_read != 0:
                    self.max_cartridge[self.num_banks] = bytearray(bank)
                    self.num_banks += 1
                total_bytes_read += bytes_read

            self.cartridge_banks = [[]] * self.num_banks

            for i in range(self.num_banks):
              self.cartridge_banks[i] = self.max_cartridge[i]
    
            # Set default bank to the last bank.
            self.current_bank = 0
    
            print("MNetworkCartridge read:")
            print(" banks = ", self.num_banks)
            print(" bytes = ", total_bytes_read)
            print(" first bank size = ", len(self.cartridge_banks[0]))

    def _chunks(self, l, n):
        for i in range(0, len(l), n):
            yield l[i:i+n]

class FECartridge(object):

    def __init__(self, file_name, max_banks, bank_size):
        self.max_banks = max_banks
        self.bank_size = bank_size
        self.cartridge_banks = [[]] * self.max_banks
        self.num_banks    = 0
        self.current_bank = 0

        self._load_cartridge(file_name)

    def get_save_state(self):
        state = {}
        state['current_bank'] = self.current_bank 
        state['file_name']    = self._file_name 
        return state

    def set_save_state(self, state):
        self.current_bank = state['current_bank']
        self._file_name   = state['file_name']

    def get_absolute_address(self, address):
        if 0x0000   == (address & 0x2000):
            current_bank = 1
        elif 0x2000 == (address & 0x2000):
            current_bank = 0
        return current_bank * self.bank_size + (address & 0xFFF)

    def read(self, address):
        if 0x0000   == (address & 0x2000):
            self.current_bank = 1
        elif 0x2000 == (address & 0x2000):
            self.current_bank = 0

        address = address & 0xFFF

        return self.cartridge_banks[self.current_bank][address]

    def write(self, address, data):
        if 0x0000 == (address & 0x2000):
            self.current_bank = 1
        elif 0x2000 == (address & 0x2000):
            self.current_bank = 0

    def _load_cartridge(self, filename):
        total_bytes_read = 0

        print("Opening:", filename)

        with open(filename, 'rb') as rom_file:

            self.max_cartridge = [[]] * self.max_banks
            full = rom_file.read()
            for bank in self._chunks(full, self.bank_size):

                bytes_read = len(bank)

                print("nb:%d,%x"%(self.num_banks, self.bank_size))
                if bytes_read != 0:
                    self.max_cartridge[self.num_banks] = bytearray(bank)
                    self.num_banks += 1

                total_bytes_read += bytes_read

            self.cartridge_banks = [[]] * self.num_banks

            for i in range(self.num_banks):
              self.cartridge_banks[i] = self.max_cartridge[i]

            # Set default bank to the last bank.
            self.current_bank = 0

            print("Cartridge read:")
            print(" banks = ", self.num_banks)
            print(" bytes = ", total_bytes_read)
            print(" first bank size = ", len(self.cartridge_banks[0]))

    def _chunks(self, l, n):
        for i in range(0, len(l), n):
            yield l[i:i+n]

class SingleBankCartridge(object):
    """ Simple, single bank cartridge, no bank switching. """

    def __init__(self, file_name, bank_size):
        self.bank_size = bank_size
        self.cartridge_bank = [] 
        self.num_banks    = 0

        self._load_cartridge(file_name)

    def get_save_state(self):
        state = {}
        state['file_name']    = self._file_name 
        return state

    def set_save_state(self, state):
        self._file_name   = state['file_name']

    def get_absolute_address(self, address):
        return (address & 0xFFF)

    def read(self, address):
        return self.cartridge_bank[address & 0xFFF]

    def write(self, address, data):
        pass

    def _load_cartridge(self, filename):
        total_bytes_read = 0

        print("Opening:", filename)

        with open(filename, 'rb') as rom_file:

            self.max_cartridge = [] 
            full = rom_file.read()

            for bank in self._chunks(full, self.bank_size):

                bytes_read = len(bank)

                if (bytes_read > 0) and (bytes_read < self.bank_size):
                    # If the bank is short, pad it with zeros.
                    bank += '\000' * (self.bank_size-bytes_read)
                    # If the read size was less than a half bank, copy the
                    # shortfall.
                    if bytes_read <= self.bank_size/2:
                        bank = bank[0:self.bank_size/2] + bank[0:self.bank_size/2]
                        self.max_cartridge = bank[0:self.bank_size/2] + bank[0:self.bank_size/2]
                self.max_cartridge = bytearray(bank)

                total_bytes_read += bytes_read

            self.cartridge_bank = []
            self.cartridge_bank = self.max_cartridge

            print("Cartridge read:")
            print(" banks = ", self.num_banks)
            print(" bytes = ", total_bytes_read)
            print(" first bank size = ", len(self.cartridge_bank))

    def _chunks(self, l, n):
        for i in range(0, len(l), n):
            yield l[i:i+n]

class GenericCartridge(object):

    def __init__(self, file_name, max_banks, bank_size, hot_swap, ram_size):
        self.max_banks = max_banks
        self.bank_size = bank_size
        self.hot_swap = hot_swap
        self.ram_size = ram_size
        self.ram_addr_mask = 0xFFFF & (self.ram_size - 1)
        self.cartridge_banks = [[]] * self.max_banks
        self.ram = []
        self.num_banks    = 0
        self.current_bank = 0
        self.bank_select  = 0
        self._file_name = file_name

        self._load_cartridge(file_name)

    def get_save_state(self):
        state = {}
        state['ram'] = list(self.ram)
        state['current_bank'] = self.current_bank 
        state['file_name'] = self._file_name 
        return state

    def set_save_state(self, state):
        self.ram           = list(state['ram'])
        self.current_bank  = state['current_bank']
        self._file_name    = state['file_name']

    def get_absolute_address(self, address):
        return self.bank_size * self.current_bank + (address & 0xFFF)

    def read(self, address):
        address = address & 0xFFF
        if (self.ram_size > 0) and (address < 2*self.ram_size) and (address >= self.ram_size):
            data = self.ram[address & self.ram_addr_mask]
        else:
             # 0xFF8 == address: Last bank - 2
             # 0xFF9 == address: Last bank - 1
             # 0xFFA == address: Last bank
            if (((self.hot_swap +1) - self.num_banks) <=  address) and ((self.hot_swap+1) >  address):
                self.current_bank = self.num_banks - ((self.hot_swap+1) - address)

            data = self.cartridge_banks[self.current_bank][address]
        return data

    def write(self, address, data):
        address = address & 0xFFF
        if (self.ram_size > 0) and (address < self.ram_size):
            self.ram[address & self.ram_addr_mask] = data

        if (((self.hot_swap+1) - self.num_banks) <=  address) and ((self.hot_swap+1) >  address):
            self.current_bank = self.num_banks - ((self.hot_swap+1) - address)

    def _load_cartridge(self, filename):
        total_bytes_read = 0

        print("Opening:", filename)

        with open(filename, 'rb') as rom_file:

            if (self.ram_size > 0):
                self.ram = [0] * self.ram_size

            self.max_cartridge = [[]] * self.max_banks
            full = rom_file.read()
            for bank in self._chunks(full, self.bank_size):

                bytes_read = len(bank)

                if (bytes_read > 0) and (bytes_read < self.bank_size):
                    # If the bank is short, pad it with zeros.
                    bank += bytearray('\000'.encode() * (self.bank_size-bytes_read))
                    # If the read size was less than a half bank, copy the
                    # shortfall.
                    if bytes_read <= int(self.bank_size/2):
                        bank = bank[0:int(self.bank_size/2)] + bank[0:int(self.bank_size/2)]
                        self.max_cartridge[self.num_banks] = bank[0:int(self.bank_size/2)] + bank[0:int(self.bank_size/2)]
                self.max_cartridge[self.num_banks] = bytearray(bank)

                self.num_banks += 1
                total_bytes_read += bytes_read

            self.cartridge_banks = [[]] * self.num_banks

            for i in range(self.num_banks):
              self.cartridge_banks[i] = self.max_cartridge[i]

            # Set default bank to the last bank.
            self.current_bank = 0

            print("Cartridge read:")
            print(" banks = ", self.num_banks)
            print(" bytes = ", total_bytes_read)
            print(" first bank size = ", len(self.cartridge_banks[0]))

    def _chunks(self, l, n):
        for i in range(0, len(l), n):
            yield l[i:i+n]

if __name__ == '__main__':
    import sys
    new_generic_cart = GenericCartridge(sys.argv[1], 4, 0x1000, 0xFF9, 0x0)
    print(new_generic_cart.read(0), new_generic_cart.read(1))

    new_pb_cart = PBCartridge(sys.argv[1])
    print(new_pb_cart.read(0), new_pb_cart.read(1))
