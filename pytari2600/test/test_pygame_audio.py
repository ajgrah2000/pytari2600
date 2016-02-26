import pygame.mixer
import time
import wave

class TestReadWAV_Sound(object):
    def __init__(self, filenames):
#        pygame.mixer.pre_init(frequency=32050, size=-8, channels=2, buffer=1024*8)
        pygame.mixer.pre_init(32050, -8, 2, 1024*8)
        pygame.init()
        pygame.mixer.set_num_channels(1)

        self._wav_input = []
        channel = []

        for filename in filenames:
            self._wav_input.append(wave.open(filename))

#        self._wav_input.setparams((1,1,32050, 0, 'NONE', 'not compressed'))
        channel = pygame.mixer.Channel(0)

        while True:
#            num_frames = self._wav_input.getnframes()
#            for i in range(num_frames):
            if not channel.get_queue():

                channel_buffer = [0] * 2 * 1024*16
                for channel_num in range(0,2):
                    sound_buffer = self._wav_input[channel_num].readframes(1024*16)
                    sound_buffer = list(sound_buffer)

                    channel_buffer[channel_num::2] = sound_buffer

                sound = pygame.mixer.Sound(bytearray(channel_buffer))

                channel.queue(sound)

class DummyClocks(object):
    def __init__(self):
        self.system_clock = 0

if __name__ == '__main__':

#    pygame.init()
#    s = pygame.display.set_mode(( 10, 10))
#    sound_files = ['test/pytari_stretch_chan0.wav',
#                   'test/pytari_stretch_chan1.wav']
#    testwav_read = TestReadWAV_Sound(sound_files)
    pass
