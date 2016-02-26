import pytari2600.inputs as inputs
import pytari2600.memory.riot as riot
import pytari2600.clocks as clocks
import unittest

class TestRiot(unittest.TestCase):
    def test_riot(self):
        clock = clocks.Clock()
        clock.system_clock = 100337
        test_input = inputs.Input()
        riot_test = riot.Riot(clock, test_input)

        riot_test.write(0x100, 7)
        self.assertEqual(riot_test.read(0x100), 7)

if __name__ == '__main__':
    unittest.main()
