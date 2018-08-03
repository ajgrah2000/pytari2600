import pytari2600.inputs as inputs
import unittest
import time
import pygame

class TestInput(unittest.TestCase):

    def test_input(self):
        i = inputs.Input()

        # Need to initialise the key lookups (keys are set by each input library).
        i.EVENT_KEYDOWN     = pygame.KEYDOWN
        i.EVENT_KEYUP       = pygame.KEYUP

        i.KEY_UP            = pygame.K_UP
        i.KEY_DOWN          = pygame.K_DOWN
        i.KEY_LEFT          = pygame.K_LEFT
        i.KEY_RIGHT         = pygame.K_RIGHT
        i.KEY_SELECT        = pygame.K_s
        i.KEY_RESET         = pygame.K_r
        i.KEY_P0_DIFICULTY  = pygame.K_1
        i.KEY_P1_DIFICULTY  = pygame.K_2
        i.KEY_BLACK_WHITE   = pygame.K_c
        i.KEY_BUTTON        = pygame.K_z
        i.KEY_QUIT          = pygame.K_q
        i.KEY_SAVE_STATE    = pygame.K_LEFTBRACKET
        i.KEY_RESTORE_STATE = pygame.K_RIGHTBRACKET

        test_inputs = [(pygame.KEYDOWN, {'key':pygame.K_1}),
                       (pygame.KEYDOWN, {'key':pygame.K_2}),
                       (pygame.KEYDOWN, {'key':pygame.K_2}),
                       (pygame.KEYDOWN, {'key':pygame.K_UP}),
                       (pygame.KEYDOWN, {'key':pygame.K_LEFT}),
                       (pygame.KEYUP,   {'key':pygame.K_r}),
#                       (pygame.KEYDOWN, {'key':pygame.K_q})
                       ]
        for e in [pygame.event.Event(*x) for x in test_inputs]:
            #i.handle_events(e)
            i.input_register_bits(e.type, e.key)
                    
        self.assertEqual(i.get_swcha(),   0xAF)
        self.assertEqual(i.get_swchb(),   0x7F)
        self.assertEqual(i.get_paddle0(),  0x1)
        self.assertEqual(i.get_input7(),  0xFF)

if __name__ == '__main__':
    unittest.main()
