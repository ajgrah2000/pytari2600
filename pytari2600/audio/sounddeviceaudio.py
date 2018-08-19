from . import tiasound
import sounddevice

class SoundDeviceSound(tiasound.TIA_Sound):
    """ Sound, output to the 'sounddevice' module.
    """

    BLOCKSIZE=2048

    def __init__(self, clocks):
        super(SoundDeviceSound, self).__init__(clocks)

        self._last_update_time = self.clocks.system_clock
        self._raw_audio = [[],[]]
        self._next_buffer_0 = bytearray([0,0])
        self._next_buffer_1 = bytearray([0,0])

        self._next_buffer_stretch_0 = bytearray([0] * self.BLOCKSIZE)
        self._next_buffer_stretch_1 = bytearray([0] * self.BLOCKSIZE)

        self._last_update_time = self.clocks.system_clock

        self.openSound()

    def openSound(self):
        self.stream = sounddevice.Stream(channels=2, blocksize=self.BLOCKSIZE, samplerate=self.SAMPLERATE,callback=self.fill_me, finished_callback=self.finished_callback)

        self.stream.start()
        
        print("Freq: ", self.SAMPLERATE, "Hz")

    def pre_write_generate_sound(self):
        """ Update the 'emulated' audio wave form, based on current time.
        """
        audio_ticks = self.clocks.system_clock - self._last_update_time
        self._raw_audio[0].extend(self.get_channel_data(0, (self.SAMPLERATE*audio_ticks/self.CPU_CLOCK_RATE)))
        self._raw_audio[1].extend(self.get_channel_data(1, (self.SAMPLERATE*audio_ticks/self.CPU_CLOCK_RATE)))
        self._last_update_time = self.clocks.system_clock

        self._next_buffer_0 += bytearray(self._raw_audio[0])
        self._next_buffer_1 += bytearray(self._raw_audio[1])

        # 'Stretch' buffer to match callback block size.
        self._next_buffer_stretch_0 = self.stretch(self._next_buffer_0, self.BLOCKSIZE)
        self._next_buffer_stretch_1 = self.stretch(self._next_buffer_1, self.BLOCKSIZE)

        self._raw_audio[0] = []
        self._raw_audio[1] = []

    def step(self):
        pass

    def stretch(self, unstretched_source, final_length):
        # Stretch source to end up with length 'final_length'
        source_pos = 0

        stretched_result = []

        remainder = len(unstretched_source) % final_length
        diviser = int(len(unstretched_source)/final_length)

        # Initialise it to part way through to change where the 'kinks' are.
        source_pos_remainder = remainder/2

        while len(stretched_result) < final_length:
            stretched_result.append(unstretched_source[source_pos])

            source_pos_remainder += remainder
            source_pos += diviser 
            if source_pos_remainder > final_length:
                source_pos += 1
                source_pos_remainder -= final_length

        return stretched_result

    def fill_me(self, indata, outdata, frames, time, status):
        if status:
            print(status)
            print(status.output_underflow)

        outdata[:,0] = self._next_buffer_stretch_0
        outdata[:,1] = self._next_buffer_stretch_1
        self._next_buffer_0 = bytearray([0])
        self._next_buffer_1 = bytearray([0])

    def finished_callback(self):
        print("Audio stream finished")


