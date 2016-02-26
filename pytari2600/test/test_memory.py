import pytari2600.memory.memory as memory
import unittest

class Dummy(object):
    def __init__(self):
        self.last_write = 0

    def read(self, address):
        return self.last_write 

    def write(self, address, data):
        self.last_write  = data

class TestMemory(unittest.TestCase):
    def test_memory(self):
        dummy = Dummy()
        m = memory.Memory()

        m.set_cartridge(dummy)
        m.set_riot(dummy)
        m.set_stella(dummy)

        m.write(0x100, 3)
        r = m.read(0x100)
        self.assertEqual(r, 3)

if __name__ == '__main__':
    unittest.main()
