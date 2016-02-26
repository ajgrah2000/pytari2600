import pytari2600.inputs as inputs
import unittest
import time
import pygame

class TestInput(unittest.TestCase):
    def test_input(self):
        i = inputs.Input()
        test_inputs = [(pygame.KEYDOWN, {'key':pygame.K_1}),
                       (pygame.KEYDOWN, {'key':pygame.K_2}),
                       (pygame.KEYDOWN, {'key':pygame.K_2}),
                       (pygame.KEYDOWN, {'key':pygame.K_UP}),
                       (pygame.KEYDOWN, {'key':pygame.K_LEFT}),
                       (pygame.KEYUP,   {'key':pygame.K_r}),
#                       (pygame.KEYDOWN, {'key':pygame.K_q})
                       ]
        for e in [pygame.event.Event(*x) for x in test_inputs]:
            i.handle_events(e)
                    
        self.assertEqual(i.get_swcha(),   0xAF)
        self.assertEqual(i.get_swchb(),   0x7F)
        self.assertEqual(i.get_paddle0(),  0x1)
        self.assertEqual(i.get_input7(),  0xFF)

if __name__ == '__main__':
    unittest.main()
