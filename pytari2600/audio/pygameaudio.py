from . import tiasound
import wave
import pygame.mixer
import pygame.locals

class PygameStretchTIA_Sound(tiasound.TIA_Sound):
    """ Capture sound (accurately), try to stretch sound to current speed.
    """

    def __init__(self, clocks):
        super(PygameStretchTIA_Sound, self).__init__(clocks)

        # Flag to indicate if samples should be stretched in frequency, or more outputs generated.
        self._maintain_pitch = True

        self._wav_output = [wave.open('pytari_stretch_chan0.wav', 'w'),wave.open('pytari_stretch_chan1.wav', 'w')]
        self._wav_output[0].setparams((1, 1, self.SAMPLERATE, 0, 'NONE', 'not compressed'))
        self._wav_output[1].setparams((1, 1, self.SAMPLERATE, 0, 'NONE', 'not compressed'))

        self._sound_chunk_size        =   1024*4

        self.openSound()
        
        self._test_accumulated_sound  = self._sound_chunk_size * 2

        # Hold 'stretch' state for each channel.
        self._stretcher = tiasound.Stretch()

        self._stretched = [[],[]]

        self._last_update_time = self.clocks.system_clock

    def openSound(self):
        pygame.mixer.pre_init(self.SAMPLERATE, -self.BITS, self.CHANNELS, 1024*8)
        pygame.mixer.init()
        pygame.mixer.set_num_channels(2)

        self.channel = pygame.mixer.Channel(0)
        self.channel.set_volume(0.3)
        
        print("Freq: ", self.SAMPLERATE, "Hz")

    def pre_write_generate_sound(self):
        """ Update the 'emulated' audio wave form, based on current time.
        """
        audio_ticks = self.clocks.system_clock - self._last_update_time
        self._last_update_time = self.clocks.system_clock

        for channel_num in range(self.CHANNELS):

            if self._maintain_pitch:
                # Generate the 'raw' channel output
                raw_audio = self.get_channel_data(channel_num, (self._stretcher.divisor*self.SAMPLERATE*audio_ticks/(self.CPU_CLOCK_RATE*self._stretcher.rate)))
                self._stretched[channel_num] += raw_audio
            else:
                # Generate the 'raw' channel output
                raw_audio = self.get_channel_data(channel_num, (self.SAMPLERATE*audio_ticks/self.CPU_CLOCK_RATE))
                # Stretch/scale sound to compensate for real/emulated speed difference
                self._stretched[channel_num] += self._stretcher.stretch(raw_audio)

            # Test sound output
            self._wav_output[channel_num].writeframes(bytearray(raw_audio))

        #self.play_channel_buffers()

    def step(self):
        #self.pre_write_generate_sound()
        self.play_channel_buffers()

    def play_channel_buffers(self):

         if len(self._stretched[0]) > self._sound_chunk_size and len(self._stretched[1]) > self._sound_chunk_size:
             if not self.channel.get_queue() or not self.channel.get_busy():
                    # Queue and current sound is empty.
                    # Increase stretch rate.
                  if self._stretcher.rate > 11:
                     self._stretcher.rate -= 2

                  # Set left and right data for the channel.
                  channel_chunk = [0] * 2 * self._sound_chunk_size

                  for channel_num in range(self.CHANNELS):
                    sound_chunk = self._stretched[channel_num][:self._sound_chunk_size]
                    self._stretched[channel_num] = self._stretched[channel_num][self._sound_chunk_size:]

                    channel_chunk[channel_num::2] = sound_chunk

                  if not self.channel.get_busy():
                     if self._stretcher.rate > 11:
                        self._stretcher.rate -= 4
                  else:
                        self._stretcher.rate += 4

                  sound = pygame.mixer.Sound(bytearray(channel_chunk))

                  if not self.channel.get_queue():
                      self.channel.queue(sound)
                  else:
                      self.channel.play(sound)

    def handle_events(self, event):
        print("handle", event.type, event)
