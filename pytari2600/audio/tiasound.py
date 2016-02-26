import ctypes
import struct

class TIA_Sound(object):
    def __init__(self, clocks):
        print("TiaSound chip created")

        # CPU Clock rate, used to scale to real time.
        self.CPU_CLOCK_RATE = 3580000

        self.SAMPLERATE = 32050
        self.CHANNELS = 2
        self.FREQ_DATA_MASK = 0x1F
        self.BITS = 8

        # Stella addresses: 
        # Ctrl0: 0x15, Ctrl1: 0x16, Freq0: 0x17, Freq1: 0x18, Vol0: 0x19, Vol1: 0x1A

        self.clocks = clocks

        self.volume     = [0] * 2
        self.freq       = [0] * 2
        self.poly4State = [0] * 2
        self.poly5State = [0] * 2
        self.waveForm   = [0] * 2

        self._freq_pos  = [0] * 2


    def get_save_state(self):
        state = {}
        state['volume']     = self.volume
        state['freq']       = self.freq
        state['poly4State'] = self.poly4State
        state['poly5State'] = self.poly5State
        state['waveForm']   = self.waveForm
        return state

    def set_save_state(self, state):
        self.volume     = state['volume']
        self.freq       = state['freq']
        self.poly4State = state['poly4State']
        self.poly5State = state['poly5State']
        self.waveForm   = state['waveForm']

    # Clock poly 4, return new poly4 state
    @staticmethod
    def poly4(audio_ctrl, poly5_state, poly4_state):

        i = not (audio_ctrl & 0xF) or  \
            (not (audio_ctrl & 0xC) and (((poly4_state & 0x3) != 0x3) and (poly4_state & 0x3) and ((poly4_state & 0xF) != 0xA))) or \
            (((audio_ctrl & 0xC) == 0xC) and  (poly4_state & 0xC) and not(poly4_state & 0x2)) or \
            (((audio_ctrl & 0xC) == 0x4) and not(poly4_state & 0x8)) or \
            (((audio_ctrl & 0xC) == 0x8) and not(poly5_state & 0x1))

        poly4Output = (0x7 ^ (poly4_state >> 1)) | i << 3

        return poly4Output

    # Clock poly 5, return new poly5 state
    @staticmethod
    def poly5(audio_ctrl, poly5_state, poly4_state):

        in_5 =    not(audio_ctrl & 0xF) or \
                  (((audio_ctrl & 0x3) or ((poly4_state & 0xF) == 0xA)) and not(poly5_state & 0x1F)) or \
                  not((((audio_ctrl & 0x3) or not(poly4_state & 0x1)) and (not(poly5_state & 0x8) or not(audio_ctrl & 0x3))) ^ (poly5_state & 0x1))

        poly5Output = (poly5_state >> 1) | (in_5 << 4)

        return poly5Output

    @staticmethod
    def poly5clk(audio_ctrl, poly5_state):
        clockoutput = (((audio_ctrl & 0x3) != 0x2) or (0x2 == (poly5_state & 0x1E))) and \
                      (((audio_ctrl & 0x3) != 0x3) or (poly5_state & 0x1))

        return clockoutput


    def get_channel_data(self, channel, length):
        # Stereo callback encodes left and right by using even/odd entries in the
        # stream.
        length = int(length)
        stream = [0] * length
        for i in range(length):
    
            if 0 == (self._freq_pos[channel] % (self.freq[channel] + 1)):
                nextPoly5 = self.poly5(self.waveForm[channel], self.poly5State[channel], self.poly4State[channel])

                if self.poly5clk(self.waveForm[channel], self.poly5State[channel]):
                    self.poly4State[channel] = self.poly4(self.waveForm[channel], self.poly5State[channel], self.poly4State[channel])

                self.poly5State[channel] = nextPoly5
    
            if self.poly4State[channel] & 1:
                stream[i] = (self.volume[channel] & 0xF) * 0x7 & 0xFF
    
            self._freq_pos[channel] += 1

        return stream

    
    # Update the current state of the emulated sound data before control
    # change, so previous wave form can be stopped at correct time before
    # control change.

    def write_audio_ctrl_0(self, data):
        self.pre_write_generate_sound()
        self.waveForm[0] = data & 0xFF
        self.post_write_generate_sound()

    def write_audio_ctrl_1(self, data):
        self.pre_write_generate_sound()
        self.waveForm[1] = data & 0xFF
        self.post_write_generate_sound()

    def write_audio_freq_0(self, data):
        self.pre_write_generate_sound()
        self.freq[0]     = data & self.FREQ_DATA_MASK
        self.post_write_generate_sound()

    def write_audio_freq_1(self, data):
        self.pre_write_generate_sound()
        self.freq[1]     = data & self.FREQ_DATA_MASK
        self.post_write_generate_sound()

    def write_audio_vol_0(self, data):
        self.pre_write_generate_sound()
        self.volume[0]   = data
        self.post_write_generate_sound()

    def write_audio_vol_1(self, data):
        self.pre_write_generate_sound()
        self.volume[1]   = data
        self.post_write_generate_sound()

    def step(self):
        pass

    def pre_write_generate_sound(self):
        pass

    def post_write_generate_sound(self):
        pass

    def handle_events(self, event):
        pass

class Stretch(object):
    def __init__(self):
        self.divisor           = 1000
        self.rate              =  200
        self.remainder         =    0
        self.source_pos_offset =    0

    def stretch(self, unstretched_source):
        # Maintain a source offset, if stretch is actually 'condense'
        source_pos = self.source_pos_offset
        stretched_result = []
        while source_pos < len(unstretched_source):

            if source_pos < len(unstretched_source):
                stretched_result.append(unstretched_source[source_pos])
            else:
                self.source_pos_offset = source_pos - len(unstretched_source)

            self.remainder += self.rate

            increment = int(self.remainder/self.divisor)
            self.remainder = self.remainder%self.divisor

            source_pos += increment

        return stretched_result

