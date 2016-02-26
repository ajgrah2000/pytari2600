import pytari2600.memory.cartridge as cartridge
import unittest
import pkg_resources

class TestCartridge(unittest.TestCase):

    def test_cartridge(self):
        cart = cartridge.GenericCartridge(pkg_resources.resource_filename(__name__, 'dummy_rom.bin'), 4, 0x1000, 0xFF9, 0x0)
        # Write should do nothing
        cart.write(0,7)
        self.assertEqual(cart.read(0), 0)
        self.assertEqual(cart.read(3), 3)
        self.assertEqual(cart.read(2048+2), 2)

    def test_ram_cartridge(self):
        cart = cartridge.GenericCartridge(pkg_resources.resource_filename(__name__, 'dummy_rom.bin'), 4, 0x1000, 0xFF9, 0x080)
        # Write should go to ram.
        cart.write(0,7)
        self.assertEqual(cart.read(0x80), 7)
        cart.write(0,31)
        self.assertEqual(cart.read(0x80), 31)

if __name__ == '__main__':
    unittest.main()
