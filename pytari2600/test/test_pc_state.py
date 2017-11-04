import pytari2600.cpu.pc_state as pc_state
import unittest

class TestPC_State(unittest.TestCase):

    def test_pc_status(self):
        status_flags = pc_state.PC_StatusFlags()
        self.assertEqual(status_flags.value, 0)
        status_flags.set_X1(0)
        self.assertEqual(status_flags.value, 0)
        status_flags.set_X1(1)
        self.assertEqual(status_flags.value, 32)
        status_flags.set_X1(0)
        self.assertEqual(status_flags.value, 0)
        status_flags.set_X1(1)
        status_flags.set_I(1)
        self.assertEqual(status_flags.get_save_state(), 36)
        status_flags.set_save_state(0x55)
        self.assertEqual(status_flags.get_B(), 1)
        self.assertEqual(status_flags.get_X1(), 0)
        self.assertEqual(status_flags.get_C(), 1)
        self.assertEqual(status_flags.get_N(), 0)
        self.assertEqual(status_flags.get_D(), 0)
        self.assertEqual(status_flags.get_Z(), 0)
        self.assertEqual(status_flags.get_I(), 1)
        self.assertEqual(status_flags.get_V(), 1)

if __name__ == '__main__':
    unittest.main()
