from pytari2600.test.test_stella_replay import DummyClocks as DummyClocks
from pytari2600.test.test_stella_replay import DummyAudio as DummyAudio
from pytari2600.test.test_stella_replay import DummyInputs as DummyInputs
from pytari2600.graphics.pygamestella import PygameStella as stella

dummy_clock = DummyClocks()
dummy_inputs = DummyInputs()
stella_instance = stella(dummy_clock, dummy_inputs, DummyAudio) 

