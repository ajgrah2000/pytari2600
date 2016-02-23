class Clock(object):
    def __init__(self):
        self.system_clock = 0

    def get_save_state(self):
        return self.system_clock

    def set_save_state(self, state):
        self.system_clock = state
