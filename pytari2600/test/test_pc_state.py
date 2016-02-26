import pytari2600.pc_state as pc_state
import unittest

class TestAddressing(unittest.TestCase):

    def test_pc_status(self):
        status_flags = pc_state.PC_StatusFlags()
        self.assertEqual(status_flags.value.value, 0)
        status_flags.set_X1(0)
        self.assertEqual(status_flags.value.value, 0)
        status_flags.set_X1(1)
        self.assertEqual(status_flags.value.value, 4)
        status_flags.set_X1(0)
        self.assertEqual(status_flags.value.value, 0)
        status_flags.set_X1(1)
        status_flags.set_I(1)
        self.assertEqual(status_flags.value.value, 36)
        status_flags.value.set_value(0x55)
        self.assertEqual(status_flags.get_X1(), 1)
        self.assertEqual(status_flags.get_N(), 1)
        self.assertEqual(status_flags.get_D(), 1)
        self.assertEqual(status_flags.get_Z(), 1)
        self.assertEqual(status_flags.get_I(), 0)

if __name__ == '__main__':
    unittest.main()
