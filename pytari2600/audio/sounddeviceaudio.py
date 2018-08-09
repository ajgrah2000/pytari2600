from . import tiasound
import sounddevice

class SoundDeviceSound(tiasound.TIA_Sound):
    """ Sound, output to the 'sounddevice' module.
    """

    def __init__(self, clocks):
        super(SoundDeviceSound, self).__init__(clocks)

        self._last_update_time = self.clocks.system_clock
        self._raw_audio = [[],[]]
        self._next_buffer_0 = bytearray([0,0])
        self._next_buffer_1 = bytearray([0,0])

        self._last_update_time = self.clocks.system_clock

        # Hold 'stretch' state for each channel.
        self._stretcher = tiasound.Stretch()

        self._stretcher.rate = 1000 # 1000 is no stretch.

        self.openSound()

    def openSound(self):
        self.stream = sounddevice.Stream(channels=2, blocksize=0, samplerate=self.SAMPLERATE,callback=self.fill_me, finished_callback=self.finished_callback)

        self.stream.start()
        
        print("Freq: ", self.SAMPLERATE, "Hz")

    def pre_write_generate_sound(self):
        """ Update the 'emulated' audio wave form, based on current time.
        """
        audio_ticks = self.clocks.system_clock - self._last_update_time
        self._raw_audio[0].extend(self.get_channel_data(0, (self.SAMPLERATE*audio_ticks/self.CPU_CLOCK_RATE)))
        self._raw_audio[1].extend(self.get_channel_data(1, (self.SAMPLERATE*audio_ticks/self.CPU_CLOCK_RATE)))
        self._last_update_time = self.clocks.system_clock

        self._next_buffer_0 += self._stretcher.stretch(self._raw_audio[0])
        self._next_buffer_1 += self._stretcher.stretch(self._raw_audio[1])

        self._raw_audio[0] = []
        self._raw_audio[1] = []

    def step(self):
        pass

    def fill_me(self, indata, outdata, frames, time, status):
        if len(self._next_buffer_0) < frames:
            self._next_buffer_0 += bytearray([0] * (frames - len(self._next_buffer_0)))
        if len(self._next_buffer_1) < frames:
            self._next_buffer_1 += bytearray([0] * (frames - len(self._next_buffer_1)))
        outdata[:,0] = self._next_buffer_0[:frames]
        outdata[:,1] = self._next_buffer_1[:frames]
        self._next_buffer_0 = [0]
        self._next_buffer_1 = [0]

    def finished_callback(self):
        print("Audio stream finished")


