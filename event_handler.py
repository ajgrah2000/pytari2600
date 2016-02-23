import pygame
import threading

class EventHandler(object):
    def __init__(self, input_handler, sound_handler):
        self._input_handler = input_handler
        self._sound_handler = sound_handler

    def start(self):
        t = threading.Thread(target=self.process_events)
        t.daemon = True
        t.start()

    def process_events(self):
        while True:
            event = pygame.event.wait()
            if event.type== pygame.KEYDOWN:
                self._input_handler(event)
            elif event.type== pygame.KEYUP:
                self._input_handler(event)
            else:
                self._sound_handler(event)

    def poll_process_events(self):
        """ Allow events to be polled. PLACEHOLDER, currently not hoooked in as
        thread is more efficient. """
        event = pygame.event.poll()
        if event.type== pygame.NOEVENT:
            pass
        elif event.type== pygame.KEYDOWN:
            self._input_handler(event)
        elif event.type== pygame.KEYUP:
            self._input_handler(event)
        else:
            self._sound_handler(event)
