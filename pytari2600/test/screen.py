import pygame
import time

def display_test():
    pygame.init()
    screen = pygame.display.set_mode((800,400))
    pygame.display.set_caption('Pygame')
    pygame.mouse.set_visible(0)

    background = pygame.Surface(screen.get_size())
    background = background.convert()
    background.fill((250,250,250))

    pxarray = pygame.PixelArray(background)

    pxarray[:] = (i%250,i%25,i%150)

    del pxarray

    screen.blit(background, (0,0))
    pygame.display.flip()
    time.sleep(3)

if __name__=='__main__':
  display_test()
