import unittest
import pytari2600.graphics.pygamestella as pygamestella
import pytari2600.graphics.stella as stella
import pytari2600.clocks as clocks
import pytari2600.inputs as inputs

class DummyClocks(object):
    def __init__(self):
        self.system_clock = 0

    def set_system_clock(self,time):
        self.system_clock = time

class DummyAudio(object):
    def __init__(self, arg):
        pass

    def get_save_state(self):
        pass

    def set_save_state(self, dummy):
        pass

    def handle_events(self, dummy):
        pass

    def step(self):
        pass

    def write_audio_ctrl_0(self):
        pass

    def write_audio_ctrl_1(self):
        pass

    def write_audio_freq_0(self):
        pass

    def write_audio_freq_1(self):
        pass

    def write_audio_vol_0(self):
        pass

    def write_audio_vol_1(self):
        pass

class DummyInputs(object):
    def __init__(self):
        pass

    def get_save_state(self):
        pass

    def set_save_state(self, dummy):
        pass

    def handle_events(self, dummy):
        pass

    def step(self):
        pass
