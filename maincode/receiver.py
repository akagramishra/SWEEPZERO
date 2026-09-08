class Receiver:
    def __init__(self, env):
        self.env = env
        self.history = []

    def observe(self, band, timestep):
        value = self.env.ground_truth[band, timestep]
        self.history.append((timestep, band, value))
        return value

    def clear_history(self):
        self.history = []